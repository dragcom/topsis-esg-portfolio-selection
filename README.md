# Project Introduction

This project is part of BlendED's AI+X Project-Based Learning (PBL), under Track 3: Multi-Criteria Decision Making for Complex Business Problem.
The project develops an analytical framework for ESG-driven portfolio ranking, aiming to evaluate companies from both sustainability and financial performance perspectives. Instead of relying on a single ESG rating or a purely financial screening rule, this project integrates multiple data sources and applies a multi-criteria decision-making model to support more transparent and explainable portfolio selection.

## Project Motivation and Purpose

ESG-related information is often fragmented across corporate filings, ESG framework documents, public news, and financial datasets. This makes it difficult to evaluate companies consistently using both sustainability and financial criteria. Motivated by this challenge, this project applies Large Language Models (LLMs) to extract and integrate information from structured and unstructured sources.

This project uses LLM-assisted analysis to:

1. Identify ESG-related signals from corporate reports, methodology documents, and media coverage
2. Combine ESG insights with financial and market indicators for company-level evaluation
3. Generate portfolio rankings through a multi-criteria decision-making framework

These rankings can provide actionable insights for investors, asset managers, and sustainability analysts to screen companies, benchmark ESG-financial performance, and support more transparent investment decision-making.

## Literature Review

The direction of this project was guided by three key research studies:

1. [Pedersen et al. (2021)](https://doi.org/10.1016/j.jfineco.2020.11.001) developed the concept of the **ESG-efficient frontier**, showing that ESG can be incorporated into investment decisions together with return and risk. This supports the idea that ESG should not be treated only as an ethical preference, but also as a meaningful dimension in portfolio evaluation.

2. [Berg et al. (2022)](https://doi.org/10.1093/rof/rfac033) examined the divergence of ESG ratings across major rating agencies, finding that ESG disagreement mainly comes from differences in measurement, scope, and weighting. This motivates this project to avoid relying on a single black-box ESG score and instead construct a more transparent ESG evaluation framework from multiple information sources.

3. [Reig-Mullor et al. (2022)](https://doi.org/10.3846/tede.2022.17004) applied an AHP-TOPSIS-based approach to evaluate corporate ESG performance, demonstrating how multi-criteria decision-making methods can be used to assign indicator weights and rank companies across ESG dimensions.

Building on these findings, this project develops an ESG-driven portfolio ranking framework that integrates LLM-assisted information extraction, ESG and financial indicators, and the AHP-TOPSIS model. Compared with traditional ESG scoring approaches, this project highlights the use of Large Language Models to extract structured ESG signals from corporate filings, ESG framework documents, and public news, making the final ranking process more transparent, flexible, and explainable for portfolio screening and company benchmarking.

# Dataset Overview

# Methodology

## Multi-Criteria Decision-Making Model

This project uses an AHP-TOPSIS framework to transform ESG and financial indicators into an interpretable company ranking, where AHP assigns criterion weights and TOPSIS evaluates each company’s closeness to the ideal portfolio profile.

## Project Approach

### Data Processing and Integration

Corporate filings, ESG framework documents, public news, and market data were collected and integrated at the company level. Large Language Models were used to extract structured ESG-related information from unstructured text, while financial and market variables were cleaned and standardized for quantitative analysis.

Duplicated or inconsistent ESG indicators were merged into unified variables, and missing values were handled to construct a complete company-level decision matrix.

### Feature Engineering

Key features were created to capture both sustainability performance and financial performance, including:

- **ESG indicators**: Scope 1 emissions, renewable energy usage, female board representation, employee turnover, independent directors, pay ratio disclosure, human rights policy, and board diversity policy
- **Financial and market indicators**: stock return, volatility, risk-adjusted performance, market trend, and financial stability measures
- **Indicator directions**: benefit criteria where higher values indicate better performance, and cost criteria where lower values indicate better performance

These features were standardized and prepared as inputs for the multi-criteria ranking model.

### TOPSIS Model Construction

The final ranking model was built using an AHP-weighted TOPSIS procedure. AHP was first used to calculate the weights of ESG criteria across Environmental, Social, and Governance dimensions. Then TOPSIS was applied to normalize the decision matrix, construct positive and negative ideal solutions, calculate each company’s relative distance from both ideals, and generate a final ranking score.

A higher TOPSIS score indicates that a company is closer to the ideal ESG-financial investment profile. The model outputs the full company ranking, the top-ranked companies, company-level scores, and the AHP weights used in the ranking process.

# Results

# Conclusion

# Main Contributors

- [@Jairui-Han-123](https://github.com/Jiarui-Han-123)
- [@dragcom](https://github.com/dragcom)
- [@myj0725](https://github.com/myj0725)
