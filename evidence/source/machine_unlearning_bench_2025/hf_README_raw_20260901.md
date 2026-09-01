---
license: mit
size_categories:
- 10K<n<100K
---
Dataset for the evaluation of data-unlearning techniques using KLOM (KL-divergence of Margins).

# How KLOM works:
KLOM works by:
1. training N models (original models)
2. Training N fully-retrained models (oracles) on forget set F
3. unlearning forget set F from the original models
4. Comparing the outputs of the unlearned models from the retrained models on different points
  (specifically, computing the KL divergence between the distribution of _margins_ of oracle models and distribution of _margins_ of the unlearned models)

Originally proposed in the work Attribute-to-Delete: Machine Unlearning via Datamodel Matching (https://arxiv.org/abs/2410.23232), described in detail in E.1.

**Outline of how KLOM works:**
![Image 5-4-25 at 9.21 PM.jpg](https://cdn-uploads.huggingface.co/production/uploads/6625510c9277b825c8c71418/RcbE1ucGOYgTnoRJmSKa4.jpeg)


**Algorithm Description:**
![Image 5-4-25 at 9.24 PM.jpg](https://cdn-uploads.huggingface.co/production/uploads/6625510c9277b825c8c71418/N3vJmc6rfQ5MLMjXSCIGZ.jpeg)

# Structure of Data

The overal structure is as follows:
```
full_models
  ├── CIFAR10
  ├── CIFAR10_augmented
  └── LIVING17
oracles
└── CIFAR10
    ├── forget_set_1
    ├── forget_set_2
    ├── forget_set_3
    ├── forget_set_4
    ├── forget_set_5
    ├── forget_set_6
    ├── forget_set_7
    ├── forget_set_8
    ├── forget_set_9
    └── forget_set_10
```
Each folder has 

* train_logits_##.pt - logits at the end of training for model `##` for validation points
* val_logits_##.pt  - logits at the end of training for model `##` for train points
* `##__val_margins_#.npy` - margins of model `##` at epoch `#` (this is derived from logits)
* `sd_##____epoch_#.pt` - model `##` checkpoint at epoch `#`


# How to download



Create script `download_folder.sh`

```
#!/bin/bash
REPO_URL=https://huggingface.co/datasets/royrin/KLOM-models
TARGET_DIR=KLOM-models # name it what you wish
FOLDER=$1  # e.g., "oracles/CIFAR10/forget_set_3"

mkdir -p $TARGET_DIR

git clone --filter=blob:none --no-checkout $REPO_URL $TARGET_DIR
cd $TARGET_DIR
git sparse-checkout init --cone
git sparse-checkout set $FOLDER
git checkout main
```
 
Example how to run script:
```
bash download_folder.sh oracles/CIFAR10/forget_set_3
```


