# Data dictionary (panel file data/processed/wdi_panel.csv; one row per country-year, 120 rows)

Short names are used in code; the WDI series code is in brackets. All series come from the World Bank WDI extract; the original compiler is named in the metadata sheet.

- **country, code** (text): country name and ISO code (Pakistan PAK, India IND, Bangladesh BGD, Nepal NPL, Sri Lanka LKA). No regional aggregates.
- **year** (integer): 2000-2023.
- **u5mr** [SH.DYN.MORT] (number, deaths per 1,000 live births): probability a newborn dies before age five at that year's age-specific rates. Source: UN IGME. Caveat: modelled estimate, not a count; see CLEANING.md for the Sri Lanka spikes.
- **fem_sec_enrol** [SE.SEC.ENRR.FE] (number, % gross): female secondary enrolment divided by the female population of the official secondary age group. Source: UNESCO UIS. Caveats: can exceed 100 because of repeaters and overage pupils; 22 of 120 values missing.
- **gdp_pc_ppp** [NY.GDP.PCAP.PP.KD] (number, constant 2021 international $): GDP per person adjusted for purchasing power. Source: ICP and national accounts. Caveat: PPPs are extrapolated away from benchmark years.
- **log_gdp** (derived, natural log of gdp_pc_ppp): created in clean_and_eda.py.
- **health_exp_gdp** [SH.XPD.CHEX.GD.ZS] (% of GDP): current health expenditure. Source: WHO. **gov_health_exp_gdp** [SH.XPD.GHED.GD.ZS] (% of GDP): domestic general government health expenditure.
- **fertility** [SP.DYN.TFRT.IN] (births per woman): total fertility rate. Source: UN Population Division. Caveat: annual values are interpolated from five-year data.
- **sanitation** [SH.STA.BASS.ZS] and **water** [SH.H2O.BASW.ZS] (% of population): people using at least basic sanitation or drinking water services.
- **electricity** [EG.ELC.ACCS.ZS] (% of population): access to electricity.
- **measles_imm** [SH.IMM.MEAS] (% of children aged 12-23 months): measles immunisation.
- **urban_pct** [SP.URB.TOTL.IN.ZS] (% of total population): urban population share.
- **unemployment** [SL.UEM.TOTL.ZS] (% of labour force): modelled ILO estimate. Caveat: Pakistan jumps from 0.80 to 3.67 in 2012.
- **fem_literacy** [SE.ADT.LITR.FE.ZS] (% of females 15+): adult female literacy. Caveat: 62 of 120 missing; left out of models.
- **skilled_birth** [SH.STA.BRTC.ZS] (% of births): births attended by skilled health staff. Caveat: 72 of 120 missing; left out of models.
