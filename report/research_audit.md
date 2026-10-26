# Research audit — Tetouan electricity forecasting

**Audit completed before report drafting: 26 October 2026 (Asia/Saigon).** Scope: the repository snapshot, not a new experimental run. All six substantive source modules, `src/__init__.py`, eight notebooks (232 cells), README, requirements, runner, three Markdown documents, two PDF documents, two documentation CSVs, 47 result CSVs, two parameter JSONs, the raw dataset and 28 PNGs were inspected. No models were fitted. No existing project artifacts were changed.

PDF extraction succeeded with installed PyMuPDF: project guideline 21 pages; literature review 33 pages. Page-delimited extracts and notebook extracts (zero-based cell indices, code and saved text outputs) are in `evidence/`. Some mathematical glyphs in PDF extraction are fragmented; equations used in this report are reconstructed from Python implementation, not guessed from damaged extraction. Figures were visually inspected using five contact sheets. Image titles sometimes overstate causal conclusions; report captions explicitly qualify them.

Evidence hierarchy: executable implementation and saved numerical artifacts determine current methods/results; notebook commentary and current Markdown explain intent; progress logs and guideline PDF document earlier designs. External publisher/dataset pages establish bibliographic identity, not a matched replication. `evidence/source_manifest.json` records SHA-256 hashes. `evidence/table_inventory.json` inventories every CSV and selected search row. `evidence/numerical_checks.json` records 118 successful checks before drafting.

## 1. Confirmed objectives

The project evaluates conventional regressors for hourly total electrical load in Tetouan, with a midnight daily forecast using history at least 24 hourly indices old (h24), and an hourly updating short-horizon setting (h1). It asks whether ML improves on seasonal naive forecasts; which feature groups help; how temporal validation, tuning, residual targets and horizon affect performance; and how evaluation choices change apparent accuracy. These are empirical pipeline contributions, not a new learning algorithm. Sources: guideline PDF pp. 1, 5; literature-review PDF pp. 31–32; notebooks 02–08.

## 2. Dataset overview

- Local raw CSV: **52,416 data rows**, 2017-01-01 00:00 to 2017-12-30 23:50; continuous 10-minute intervals; **8,736 hourly means**, 364 days. Sources: `T01_data_quality.csv`, rows `Rows (10-min)`, `Rows (hourly)`, first/last timestamp; notebook 01 cells 4, 6; independently checked from raw CSV.
- UCI landing page and literature-review PDF p. 2 say **52,417**. Report uses the observed local count and explicitly records this discrepancy; header counting is a possible explanation, not established fact.
- Raw columns: DateTime, five weather/radiation variables, three zone loads. Repository units: temperature degrees Celsius, humidity percent, loads kW. UCI variable table does not supply units; wind and radiation units remain unspecified. No unverified physical unit is added.
- Zero missing values, duplicate rows/timestamps, irregular intervals and non-positive numeric values in the saved quality check. Longest constant run is nine samples. These checks establish structural regularity, not sensor correctness.
- Source statistics: `T01_descriptive_stats.csv` indexes each variable with mean/std/min/quartiles/max; these describe **10-minute whole-year** data, not hourly training data. Total mean 71,222.89034 kW (displayed rounded in report), range 36,785.03933–134,208.1489 kW; exact values always taken from CSV when typesetting.
- DQ01 is consistent with a zone redistribution on 20 April; grid-switching mechanism and outage duration are not independently confirmed. DQ02 is bimodal wind, not a proved sensor failure. Observations retained; no imputation, outlier deletion or clipping implemented.
- F01, F02, DQ02 and descriptive statistics include December; decision-oriented F03–F08 use January–November. Thus December was not literally unseen in all exploratory work.

## 3. Target and horizons

`src/data.py::load_raw` sums Z1+Z2+Z3; `to_hourly` averages six ten-minute records per left-labelled hour. The target is average power in kW, not a cumulative energy reading. No separate zone forecast experiment exists.

