# Tetouan ML report — completion and handoff

Updated: 26 October 2026 (Asia/Saigon).

## Current status

Final scientific/LaTeX peer review is complete: see `FINAL_REVIEW.md`. It added a verified S2 response-dependency explanation, corrected preregistration wording and audit precision, and clarified table units. The current suites pass 118 numerical, 223 integration and 14 targeted peer-review checks. A fresh build still stops at missing `geometry.sty`; the report is not yet PDF-submission-ready.

**All thirteen sections and the supplementary appendix are drafted and integrated.** The report includes **26 figures, 24 tables and 12 cited bibliography entries**. Local and Overleaf instructions are complete. Static/content validation passes; PDF compilation was attempted and stopped at missing `geometry.sty`. No PDF or successful layout review is claimed.

Sections 01–05 were completed in the initial audit/drafting session. Sections 06–09 were completed in the preceding continuation. This final continuation preserved Sections 01–09 and completed the remaining sections, appendix, documentation and final integration. No repository analysis was restarted and no ML experiments were rerun.

## Deliverables

| Deliverable | Status |
|---|---|
| `main.tex` | Complete; includes all thirteen sections and appendix; root-relative paths retained |
| `sections/01_introduction.tex` through `09_ablation_horizon.tex` | Previously complete; preserved |
| `sections/10_final_evaluation.tex` | Complete: selection/test-best distinction, both horizons, errors and residual-tree explanations |
| `sections/11_leakage.tex` | Complete: availability, S1–S4 confounding and separate KFold diagnostic |
| `sections/12_discussion.tex` | Complete: synthesis, complexity, literature comparability and limitations |
| `sections/13_conclusion.tex` | Complete: supported findings and explicitly proposed future work |
| `appendices/supplementary.tex` | Complete: reproducibility, environment, structure, configurations, survey and figures |
| `references.bib` | Twelve existing traceable entries retained; all cited |
| `reference_verification.md` | Complete provenance/access-limit ledger |
| `research_audit.md` | Original audit retained; appended precision erratum and environment update |
| `README.md` | Complete local/Overleaf build and evidence-check instructions |
| `validate_report.py` | Complete report/evidence validator |
| `validation_summary.md` | Checks, actual build failure and remaining qualifications |
| `main.pdf` | Not produced: MiKTeX lacks `geometry.sty` |

## Evidence and tables

The completed audit and notebook/PDF extracts remain the evidence base. Final integration reused T08 final-test/prediction/worst-day files; T07/T10 development selection; T12/T12b diagnostics; T11 survey; parameter JSONs; dependencies; and existing figure assets. Earlier report material was not reanalyzed beyond appropriate numerical verification.

`build_tables.py` generates 22 evidence tables and `table_sources.json`. All 22 are now integrated. Two manually structured tables summarize feature groups and literature. The final sections integrate `test24`, `test1`, `worst_days`, `leakage`, `kfold` and `runtime`. The appendix integrates `dependencies`, `cv_variability`, `parameters`, `search_inventory` and `survey`; the other tables remain in Sections 01–09.

Six new main-text figure references use F17, F17b, F18, F19a, F19b and F16. The appendix adds DQ01, DQ02, F08, F17c and F19c. With the preceding fifteen, this gives 26. F14 and F20 remain intentionally unembedded, with reasons explained; planned F09 is absent and not fabricated. No image assets were duplicated or recreated.

## Validation

- Detailed saved-evidence verification: **118 passed checks**, including all 18 h24 prediction columns, selected searches/folds and worst days.
- Final integration validator: **223 passed checks, zero failures**, covering inputs, labels, citations, captions/references, numerical claims and original-artifact hashes.
- No missing LaTeX inputs, duplicate labels, unresolved source references or missing citation keys remain. All seven previously pending section/appendix references are defined.
- Original audited data, notebooks, documentation, source modules and results match their SHA-256 manifest. Only report-related files were changed.
- Earlier scoped checks remain in `evidence/sections_06_09_validation.json`; that record is historical, not the final compilation record.

Current records: `evidence/report_validation.json`, `evidence/numerical_checks.json`, `reference_verification.md` and `validation_summary.md`. Source tables govern precision; the audit addendum corrects a few excess decimal places without changing the findings.

## Compilation outcome

MiKTeX executables were found. Sandboxed access to the user profile failed; a permitted outside-sandbox probe succeeded. A full pdfLaTeX run with **automatic package installation disabled** stopped at missing `geometry.sty`. `main.log` and `main.fls` retain the attempt. No packages/software were installed; Biber was not run after the failed first pass. Other package availability remains unknown beyond the first blocker.

Printed layout, overfull boxes, pagination, figure readability and Biber-resolved citations remain unverified. The source can be compiled after the user provisions the existing TeX environment or uploads the documented structure to Overleaf. Exact commands are in `README.md`.

## Scientific boundaries preserved

Absolute SVR is CV-selected for both settings; residual SVR is only the observed h24 test-best candidate. Test evaluation is chronological but not certified single-use: descriptive EDA and documented reruns expose December. Both settings use observed target-hour weather; measurement latency is unspecified. Histories update during evaluation. h24 is a midnight batch/minimum-lag convention, not a uniform 24-hour lead.

Development folds inform several choices; SDs are not confidence intervals. D-selected parameters are frozen in ablations; F removes weather from E. No selected-SVR weather replacement experiment exists. h1 also changes inputs/base/parameters. S1–S4 are confounded diagnostics; shorter horizons and future calendar values are not inherently leakage. DT/RF response-range bounds must not be generalized to every nonlinear estimator. No significance, causal importance, deployment readiness or state-of-the-art claim is made.

Unresolved metadata remain explicit: team/student IDs, instructor, submission date, sensor/clock semantics, hardware, weather archives, h1 predictions and historical side-experiment outputs. The local row-count discrepancy and literature ambiguities are retained in the audit.

## Remaining user-side work

Fill the title-page identity fields. Provide the missing LaTeX packages through an approved installation or use Overleaf, then run the documented build and inspect the pages. No further scientific drafting or integration is pending under this task. Stronger research claims require new, separately authorized experiments and additional data.

**Stop reached:** requested report source/integration work is complete; PDF production is blocked by the TeX environment's missing package.
