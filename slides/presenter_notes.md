# Presenter notes - 15 minutes

18 slides, no backups; **900 seconds = 15:00** including transitions and visual pauses.

**Dang Nhat Minh: slides 1-9 (6:30). Giang Hoang Son: slides 10-18 (8:30).** Handover follows chronological CV. The second presenter starts with models immediately after the handover.

| Slide | Speaker | Time | Cumulative |
|---|---|---:|---:|
| 1 | Minh | 0:25 | 0:25 |
| 2 | Minh | 0:35 | 1:00 |
| 3 | Minh | 0:45 | 1:45 |
| 4 | Minh | 0:35 | 2:20 |
| 5 | Minh | 0:50 | 3:10 |
| 6 | Minh | 0:55 | 4:05 |
| 7 | Minh | 0:45 | 4:50 |
| 8 | Minh | 0:40 | 5:30 |
| 9 | Minh | 1:00 | 6:30 |
| 10 | Son | 0:55 | 7:25 |
| 11 | Son | 1:05 | 8:30 |
| 12 | Son | 1:30 | 10:00 |
| 13 | Son | 1:05 | 11:05 |
| 14 | Son | 1:05 | 12:10 |
| 15 | Son | 0:55 | 13:05 |
| 16 | Son | 0:50 | 13:55 |
| 17 | Son | 0:45 | 14:40 |
| 18 | Son | 0:20 | 15:00 |

## 1. Machine Learning-Based Electricity Consumption Forecasting in Tetouan City

**Speaking time:** 25 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Good morning, Dr. Thien and everyone. We are Dang Nhat Minh and Giang Hoang Son from class DS66A. Our project studies electricity demand forecasting in Tetouan City. We compare conventional regression models with simple seasonal forecasts, while preserving the order of time. Our main question is whether machine learning adds useful accuracy once the forecasting task and the evaluation protocol are clearly defined. We will also discuss the assumptions that limit the interpretation of our results.

**Key takeaway:** A chronological comparison with explicit information assumptions.

**Transition:** Let us start with the forecasting problem and our research questions.

## 2. Can machine learning beat a strong daily pattern?

**Speaking time:** 35 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Electricity planning needs an hourly demand profile, because the morning, afternoon and evening can require very different amounts of power. However, electricity demand also repeats strongly from day to day. This makes copying yesterday a meaningful baseline. We ask three questions. First, how much do conventional models improve on seasonal baselines? Second, which feature groups help? Third, what changes when we tune the models or predict a correction to yesterday instead of the absolute load? We evaluate predictive accuracy here; we have not measured financial savings or operational benefits.

**Key takeaway:** A useful model must improve on a realistic seasonal reference.

**Transition:** To compare errors fairly, we first need an exact definition of the target.

## 3. The target is mean hourly power across three zones

**Speaking time:** 45 seconds. **Speaker:** Dang Nhat Minh.

**Script:** The local dataset contains fifty-two thousand four hundred and sixteen ten-minute observations, covering January first through December thirtieth, 2017. Each observation includes five weather measurements and power consumption in three distribution zones. We add the three zone loads and average the six observations within each hour. This gives eight thousand seven hundred and thirty-six hourly values. The target is mean power in kilowatts. Energy over an hour would be this mean power multiplied by one hour, with units of kilowatt-hours. The annual figure shows the daily cycles and the summer increase. It is descriptive and includes December; we do not claim that December was invisible in all exploratory work.

**Key takeaway:** We forecast the hourly mean of the three-zone sum, not accumulated energy.

**Transition:** The development data reveal a clear daily structure.

## 4. Daily shape and season both matter

**Speaking time:** 35 seconds. **Speaker:** Dang Nhat Minh.

**Script:** These profiles use January through November only. Every season has a similar shape: the minimum occurs around six or seven in the morning, followed by daytime demand and an evening peak around nineteen or twenty hours. Summer has a higher load profile. These patterns motivate two complementary sources of information. Calendar features describe where an hour falls in the daily and weekly cycle. Recent daily load helps represent the current level of demand. The plot shows an association with season; it does not by itself prove a particular physical cause.

