# Presentation evidence map

Audit date: 28 October 2026, Asia/Saigon. Evidence inspection completed before slide drafting. No experiment or notebook was executed and no model was trained.

## Paths, version and evidence hierarchy

- Workspace: `C:/Users/Giang Hoang Son/OneDrive/Desktop/nam 3 ki 1/statistic/`.
- ML evidence: **`Prj Tetouan ML/Machine-Learning/`**, abbreviated **ML** below. The outer `Machine-Learning/` was not used.
- Report: **`Tetouan-ML-Report/`**, abbreviated **R**. The originally requested nested report path does not exist. The user explicitly authorized this existing root-level repository instead.
- All new artifacts are in **R/slides/**. No Git configuration, branch, remote, source report, experimental artifact or dataset was changed.
- `R/report/README.md` identifies the active report as the shortened ten-section version dated 28 October. `main.tex`, all ten included sections, the supplementary appendix, referenced tables and bibliography were read.
- `FINAL_REVIEW.md`, `research_audit.md` and `validation_summary.md` describe the earlier 54-page draft. Their separate h1 search/test results, obsolete baseline inventory and section counts are **not current presentation evidence**. Their methodological cautions were checked against the current source.
- Current ML README, guideline, result summary, requirements, runner, source modules and relevant notebook code were inspected. Current saved CSVs and executable definitions take priority over narrative summaries.

## Slide-by-slide map

All T-prefixed files below are in **ML/results/tables/**. Source functions were under **ML/src/** at the time of the audit; they now live inside the two notebooks (`01_data_eda_features.ipynb`, `02_models.ipynb`). Slides use one decimal for headline kW, two for MAPE and four for R²; chart rankings use whole kW. Exact data remain in the original CSVs. `metrics.tex` is generated from those CSVs.

| Slide | Claim / displayed result | Evidence and interpretation |
|---|---|---|
| 1 | University, faculty, course, exact title/subtitle, names, IDs, DS66A, instructor | User's supplied identity. Logo is `R/report/assets/fda-logo.png`, proportional. No submission date. |
| 2 | Three research questions: beat seasonal baselines; useful features; tuning/target effects | Active report sections 01, 06, 07; current ML guideline. No operational savings claimed. |
| 3 | Three-zone sum; mean of six samples; 52,416 records × 9 columns (timestamp, 5 weather, 3 zones); 8,736 hourly rows; Jan 1–Dec 30, 2017 | `data.py::load_raw/to_hourly`; `T01_data_quality.csv`; verified by read-only raw-data aggregation. Target is mean hourly power, in repository kW convention, not cumulative kWh. Energy over an hour is mean power × 1 h. F01 is whole-year descriptive context, including December. |
| 4 | Minimum 06–07h, peak 19–20h; summer curve higher | `R/results/figures/F03_profile_by_season.png`, notebook 01, development-only hourly profiles independently recomputed. No causal cooling or zone-transfer mechanism is asserted. |
| 5 | ACF: 24 h .98, 48 h .96, 168 h .95; lag12 negative; daily-lag feature takeaway | F07_acf_total.png, January-November EDA. Team explicitly supplied .96 for 48 h; saved docs/result.md rounds 48 h to .97. Supplied .96 retained and discrepancy disclosed. No numeric lag12 value is added. |
| 6 | Sunday -5.9% average, about -15% at 7-8 h; Saturday mornings -4 to -6%; weekday/hour interaction | F04_heatmap_hour_weekday.png, notebook 01 same-hour Mon-Fri normalization. Presentation-only right-panel view uses the same raw-data aggregation; Sunday recomputes -5.911697985%, Sunday 7-8 h -14.8501/-15.0160%. |
| 7 | Religious holidays 3–13% below the surrounding 15-day median (about −9% on average); civil about −3%; Ramadan night load +32,000 kW at 02:00 with 1.9 °C temperature difference | F08_weekday_holiday.png and F05_ramadan_profile.png, notebook 01 Part 1 (January–November). Per-day deviations: Eid al-Fitr −8.1/−12.5%, Eid al-Adha −13.4/−7.6%. Ramadan − 4 weeks before at 02:00: +32,142 kW. Holiday dates from the official 2017 calendar, known in advance. |
| 8 | Conceptual h24 midnight batch and h1 hourly update; load/weather availability | features.py MODEL_FEATURES and notebook 06. The saved CV performance comparison is now on slide 13. h24 interval starts are 0-23 hours after issuance and completions 1-24 hours. |
| 9 | h24 uses 17 inputs: 5 original (weather) + 12 engineered (calendar 7 from the timestamp, special-day flags 3 from the 2017 calendar, lags 2 from past load) | `features.py`, `T03_features.csv`; set D. Weather is unshifted target-hour observed weather. Weekly and rolling features are built but excluded from D. Rolling uses shift before aggregation; full-matrix dropna removes 191 h24 hours. |
| 10 | Jan–Nov development 7,825 hours; Dec 1–30 test 720; five expanding folds of 720 validation hours | `T02_split_summary.csv`, `T02_cv_folds.csv`, `evaluate.py::make_tscv/split_masks`. Chronological model selection; no gap; no nested CV. Diagram rebuilt using exact CSV dates, without the original F10's misleading “untouched” label. |
| 11 | Naive-24h/168h; LR/Ridge, DT, RF, RBF SVR, XGB; absolute and residual formulations | `models.py::baselines/default_models/search_spaces/DeltaTarget`; residual is y(t)−y(t−24), prediction adds lag24 back. Standard DT/RF averages are bounded by training targets; this does not generally apply to additive boosted trees or RBF SVR. |
| 12 | July range shift: training max 110710.546885, validation max 133129.826080 kW; 12.2222% above training max; 0% outside training residual range | Read-only aggregation of the saved raw CSV with T02_cv_folds.csv fold 0 boundaries. Residual is hourly y minus lag24. T07_level3_cv.csv fold0: RF 5553.542991 / RF_delta 3215.034756; XGB 5343.910907 / XGB_delta 2979.494346. Target variants separately tuned, not a pure target-only intervention. |
| 13 | All ten tuned h24 CV means and sample SDs; absolute SVR 2410.6 ± 766.3; close residual alternatives | `T07_level3_cv.csv`, `T07_default_vs_tuned.csv`; recomputed five-fold means/SDs and matched selected search rows. Naive-24h mean 3392.371548 from T05/T08 CV estimate. SD is temporal fold variability, not a confidence interval. Same folds choose and report configurations. No statistical superiority claim.; Tuning evidence formerly on a separate slide: Random search counts 20/40/30/30/50 per target type; SVR C 26.926469, gamma .006338653, epsilon .01; tuning gain 39.2594% vs default absolute SVR ; `T06_search_space.csv`, `best_params.json`, `search_SVR.csv`, `T07_default_vs_tuned.csv`; notebook 05 uses minimum mean CV RMSE. Input and target scaling are training-fitted. Epsilon is in standardized-target units. Other parameters vary in the search; no single-parameter causal explanation is claimed. ; Default November XGB winner: T04_level0_level1_wide.csv; default CV LR 2792.3146 and Naive24 3392.3715: T05_level2_summary.csv. Search count is 20+40+30+30+50 =170 per target type. |
| 14 | Absolute RF ablation A-E; set D selected; XGB D/E deterioration | T09_ablation_summary.csv and notebook 06. RF means: 15010.333548, 10040.891213, 9168.127031, 3010.367718, 3700.299837; feature counts 5/12/15/17/21. Successive changes -33.1068%, -8.6921%, -67.1649%, +22.9185%. XGB D/E 3009.858081/4921.389583. D-tuned parameters fixed. Compact table replaces dense F15; no experiment rerun. |
| 15 | Selected SVR December RMSE 1624.640103, MAE 1094.613434, MAPE 1.778109%, R² .986864384; 50.7131% gain vs Naive-24h 3296.291702; 37.9873% vs Naive-168h 2619.849090 | `T08_final_test.csv`; metrics independently reconstructed from `T08_test_predictions.csv`. `SVR_delta-tuned` has test RMSE 1419.059364 but CV 2427.116361, so does not replace the CV-selected model. Notebook 07's selection expression references CV even though its test computations appear earlier in notebook order. This is an implemented selection rule, not proof of prospective registration. |
| 16 | Actual vs selected-SVR December; residual = forecast−actual; bias −202.101864 kW; worst day December 1 MAE 4579.182293 kW | All 720 rows in `T08_test_predictions.csv`, `T08_worst_days.csv`. Rebuilt aligned full-month load/residual panels. Highlighted day matches repository religious-holiday flag. Holiday heterogeneity is a plausible interpretation, not a proven cause. |
| 17 | Published Tetouan studies (values as reported, not re-run): RoSe 2023 R² 0.976 (Total, no past load, 70/30 order not stated); Islam 2025 MAPE 6.3%, R² 0.853 (10 min ahead, 75/15/10 chronological); Alsalem 2025 R² 0.989 (Zone 3, 10 min ahead); Biswas 2026 MAPE 1.04% (mean of 3 zones, chronological, horizon not stated); this study MAPE 1.78%, R² 0.987 (day-ahead) | Course literature review Table 7 and report Table "Published studies" (`report/sections/02_related_work.tex`); `reference_verification.md`. Islam target of the selected row is unclear, so shown as "not stated". Salam & El Hibaoui 2018 (RMSE only, target unclear) and da Silva & Meneses 2023 (no metric in the review) are named in the slide note. Positioning only, no ranking. The leakage diagnostic (T12, T12b) moved to Q&A 10. |
| 18 | Weather, load latency, test exposure and generalization limitations | `features.py` uses target-hour observations; notebook 07 uses observed earlier December loads, fixed fitted weights. `docs/result.md` §10.5 records reruns, and full-year F01/F02 show December. One city, one year, one 30-day test. No weather-forecast archive, live latency study, multi-year validation or prediction intervals.; Findings: Daily-history evidence and careful model-selection interpretation ; T09 RF absolute C→D 9168.127031→3010.367718 kW (67.1649% lower); XGB C→D 8740.175427→3009.858081 (65.5630% lower). D-tuned parameters held fixed; ablation is RF/XGB, not selected SVR. T07/T08/T10 support other recap claims. ; Reruns and monthly history-update details retained in notes and Q&A. |
| 19 | Main conclusion and Q&A | Restates selected-SVR December result and its oracle-weather / one-period qualifications. Future work is proposed, not completed. |

## Corrections to source prose retained in this presentation

1. **h24 is not a common 24-hour lead.** With left-labelled hourly intervals and issuance at midnight, interval starts are 0–23 hours after issue and completions are 1–24 hours after issue. History lags are target-relative. A pooled model uses lags ≥24 for the whole batch; that is a conservative design rule, not a necessity for every individual hour. h1 forecasts the next complete hourly interval with the previous completed-hour mean assumed available.
2. **Chronological does not imply fully available inputs.** Target-hour observed weather is an oracle-information condition for both settings. Missing forecast-weather evaluation prevents estimating the deployed accuracy penalty. The main load-history construction itself does not use future load relative to daily/hourly issuance under zero latency.
3. **December was not certified single-use.** Current ML result history records reruns and annual descriptive plots include December. The final code selects by development CV; the snapshot does not certify a pristine prospective holdout. No claim that test reuse definitely changed model choice is made.
4. **No h1 December result in the current scope.** Earlier report audits contain 1195.8 kW and independently tuned h1 variants; these are historical and excluded. Current h1 residual variants retain lag24 as the residual base.
5. **No global tree extrapolation theorem.** Standard DT/RF averaging is range-bounded; additive XGBoost need not be. Residual targets provide a useful moving reference, with empirical improvements, not a guarantee.
6. **No “all tuned models beat naive on CV.”** Absolute tuned DT is worse than Naive-24h on CV. At least one tuned variant per family beats it; the complete CV ranking makes this visible.
7. **No causal leakage effect from S1–S4.** Even dimensionless metrics do not remove differences in task/population. Short horizons and calendar features are not inherently leakage. S3 still has the observed-weather limitation.
8. **No SHAP attribution to SVR.** F19a–d explain residual RF/correction, not the selected SVR. The 18-slide deck omits SHAP to prioritize residual motivation and ablation within 15 minutes. F19a and F19b also differ in file hashes between repositories; all other 22 common figures match. No quantitative SHAP claim is used.
9. **No causal holiday explanation.** Mawlid is the observed worst day. Transfer from other holiday patterns is a plausible hypothesis requiring an ablation or additional years.
10. **No weather-free-SVR conclusion from E/F.** E/F tests RF/XGB with weekly/rolling features, fixed D-selected parameters; it cannot quantify weather value for selected SVR on D.
11. **No claim of statistical significance or universal generalization.** Closely spaced means and large fold SDs motivate caution, not a formal equivalence result. CV reuse is not nested validation.
12. **UCI count discrepancy.** UCI metadata lists 52,417 instances; local CSV has 52,416 data rows. The slides use the verified local count. UCI variable metadata leaves units unspecified; kW follows the project convention, with no invented wind/radiation units.

## Visual provenance

Eight plotted data visuals and one ablation table are shown in the 18-slide deck. All original figures were inspected or cross-checked by hash; selected originals were visually inspected.

| Visual | Location | Provenance |
|---|---|---|
| Annual hourly load | `results/figures/F01_total_hourly_year.png` | Original report figure, exact hash match with ML. Centred seven-day smooth is descriptive only, not a predictive feature. |
| Seasonal daily profiles | `results/figures/F03_profile_by_season.png` | Original report figure, exact hash match, Jan–Nov only. |
| Chronological folds | `slides/figures/chronological_cv.pdf` | Exact T02 fold dates; neutral December label; folds 0-4 match report section 05 and the saved CSV. |
| CV ranking | `slides/figures/cv_ranking.pdf` | T07 ten tuned candidates; ± sample SD; T05 naive reference. |
| December comparison | `slides/figures/december_comparison.pdf` | T08 selected model, both seasonal baselines, observed test-best residual SVR. |
| December load and residuals | `slides/figures/december_trace.pdf` | All 720 saved forecasts, no smoothing or selective window. |
| Ablation table | slides/main.tex, slide 14 | T09 absolute RF A-E plus XGB D/E; fixed D-tuned parameters. Older ablation plot is retained as an unused supporting asset. |

`build_assets.py` only reads existing data and results, performs arithmetic, and writes charts/macros/checks inside slides. It does not import project modules (which could create output directories) or fit estimators. PNG previews accompany vector PDFs.

## Verification and preservation

`verification.json` records checks of all 17 saved model/baseline prediction columns (four metrics each), ten CV summaries, winning search scores and their five folds, data counts/target aggregation, worst day, source figure matches, and the original-file manifest. XGBoost serialization differences are tolerated at 0.001 kW, 0.000001 percentage point, and 1e−8 R²; displayed precision is unaffected.

`original_files_manifest.json` hashes 194 pre-existing files in both authorized repositories, excluding Git internals. It was captured before creating the presentation assets. Final verification compares these hashes and checks for new files outside slides. Git status was blocked by ownership safeguards; Git configuration was not changed to work around it. Filesystem hashes provide the preservation check instead.

## Primary citations checked

- Salam, A. and El Hibaoui, A. (2018), *Power Consumption of Tetouan City*, UCI Machine Learning Repository, [DOI 10.24432/C5B034](https://doi.org/10.24432/C5B034). [UCI record](https://archive.ics.uci.edu/dataset/849/power+consumption+of+tetouan+city) checked for identity, variable inventory and metadata discrepancy.
- Bergstra, J. and Bengio, Y. (2012), *Random Search for Hyper-Parameter Optimization*, JMLR 13, 281–305. [Publisher record](https://jmlr.org/papers/v13/bergstra12a.html) supports the method identity, not this project's numerical results.
- scikit-learn developers, [TimeSeriesSplit documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html), accessed 28 October 2026. Current project configuration is established from local `evaluate.py`.

No literature performance ranking or unmatched external benchmark result is presented.

## Incremental revision verification - 29 October 2026

- Current deck: 18 main slides, no backups, 900 seconds. Minh 1-9; Son 10-18. Handover remains after chronological CV.
- Slide 13 contains the saved h24/h1 comparison: 2410.592800 to 1866.422951 kW, 22.5741% lower. Same validation dates and h24-selected parameters; h1 histories and initial training row count differ. It is not an isolated horizon effect.
- Top-four CV spread is **1.2615524%**, displayed as 1.3%. No significance test is claimed.
- E/F weather removal changes absolute RF by +1.5920%, absolute XGB +1.9453%, residual RF +5.3145%, residual XGB -0.9046%. The maximum absolute change is **5.3%**, not strictly at most 5%. This cannot establish weather value for the selected SVR on D.
- No saved weekly-only ablation was located in current tables, notebooks or report. D/E jointly adds lag168, rolling mean24, rolling SD24 and rolling mean168. The deck does not assert that weekly lag alone is neutral or rolling means alone caused the loss.
- Rolling-level extrapolation is a possible mechanism. RF/DT range bounds do not apply generally to additive XGBoost. Small RBF gamma does not imply a mathematically linear SVR.
- Slide 16 presents Eid-to-Mawlid transfer as a possible explanation only. No causal holiday claim is made.
- Bergstra and Bengio (2012) is visible on slide 13. Internal paths remain here rather than in visible slide footers.
- FDA logo is the existing report/assets/fda-logo.png; the requested alternate filename logo-fda.png is absent.

Final revision validation: 18 compiled PDF pages; 900 seconds in slide comments and presenter notes; folds 0-4; no visible internal source footers; headline December metrics checked in extracted PDF text. All 18 rendered pages were inspected, with slide 9 rechecked after its final spacing change. No overfull/underfull box warnings remain. All 194 original-file hashes match the preservation manifest.

## EDA expansion and model condensation - current revision

Two EDA slides follow the seasonal profile. Tuning is merged into CV results (slide 12); findings and limitations are merged (slide 17). Total 18 slides, 900 seconds; handover remains after the chronological CV title (now slide 9). Title page and the six model/result frames marked for preservation retain their content. Test-rerun and load-history-update caveats remain in notes and Q&A. Internal source footers remain absent; Bergstra and Bengio (2012) stays visible on the CV slide. The F04 original is unchanged; refresh_eda_view.py redraws only its right-panel values with slide-size labels.

Projection-figure detail: F07 is shown through slides/figures/acf_view.pdf, using the same biased ACF definition as notebook 01 and larger labels. Read-only recomputation gives lags 24/48/168 = 0.9770493217/0.9652388248/0.9470116842. Displayed values remain the team's requested .98/.96/.95; nearest-two-decimal rounding would give .97 at lag48. Original F07/F04 PNGs remain unchanged. The right-panel F04 derivative uses the exact same-hour Mon-Fri normalization.

Current EDA/model-merge validation: 18 PDF pages and 900 seconds in both frame comments and presenter notes; handover after slide 9; nine slides per presenter. All 18 rendered pages inspected, with slides 6, 12 and 17 rechecked at higher resolution after final spacing changes. Final log has no overfull/underfull box warnings; headline December numbers are unchanged; all 194 original-file preservation hashes match.

29/10 revision: 19 slides, 900 seconds. New slide 7 (holidays and Ramadan); slide 9 feature table split into original vs engineered inputs; slide 3 shows 52,416 × 9; slide 17 replaces the leakage diagnostic with the comparison against published studies. Handover after slide 10: Son 1–10, Minh 11–19. Compiled without overfull boxes; changed pages inspected visually.
