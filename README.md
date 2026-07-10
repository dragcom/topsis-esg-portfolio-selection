# Project Introduction

This project is part of BlendED's AI+X Project-Based Learning (PBL), under Track 3: Multi-Criteria Decision Making for Complex Business Problem.
The project develops an analytical framework for ESG-driven portfolio ranking, aiming to evaluate companies from both sustainability and financial performance perspectives. Instead of relying on a single ESG rating or a purely financial screening rule, this project integrates multiple data sources and applies a multi-criteria decision-making model to support more transparent and explainable portfolio selection.

## Project Motivation and Purpose

ESG-driven investment decisions require reliable information from multiple sources, including regulatory filings, institutional ESG datasets, public media coverage, and market performance data. However, these data are often fragmented, inconsistent, and reported in different formats, making it difficult to build a clean and comparable company-level evaluation framework.

Motivated by this challenge, this project develops an automated **Azure cloud ETL pipeline** to extract, transform, and standardize data from diverse financial, ESG, media, and market sources. The pipeline improves data quality through automated cleaning, synchronization, and relational code mapping before loading the processed data into an **Entropy-Weighted TOPSIS** multi-criteria decision-making model.

The final rankings can provide actionable insights for investors, asset managers, and sustainability analysts to screen companies, benchmark ESG-financial performance, and support more transparent investment decision-making.

## Literature Review

The direction of this project was guided by three key research studies:

