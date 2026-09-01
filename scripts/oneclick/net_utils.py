# -*- coding: utf-8 -*-
"""共享 HTTP 辅助：统一 UA、超时、TLS 与解码策略。

代理策略：默认遵循 HTTP_PROXY/HTTPS_PROXY 环境变量；
需要显式代理时调用 set_proxy()（各脚本提供 --proxy 参数）。
TLS 默认校验证书，仅在网络中间人拦截等调试场景用 --insecure 关闭。
"""
import json
import ssl
import sys
import urllib.error
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
DEFAULT_TIMEOUT = 20


def setup_stdout_utf8():
    """Windows 控制台默认 GBK，统一重定向输出为 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8')
            except Exception:
                pass


def set_proxy(proxy_url):
    """安装显式代理；不调用时 urllib 自动遵循环境变量代理。"""
    if proxy_url:
        handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
        urllib.request.install_opener(urllib.request.build_opener(handler))


def make_ssl_context(insecure=False):
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_text(url, timeout=DEFAULT_TIMEOUT, insecure=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=make_ssl_context(insecure)) as resp:
        return resp.read().decode('utf-8', errors='replace')


def fetch_json(url, timeout=DEFAULT_TIMEOUT, insecure=False):
    return json.loads(fetch_text(url, timeout=timeout, insecure=insecure))


def check_url(url, timeout=8, insecure=False):
    """检查 URL 可访问性，返回 (status, detail)，status ∈ OK/EMPTY/ERROR/TIMEOUT。

    连接层错误（DNS/网络瞬断）自动重试一次；HTTP 状态码错误不重试。
    """
    if not url:
        return ('EMPTY', '无URL')
    last = ('ERROR', '未知错误')
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout, context=make_ssl_context(insecure)) as resp:
                code = resp.status
            if 200 <= code < 400:
                return ('OK', str(code))
            return ('ERROR', f'HTTP {code}')
        except urllib.error.HTTPError as e:
            return ('ERROR', f'HTTP {e.code}')
        except urllib.error.URLError as e:
            last = ('ERROR', f'无法连接: {str(e.reason)[:40]}')
        except TimeoutError:
            last = ('TIMEOUT', '超时')
        except OSError as e:
            last = ('ERROR', f'{str(e)[:40]}')
    return last
