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

**Script:** Thank you, Son. We compare two seasonal baselines, copying the same hour yesterday (Naive-24h) or last week (Naive-168h), with five regression models: linear regression, decision tree, random forest, RBF SVR and XGBoost. Each model is trained in two ways. The absolute version learns the load directly. The residual version, marked Delta, learns the change from yesterday, y minus lag 24, and adds yesterday's load back when predicting. Both versions are tuned and compared on the same cross-validation.

**Key takeaway:** A residual target changes what the model learns, while preserving the final forecast units.

**Transition:** The July fold shows why this correction is useful.

## 12. Why predict a correction? July tests extrapolation

**Speaking time:** 65 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Why learn a change? Look at fold 0, the July validation window. The highest load in training is about 110,700 kW, but July reaches 133,100, and 12% of July hours are above anything the model has seen. Tree models predict averages of training values, so they cannot go above that maximum. The change from yesterday stays in a familiar range: no hour falls outside it. After tuning, the residual target cuts the July RMSE of random forest from 5,554 to 3,215 kW, and of XGBoost from 5,344 to 2,979.

**Key takeaway:** The residual target removes the July range shift for tree models.

**Transition:** We next combine model tuning with the chronological CV comparison.

## 13. Absolute SVR leads CV, with close alternatives

**Speaking time:** 90 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Next, tuning. Randomized search tries 170 configurations across the five models for each target type, each scored on the same five time-ordered folds. The chart ranks the tuned versions by mean CV RMSE: absolute SVR is first with 2,410.6 kW, plus or minus 766. The table shows the gain over the default models: SVR improves by 39%, decision tree by 38%, XGBoost and random forest by 21 to 25%, mostly thanks to the residual target. Linear regression barely changes, because it has almost nothing to tune. At the bottom: forecasting only one hour ahead, the same SVR drops to 1,866 kW, 22.6% lower, because it can use the last few hours of load.

**Key takeaway:** Temporal CV, tuning, and recent history answer different comparison questions.

**Transition:** The feature ablation shows where the largest gains come from.

## 14. Daily lags drive accuracy; the expanded set hurts

**Speaking time:** 65 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Which features matter? This ablation uses one model: the tuned absolute random forest, with its parameters fixed, on the same five CV folds. We add one feature group at a time. Weather alone gives an RMSE of 15,010 kW. Calendar features cut it by a third, and special days by another 9%. Daily lags, the load 24 and 48 hours earlier, give the biggest drop, 67%, down to 3,010. Adding the weekly lag and rolling averages makes it worse, 3,700, and XGBoost shows the same pattern. So every model uses set D, 17 features.

**Key takeaway:** Daily lags dominate this fixed-parameter RF ablation; combined weekly/rolling inputs hurt.

**Transition:** We keep the CV-selected model when evaluating December.

## 15. The selected SVR halves daily-baseline December RMSE

**Speaking time:** 65 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Now December, used only once. The CV-selected SVR reaches an RMSE of 1,624.6 kW: 50.7% lower than Naive-24h and 38% lower than Naive-168h. MAE is about 1,095 kW, MAPE 1.78% and R squared 0.987. The residual SVR at the bottom happens to be better on December, 1,419 kW, but it was not the best on CV; picking it now would mean choosing with the test set. So the absolute SVR stays our final model.

**Key takeaway:** Test-best and CV-selected are distinct roles.

**Transition:** Average accuracy still leaves important local errors.

## 16. Good daily tracking still leaves concentrated errors

**Speaking time:** 55 seconds. **Speaker:** Dang Nhat Minh.

**Script:** The top panel shows the actual load and our forecast for all 720 December hours; the two lines almost overlap. The bottom panel shows the error, forecast minus actual. The overall bias is minus 202 kW, so the model slightly under-forecasts. The errors are concentrated: the worst day is December 1st, Mawlid, a religious holiday, with an MAE of 4,579 kW. Holidays are rare in the training data, so they remain the hardest days.

**Key takeaway:** Overall metrics should be accompanied by time-local error analysis.

**Transition:** How does this result compare with published studies on the same dataset?

## 17. Compared with published Tetouan studies

**Speaking time:** 50 seconds. **Speaker:** Dang Nhat Minh.

**Script:** How does this compare with published work on the same dataset? These are the numbers each study reports; we did not re-run them. Islam and Alsalem forecast only ten minutes ahead, and Alsalem's R squared is for Zone 3 only. RoSe uses no past load, so it is not a real forecast. Biswas reports a MAPE of 1.04%, but on the mean of the zones and without stating the horizon. Our task is day-ahead, the model is chosen on chronological CV and December is used once, and we still reach a MAPE of 1.78% and R squared of 0.987. Since targets and horizons differ, this positions our result rather than ranking the studies.

**Key takeaway:** A longer horizon and stricter evaluation than the published studies, with errors in the same range or lower.

**Transition:** We close the discussion with the main findings and limitations.

## 18. Findings & limitations

**Speaking time:** 40 seconds. **Speaker:** Dang Nhat Minh.

**Script:** Three findings. First, choose the final model on chronological CV and report December separately. Second, daily lags give the largest gain, while weekly and rolling features hurt. Third, the selected SVR halves the Naive-24h error in December, a 50.7% reduction. Two limitations. We use the weather measured at the target hour; a real forecast at midnight would only have weather forecasts, so errors could be higher. And the dataset is small: one year from one city. Next steps are weather forecasts as inputs and more years of data.

**Key takeaway:** The December gains depend on observed weather and a small dataset.

**Transition:** We finish with the selected SVR's December result.

## 19. Conclusion & Q&A

**Speaking time:** 20 seconds. **Speaker:** Dang Nhat Minh.

**Script:** To conclude: our CV-selected SVR forecasts December with an RMSE of 1,624.6 kW, 50.7% better than copying yesterday. It is a promising result under strict chronological evaluation, with the caveat of observed weather. Thank you; we are happy to take your questions.

**Key takeaway:** Strong measured performance, carefully bounded interpretation.

**Transition:** Open discussion.