`src/features.py::make_features` retains y at target timestamp t and shifts predictors, rather than shifting the response forward. h24 is one pooled scalar regressor using the target hour's calendar, observed weather and y(t−24), y(t−48); forecasts can be assembled for all 24 hours at midnight. **The 24 is the minimum history lag, not a uniform 24-hour issuance-to-target lead.** Target intervals within a midnight batch start 0–23 hours after issuance. h1 predicts successive hourly intervals using the completed prior hour. Assume prompt measurement availability; no latency is modeled.

Test features include realized earlier December loads once they become available. This is daily/hourly updating evaluation with model weights fixed after development refit, not a month-long open-loop forecast from 1 December. Weather at target hour is observed (oracle weather), not a forecast archive. Sources: notebook 02 cell 3; notebook 07 cells 4, 6, 35; `features.py`.

## 4. Implemented feature groups

| Group | Contents | Use |
|---|---|---|
| Weather (5) | Temperature, Humidity, WindSpeed, GenDiffuse, Diffuse | Unshifted target-hour observations; operationally unavailable without forecasts |
| Calendar (7) | hour, dayofweek, is_weekend, hour_sin/cos, dow_sin/cos | Known at prediction time |
| Special days (3) | religious holiday, civil holiday, Ramadan | Hard-coded 2017 calendar; holiday effects inferred on development data |
| h24 daily lags (2) | lag_24, lag_48 | Selected set D, 17 columns total |
| h1 recent/daily lags (4) | lag_1, lag_2, lag_3, lag_24 | Selected h1 set, 19 columns total |
| Weekly/rolling (4) | lag_168, roll_mean_24, roll_std_24, roll_mean_168 | Built but excluded from main models; used in ablation/baselines |

Sets A/B/C/D/E/F have 5/12/15/17/21/16 columns. F is E without weather, **not D without weather**. Rolling statistics shift y by h first and cover [t−h−w+1,t−h]; pandas std uses sample denominator w−1. Built matrices have 21 h24 and 23 h1 columns. `dropna()` precedes main-column selection, so unused long rolling/lag columns still discard 191 h24 / 168 h1 initial rows. Sources: `src/features.py`, `T03_features.csv`, notebook 02 cells 5–10, notebook 06 cells 6–8.

No month/dayofyear, same-time zones, target, DST flag, time-zone conversion, imputer, weather prediction model or recursive forecasting exists in the main pipeline. Calendar month/dayofyear are not inherently leakage; their exclusion is a modeling choice. Their use in S1–S3 is separate.

## 5. Models

- L0: Naive-24h, Naive-168h, training-only mean profile per (hour, weekday), with global-mean fallback. h1 additionally uses Persistence (lag_1).
- Default LR: StandardScaler + ordinary least squares; tuned LR is **Ridge**, a changed regularized model family.
- DT: sklearn DecisionTreeRegressor, random_state 42; no explicit depth cap by default.
- RF: 100 trees by default, random_state 42; additional RF-P1 with 30 trees/max_features=7/unlimited depth/min split 2/min leaf 1.
- SVR: RBF kernel default estimator, input StandardScaler inside Pipeline, target StandardScaler inside TransformedTargetRegressor. C/epsilon operate on the scaled target.
- XGB: XGBRegressor, random_state 42; unspecified default parameters are inherited from the recorded dependency version, not invented here.
- Ten tuned variants per horizon: five absolute and five `DeltaTarget` variants. DeltaTarget fits y−lag_24 for h24 and y−lag_1 for h1, then adds the corresponding known lag during prediction. Base is also retained among features.

Sources: `src/models.py` (entire module), notebooks 03, 05–07. No ARIMA, SARIMA, Prophet, LSTM, fuzzy clustering, LightGBM or neural network is trained in this repository.

## 6. Data splitting and validation

| Setting | Training | November validation | Development | December test |
|---|---:|---:|---:|---:|
| h24 | 7,105 | 720 | 7,825 | 720 |
| h1 | 7,128 | 720 | 7,848 | 720 |

