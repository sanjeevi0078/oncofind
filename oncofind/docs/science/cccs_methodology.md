# Cross-Cancer Consistency Score (CCCS) Methodology

## Introduction

Biomarker discovery in oncology is often hampered by tumor heterogeneity and study-specific batch effects. A common challenge is determining whether a candidate biomarker represents a fundamental pan-cancer oncogenic driver or is merely an artifact of a single study or tissue type.

The **Cross-Cancer Consistency Score (CCCS)** is a novel quantitative metric designed to rank and prioritize genes based on their differential expression consistency, dysregulation magnitude, clinical survival relevance, and statistical significance across multiple independent cancer types.

---

## Mathematical Formulation

For a given gene $G$ evaluated across a set of $N$ cancer types, the CCCS is defined as a weighted sum of four sub-scores:

$$CCCS(G) = w_1 \cdot S_{\text{dir}}(G) + w_2 \cdot S_{\text{mag}}(G) + w_3 \cdot S_{\text{surv}}(G) + w_4 \cdot S_{\text{sig}}(G)$$

Where:
- $w_1 = 0.25$ (Directionality Weight)
- $w_2 = 0.25$ (Magnitude Weight)
- $w_3 = 0.35$ (Survival Significance Weight)
- $w_4 = 0.15$ (Statistical Significance Weight)

The survival significance is weighted highest ($0.35$) because clinical translatability is the ultimate goal of biomarker discovery; a candidate gene must correlate with clinical outcome (overall survival) to be actionable.

### 1. Direction Score ($S_{\text{dir}}$)

The direction score measures the degree to which a gene is consistently upregulated or consistently downregulated across the tested cancers. Let $U$ be the number of cancer types where $G$ is significantly upregulated ($p_{\text{adj}} < 0.05, \log_2FC > \text{threshold}$), and $D$ be the number of cancer types where $G$ is significantly downregulated ($p_{\text{adj}} < 0.05, \log_2FC < -\text{threshold}$).

$$S_{\text{dir}}(G) = \frac{|U - D|}{N}$$

- **Range**: $[0, 1]$
- **Interpretation**: A score of $1.0$ indicates that the gene is altered in the same direction in all tested cancers. A score of $0.0$ indicates either that the gene is not significant in any cancer, or that its upregulation in some cancers is perfectly balanced by downregulation in others (mixed/contradictory signals).

### 2. Magnitude Score ($S_{\text{mag}}$)

The magnitude score measures the average effect size (absolute fold change) in cancer types where the gene is significantly dysregulated. Let $K$ be the set of cancer types where $p_{\text{adj}} < 0.05$, and $M$ be the size of $K$.

$$\text{Mean FC}(G) = \frac{1}{M} \sum_{c \in K} |\log_2FC_c|$$

If $M = 0$, $S_{\text{mag}}(G) = 0$. Otherwise, the score is normalized to $[0, 1]$ using a sigmoid function:

$$S_{\text{mag}}(G) = \frac{\text{Mean FC}(G)}{\text{Mean FC}(G) + 1.0}$$

- **Range**: $[0, 1)$
- **Interpretation**: Standardizes fold changes. An average fold change of $1.0$ (two-fold change) maps to $0.5$, whereas an average fold change of $3.0$ maps to $0.75$, and a fold change of $9.0$ maps to $0.90$.

### 3. Survival Score ($S_{\text{surv}}$)

The survival score measures the proportion of cancer types where the expression of the gene significantly predicts overall survival (log-rank $p < 0.05$). Let $S$ be the number of cancers where the log-rank p-value is significant.

$$S_{\text{surv}}(G) = \frac{S}{N}$$

- **Range**: $[0, 1]$
- **Interpretation**: Measures the clinical translatability. A score of $1.0$ means high and low expression groups have statistically distinct survival outcomes in all tested cancers.

### 4. Significance Score ($S_{\text{sig}}$)

The significance score reflects the statistical strength of the differential expression tests. To prevent extremely low p-values from dominating the score, the adjusted p-values are clipped to a minimum of $10^{-15}$, and the negative $\log_{10}$ is averaged and normalized:

$$\text{Mean Significance}(G) = \frac{1}{N} \sum_{c=1}^N -\log_{10}(\max(p_{\text{adj}, c}, 10^{-15}))$$

$$S_{\text{sig}}(G) = \frac{\text{Mean Significance}(G)}{\text{Mean Significance}(G) + 2.0}$$

- **Range**: $[0, 1]$
- **Interpretation**: A mean $p_{\text{adj}} = 0.01$ yields a score of $0.5$. A mean $p_{\text{adj}} = 10^{-6}$ yields $0.75$.

---

## Final Composite Score & Breadth Scaling

After computing the weighted raw score, the final Cross-Cancer Consistency Score (CCCS) is scaled by the fraction of tested cancer types in which the gene is statistically significant ($p_{\text{adj}} < 0.05$):

$$\text{CCCS}(G) = \text{RawScore}(G) \times \frac{N_{\text{significant}}}{N}$$

Where:
- $N_{\text{significant}}$ is the number of cancers where the gene has significant differential expression ($p_{\text{adj}} < 0.05$).
- $N$ is the total number of cancer types tested.

### The Double-Penalization Design Choice
This formulation introduces a **double-penalization** for genes that are non-significant in some cancers:
1. **Within Component**: The direction score $S_{\text{dir}}$ is normalized by the total number of tested cancers $N$, meaning that non-significant cancers reduce the maximum achievable direction score.
2. **Final Scaling**: The overall composite score is multiplied by the ratio of significant cancers to total cancers $\frac{N_{\text{significant}}}{N}$.

This mathematical design is an intentional choice to enforce high selectivity for pan-cancer biomarkers. In multi-cohort biomarker discovery, false positives are easily inflated if a gene is highly significant in only one cancer type but has weak or non-significant signals in others. By applying a multiplicative breadth penalty, we ensure that:
- A gene with extremely high significance in only 1 of 5 cancers is heavily penalized and ranked lower.
- Only genes with consistent, significant, and survival-associated signals across a broad range of cancers achieve high CCCS scores.
- For single-cancer analyses ($N=1$), this scaling naturally evaluates to $1.0$, bypassing the penalty.

---

## Validation Controls

To verify the scientific validity of the score, two standard control experiments are conducted:

1. **Pan-Cancer Positive Control (e.g., $TP53$, $MYC$)**
   - **Hypothesis**: Key oncogenes and tumor suppressors involved in cell cycle control and genome stability are altered across a wide variety of tissues.
   - **Expectation**: CCCS $\ge 0.70$.
2. **Tissue-Specific Negative Control (e.g., $ESR1$)**
   - **Hypothesis**: The estrogen receptor gene ($ESR1$) is heavily dysregulated in breast cancers (BRCA) but does not serve as a consistent biomarker in lung (LUAD) or colon (COAD) cancers.
   - **Expectation**: CCCS $< 0.30$.
3. **Citation Benchmark Correlation**
   - **Hypothesis**: Genes with higher CCCS scores should correlate with the volume of cancer biomarker literature.
   - **Expectation**: A Spearman rank correlation coefficient $\ge 0.80$ between CCCS and historical literature citation count.

