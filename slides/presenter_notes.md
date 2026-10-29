# Presenter notes - 15 minutes

19 slides, no backups; **900 seconds = 15:00** including transitions and visual pauses.

**Giang Hoang Son: slides 1-10 (6:40). Dang Nhat Minh: slides 11-19 (8:20).** Handover follows chronological CV. The second presenter starts with models immediately after the handover.

| Slide | Speaker | Time | Cumulative |
|---|---|---:|---:|
| 1 | Son | 0:25 | 0:25 |
| 2 | Son | 0:35 | 1:00 |
| 3 | Son | 0:40 | 1:40 |
| 4 | Son | 0:30 | 2:10 |
| 5 | Son | 0:50 | 3:00 |
| 6 | Son | 0:50 | 3:50 |
| 7 | Son | 0:40 | 4:30 |
| 8 | Son | 0:40 | 5:10 |
| 9 | Son | 0:35 | 5:45 |
| 10 | Son | 0:55 | 6:40 |
| 11 | Minh | 0:50 | 7:30 |
| 12 | Minh | 1:05 | 8:35 |
| 13 | Minh | 1:30 | 10:05 |
| 14 | Minh | 1:05 | 11:10 |
| 15 | Minh | 1:05 | 12:15 |
| 16 | Minh | 0:55 | 13:10 |
| 17 | Minh | 0:50 | 14:00 |
| 18 | Minh | 0:40 | 14:40 |
| 19 | Minh | 0:20 | 15:00 |

## 1. Machine Learning-Based Electricity Consumption Forecasting in Tetouan City

**Speaking time:** 25 seconds. **Speaker:** Giang Hoang Son.

**Script:** Good morning, Dr. Thien and everyone. We are Dang Nhat Minh and Giang Hoang Son from class DS66A. Our project studies electricity demand forecasting in Tetouan City. We compare conventional regression models with simple seasonal forecasts, while preserving the order of time. Our main question is whether machine learning adds useful accuracy once the forecasting task and the evaluation protocol are clearly defined. We will also discuss the assumptions that limit the interpretation of our results.

**Key takeaway:** A chronological comparison with explicit information assumptions.

**Transition:** Let us start with the forecasting problem and our research questions.

## 2. Can machine learning beat a strong daily pattern?

**Speaking time:** 35 seconds. **Speaker:** Giang Hoang Son.

**Script:** Electricity planning needs an hourly demand profile, because the morning, afternoon and evening can require very different amounts of power. However, electricity demand also repeats strongly from day to day. This makes copying yesterday a meaningful baseline. We ask three questions. First, how much do conventional models improve on seasonal baselines? Second, which feature groups help? Third, what changes when we tune the models or predict a correction to yesterday instead of the absolute load? We evaluate predictive accuracy here; we have not measured financial savings or operational benefits.

**Key takeaway:** A useful model must improve on a realistic seasonal reference.

**Transition:** To compare errors fairly, we first need an exact definition of the target.

## 3. The target is mean hourly power across three zones

**Speaking time:** 40 seconds. **Speaker:** Giang Hoang Son.

**Script:** The local dataset is a table of fifty-two thousand four hundred and sixteen ten-minute rows and nine columns: a timestamp, five weather measurements and three zone loads. It covers January first through December thirtieth, 2017. We add the three zone loads and average the six observations within each hour. The zone loads are used only to build this target; they are never given to the model as inputs, because that would hand it the answer. This gives eight thousand seven hundred and thirty-six hourly values. The target is mean power in kilowatts. Energy over an hour would be this mean power multiplied by one hour, with units of kilowatt-hours. The annual figure shows the daily cycles and the summer increase. It is descriptive and includes December; we do not claim that December was invisible in all exploratory work.

**Key takeaway:** We forecast the hourly mean of the three-zone sum, not accumulated energy.

**Transition:** The development data reveal a clear daily structure.

## 4. Daily shape and season both matter

**Speaking time:** 30 seconds. **Speaker:** Giang Hoang Son.

**Script:** These profiles use January through November only. Every season has a similar shape: the minimum occurs around six or seven in the morning, followed by daytime demand and an evening peak around nineteen or twenty hours. Summer has a higher load profile, with more demand in the afternoon. The hour of day therefore explains most of the shape, so we add the hour and its sine and cosine encodings as features. The summer shift is linked to temperature, which is one of the weather inputs. The plot shows an association with season; it does not by itself prove a particular physical cause.

