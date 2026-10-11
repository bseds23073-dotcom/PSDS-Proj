PROJECT PROPOSAL
Mustafa Shahid – BSEDS 23073
Ayan Mahmood – BSEDS 23073

Lane

Development.

Framing Formula

For developing countries with available world bank WDI data from 2000-2023, predict under the
age of 5 – mortality rate (deaths per 1000 live births) using female education, economic, health,
demographic and infrastructure indicators, with a target RMSE below 15 deaths per 1000 live
births on the framed dataset, so that development and public health policy makers can identify
important factors associated with child mortality and explore possible development scenarios.

Stakeholder
1. Development Organizations within Countries
2. International development organizations and bureaus.
Users
Policy analysts and development researchers.

Problem type.

Regression and Causal analysis.

Sampling Frame + Who&#39;s Missing

The data will consist of country-year observations for developing countries from 2000–2023,
subject to the availability of the required World Bank World Development Indicators.
https://databank.worldbank.org/source/world-development-indicators#
Countries and years with substantial missing data may be excluded. Countries with weaker
statistical reporting may therefore be underrepresented in the final dataset.

Baseline

The baseline will predict the training-set mean under-5 mortality rate for every test observation.
The machine-learning models must improve upon this baseline using RMSE, MAE, and R².

FP/FN Cost Analysis + Metric

Since this is a regression problem, traditional false-positive and false-negative classification
costs do not directly apply.
Over prediction: May cause analysts to overestimate the level of child-mortality risk.
Under prediction: May cause analysts to underestimate the level of child-mortality risk and
potentially overlook areas requiring attention.
Therefore, the primary evaluation metric will be RMSE, with MAE and R² reported as
supporting metrics. The target is RMSE &lt; 15 deaths per 1,000 live births on the held-out test set.
The causal analysis will be evaluated separately and will not treat predictive accuracy as
evidence of causality.

Variables
World Bank WDI Variables Used to Predict Under-5 Mortality

Variable WDI Indicator

Under-5 mortality Mortality rate, under-5

Female secondary enrollment School enrollment, secondary, female (% gross)

GDP per capita GDP per capita, PPP (constant 2021 international $)

Current health expenditure Current health expenditure (% of GDP)

Fertility rate Fertility rate, total (births per woman)

Basic sanitation People using at least basic sanitation services (% population)

Basic drinking water People using at least basic drinking water services (%

population)

Electricity access Access to electricity (% population)

Measles immunization Immunization, measles (% children ages 12–23 months)

Urban population Urban population (% total population)

Female literacy Literacy rate, adult female (% females 15+)

Skilled birth attendance Births attended by skilled health staff (% total)

Unemployment Unemployment, total (% labor force), modeled ILO estimate

Government health
expenditure

Domestic general government health expenditure (% GDP)