1. [Pedersen et al. (2021)](https://doi.org/10.1016/j.jfineco.2020.11.001) developed the concept of the **ESG-efficient frontier**, showing that ESG can be incorporated into investment decisions together with return and risk. This supports the idea that ESG should not be treated only as an ethical preference, but also as a meaningful dimension in portfolio evaluation.

2. [Berg et al. (2022)](https://doi.org/10.1093/rof/rfac033) examined the divergence of ESG ratings across major rating agencies, finding that ESG disagreement mainly comes from differences in measurement, scope, and weighting. This motivates this project to avoid relying on a single black-box ESG score and instead construct a more transparent ESG evaluation framework from multiple information sources.

3. Recent MCDM studies, including [López-García et al. (2025)](https://doi.org/10.1007/s10479-023-05543-8), [Garcia-Bernabeu et al. (2024)](https://doi.org/10.1016/j.orp.2024.100305), and [Lu et al. (2023)](https://doi.org/10.3390/su151612235), show that multi-criteria decision-making methods can be used to evaluate ESG performance, rank companies, and incorporate different preferences or uncertainty in sustainable investment decisions. In particular, UW-TOPSIS and robust preference-based MCDM approaches motivate this project to move beyond traditional subjective AHP weighting and adopt a more data-driven entropy-based TOPSIS model.

Building on these findings, this project develops an ESG-driven portfolio ranking framework that integrates an automated Azure cloud ETL pipeline, multi-source ESG and financial indicators, controversy signals, and an entropy-based TOPSIS model. Compared with traditional ESG scoring approaches, this project highlights automated data extraction, transformation, synchronization, and relational code mapping across regulatory filings, institutional datasets, media coverage, and market data. The inclusion of controversy information further improves the framework by capturing public risk signals and reputational events that may not be fully reflected in conventional ESG or financial indicators.

# Dataset Overview

The dataset used in this project was extracted, transformed, and standardized through an automated **Azure cloud ETL pipeline**.

## ESG-Financial Integrated Dataset

| Aspect | Details |
|---|---|
| Description | This dataset integrates ESG, financial, media, and market information from multiple sources into a standardized company-level dataset. <br>The original data were collected from four major sources: <br>- **Regulatory financial data** from SEC EDGAR Form 10-K filings, audited financial statements, operational metrics, and corporate risk disclosures<br>- **Institutional financial and ESG data** from SEC XBRL, Alpha Vantage, World Bank, Kaggle, and company overview datasets<br>- **Public media coverage** from NewsAPI and Alpha Vantage news reports capturing corporate events, public perception, and market sentiment<br>- **Quantitative market performance data** from Yahoo Finance, including historical prices, trading volume, volatility, and valuation signals|
| Useful Columns |- Company identifiers<br>- ESG indicators<br>- Financial indicators:  profitability indicators, growth indicators, financial health indicators, market performance variables<br>- Risk measures<br>- Controversial News|

# Methodology

## Multi-Criteria Decision-Making Model

This project uses an Entropy-Weighted TOPSIS framework to transform ESG and financial indicators into an interpretable company ranking, where Entropy-Weighted and TOPSIS evaluates each company’s closeness to the ideal portfolio profile.

## Project Approach

### Feature Engineering

Key features were selected to capture ESG quality, financial fundamentals, market performance, and risk exposure. The final indicator framework includes:

- **ESG quality indicators**: environmental Kaggle score, social Kaggle score, and governance quality
- **Financial performance indicators**: return on equity, return on assets, profit margin, revenue growth, and earnings growth
- **Financial health indicators**: debt-to-equity ratio and current ratio
- **Market performance indicators**: one-year stock return and market capitalization
- **Risk indicators**: beta and 30-day price volatility
- **Controversy indicator**: negative news or controversy count, used separately as a penalty adjustment

Each indicator was classified as either a **benefit indicator**, where higher values represent better performance, or a **cost indicator**, where lower values represent better performance. The selected variables were then normalized and prepared as the company-level decision matrix.

### Entropy-Weighted TOPSIS Model Construction

The final ranking model was built using an **Entropy-weighted TOPSIS** procedure. Unlike traditional AHP-based weighting, the entropy method assigns weights based on the information contained in the data. Indicators with greater variation across companies receive higher weights, while indicators with limited differences receive lower weights.

The model construction follows the workflow below:

[![Entropy-Weighted TOPSIS Workflow](figures/entropy_weighted_topsis_workflow.png)](figures/entropy_weighted_topsis_workflow.png)

A higher TOPSIS score indicates that a company is closer to the ideal ESG-financial investment profile.

### Controversy Penalty Adjustment

After the initial TOPSIS ranking, a controversy penalty was applied to capture negative public information and reputational risk. The controversy indicator is not included directly in the TOPSIS decision matrix. Instead, it is used as a separate adjustment based on negative news exposure.

The adjusted score reflects both the company’s ESG-financial performance and its controversy risk. The final output includes the adjusted company ranking, TOPSIS scores, controversy-adjusted scores, and final investment ranking.

# Results

## Ranking

![Top 5 vs Bottom 5 Technology Companies](figures/top5_vs_bottom5_technology_companies.png)

The ranking results show a clear performance gap between the top-ranked and bottom-ranked technology companies under the controversy-adjusted entropy-weighted TOPSIS framework. 
Among the **top 5 companies**, **Dell** ranks first with the highest adjusted TOPSIS score of **0.506**, showing a substantial lead over the rest of the sample. **Seagate** ranks second with a score of **0.277**, followed by **NVIDIA** with **0.239**. **Micron** and **Alphabet (Google)** are closely matched, both achieving an adjusted TOPSIS score of **0.224**.

These top-ranked companies generally demonstrate stronger overall investment attractiveness because they perform well across multiple objectives, including ESG quality, financial performance, market strength, risk exposure, and controversy management, rather than excelling in only one dimension. In particular:

- **Dell** shows the strongest overall balance across ESG, financial, market, and risk-related indicators.
- **Seagate** performs well due to its comparatively stable sustainability and governance profile.
- **NVIDIA** benefits from strong market performance and innovation leadership.
- **Micron** and **Alphabet (Google)** remain competitive, although their final scores are affected by weaker performance in some dimensions or controversy-related adjustments.

By contrast, the **bottom 5 companies** have much lower adjusted TOPSIS scores. These companies are not necessarily poor firms overall, but they rank lower within this specific multi-criteria framework because they are farther from the ideal ESG-financial investment profile.

Their weaker performance may be related to:

- **Lower ESG-financial balance**: weaker performance in one or more ESG, financial, market, or risk dimensions reduces their overall closeness to the ideal company profile.
- **Less differentiated indicator performance**: some firms may perform adequately but do not stand out strongly on the high-weight criteria identified by the entropy method.
- **Cumulative TOPSIS penalties**: small disadvantages across several indicators can accumulate and lead to a much lower final adjusted score.
- **Niche or specialized positioning**: companies in narrower technology segments may score less competitively under a broad technology-sector comparison framework.

From a decision-making perspective, this task is primarily a **ranking problem**, because the objective is to order companies according to their relative investment attractiveness. It is different from a simple **sorting problem**, which would only classify companies into groups such as high, medium, and low performers, and it is also different from a **design problem**, which would focus on creating an optimal portfolio structure from scratch.

The results also reflect a multi-objective optimization logic. The model does not maximize financial return alone, nor does it select companies based only on ESG performance. Instead, it evaluates tradeoffs among **cost, quality, sustainability, risk, and public controversy exposure**. This makes the framework useful for real-world investment, operations, and policy-related challenges where decision-makers must balance profitability with long-term responsibility and resilience.

## Importance

![Entropy-Weighted Contribution](figures/entropy_weighted_contribution.png)

The entropy-weighted results show that **Environmental** factors receive the largest contribution (**25.3%**), followed by **Profitability** (**21.2%**), **Market performance** (**18.3%**), and **Social** indicators (**17.0%**). **Growth** contributes **10.0%**, while **Financial health** (**4.9%**), **Risk** (**2.3%**), and **Governance** (**1.1%**) receive relatively smaller weights.

This distribution indicates that the model places greatest emphasis on dimensions that provide stronger discriminatory power across firms. In particular:

- **Environmental performance** emerges as the most influential dimension, suggesting that sustainability-related indicators play a central role in distinguishing company quality.
- **Profitability** and **market performance** also carry substantial weight, showing that financial fundamentals remain critical in investment ranking.
- **Social performance** contributes meaningfully, reinforcing the importance of broader stakeholder-related considerations.
- The relatively smaller weights for **governance**, **risk**, and **financial health** suggest that these indicators show less variation across the sampled firms, and therefore contribute less to differentiation under the entropy-weighting scheme.

Overall, the importance analysis confirms that the final ranking is driven by a combination of sustainability and financial dimensions, rather than by any single criterion alone.

## Sensitivity

![Sensitivity Analysis of Controversy Penalty](figures/sensitivity_analysis_controversy_penalty.png)

The sensitivity analysis evaluates how company rankings change as the **controversy penalty parameter** \\(\lambda\\) increases from **0.10** to **0.40**. The results show that the model is generally robust, with the top-ranked firms maintaining relatively stable positions across different penalty settings.

Several patterns stand out:

- **Dell** remains ranked **1st** throughout the full range of penalty values, indicating strong robustness.
- **Seagate** consistently holds the **2nd** position, suggesting that its ranking is not highly sensitive to controversy adjustments.
- **NVIDIA** remains near the top, with only a modest shift from **3rd** to **4th** at higher penalty levels.
- **Alphabet (Google)** fluctuates only slightly, moving between **4th** and **5th**.
- **Micron** shows the largest movement, improving from **6th** to **3rd** as the parameter changes, indicating higher sensitivity relative to the other firms.

These results suggest that the framework is **stable at the top of the ranking**, while still remaining responsive to controversy-related adjustments. In other words, the model does not produce arbitrary ranking changes when the penalty parameter varies, which supports the robustness of the controversy-adjusted investment ranking approach.

# Conclusion

This project provided valuable experience in automated data integration, ESG-financial feature engineering, and multi-criteria decision-making, including building an Azure cloud ETL pipeline and transforming raw ESG, financial, market, and media data into standardized company-level indicators. More importantly, the results demonstrate how entropy-weighted TOPSIS can be used to generate transparent, data-driven portfolio rankings that balance sustainability performance, financial fundamentals, market risk, and controversy exposure.

A key contribution of this project is the integration of **controversy adjustment** into the ranking process. Instead of relying only on conventional ESG and financial scores, the model also considers negative news exposure and reputational risk, allowing the final ranking to better reflect potential downside ESG risks.

The ranking results and sensitivity analysis generated in this project have important real-world applications. They can support investors, asset managers, and sustainability analysts in screening technology companies, benchmarking ESG-financial performance, identifying firms with stronger long-term resilience, and managing downside risks related to corporate controversies. By linking ESG quality, financial performance, market signals, and public media information into one decision framework, this project highlights the potential for scalable, data-driven strategies to support more responsible and explainable investment decision-making.

# Main Contributors

- [@Jairui-Han-123](https://github.com/Jiarui-Han-123)
- [@dragcom](https://github.com/dragcom)
- [@myj0725](https://github.com/myj0725)