**Key takeaway:** Timing and recent load level both belong in the model inputs.

**Transition:** The strong daily shape also appears in the autocorrelation plot.

## 5. Today looks like yesterday

**Speaking time:** 50 seconds. **Speaker:** Dang Nhat Minh.

**Script:** The autocorrelation plot uses January through November only. At the same hour one day later, correlation is zero point nine eight; two days later it is about zero point nine six. The weekly peak is also strong, at zero point nine five. In contrast, lag twelve hours is negative because daytime and nighttime sit in opposite phases of the daily cycle. This tells us that yesterday's load at the same hour is a strong starting point. Naive-24h is therefore a demanding baseline. It also motivates our two daily-history features, lag twenty-four and lag forty-eight. Correlation supports a predictive feature choice here; it does not establish a causal relationship.

**Key takeaway:** Daily persistence motivates lag24/48 and a strong seasonal baseline.

**Transition:** Daily similarity is strong, but weekday transitions reveal where copying yesterday can fail.

## 6. Sundays and Mondays break the daily pattern

**Speaking time:** 55 seconds. **Speaker:** Dang Nhat Minh.

**Script:** This is the right panel of the weekday analysis, with larger labels for projection. Each cell compares a day and hour with the Monday-to-Friday mean at that same hour. This removes the ordinary daily cycle. Sundays are five point nine percent lower on average, and around fifteen percent lower at seven to eight in the morning. Saturday mornings are four to six percent lower. The effect changes with the hour, so a nonlinear model can learn the interaction between hour and weekday. Copying yesterday transfers Sunday's low morning demand into Monday, and Saturday's pattern into Sunday. We therefore include day of week, weekend status and cyclic weekday encodings.

**Key takeaway:** Weekday effects vary by hour and explain why daily persistence struggles at weekly transitions.

**Transition:** These feature choices still depend on what is available when we issue a forecast.

## 7. h24 and h1 use different information at issuance

**Speaking time:** 45 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Our main setting, h24, issues one batch at midnight for that day's twenty-four hourly intervals. The interval starts are zero to twenty-three hours after issuance; their completions are one to twenty-four hours after issuance. The name h24 describes the minimum load-history lag, not a uniform lead time. The h1 setting updates each hour and can use the latest completed-hour load. These are different information settings. Both assume that completed loads arrive promptly, and both use observed target-hour weather. Operational forecasting would need weather forecasts available at issuance. We compare their saved CV results later, after introducing the models.

**Key takeaway:** Forecast resolution, history age and issuance lead are different concepts.

**Transition:** Here is the feature set used for the main h24 task.

## 8. Seventeen inputs combine timing, weather and history

**Speaking time:** 40 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Feature set D has seventeen columns. Five describe weather; seven encode the hour, weekday and weekend, including cyclic encodings; three mark special days; and two contain the load at the same hour one and two days earlier. The weekly lag and rolling summaries were tested but excluded from the main model inputs. Historical rolling statistics are shifted before aggregation, and fitted scalers only see each training fold. We also exclude the simultaneous zone loads, because they are components of the answer. There is an important remaining limitation: the weather variables are measured at the target hour. An advance operational forecast would need weather forecasts available at issuance instead.

**Key takeaway:** Load-history safeguards do not solve target-hour weather availability.

**Transition:** Next, we separate development decisions from the final chronological evaluation.

## 9. Model selection stays within January-November

**Speaking time:** 60 seconds. **Speaker:** Dang Nhat Minh.

**Script:** After the history warm-up, the h24 development set contains seven thousand eight hundred and twenty-five hours. December first through thirtieth supplies seven hundred and twenty test hours. Inside development, we use five expanding training windows. Each validates the next seven hundred and twenty hours, or thirty days. Folds are numbered zero through four, matching the report. Fold zero covers July fourth through August second; fold four is November. This exposes models to both summer and autumn conditions. We select the tuned variant with the lowest mean CV RMSE, refit on all development data, and report its December performance. Scalers are fitted separately within training folds. The same folds support selection and reporting, so the CV estimates are not an unbiased nested evaluation. There is no gap, which assumes prompt availability at the boundary.