h24 begins 2017-01-08 23:00; h1 begins 2017-01-08 00:00. Train ends 31 October 23:00, validation 1–30 November, test 1–30 December. Exact rows/dates: `T02_split_summary.csv`, keyed by scenario/set; `src/config.py`, `src/evaluate.py::split_masks`.

Five expanding folds, each 720 validation hours, gap=0. h24 train counts 4,225 / 4,945 / 5,665 / 6,385 / 7,105. Validation windows: 4 July–2 August, 3 August–1 September, 2 September–1 October, 2–31 October, 1–30 November. All end at 23:00; all start at 00:00. Source `T02_cv_folds.csv`, fold rows 0–4. h1 validation windows identical; h1 training contains 23 additional January hours. Last L2 fold reproduces L1 for the eight shared models/baselines (checked).

Each fold is fitted once, with histories updating inside its validation window. The no-gap configuration is documented, but no gap sensitivity experiment is stored. The guideline's claim that adding gap=24 barely changes results is **unverified**. EDA, feature choice, residual-base choice and hyperparameter selection reuse development data; no nested CV. Fold standard deviations describe temporal variation, not confidence intervals or independent-replicate uncertainty.

## 7. Hyperparameter search

RandomizedSearchCV, fixed seed 42, five same temporal folds, four scorers, `refit=False`; manually choose minimum `rank_test_RMSE`. Candidates per model **and target formulation and horizon**: LR 20, DT 40, RF 30, SVR 30, XGB 50. Each horizon therefore has 340 candidates × 5 = 1,700 CV fits across ten searches; two horizons 3,400, excluding other experiments. Same parameter samples for absolute/delta versions. Inner estimators single-threaded; search parallelism uses `TETOUAN_N_JOBS` (default −1).

All 20 `search_*.csv` files read and checked: candidate counts, finite selected scores, selected parameters matching both JSONs, all five selected folds matching T07/T10. Exact ranges: `src/models.py::search_spaces` and `T06_search_space.csv`; selected 38 parameters per horizon in JSONs. XGB integer high bounds exclusive (200–1499 trees, depth 3–10, min child weight 1–10). Search `std_test_RMSE` is population SD; report fold summaries use pandas sample SD, ddof=1. No second grid search, Bayesian search or early stopping was implemented.

Supplementary notebook 08 KFold comparison is a distinct **20-candidate RF search**, not the 30-candidate L3 RF result.

## 8. Metrics

RMSE and MAE in kW; MAPE = mean(abs(error/y))×100; R² relative to the evaluation subset's own target mean. Zero-target protection absent in custom MAPE; observed targets positive. sklearn scorer MAPE is converted from ratio to percent. Skill = 1−RMSE/model-reference RMSE. L2/ablation skill averages per-fold ratios; T07/T08 may use ratios of aggregate RMSEs. These are distinct summaries. Residual convention prediction−actual. Mean bias, MAE/mean load, runtime and validation/train RMSE ratio are supplementary diagnostics, not extra selection criteria. No significance tests or prediction intervals.

## 9. Key results and numerical source map

All paths below are relative to `results/tables/`. Rounding for report: kW mostly 1 decimal, percentage 2 decimals, R² 4 decimals; source precision retained in CSVs. Every generated numeric table has a direct source mapping in `table_sources.json` (created during typesetting); all key narrative numbers are mapped here.

