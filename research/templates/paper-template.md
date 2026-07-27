---
title: "Your Paper Title Here"
authors:
  - name: "Author One"
    org: "Institution or Organization"
    email: "author@example.com"
  - name: "Author Two"
    org: "Institution or Organization"
date: "YYYY-MM-DD"
category: "Large Language Models"   # Pick from: Large Language Models, Machine Learning, Deep Learning,
                                     # Reinforcement Learning, Computer Vision, Natural Language Processing,
                                     # AI Alignment, Interpretability, Cognitive Architectures,
                                     # Synthetic Intelligence, Federated Learning, Ethics
tags:
  - "Tag1"
  - "Tag2"
  - "Tag3"
hasDataset: false       # true if you include a dataset in research/datasets/
hasCode: false          # true if you link a code repository
license: "CC BY 4.0"
---

## Abstract

Write a 150–250 word abstract here. Summarize the problem, approach, key results, and conclusions.

---

## 1. Introduction

Introduce the problem domain and motivation. Explain why this work matters and what gap it fills.

### 1.1 Background

Provide necessary background and related work references.

### 1.2 Contributions

List your primary contributions:

- **Contribution 1:** Brief description
- **Contribution 2:** Brief description
- **Contribution 3:** Brief description

---

## 2. Methodology

Describe your approach in detail.

### 2.1 Problem Formulation

Define the problem formally. You can include math using LaTeX syntax:

Inline math: $f(x) = \sum_{i=1}^{n} w_i x_i$

Display math:

$$
\mathcal{L}(\theta) = -\sum_{i} y_i \log p_\theta(y_i | x_i)
$$

### 2.2 Approach

Describe your method. Include figures, tables, and code snippets as needed.

```python
# Example code block — Python, JavaScript, and other languages are syntax-highlighted
def example_function(x):
    return x * 2
```

---

## 3. Experiments

### 3.1 Setup

Describe your experimental setup: hardware, datasets used, evaluation metrics.

### 3.2 Results

Present your results in a table:

| Model | Metric A | Metric B | Metric C |
|:------|:--------:|:--------:|:--------:|
| Baseline | 72.1% | 45.3% | 0.81 |
| **Ours** | **83.4%** | **59.7%** | **0.91** |

### 3.3 Ablation Study

*(Optional)* Describe ablation experiments that validate your design choices.

---

## 4. Discussion

Interpret your results. Discuss limitations, failure modes, and potential societal impact.

---

## 5. Conclusion

Summarize the key takeaways and suggest directions for future work.

---

## References

1. Author, A. & Author, B. (Year). *Title of Paper*. Conference/Journal. [link]
2. Author, C. (Year). *Title of Paper*. Conference/Journal. [link]

---

## Dataset

*(Include this section if `hasDataset: true`)*

Link to the dataset in `research/datasets/your-dataset-name/` or provide an external DOI.

**Access:** [Dataset Repository](https://example.com)  
**License:** CC BY 4.0  
**Size:** XX MB  
**Format:** CSV / JSON / HDF5

---

## Code

*(Include this section if `hasCode: true`)*

**Repository:** [https://github.com/your-org/your-repo](https://github.com)  
**License:** MIT / Apache-2.0  
**Requirements:** Python 3.10+, PyTorch 2.x

```bash
# Reproduce main results
git clone https://github.com/your-org/your-repo
cd your-repo
pip install -r requirements.txt
python train.py --config configs/main.yaml
```