**Key takeaway:** Chronological CV supplies the model-selection rule; December supplies a separate period of evaluation.

**Transition:** Son will now explain the candidate models and what the saved results show.

## 10. Learn the load level - or a correction to yesterday

**Speaking time:** 55 seconds. **Speaker:** Giang Hoang Son.

**Script:** Thank you, Minh. We compare two seasonal baselines with five regression families: linear regression or tuned Ridge, decision tree, random forest, RBF support vector regression, and XGBoost. Each family learns either the absolute load or a residual relative to the same hour yesterday. We subtract yesterday's load during fitting and add it back to the predicted correction. This lets the known recent load carry the current level. That matters when July demand rises beyond the training range. Standard tree and forest averages cannot exceed their training targets; additive boosted trees do not share that strict mathematical bound. We compare both formulations using development CV.

**Key takeaway:** A residual target changes what the model learns, while preserving the final forecast units.

**Transition:** The July fold shows why this correction is useful.

## 11. Why predict a correction? July tests extrapolation

**Speaking time:** 65 seconds. **Speaker:** Giang Hoang Son.

**Script:** Fold zero covers July fourth through August second. The training maximum is one hundred ten thousand seven hundred eleven kilowatts, while the validation maximum reaches one hundred thirty-three thousand one hundred thirty. About twelve percent of validation hours exceed the training maximum. For the difference from yesterday, no validation residual falls outside the training residual range. The tuned random forest's July RMSE falls from five thousand five hundred fifty-four to three thousand two hundred fifteen kilowatts. XGBoost also improves, from five thousand three hundred forty-four to two thousand nine hundred seventy-nine. These separately tuned comparisons support residual learning, but do not isolate the target transformation from parameter choices. SVR is different: absolute and residual CV results are nearly tied, and absolute SVR remains selected.

**Key takeaway:** Residuals reduce the July range shift; absolute SVR still wins the specified CV criterion.

**Transition:** We next combine model tuning with the chronological CV comparison.

## 12. Absolute SVR leads CV, with close alternatives

**Speaking time:** 90 seconds. **Speaker:** Giang Hoang Son.

**Script:** We now combine the tuning and CV results. Randomized search evaluates one hundred seventy configurations across the five families per target type, each on five temporal folds. Following Bergstra and Bengio, we compare candidates by mean CV RMSE. Tuning cuts absolute SVR's CV error by thirty-nine point three percent relative to default SVR. Temporal evaluation changes the default-model comparison: XGBoost wins the single November validation, while linear regression wins five-fold CV at two thousand seven hundred ninety-two kilowatts. Default SVR and decision tree both lose to Naive-24h, whose CV RMSE is three thousand three hundred ninety-two. After tuning, absolute SVR has the lowest mean at two thousand four hundred ten point six. The top four means are within one point three percent, below fold variation. Finally, with more recent history, the saved h1 CV result is one thousand eight hundred sixty-six point four, twenty-two point six percent lower. Configurations and validation dates match, but histories and initial training rows differ. This is a comparison of information settings, and the reused CV folds are not a nested evaluation.

**Key takeaway:** Temporal CV, tuning, and recent history answer different comparison questions.

**Transition:** The feature ablation shows where the largest gains come from.

## 13. Daily lags drive accuracy; the expanded set hurts

**Speaking time:** 65 seconds. **Speaker:** Giang Hoang Son.

**Script:** We add feature groups to absolute-target random forest, keeping the parameters selected for D fixed. Calendar information cuts error by about a third. Special days add a smaller gain. Daily lags deliver the largest improvement, from nine thousand one hundred sixty-eight to three thousand ten kilowatts. Weekly and rolling features then raise error to three thousand seven hundred. XGBoost also worsens, from three thousand ten to four thousand nine hundred twenty-one. One possible mechanism is reliance on rolling seasonal levels that are hard to extrapolate in July. The saved comparison does not isolate the weekly lag, so we cannot claim it is neutral alone. Removing weather from E changes errors by at most five point three percent; this does not measure weather's value for the selected SVR.

