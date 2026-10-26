# Tetouan ML research report

The English report is an A4, single-column academic document with thirteen sections, a title page, abstract, bibliography and supplementary appendix. It uses saved repository evidence. Building the report does **not** require running notebooks or training models.

## Files and evidence

- `main.tex`: entry point; all paths are relative to the **repository root**.
- `sections/`, `appendices/`: modular report text.
- `references.bib`: BibLaTeX bibliography, processed with Biber.
- `tables/`: LaTeX tables generated from existing CSV/JSON artifacts.
- `research_audit.md`: claim/source mapping, discrepancies and limitations.
- `reference_verification.md`: bibliography provenance and verification limits.
- `REPORT_PROGRESS.md`: completion and handoff status.
- `validation_summary.md` and `evidence/report_validation.json`: final checks and compilation status.
- `FINAL_REVIEW.md`: strict scientific/LaTeX peer review, confirmed corrections and readiness assessment.
- Figures are loaded directly from `../results/figures/` relative to this folder; no image copies are needed locally.

Student/team information, IDs, class, instructor and submission date are intentional title-page placeholders. Fill these in `main.tex` before submission.

## Local compilation

Use an existing TeX Live or MiKTeX installation with pdfLaTeX, Biber and the packages declared in `main.tex` (including `biblatex`, `siunitx`, `cleveref`, `microtype`, `lmodern`, `placeins` and the table/graphics packages). `latexmk` is optional; its installation may additionally require Perl. No LaTeX software or packages were installed while producing this report.

Open a terminal in the repository root, the directory containing `data/`, `results/` and `report/`. Run the following commands individually:

```powershell
pdflatex --disable-installer -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=report report/main.tex
biber --input-directory report --output-directory report main
pdflatex --disable-installer -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=report report/main.tex
pdflatex --disable-installer -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=report report/main.tex
```

`--disable-installer` is a **MiKTeX-specific** option that prevents automatic package installation. On TeX Live, omit that option; keep the remaining arguments. Biber uses `report/main.bcf` and writes `report/main.bbl`. Expected final output is **`report/main.pdf`**. The first pass normally reports undefined citations/references; inspect warnings after the final pass. Additional passes may be needed when table-of-contents or bibliography pagination changes.

Alternatively, if `latexmk` and its prerequisites are operational:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=report report/main.tex
```

On MiKTeX, configure package installation to require confirmation or disable it before this alternative command; the explicit pdfLaTeX commands above enforce the restriction themselves. Do not use `latexmk -cd`, since this document expects the repository root as its working directory.

If MiKTeX reports an incomplete installation or cannot initialize its user configuration, finish configuring the existing installation in MiKTeX Console under your normal account. If a `.sty` file is missing, the log identifies the required package. Installing missing software/packages is a separate user action, not part of report generation. The current build outcome and exact blocking error, if any, are recorded in `validation_summary.md`.

## Overleaf

Create a blank project and upload the following paths **with their directory structure preserved**:

```text
report/main.tex
report/references.bib
report/sections/*.tex
report/appendices/*.tex
report/tables/*.tex
results/figures/*.png
```

You do not need the dataset, notebooks, Python helpers or extracted evidence to compile. At the Overleaf project root, create a short launcher named `main.tex` containing:

```latex
\input{report/main.tex}
```

Select that **root-level launcher** as the main document and pdfLaTeX as the compiler. Overleaf's build system should run Biber for the document's BibLaTeX configuration. The launcher keeps the compilation working directory at the root, so both `report/...` inputs and `results/figures/...` paths resolve. Do not upload only the contents of `report/` without adjusting paths. Clear cached files and recompile if the bibliography remains stale after changes.

## Evidence checks without retraining

These Python helpers use the locally available review environment. Pandas and NumPy are needed for saved-result checks/table generation; the full ML dependency environment is not required for compiling LaTeX.

```powershell
python report/check_evidence.py
python report/build_tables.py
python report/validate_report.py
```

`check_evidence.py` reads existing data and outputs, recalculates metrics from saved h24 forecasts, and writes `report/evidence/numerical_checks.json`. `build_tables.py` reads saved tables/JSONs and writes only report table fragments/source mappings. `validate_report.py` walks the LaTeX include graph, checks labels/citations/assets, verifies selected numerical claims and original artifact hashes, and records any available build-log diagnostics. It exits nonzero for failed content checks; lack of a successful PDF build is reported separately.

`validate_sections_06_09.py` retains the earlier scoped checks. `inspect_evidence.py` is the original audit-extraction helper and normally need not be rerun. None of these commands executes notebooks. Do not run `run_all.py` merely to compile or validate the report: its normal workflow fits models and replaces project experiment outputs.

The optional `python report/review_checks.py` reproduces the final peer-review checks, including S2's row-split dependency. It also requires scikit-learn for `train_test_split`, but fits no model. Results are saved in `evidence/peer_review_checks.json`.

## Reading the results correctly

The final model is absolute SVR selected by development CV for both settings. Residual SVR has lower observed h24 December RMSE and is reported as the test-best candidate, without changing that selection. h24 is a midnight daily-batch/minimum-history-lag setting, not a uniform 24-hour issuance lead. Both settings condition on observed target-hour weather, and project documentation records repeated test evaluations. S1–S4 change several factors, so their differences do not isolate leakage. The audit and report state these limits explicitly.
