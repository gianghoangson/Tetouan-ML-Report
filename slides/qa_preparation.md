# Q&A preparation

Use the short answer first; expand only if asked. All numerical values below refer to the current saved evidence in the authorized ML repository. See `evidence_map.md` for exact source files.

## 1. Why did you choose SVR rather than random forest or XGBoost?

**Short answer:** Tuned absolute-target RBF SVR had the lowest mean development CV RMSE: 2,410.6 kW.

Residual SVR, RF and XGB scored 2,427.1, 2,429.3 and 2,441.0 kW respectively. The differences are small relative to fold variation; no significance test establishes SVR's superiority. RBF SVR models nonlinear relationships, with C controlling the penalty for errors outside its epsilon-insensitive region and gamma controlling kernel locality. We did not select it because of December. Source: T07 and `models.py`.

## 2. Why scale both SVR inputs and its target? What does epsilon 0.01 mean?

**Short answer:** Input scaling makes feature distances comparable; target scaling makes C and epsilon operate on a stable scale.

The pipeline fits `StandardScaler` to training inputs, and `TransformedTargetRegressor` fits a separate training-target scaler. Predictions are returned to kW. Selected parameters are C = 26.926469, gamma = 0.006338653 and epsilon = 0.01. Epsilon is 0.01 in standardized-target units, not 0.01 kW. Its equivalent kW width depends on the training-target standard deviation of each fit. All scaling is trained inside each CV fold. Source: `models.py`, best_params.json.

## 3. Is h24 really a 24-hour-ahead forecast?

**Short answer:** It is a midnight batch with target-relative history lags of at least 24 hours, not a common 24-hour issuance lead.

At midnight on day D, the batch forecasts that day's hourly mean powers. With left-labelled intervals, their starts are 0–23 hours after issue; their completions are 1–24 hours after issue. For the final hour, lag24 is the previous day's 23:00–24:00 mean, assumed immediately available. Earlier hours could theoretically use shorter lags, but the pooled implementation uses lag24/48 throughout. h1 updates for the next complete hourly interval using the previous completed-hour mean. Clock provenance and measurement latency are not established by the dataset.

## 4. Why TimeSeriesSplit? Why no 24-hour gap?

**Short answer:** Expanding folds train on earlier observations and validate on the next 30 days, matching the direction of forecasting.

Five folds lie entirely in January–November; December is excluded from selection. The first validation period is July 4–August 2 and the last is November. `gap=0` assumes observations up to the boundary are promptly available and the model can be ready at issuance. Target-relative lag checks alone do not establish realistic measurement or refitting latency. We did not perform a gap sensitivity experiment. Hyperparameters and features reuse development folds, so the reported CV scores have selection bias and the fold SDs are not confidence intervals.

## 5. What is the target, and why are the errors in kW rather than kWh?

**Short answer:** We predict the mean hourly power of the three-zone sum.

For each hour, add zone powers at each of six ten-minute timestamps, then average those six sums. Averaging and summing zones commute. kW is power; kWh is energy. Multiplying the hourly mean power by the one-hour duration gives the corresponding energy approximation, numerically equal for this particular interval but with a different physical unit. RMSE and MAE retain the target's kW units. The local CSV has 52,416 data rows and 8,736 hourly means; UCI metadata says 52,417, a discrepancy explicitly retained in the audit. kW follows the repository convention; UCI's variable table does not document units.

## 6. Why show two naive baselines, and what does the 50.7% gain mean?

**Short answer:** Naive-24h copies the same hour yesterday; Naive-168h copies the same hour last week. The 50.7% figure specifically uses Naive-24h's December RMSE.

Compute `100 × (1 − 1624.640103 / 3296.291702) = 50.7131%`. The weekly baseline is stronger in December, with RMSE 2,619.849090 kW; the selected SVR improves on it by 37.9873%. We present both references. This gain is different from the 39.3% tuning gain versus default SVR on CV and from the 22.6% h1/h24 CV contrast. A lag1 persistence baseline would be useful for h1 but is absent from the current comparison; we do not claim superiority over it.

## 7. Why not choose residual SVR, since its December RMSE is lower?

**Short answer:** That would change the selection criterion after seeing the test outcome.

The implemented criterion picks absolute SVR, whose CV RMSE is 2,410.6 kW versus 2,427.1 for residual SVR. December reverses their order: 1,624.6 versus 1,419.1 kW. We disclose the reversal and retain the CV-selected model. The notebook's selection expression depends only on stored CV scores, although its test calculations occur earlier in code order. The snapshot supports the implemented rule, not a claim of preregistration. Any new choice motivated by December needs a new independent evaluation period.

## 8. Was December untouched and evaluated exactly once?

**Short answer:** No such claim is warranted from this repository.

December is outside model-selection CV and is the chronological test period. However, the current result history documents notebook reruns, annual descriptive figures include December, and leakage diagnostics use December again. Rerunning an unchanged pipeline is not automatically proof of test-driven model tuning, but these facts prevent certifying a pristine single-use holdout. We report the current pipeline and this limitation explicitly. Earlier report reviews contain an h1 December experiment removed from the current scope; its numbers are not in the deck.

