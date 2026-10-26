# Final report validation

Date: 26 October 2026 (Asia/Saigon).

## Outcome

The subsequent strict peer review is recorded in `FINAL_REVIEW.md`. Its 14 additional targeted checks pass, including the index-only verification of 9,834 S2 held-out responses entering successor training-row lag inputs. The 118 evidence and 223 integration checks were rerun successfully after the report corrections. Compilation was retried and remains blocked by `geometry.sty`.

The source report is fully integrated: **13 main sections, one supplementary appendix, 26 figure environments, 24 numbered tables and 12 cited bibliography entries**. All 22 generated evidence tables are included, alongside two manually structured feature/literature tables. The abstract contains 233 whitespace-delimited words.

`python report/validate_report.py` completed with **223 passed checks and zero failed checks**. `python report/check_evidence.py` completed with **118 passed numerical checks**, without fitting models. These are different suites, not counts of independent experiments. The earlier Sections 06–09 validation remains archived separately.

## Content and integration checks

- All transitive LaTeX inputs exist; thirteen sections and the appendix are included.
- All 26 figure assets exist in `results/figures/`, reused without copying or recreating them.
- Every included figure/table has a caption, label and in-text reference.
- No duplicate labels, unresolved explicit source references or missing citation keys were found.
- All 12 bibliography entries are cited, with unique keys and balanced braces. `reference_verification.md` records provenance and access limitations; not every primary full text was accessible.
- Included LaTeX files pass basic brace, environment and control-character checks. These do not replace a compiler.
- Numerical checks confirm selected-SVR metrics, baseline-relative skills, residual-SVR's lower observed h24 test RMSE, h1 metric-dependent winners, bias/extrema, worst day, S4/RF identity and KFold diagnostic discrepancies.
- The detailed evidence checker recalculates metrics from all 18 stored h24 prediction columns, checks selected searches/fold summaries and verifies worst days. Forecast-level h1 verification is unavailable because those predictions were not saved.
- Original artifacts covered by the audit SHA-256 manifest remain unchanged. No datasets, source modules, notebooks or experimental outputs were modified. No full/smoke ML experiments were executed.

The final record is `evidence/report_validation.json`; detailed numerical checks are in `evidence/numerical_checks.json`. `table_sources.json` maps generated tables to CSV/JSON evidence. The audit includes a small integration erratum correcting excess decimal places and clarifying the fold-0 fraction of observations.

## Actual compilation attempt

MiKTeX pdfLaTeX is installed under `D:\MiKTeX\miktex\bin\x64`. A sandboxed probe failed on access to the user profile. A permitted outside-sandbox run confirmed the executable works, and this full-source build was attempted from the repository root:

```powershell
pdflatex --disable-installer -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -recorder -output-directory=report report/main.tex
```

**Compilation failed before document layout because `geometry.sty` is missing. No `report/main.pdf` was produced.** The failure is retained in `main.log`; the input recorder is `main.fls`. Automatic installation was disabled. No software or TeX packages were installed. Other packages may also be missing; the compiler stops at the first missing dependency.

Biber was not run because no `.bcf` file could be generated. Bibliography syntax/formatting has not been validated by Biber. No overfull boxes were reported in the partial log, but the build stopped in the preamble: this is **not evidence that layout is clean**. Page breaks, table widths, float placement, printed figure readability and final resolved-reference output remain unverified.

`README.md` gives the local pdfLaTeX/Biber workflow and an Overleaf structure preserving root-relative paths. Compilation can resume once the existing installation has the required packages or in an appropriately provisioned Overleaf environment.

## Scientific qualifications retained

The text keeps absolute SVR selected by development CV distinct from residual SVR's lower observed h24 test RMSE. December is a chronological evaluation period, with documented reruns and descriptive exposure rather than certified single-use secrecy. Observed target-hour weather is an oracle-information condition; acquisition latency is not verified. S1–S4 confound split, resolution, features, test population and horizon. Fold reuse, fixed-D ablations and the single-year/city scope preclude stronger generalization, causal or significance claims.

Student/team details, instructor and submission date remain placeholders. Sensor units/clock provenance, hardware, archived weather forecasts, h1 individual predictions and some historical side-experiment artifacts remain unavailable. The report identifies these gaps without inventing replacements.