| Claim | Verified value | Exact source / selector |
|---|---|---|
| November best default | XGB RMSE 2161.4 kW | `T04_level0_level1_wide.csv`, XGB, val_RMSE |
| November seasonal naive | 3076.4 kW RMSE | same, Naive-24h |
| DT improves November RMSE slightly | 2992.4 kW; 2.73% reduction | same, DT, val_RMSE and skill_vs_naive24 |
| Best default temporal CV | LR 2792.3 ± 623.3 kW | `T05_level2_summary.csv`, LR, RMSE_mean/std |
| CV naive | 3392.3715 ± 421.5468 kW | same, Naive-24h |
| Best tuned h24 CV | SVR 2410.6 ± 766.3 kW | `T07_default_vs_tuned.csv`, SVR, tuned_RMSE_mean/std |
| Next h24 CV candidates | SVR_delta 2427.1164; RF_delta 2429.3333; XGB_delta 2441.0037 kW | same, matching rows |
| SVR tuning reduction vs default | 39.2594% (round 39.26%) | same, SVR, improvement_% |
| Residual targets improve 4/5 h24 families | LR, DT, RF, XGB; SVR absolute slightly better | same, paired rows |
| RF daily lags C→D | 9168.1→3010.4 kW; −67.16% change | `T09_ablation_summary.csv`, model RF, sets C/D |
| XGB daily lags C→D | 8740.2→3009.9 kW; −65.56% change | same, XGB, C/D |
| RF weekly/rolling D→E | 3010.4→3700.3 kW; +22.92% change | same, RF, D/E |
| XGB weekly/rolling D→E | 3009.9→4921.4 kW; +63.51% change | same, XGB, D/E |
| Weather removal E→F | RF +1.592%, XGB +1.945%, RF_delta +5.314%, XGB_delta −0.905% | same, each F row, delta_% |
| Best h1 CV | SVR 1866.42295 kW; 22.5741% below h24 SVR | `T10_horizon.csv`, SVR, h1_RMSE/h24_RMSE; computed ratio |
| Final selected h24 SVR | RMSE 1624.6 kW; MAE 1094.6 kW; MAPE 1.78%; R² 0.9869 | `T08_final_test.csv`, SVR-tuned; exact values typeset from CSV |
| h24 naive and skill | RMSE 3296.29170; selected SVR reduction 50.71310% | same, Naive-24h and SVR-tuned, skill_vs_naive24 |
| Lowest observed h24 test error (not selected) | SVR_delta-tuned RMSE 1419.05936 | same, SVR_delta-tuned |
| Final selected h1 SVR | RMSE 1195.8 kW; MAE 861.8 kW; MAPE 1.41%; R² 0.9929 | `T08_final_test_h1.csv`, SVR-tuned; exact values typeset from CSV |
| h1 metric-dependent ranking | SVR best RMSE; XGB_delta best MAE/MAPE | same, five tuned rows |
| h1 improvement | about 63.72% vs Naive-24h; 78.16% vs Persistence | same, SVR-tuned, skill columns |
| Selected h24 residual bias/range | −202.1019 kW; −9362.1186 to +6514.2441 kW | `T08_test_predictions.csv`, SVR-tuned minus actual; notebook 07 cells 13/17 |
| December mean load | 63750.82717 kW | same, mean(actual) |
| Worst day | 1 December MAE 4579.2, bias −3616.7 kW (rounded) | `T08_worst_days.csv`, 2017-12-01 |
| Monday MAE | SVR 1007 vs naive 5294 kW (rounded) | notebook 07 cell 22 output; derivable from predictions |
| Fold 0 distribution shift | training maximum 110710.5 kW, validation maximum 133129.8 kW; 12.22% of validation hours exceed the training maximum | raw CSV hourly means with T02 fold0 dates; `numerical_checks.json` |
| Leakage S1/S2/S3/S4 RMSE | 1325.295 / 619.978 / 643.969 / 2017.092 kW (rounded) | `T12_leakage_settings.csv`, setting rows |
| KFold experiment | CV 2007.61679, test 2173.57888 kW; +8.26662% | `T12b_kfold_vs_tscv.csv`, KFold (shuffled) |
| TSCV experiment | CV 3012.38092, test 2044.17374 kW; −32.14093% | same, TimeSeriesSplit |
| Survey | 10 GitHub entries, 7 marked shuffled=yes | `docs/kaggle_survey.csv`; exact copy T11 |

Numerical spot-check values in this prose are rounded guides; exact CSV-derived tables govern final formatting. `check_evidence.py` independently recomputes all 18 h24 prediction columns, allows 0.001 kW/0.000001 percentage-point/1e−8 R² serialization tolerance for XGBoost, and verifies worst days. h1 individual predictions were not saved, so h1 test metrics cannot be independently reconstructed without retraining (not performed).

## 10. Best-performing models by setting