**Key takeaway:** The hour of day drives the daily shape; temperature helps with the seasonal level.

**Transition:** The season sets the level, but the best guide to today's level is yesterday, as the autocorrelation shows.

## 5. Today looks like yesterday

**Speaking time:** 50 seconds. **Speaker:** Giang Hoang Son.

**Script:** The autocorrelation plot uses January through November only. At the same hour one day later, correlation is zero point nine eight; two days later it is about zero point nine six. The weekly peak is also strong, at zero point nine five. In contrast, lag twelve hours is negative because daytime and nighttime sit in opposite phases of the daily cycle. This tells us that yesterday's load at the same hour is a strong starting point. Naive-24h is therefore a demanding baseline. It also motivates our two daily-history features, lag twenty-four and lag forty-eight. Correlation supports a predictive feature choice here; it does not establish a causal relationship.

**Key takeaway:** Daily persistence motivates lag24/48 and a strong seasonal baseline.

**Transition:** Daily similarity is strong, but weekday transitions reveal where copying yesterday can fail.

## 6. Sundays and Mondays break the daily pattern

**Speaking time:** 50 seconds. **Speaker:** Giang Hoang Son.

**Script:** This is the right panel of the weekday analysis, with larger labels for projection. Each cell compares a day and hour with the Monday-to-Friday mean at that same hour. This removes the ordinary daily cycle. Sundays are five point nine percent lower on average, and around fifteen percent lower at seven to eight in the morning. Saturday mornings are four to six percent lower. The effect changes with the hour, so a nonlinear model can learn the interaction between hour and weekday. Copying yesterday transfers Sunday's low morning demand into Monday, and Saturday's pattern into Sunday. We therefore include day of week, weekend status and cyclic weekday encodings.

**Key takeaway:** Weekday effects vary by hour and explain why daily persistence struggles at weekly transitions.

**Transition:** Calendar effects do not stop at weekends: holidays and Ramadan matter too.

## 7. Holidays and Ramadan move the load

**Speaking time:** 40 seconds. **Speaker:** Giang Hoang Son.

**Script:** Special days also change demand. We compare each holiday's daily load with the median of the fifteen surrounding days, which removes the season. Religious holidays, mainly the two Eids, are three to thirteen percent lower, about nine percent on average. Civil holidays are weaker and uneven, about three percent. That is why we use two separate flags instead of one holiday flag. Ramadan changes the shape of the day: the night load rises sharply, about thirty-two thousand kilowatts higher at two in the morning, while the temperature differs by less than two degrees. All these dates come from the official calendar, so they are known in advance.

**Key takeaway:** Religious holidays, civil holidays and Ramadan each need their own indicator.

**Transition:** These feature choices still depend on what is available when we issue a forecast.

## 8. h24 and h1 use different information at issuance

**Speaking time:** 40 seconds. **Speaker:** Giang Hoang Son.

**Script:** Our main setting, h24, issues one batch at midnight for that day's twenty-four hourly intervals. The interval starts are zero to twenty-three hours after issuance; their completions are one to twenty-four hours after issuance. The name h24 describes the minimum load-history lag, not a uniform lead time. The h1 setting updates each hour and can use the latest completed-hour load. These are different information settings. Both assume that completed loads arrive promptly, and both use observed target-hour weather. Operational forecasting would need weather forecasts available at issuance. We compare their saved CV results later, after introducing the models.

**Key takeaway:** Forecast resolution, history age and issuance lead are different concepts.

**Transition:** Here is the feature set used for the main h24 task.

## 9. Seventeen inputs combine timing, weather and history

**Speaking time:** 35 seconds. **Speaker:** Giang Hoang Son.

**Script:** Feature set D has seventeen columns, and the table separates what the dataset gives us from what we built. Only the five weather variables come directly from the original data, averaged per hour. The other twelve are engineered: seven calendar columns from the timestamp, including sine and cosine encodings; three special-day flags from the 2017 holiday calendar; and two history columns, the total load at the same hour one and two days earlier.

**Key takeaway:** Five inputs come from the data; twelve are engineered from time, the calendar and past load.

**Transition:** Next, we separate development decisions from the final chronological evaluation.

## 10. Model selection stays within January-November

**Speaking time:** 55 seconds. **Speaker:** Giang Hoang Son.

