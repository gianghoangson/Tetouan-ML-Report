# Tetouan electricity forecasting presentation

**18 slides, no backup slides, English, 16:9 LaTeX Beamer.** The presenter plan totals exactly **15:00**, followed by Q&A.

The user authorized the existing root-level `Tetouan-ML-Report/` repository after the originally specified nested report path was found missing. ML evidence was read exclusively from `Prj Tetouan ML/Machine-Learning/`. The outer `Machine-Learning/` was not used.

## Deliverables

| File | Purpose |
|---|---|
| `main.tex` | Presentation source; exact title-page identity, proportional FDA faculty logo, no submission date |
| `metrics.tex` | Display values generated from verified saved results |
| `evidence_map.md` | Claim-by-claim sources, active-version decisions and scientific qualifications |
| `presenter_notes.md` | 18 scripts, timings, takeaways and transitions; Minh/Son speaking plan |
| `qa_preparation.md` | 12 likely instructor questions with concise and expanded answers |
| `figures/` | Five simplified vector PDF charts and PNG previews |
| `build_assets.py` | Read-only analysis of original evidence; writes only presentation artifacts |
| `verification.json` | Numerical checks, figure matches and preservation checks |
| `original_files_manifest.json` | SHA-256 hashes of 194 pre-existing files in both authorized repositories |
| `validate_slides.py`, `quality_check.json` | Source structure, paths, identities, timing and preservation checks |
| `main.pdf` | Compiled 18-page presentation |

The current `main.pdf` compiles successfully with the installed LaTeX environment. All 18 rendered pages were visually inspected after the layout refinement. No new software or packages were installed.

## Design and visuals

White background, dark navy text, restrained blue accents, Latin Modern Sans typography and a slide-number footer. Source lines are removed from the visible deck; claim provenance remains in `evidence_map.md`. Metropolis is used if available, with a custom-styled default Beamer fallback. The 18 frames have no overlays or automatic section dividers.

Eight data visuals are used:

1. Annual hourly load: original `results/figures/F01_total_hourly_year.png`.
2. Seasonal daily profiles: original `results/figures/F03_profile_by_season.png`.
3. Exact expanding-window folds, generated from T02.
4. All ten tuned CV variants with sample SD, generated from T07.
5. Selected SVR, two baselines and observed test-best residual SVR, from T08.
6. Whole-December load and aligned residuals, from all 720 saved forecasts.
7. January-November autocorrelation, a slide-size view of F07.
8. Same-hour weekday percentage differences, the right-panel data from F04.

The two reused figures match the authorized ML figures byte-for-byte. F19a/F19b differ between repositories and are not used. All final LaTeX figure paths remain inside the report repository. Neither the dataset nor the experiment repository was copied.

## Compile from the report repository root

From the workspace root in PowerShell:

```powershell
Set-Location -LiteralPath 'C:\Users\Giang Hoang Son\OneDrive\Desktop\nam 3 ki 1\statistic\Tetouan-ML-Report'
```

If already there, do not change directory again. This authorized root-level report location replaces the missing nested path.

Build with the installed TeX environment:

```powershell
latexmk -pdf -interaction=nonstopmode -file-line-error -halt-on-error -outdir=slides slides/main.tex
```

To explicitly prevent automatic package installation under MiKTeX:

```powershell
latexmk -pdf '-pdflatex=pdflatex --disable-installer %O %S' -interaction=nonstopmode -file-line-error -halt-on-error -outdir=slides slides/main.tex
```

If latexmk/Perl is unavailable, use the existing pdfLaTeX directly, twice:

```powershell
pdflatex --disable-installer -no-shell-escape -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=slides slides/main.tex
pdflatex --disable-installer -no-shell-escape -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=slides slides/main.tex
```

`--disable-installer` is MiKTeX-specific; omit it on TeX Live. No Biber/BibTeX is needed; source mappings remain in `evidence_map.md`. Expected successful output is `slides/main.pdf`.

### Actual build status

The requested `latexmk` command completed from the report root and produced a 18-page PDF. The final build log has no overfull box warnings. Every rendered page was inspected for collisions, clipping, chart and table readability, and footer clearance. Scientific caveats previously embedded in source lines now appear in slide bodies.

### Overleaf option

Upload this minimal structure, preserving folders:

```text
slides/main.tex
slides/metrics.tex
slides/figures/*.pdf
report/assets/fda-logo.png
results/figures/F01_total_hourly_year.png
results/figures/F03_profile_by_season.png
```

At the Overleaf project root, create a launcher `main.tex` containing `\input{slides/main.tex}` and select that launcher as the main document. Use pdfLaTeX. This preserves the repository-equivalent working directory. No project was uploaded or published during this task.

## Scientific verification

The selected absolute-target SVR was determined by development CV (RMSE 2,410.6 ± 766.3 kW). December performance is RMSE 1,624.6 kW, MAE 1,094.6 kW, MAPE 1.78% and R² 0.9869. RMSE reductions are 50.7% versus Naive-24h and 38.0% versus Naive-168h. Residual SVR's observed 1,419.1 kW test RMSE does not change model selection.

Current h1 results are CV-only with h24-selected parameters. Historical h1 December results from the older report audit are excluded. The deck discusses target-hour observed weather, prompt load availability, documented test reruns, repeated development selection, non-isolated leakage comparisons and limited geographic/temporal coverage.

`build_assets.py` passed **304 checks**, including four metrics for all 17 saved December prediction columns, CV/search consistency, data/target checks and 194 original file hashes. XGBoost serialization differences are below displayed precision. `quality_check.json` records additional source-integrity checks. These counts are validation checks, not independent experiments or statistical tests.

## Rebuild assets or rerun checks

From the report root, using already installed NumPy, pandas and Matplotlib:

```powershell
python slides/build_assets.py
python slides/validate_slides.py
```

Asset rebuilding reads the exact authorized ML path and needs its existing raw data and saved tables. **Compiling LaTeX needs neither Python nor the ML repository.** The scripts do not import project modules, execute notebooks, train models or rewrite original outputs.

The manifest excludes Git internals. Git status was blocked by an ownership safeguard; no Git configuration was changed. Hashes and new-file enumeration independently confirm that all pre-existing files were preserved and all new files are inside `slides/`.

## Current narrative and timing

The 18-slide deck contains two EDA slides after the seasonal load profile. Tuning is merged into the CV result, and findings are merged with limitations. The 15:00 plan gives Minh slides 1-9 (6:30) and Son slides 10-18 (8:30); the handover remains after chronological CV. No backup or SHAP slides are included.

The F07 ACF and F04 right panel are redrawn with larger labels in slides/figures/acf_view.pdf and slides/figures/weekday_difference.pdf. Running python slides/refresh_eda_view.py refreshes both views from January-November data without training any model or changing experiment outputs. The evidence map records the supplied 48-hour ACF .96 versus the saved prose's .97.

The selected SVR metrics, title design, FDA logo and slide visual identity are preserved.