- L1 November: XGB has lowest RMSE/MAE/MAPE among compared L1/L1b models; no selection based on December.
- L2 default CV: LR lowest mean RMSE; RF lowest mean MAPE. LR has smallest RMSE SD among default ML models; seasonal naive has smaller SD overall.
- L3 h24 CV: SVR lowest mean RMSE; RF_delta lowest mean MAE/MAPE (check raw T07 when reporting). Four leading RMSE means differ by only 30.41 kW (1.26% of best), much less than between-fold SD. No statistical equivalence or significance established.
- h24 ablation: RF_delta on D has lowest mean RMSE among tested ablation configurations.
- h1 CV: SVR lowest mean RMSE, including all tuned variants and baselines.
- h24 test: lowest observed RMSE SVR_delta-tuned; **pre-test rule selects SVR-tuned**. h1 test: selected SVR lowest RMSE, XGB_delta lower MAE/MAPE. Final selected SVR hyperparameters happen to be identical across horizons: C=26.92646910086177, epsilon=.01, gamma=.006338653441536257; independent saved searches confirm this.

## 11. Leakage, mitigation and interpretation

Confirmed protections: chronological development/test boundaries; lag asserts and shifted rolling windows; 200 random lag/rolling recomputations for each horizon; intentional unshifted-rolling negative test; training-fitted scalers and profile; model selection expression references stored development CV only. The static final notebook computes test results before printing selection, but `CHOSEN` depends only on CV; chronological execution order alone is not proof of pre-registration.

Remaining assumptions/risks: oracle target-hour weather; immediate load availability; full-year descriptive EDA; reuse of development folds for feature and hyperparameter selection; fixed 2017 holiday list; repeated December execution in progress log. Main evaluation is conditional on those assumptions, not unconditionally leakage-free.

S1/S2: raw 10-minute rows after one initial drop; shared random 75/25 split (39,311 train, 13,104 test), same tuned absolute RF. S1 uses five weather and eight calendar columns; S2 adds lag_10min. S3 uses 48,095 past train rows and 4,320 December test rows; removes dayofyear but **retains month/day/weekofyear/quarter**, adds lag_10min. S4 has 7,825/720 rows and 17 h24 features. RF settings fixed (200 trees, depth 30, minimum leaf 2, max_features .8); same fractional max_features can imply different feature counts with different input dimensions.

S1–S4 confound split, resolution, target averaging, features, test population and forecast horizon. Therefore they do not estimate a pure causal leakage penalty. Short horizons and known calendar information are not themselves leakage. S1's lack of load lags does not logically preclude forecasting if covariates are available; observed future weather is the critical availability qualification. RMSE/MAE share kW units across settings but describe different temporal targets; dimensionless MAPE/R² do not repair comparability.

The supplementary KFold comparison controls data/features/search budget more closely, although validation distribution and training sizes differ. Its observed 8.27% optimism and worse December model are one experiment, not a universal calibration law. The leakage investigations run after final analysis and reuse December; they are diagnostic, not an additional independent test.

## 12. Contradictions resolved and limitations

