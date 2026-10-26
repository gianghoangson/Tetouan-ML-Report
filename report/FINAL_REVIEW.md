# Final Scientific and LaTeX Quality Review

Review date: 26 October 2026 (Asia/Saigon).

## Assessment

**The report is scientifically coherent as a qualified analysis of the saved repository experiments. It is not yet ready for final PDF submission.** Main metrics, model identities, selection rules and empirical conclusions are supported by the stored evidence. The remaining submission blocker is the incomplete LaTeX environment, followed by an actual PDF layout/bibliography review and completion of title-page identity fields.

No critical error was found that reverses the project's primary numerical conclusions. The material scientific correction concerns the explanation of S2: its shuffled split allows held-out responses to enter training through lagged inputs. This mechanism was underdescribed in the report and is now made explicit. No experimental scores were changed and no models were fitted.

## Issues found and fixed

| Severity | Finding | Correction and evidence |
|---|---|---|
| Material scientific interpretation | Section 11 discussed future observations in shuffled training but omitted the direct response dependency created by constructing S2's lag before splitting. Its S1/S2 discussion could consequently imply that their difference reflects only useful history. | Added the explicit mechanism: held-out `y_t` appears as `lag_10min` in training row `t+10 min`. An index-only reconstruction of notebook 08's seed-42 split confirms **9,834 of 13,104 held-out responses** enter such training inputs. S1/S2 accuracy differences cannot separate useful history from this dependency. Source: notebook 08 cell 9 feature construction and cell 11 split, `review_checks.py`, `evidence/peer_review_checks.json`. This does not accuse the main chronological pipeline of fitting on December labels. |
| Moderate methodological wording | Section 07 called mean RMSE a “predeclared” objective, although other sections correctly acknowledge that the snapshot does not establish prospective registration. | Replaced this with “implemented selection objective” and an explicit lack of evidence for preregistration. The CV selection expression is unchanged. |
| Moderate evidence consistency | The audit's main numerical table retained excess-decimal inaccuracies and a default-OLS/tuned-Ridge precision mix-up, although its later erratum and the displayed LaTeX results were correct. | Reconciled affected audit entries with CSV display precision. Examples: default LR CV mean is 2792.314602... kW; tuned absolute Ridge is 2792.315406... kW. Selected h24 SVR MAPE is 1.778109...%, not 1.77759%. Clarified that 12.22% is the fraction of fold-0 validation observations exceeding the training maximum. Findings and rounded report results are unchanged. |
| Minor quantitative presentation | Some standalone captions did not state RMSE units or the reference behind “Skill”; the near-zero negative Ridge gain rendered as `-0.00`. | Added kW units to tuning/horizon captions, named Naive-24h as the test skill reference, clarified literature-table metric units, and normalized rounded zero formatting in `build_tables.py`. Raw CSV precision is preserved. |

Affected report text: Sections 02, 07 and 11 only. Other correct sections were retained. The research audit was corrected locally rather than replaced. Existing bibliography entries were retained; no unsupported new citations or performance results were added.

## Scientific and methodological review

The target is hourly mean power of the three-zone sum, reported in repository kW conventions, rather than accumulated energy. Local row count, observation dates, hourly aggregation, feature warm-up and split sizes agree with implementation and saved outputs. No imputation or outlier removal is claimed where none is implemented.

Calendar, lag, rolling and residual-target equations agree with the source modules. Training-fitted scaling is correctly distinguished from predictor availability. The h24 midnight-batch/minimum-lag interpretation is stated explicitly; it is not described as a uniform 24-hour issuance lead. Validation/test histories update from completed observations rather than forming a month-long open-loop forecast. The zero-gap design assumes prompt measurement and fitting availability.

The report correctly distinguishes November validation, default temporal CV, tuning on reused development folds and December test evaluation. Fold SDs are not presented as confidence intervals. Feature ablation holds D-selected parameters fixed; F removes weather from E, not D. The horizon comparison changes features, residual base, parameter choices and warm-up as well as history age. These limitations are retained.

Absolute SVR remains selected by CV for both settings. Residual SVR is the observed h24 test-best candidate, not a replacement selected after observing December. h1's evaluated set contains CV-preferred family representatives rather than every searched variant. Test reuse, whole-year EDA and post-test diagnostics are disclosed. Tree SHAP is correctly attributed to residual RF and its correction output, not to the selected SVR.

Observed target-hour weather remains a confirmed availability mismatch for an operational advance forecast. Calling the study conditional on oracle weather makes the estimand explicit; it does not establish operational readiness or quantify the penalty of using real forecast weather. S1–S4 alter multiple factors and do not isolate a causal leakage penalty. The new S2 finding is a verified mechanism, not a new estimate of the score inflation it causes.

## Numerical verification status

All three relevant suites passed after the review changes:

| Verification | Passed | Scope |
|---|---:|---|
| `check_evidence.py` | 118 | Raw/hourly counts; 18 stored h24 prediction columns; selected search/fold consistency; ablation and other saved-result checks |
| `validate_report.py` | 223 | Integrated inputs, labels, citations, assets, figure/table references, selected numerical claims and original-artifact hashes |
| `review_checks.py` | 14 | EDA means, wind shares, weekday effects, development ACF, subgroup test MAEs, tuned metric winners and S2 split dependency |