**Script:** After the history warm-up, the h24 development set contains seven thousand eight hundred and twenty-five hours. December first through thirtieth supplies seven hundred and twenty test hours. Inside development, we use five expanding training windows. Each validates the next seven hundred and twenty hours, or thirty days. Folds are numbered zero through four, matching the report. Fold zero covers July fourth through August second; fold four is November. This exposes models to both summer and autumn conditions. We select the tuned variant with the lowest mean CV RMSE, refit on all development data, and report its December performance. Scalers are fitted separately within training folds. The same folds support selection and reporting, so the CV estimates are not an unbiased nested evaluation. There is no gap, which assumes prompt availability at the boundary.

**Key takeaway:** Chronological CV supplies the model-selection rule; December supplies a separate period of evaluation.

**Transition:** Son will now explain the candidate models and what the saved results show.

## 11. Learn the load level - or a correction to yesterday

**Speaking time:** 50 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Thank you, Minh. We compare two seasonal baselines with five regression families: linear regression or tuned Ridge, decision tree, random forest, RBF support vector regression, and XGBoost. Each family learns either the absolute load or a residual relative to the same hour yesterday. We subtract yesterday's load during fitting and add it back to the predicted correction. This lets the known recent load carry the current level. That matters when July demand rises beyond the training range. Standard tree and forest averages cannot exceed their training targets; additive boosted trees do not share that strict mathematical bound. We compare both formulations using development CV.

**Key takeaway:** A residual target changes what the model learns, while preserving the final forecast units.

**Transition:** The July fold shows why this correction is useful.

## 12. Why predict a correction? July tests extrapolation

**Speaking time:** 65 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Fold zero covers July fourth through August second. The training maximum is one hundred ten thousand seven hundred eleven kilowatts, while the validation maximum reaches one hundred thirty-three thousand one hundred thirty. About twelve percent of validation hours exceed the training maximum. For the difference from yesterday, no validation residual falls outside the training residual range. The tuned random forest's July RMSE falls from five thousand five hundred fifty-four to three thousand two hundred fifteen kilowatts. XGBoost also improves, from five thousand three hundred forty-four to two thousand nine hundred seventy-nine. These separately tuned comparisons support residual learning, but do not isolate the target transformation from parameter choices. SVR is different: absolute and residual CV results are nearly tied, and absolute SVR remains selected.

**Key takeaway:** Residuals reduce the July range shift; absolute SVR still wins the specified CV criterion.

**Transition:** We next combine model tuning with the chronological CV comparison.

## 13. Absolute SVR leads CV, with close alternatives

**Speaking time:** 90 seconds. **Speaker:** Dang Nhat Minh.

**Script:** We now combine the tuning and CV results. Randomized search evaluates one hundred seventy configurations across the five families per target type, each on five temporal folds. Following Bergstra and Bengio, we compare candidates by mean CV RMSE. Tuning cuts absolute SVR's CV error by thirty-nine point three percent relative to default SVR. Temporal evaluation changes the default-model comparison: XGBoost wins the single November validation, while linear regression wins five-fold CV at two thousand seven hundred ninety-two kilowatts. Default SVR and decision tree both lose to Naive-24h, whose CV RMSE is three thousand three hundred ninety-two. After tuning, absolute SVR has the lowest mean at two thousand four hundred ten point six. The top four means are within one point three percent, below fold variation. Finally, with more recent history, the saved h1 CV result is one thousand eight hundred sixty-six point four, twenty-two point six percent lower. Configurations and validation dates match, but histories and initial training rows differ. This is a comparison of information settings, and the reused CV folds are not a nested evaluation.

**Key takeaway:** Temporal CV, tuning, and recent history answer different comparison questions.

**Transition:** The feature ablation shows where the largest gains come from.

## 14. Daily lags drive accuracy; the expanded set hurts

**Speaking time:** 65 seconds. **Speaker:** Dang Nhat Minh.

**Script:** We add feature groups to absolute-target random forest, keeping the parameters selected for D fixed. Calendar information cuts error by about a third. Special days add a smaller gain. Daily lags deliver the largest improvement, from nine thousand one hundred sixty-eight to three thousand ten kilowatts. Weekly and rolling features then raise error to three thousand seven hundred. XGBoost also worsens, from three thousand ten to four thousand nine hundred twenty-one. That is why the weekly lag and the rolling summaries are excluded from the final model, which uses set D. Set F removes the five weather columns from E: the error changes by at most five point three percent, plus one point six for RF and plus one point nine for XGBoost. So these tree models do not depend heavily on weather, although F does not test the selected SVR. One possible mechanism is reliance on rolling seasonal levels that are hard to extrapolate in July. The saved comparison does not isolate the weekly lag, so we cannot claim it is neutral alone.