1. **52,417 vs 52,416:** actual local data determine sample count; UCI metadata discrepancy retained.
2. **DT does not beat baseline:** stale notebook/document prose says this; current November table shows DT RMSE 2992.4 < 3076.4, but MAPE 3.345 > 3.267. Report states metric-specific result.
3. **Test exactly once:** contradicted by progress sections `Hoàn thiện repo để nộp` and `Sửa cách diễn đạt so sánh literature`, and result.md §11.5. Multiple unchanged-pipeline reruns reported. Report describes held-out model-selection intent; independent one-shot secrecy cannot be certified from snapshot.
4. **All tuned versions beat naive on CV:** false; absolute DT tuned mean 3589.7 > 3392.4. At least one tuned variant per family beats baseline; all tuned h24 versions beat it on December.
5. **All tree models cannot exceed target range:** applies to standard averaging DT/RF, not generally additive XGBoost; RBF SVR is not strictly bounded by training y. Poor extrapolation is a plausible mechanism, not a proof for every estimator.
6. **Oracle-weather optimism small:** E/F ablation covers RF/XGB with extra weekly/rolling features; no weather-free D or selected-SVR ablation. Cannot quantify deployed SVR penalty from these results.
7. **Every relative version improves every ablation:** XGB_delta on F (3928.4) is slightly below E (3964.2), unlike general prose; report keeps exact results. Fixed D-selected hyperparameters also favor D in final ablation; no per-set retuning.
8. **Early progress values differ:** recorded earlier E-feature searches are historical; final T04–T10 values take precedence. All-model D/E and residual-base side experiments are described in result.md §11.2–11.4 but no standalone raw fold/search files remain; treat as documented rationale, not independently auditable current experiment.
9. **h1 LR selection:** progress rounded it to LR; actual selection is LR_delta, only ~0.000494 kW better CV. No practical difference claimed.
10. **Feature label `full`:** many result rows inherit default logging label even though notebooks pass D to models. Actual columns established from MF and source, not that metadata string.
11. **Plan vs implementation:** PDF uses combined is_holiday, same hyperparameters for h1, and optional GridSearch. Current implementation uses separate holiday types, independent h1 search and no grid search. T13 is now literature comparison, not the planned contribution table; F09 pipeline figure absent. Neither missing planned artifact is fabricated.
12. **Unit/measurement semantics:** no wind/radiation units, no time-zone/DST provenance, no measurement latency or archived weather forecasts; the naming of general/diffuse flows should not be reinterpreted as a verified specific radiation component.
13. **No demonstrated significance/generalization:** one year, one city, one 30-day test; overlapping training folds; no uncertainty intervals, multi-year validation, deployment cost experiment or matched external replication.
14. **Reproducibility scope:** dependencies pinned in requirements (Python 3.12) and seed 42; no environment lock with hashes, hardware details, fitted model artifacts or h1 individual predictions. Local review environment is Python 3.13 and is used only for reading/checking; no claim of retraining reproducibility is made.

## 13. Claim/source map and bibliography verification

| Report topic | Primary repository evidence |
|---|---|
| Motivation, questions, original plan | Guideline PDF pp. 1–5; literature review pp. 25–32 |
| Preprocessing and target | `src/data.py`; notebook 01 cells 4–8 |
| EDA seasonality/correlations/autocorrelation | notebook 01 cells 17–43 and F01–F08; T01 descriptive data |
| Feature equations and availability | `src/features.py`; notebook 02 cells 3–10 and 20–24; T03 |
| Split and folds | `src/config.py`, `src/evaluate.py`; notebook 02 cells 12/14; T02 |
| Baseline definitions and predictions | `src/models.py`; notebook 03 cells 6/9/11/13; T04 |
| Default temporal CV | notebook 04 cells 6/8/11/13/19; T05 |
| Search and target variants | `src/models.py`; notebook 05 cells 4/6/8/10/13/15; all h24 search CSVs + JSON |
| Ablation and h1 tuning | notebook 06 cells 6/8/14/16; T09/T10, h1 searches + JSON |
| CV-based final choice | notebook 07 cells 11/35; T07/T10 |
| Final errors and timings | notebook 07 cells 6/8/13/17/22/25/35; T08 files |
| Tree explanations | notebook 07 cells 28/30/32; F19a–c; no SHAP-value CSV available |
| Literature performance | literature review p.22 Table7; docs/literature_results.csv; T13; external verification record |
| Online-code survey | docs/kaggle_survey.csv and T11 (repository-authored survey, not freshly reproduced) |
| S1–S4 and CV-method diagnosis | notebook 08 cells 9/11/17; T12/T12b |
| Development history, reruns, unarchived trials | docs/progress.md; docs/result.md §11 |