These are validation checks, not independent research experiments or significance tests. The review script reconstructs only row assignments and performs arithmetic on saved data. It does not fit an RF or estimate a corrected S2 performance score.

Key results remain:

| Setting | Role | RMSE (kW) | MAE (kW) | MAPE (%) | R² |
|---|---|---:|---:|---:|---:|
| h24 December, absolute SVR | CV-selected | 1624.6 | 1094.6 | 1.78 | 0.9869 |
| h24 December, residual SVR | Lowest observed test RMSE | 1419.1 | 1046.1 | 1.72 | 0.9900 |
| h1 December, absolute SVR | CV-selected; lowest RMSE among evaluated h1 models | 1195.8 | 861.8 | 1.41 | 0.9929 |

Selected h24 SVR improves RMSE over Naive-24h by 50.71%. h1 residual XGB has lower MAE/MAPE than h1 SVR, so no metric-independent winner is claimed. h1 individual forecast-level verification remains unavailable because those predictions were not saved.

All original artifacts covered by `evidence/source_manifest.json` retain their SHA-256 hashes. Datasets, notebooks, source modules and existing experimental results were preserved.

## Citation verification status

All **12 bibliography keys** are unique, cited and resolved in source. The six-study comparison matches the repository's literature CSV/review transcriptions at displayed precision. No common-benchmark or state-of-the-art ranking is inferred from their incompatible targets and protocols.

Primary records were rechecked during this review:

- [UCI dataset record](https://archive.ics.uci.edu/dataset/849/power+consumption+of+tetouan+city): confirms dataset identity and suggested citation; the local/metadata row-count difference remains disclosed.
- [RoSe et al., Atlantis Press](https://www.atlantis-press.com/proceedings/icacecs-23/125995751), [Islam et al., Springer](https://link.springer.com/article/10.1007/s11135-024-02043-0), and [Alsalem, Scientific Reports](https://www.nature.com/articles/s41598-025-91123-8): publisher records corroborate bibliographic identities. Islam's online/volume years are correctly distinguished. Numerical configuration details are not certified beyond the accessible source material.
- [Da Silva and Meneses, publisher article](https://www.sciencedirect.com/science/article/pii/S2352484723014208) and [Biswas et al., publisher article](https://www.sciencedirect.com/science/article/pii/S259012302601323X): publisher search records corroborate the cited titles/DOIs and publication metadata. Direct requests returned HTTP 403, so this review does not certify a fresh full-text inspection.
- [Salam and El Hibaoui, IEEE record](https://ieeexplore.ieee.org/document/8703007): direct access requires a browser verification step. UCI corroborates the introductory-paper identity; performance/setup details remain explicitly local-review transcriptions.
- [Random search](https://jmlr.org/papers/v13/bergstra12a.html), [XGBoost](https://arxiv.org/abs/1603.02754), [SHAP](https://arxiv.org/abs/1705.07874), [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) and [preprocessing pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): official/original records support the methodological citations.

Thus citation identity and source-key consistency pass, while complete independent primary-paper verification remains limited. The unresolved optimizer description in P2 and selected-target/horizon ambiguities in some comparison rows are retained. Biber processing has not been completed because the first LaTeX pass is blocked.

## LaTeX integrity and actual compilation status

The include graph contains **13 sections, one appendix, 26 figures and 24 tables**. All input files/assets exist; every figure/table has a caption, label and in-text reference. There are no duplicate labels, missing citation keys or unresolved explicit source references. The abstract has 233 words. Basic brace/environment checks pass. Root-relative paths and the documented Overleaf launcher are consistent with the document design.

A fresh compilation was attempted during this review using the installed MiKTeX executable, outside the sandbox after the previously established user-profile access issue:

```powershell
pdflatex --disable-installer -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -recorder -output-directory=report report/main.tex
```

It failed at **missing `geometry.sty`**, before document layout. This is an environment dependency blocker, not a confirmed syntax error in a report section. Automatic package installation remained disabled, consistent with the user's existing restriction. No software/packages were installed. The log is `report/main.log`; no PDF was produced. Other packages may also be missing beyond this first blocker.

The review therefore cannot certify final table widths, page breaks, overfull boxes, printed figure readability or resolved Biber output. The absence of such warnings in an early-failure log is not a layout pass. Removing required formatting packages merely to force compilation would undermine the requested document design and was not done.

## Remaining limitations and readiness decision

**Scientific readiness:** suitable for an academic report of these saved, conditional experiments, with the stated limitations. It is not evidence of operational deployment performance, causal feature effects, statistical superiority or generalization beyond the observed city/year and December period.

**Submission readiness:** conditional, pending an actual successful LaTeX/Biber build and visual inspection. The title-page student/team, instructor and submission fields must also be completed. Missing weather forecasts, acquisition latency, hardware provenance, h1 individual predictions and independently reserved seasonal/yearly data cannot be resolved by editing prose.

To finish the document, provision the missing packages in an approved TeX environment or use the documented Overleaf workflow, run the full bibliography/reference passes, and inspect the resulting pages. No further model training is needed for those steps. Additional research claims would require new, separately authorized experiments.