**Key takeaway:** Daily lags dominate this fixed-parameter RF ablation; combined weekly/rolling inputs hurt.

**Transition:** We keep the CV-selected model when evaluating December.

## 14. The selected SVR halves daily-baseline December RMSE

**Speaking time:** 65 seconds. **Speaker:** Giang Hoang Son.

**Script:** On the seven hundred and twenty December hours, the selected SVR has RMSE one thousand six hundred and twenty-four point six kilowatts. MAE is about one thousand ninety-five, MAPE is one point seven eight percent, and R squared is zero point nine eight six nine. The RMSE reduction is fifty point seven percent against Naive-24h. However, the weekly baseline is stronger than the daily baseline in December. Against Naive-168h, the reduction is thirty-eight percent. The residual SVR has an even lower observed test RMSE, about one thousand four hundred and nineteen. We report this transparently, but do not change the final selection after seeing December. These are results for this specific test month with observed target-hour weather; they do not establish year-round operational accuracy.

**Key takeaway:** Test-best and CV-selected are distinct roles.

**Transition:** Average accuracy still leaves important local errors.

## 15. Good daily tracking still leaves concentrated errors

**Speaking time:** 55 seconds. **Speaker:** Giang Hoang Son.

**Script:** The top panel shows all seven hundred twenty December predictions; the lower panel shows forecast minus actual. Negative errors mean underprediction. Overall bias is minus two hundred two point one kilowatts. The worst day is December first, Mawlid, with daily MAE four thousand five hundred seventy-nine point two. One possible explanation is that the shared holiday indicator transfers the larger reductions seen around Eid to Mawlid. This is a hypothesis, not a causal conclusion: saved forecast errors cannot establish it. A targeted ablation or additional holiday observations would be needed. The full-month view shows that good average accuracy can hide concentrated daily errors.

**Key takeaway:** Overall metrics should be accompanied by time-local error analysis.

**Transition:** We also need to ask whether an evaluation lets information cross the forecast boundary.

## 16. Evaluation shortcuts change what the score means

**Speaking time:** 50 seconds. **Speaker:** Giang Hoang Son.

**Script:** The diagram shows how a held-out response can enter a later training row's lag in the shuffled diagnostic. A separate twenty-candidate RF tuning comparison also shows that shuffled CV can estimate error optimistically and select a worse December model. The wider protocol comparison reaches R squared zero point nine nine nine with shuffled ten-minute data, against about zero point nine eight zero for chronological h24 forecasting with the same RF configuration. This does not isolate a leakage penalty: features, forecast horizons and test populations also differ. The diagnostic reuses December and observed weather. The important point is that a score must be interpreted together with the forecasting task and its information boundary.

**Key takeaway:** An impressive score is meaningful only in the context of its information and evaluation protocol.

**Transition:** We close the discussion with the main findings and limitations.

## 17. Findings & limitations

**Speaking time:** 45 seconds. **Speaker:** Giang Hoang Son.

**Script:** Three findings stand out. Choose the final model using chronological development CV and report December separately. Daily lags provide the largest gain in the fixed-parameter RF ablation, while adding weekly and rolling features hurts that tested model. The CV-selected SVR halves the daily-baseline December error, a fifty point seven percent reduction. Two limitations stay visible: target-hour weather is observed rather than forecast, and coverage is limited to one city, one year and one thirty-day test. Prompt arrival of recent loads is also assumed. The fitted weights remain fixed while earlier observed December loads update the inputs. Documentation records test reruns, so December's independence is limited. These last details remain in our notes and Q&A rather than crowding the slide.

**Key takeaway:** The December gains depend on available inputs and limited observed coverage.

**Transition:** We finish with the selected SVR's December result.

## 18. Conclusion & Q&A

**Speaking time:** 20 seconds. **Speaker:** Giang Hoang Son.

**Script:** Our CV-selected SVR reaches December RMSE of one thousand six hundred and twenty-four point six kilowatts, fifty point seven percent below Naive-24h. It is a promising chronological benchmark, conditional on observed weather. Thank you. We welcome your questions.

**Key takeaway:** Strong measured performance, carefully bounded interpretation.

**Transition:** Open discussion.