Verified primary landing pages include UCI dataset DOI 10.24432/C5B034; RoSe et al. 2023 (Atlantis Press, DOI 10.2991/978-94-6463-314-6_7); da Silva/Meneses 2023 (publisher search record, Energy Reports, DOI 10.1016/j.egyr.2023.09.175); Islam et al. 2025 (Springer, online 2024, volume year 2025, DOI 10.1007/s11135-024-02043-0); Alsalem 2025 (Scientific Reports DOI 10.1038/s41598-025-91123-8); Biswas et al. 2026 (publisher search record, DOI 10.1016/j.rineng.2026.110289). Salam/El Hibaoui 2018 identity is corroborated by UCI's introductory-paper record; DOI and settings are in local literature review pp.16,32; IEEE blocks full inspection. Claims sourced only to the local review are explicitly marked as review-reported, not primary-paper revalidation.

External corrections: Islam's abstract describes individual zones and their **average**; the CSV's selected metric row says target not stated, so attribution of that particular row remains unresolved. Biswas publisher text reports RF hourly-mean MAE 224.2, MAPE 1.04 and RMSE 294.59, but repository comparison has missing RMSE; retain it as unavailable in repository table and do not invent a matched horizon. P2 numerical/textual optimizer inconsistency flagged in local review remains unresolved. P3 has no numeric row in docs/literature_results.csv; discuss validation design, mark metrics unavailable. Verified method references: Bergstra/Bengio (JMLR, random search), Chen/Guestrin (arXiv 1603.02754), Lundberg/Lee (arXiv 1705.07874), scikit-learn TimeSeriesSplit and common-pitfalls official pages. No paper citation is fabricated.

## 14. Missing information requiring clarification

Student/team names, IDs, contributions, instructor and submission date remain placeholders. Institutional/course names follow the user instruction. No clarification is needed to draft the technical report. For a stronger scientific claim, authors would need measurement/issuance conventions and latency, weather forecasts available at issuance, precise hardware and environment provenance, archived side-experiment outputs, h1 predictions, additional seasonal/yearly test data, and primary-paper setup details. None is fabricated or regenerated.

## Audit gate

**Complete.** Repository inspection, evidence hierarchy, numerical consistency checks, source mapping, discrepancy resolution and missing-information inventory are complete. LaTeX drafting may now begin using this audit. No claim of successful PDF compilation is made: latexmk, pdflatex, xelatex, biber and tectonic were not found on PATH or in checked standard TeX install locations.

## Integration errata and environment update — 26 October 2026

The audit retains the original pre-drafting findings; the final peer review reconciled the affected main-table values with the source CSVs. This addendum records the earlier precision corrections. Final integration uses current CSV precision, correcting a few excess decimal places in the narrative spot checks without changing the findings or rerunning experiments:

- T04 XGB November RMSE is 2161.4126887025045 kW; DT is 2992.4315853832245 kW.
- T05 default LR mean/sample SD are 2792.3146020254835 / 623.251239778452 kW. The 2792.3154060132715 kW value belongs to tuned absolute Ridge in T07, not default OLS.
- T07 selected h24 SVR sample SD is 766.3404466532597 kW.
- T08 selected h24 SVR MAE is 1094.6134337374006 kW and MAPE is 1.7781093247166837%. T08 h1 SVR RMSE/MAE/MAPE are 1195.8381545129091 kW / 861.7540597648533 kW / 1.409707944739095%.
- Fold-0's 12.2222% means the fraction of validation observations exceeding the training maximum, not the relative difference between training and validation maxima.

These corrections leave the report's one-decimal kW/two-decimal percentage findings unchanged. Other tables are generated directly from their source files. MiKTeX executables are now discoverable under `D:\MiKTeX`; an actual compilation attempt with automatic installation disabled stopped at missing `geometry.sty`. No software/packages were installed and no PDF compilation success is claimed. See `validation_summary.md` for the final integration checks and build status.

## Final peer-review finding

An index-only reconstruction of notebook 08 confirms that S2 places 9,834 of its 13,104 held-out response values into lag inputs of successor training rows. This arises because the lag is constructed before the shuffled split. Section 11 now distinguishes this verified cross-boundary dependency from legitimate chronological history updates. It does not estimate the resulting score inflation or change any stored experiment. See `evidence/peer_review_checks.json` and `FINAL_REVIEW.md`.