## 9. Is observed target-hour weather leakage? Does the ablation show it barely matters?

**Short answer:** It is an availability mismatch for real advance forecasts. The result is conditional on oracle weather, and its deployment penalty is unknown.

Weather observations from the hour being predicted are not known at midnight or at the previous hourly boundary. Real deployment needs forecasts archived at issuance, or a model using only available inputs. The E/F ablation removes weather from the expanded E feature set, for RF/XGB with D-selected parameters held fixed. It does not test weather-free D for the selected SVR. Therefore it cannot justify saying oracle weather has a small effect on the selected model. Known calendar variables and sufficiently old loads are separate from this problem.

## 10. Do your leakage experiments prove how much random splitting inflates accuracy?

**Short answer:** They demonstrate problematic mechanisms and protocol sensitivity, but do not identify an isolated causal penalty.

S2 builds lag10min before shuffling, so a held-out response may become an input of a later training row. That is a direct cross-boundary dependency. S1–S4 also change features, resolution, history age, training size and test population. Even MAPE and R² cannot make these tasks directly comparable. The closer T12b diagnostic uses the same hourly data/features and a 20-candidate RF search with different CV strategies: shuffled CV/test RMSE 2,007.6/2,173.6, temporal CV/test 3,012.4/2,044.2 kW. It remains one post-test diagnostic; validation distributions and training sizes differ. A ten-minute horizon is not inherently leakage, and chronological S3 still uses observed weather.

## 11. Why does learning a residual help? Do trees really fail to extrapolate?

**Short answer:** A lag-relative target lets the known recent load carry the current level while the model learns a correction.

The current residual formulation is `r_t = y_t − y_(t−24)` and the forecast is `y_(t−24) + g(x_t)`. Standard regression trees predict leaf means; forests average such predictions, so they are bounded by training targets. Boosted sums of trees need not be bounded in that way, and RBF SVR is not strictly bounded by training y either. We therefore describe poor extrapolation as a plausible contributor to summer errors, with empirical support for residual formulations, not a universal theorem. Both target versions were independently tuned using the same search spaces/samples; gains can involve their selected parameters as well as the target representation.

## 12. What do the error analysis and SHAP results tell us about deployment?

**Short answer:** Errors concentrate on particular days, but explanations and aggregate scores have limited scope.

The selected SVR's worst December day is December 1, MAE 4,579.2 kW, with mean bias −3,616.7 kW that day. A shared holiday flag is a plausible hypothesis, not a proven cause. The repository's tree SHAP plots explain residual random forest's correction, not the selected SVR, so the deck does not use them as SVR explanations. Deployment still requires issuance-time weather, realistic load latency, broader seasonal/yearly tests, uncertainty assessment and monitoring. The current model weights are fixed after refitting, but observed histories update daily/hourly; it is not an open-loop monthly forecast. No new operational experiment was run for this presentation.

## Additional questions for the revised slides

**Is the comparison with published studies fair?** No study shares our target, horizon, split and test period, so the table positions the result and does not rank it. The values are those each study reports (course literature review, Table 7); we did not re-run their settings. The clearest contrast is Islam et al. (2025): a 10-minute-ahead chronological task with MAPE 6.3%, against our day-ahead MAPE 1.78%. Biswas et al. (2026) report a lower MAPE (1.04%) on the mean of the three zones (same MAPE as the total), but the horizon is not stated, so the gap cannot be interpreted. Studies without past-load inputs or with a shuffled split are not forecasts of unseen future periods.

**Why was the leakage slide removed?** The comparison with published studies answers the same question (why other numbers look different) more directly. The leakage diagnostic is kept for Q&A (question 10).

**Why not say the weekly lag alone is neutral?** The saved ablation adds the weekly lag and three rolling summaries together. It does not identify their individual effects. A weekly-only result would be needed.

**Does removing weather change error by no more than 5%?** Approximately, but the largest saved change is +5.3145% for residual RF. Slides use 5.3%. Absolute RF and XGB change by about +1.6% and +1.9%; E/F tests do not quantify the selected SVR's weather dependence.

**What motivates residual targets in July?** In fold 0, 12.2222% of validation hours exceed the training load maximum; 0% of validation residuals are outside the training residual range. RF and XGB improve in separately tuned comparisons. Absolute SVR retains the lower mean CV error (2410.6 versus 2427.1 kW).

**Is the small-gamma SVR linear?** No. Gamma controls RBF length scale in standardized feature space. A relatively smooth kernel is still nonlinear.

## Tuning details retained for Q&A

Random search budgets per target type are Ridge 20, DT 40, RF 30, SVR 30 and XGBoost 50: 170 configurations, each on five temporal folds. Selected RBF SVR: C=26.926469, gamma=0.006338653, epsilon=0.01. Inputs and target are standardized using training-fold data; epsilon is in scaled-target units. The merged CV slide cites Bergstra and Bengio (2012).

The saved EDA prose rounds 48-hour ACF to 0.97; the team supplied 0.96 for this slide and explicitly requested preservation. Lag12 is described only as negative. The shuffled ten-minute RF R2 .999 versus chronological h24 RF .980 is descriptive: horizons, feature sets and test populations differ, so it is not an isolated leakage effect.