**Key takeaway:** Daily lags dominate this fixed-parameter RF ablation; combined weekly/rolling inputs hurt.

**Transition:** We keep the CV-selected model when evaluating December.

## 15. The selected SVR halves daily-baseline December RMSE

**Speaking time:** 65 seconds. **Speaker:** Dang Nhat Minh.

**Script:** On the seven hundred and twenty December hours, the selected SVR has RMSE one thousand six hundred and twenty-four point six kilowatts. MAE is about one thousand ninety-five, MAPE is one point seven eight percent, and R squared is zero point nine eight six nine. The RMSE reduction is fifty point seven percent against Naive-24h. However, the weekly baseline is stronger than the daily baseline in December. Against Naive-168h, the reduction is thirty-eight percent. The residual SVR has an even lower observed test RMSE, about one thousand four hundred and nineteen. We report this transparently, but do not change the final selection after seeing December. These are results for this specific test month with observed target-hour weather; they do not establish year-round operational accuracy.

**Key takeaway:** Test-best and CV-selected are distinct roles.

**Transition:** Average accuracy still leaves important local errors.

## 16. Good daily tracking still leaves concentrated errors

**Speaking time:** 55 seconds. **Speaker:** Dang Nhat Minh.

**Script:** The top panel shows all seven hundred twenty December predictions; the lower panel shows forecast minus actual. Negative errors mean underprediction. Overall bias is minus two hundred two point one kilowatts. The worst day is December first, Mawlid, with daily MAE four thousand five hundred seventy-nine point two. One possible explanation is that the shared holiday indicator transfers the larger reductions seen around Eid to Mawlid. This is a hypothesis, not a causal conclusion: saved forecast errors cannot establish it. A targeted ablation or additional holiday observations would be needed. The full-month view shows that good average accuracy can hide concentrated daily errors.

**Key takeaway:** Overall metrics should be accompanied by time-local error analysis.

**Transition:** How does this result compare with published studies on the same dataset?

## 17. Compared with published Tetouan studies

**Speaking time:** 50 seconds. **Speaker:** Dang Nhat Minh.

**Script:** How does this compare with published work on the same dataset? The table lists the numbers each study reports; we did not re-run their settings. Two studies forecast only ten minutes ahead: Islam and colleagues report a MAPE of six point three percent, and Alsalem an R squared of zero point nine eight nine, but for Zone 3 only. RoSe and colleagues use no past load at all, so their model is not a forecast of the future. Biswas and colleagues report a MAPE of one point zero four percent on the mean of the three zones, but the horizon is not stated. Our task is day-ahead, the model is chosen on chronological cross-validation and December is used once, and we still reach a MAPE of one point seven eight percent and R squared of zero point nine eight seven. Because targets, horizons and test periods differ, this positions our result rather than ranking the studies.

**Key takeaway:** A longer horizon and stricter evaluation than the published studies, with errors in the same range or lower.

**Transition:** We close the discussion with the main findings and limitations.

## 18. Findings & limitations

**Speaking time:** 40 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Three findings stand out. Choose the final model using chronological development CV and report December separately. Daily lags provide the largest gain in the fixed-parameter RF ablation, while adding weekly and rolling features hurts that tested model. The CV-selected SVR halves the daily-baseline December error, a fifty point seven percent reduction. Two limitations stay visible. First, the weather inputs are the values actually measured at the target hour; a real forecast issued at midnight would only have weather forecasts, so errors could be higher in practice. Second, coverage is limited to one city, one year and one thirty-day test. Prompt arrival of recent loads is also assumed. The fitted weights remain fixed while earlier observed December loads update the inputs. Documentation records test reruns, so December's independence is limited. These last details remain in our notes and Q&A rather than crowding the slide.

**Key takeaway:** The December gains depend on available inputs and limited observed coverage.

**Transition:** We finish with the selected SVR's December result.

## 19. Conclusion & Q&A

**Speaking time:** 20 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Our CV-selected SVR reaches December RMSE of one thousand six hundred and twenty-four point six kilowatts, fifty point seven percent below Naive-24h. It is a promising chronological benchmark, conditional on observed weather. Thank you. We welcome your questions.

**Key takeaway:** Strong measured performance, carefully bounded interpretation.

**Transition:** Open discussion.
