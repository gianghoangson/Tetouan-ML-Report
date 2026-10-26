# Bibliography provenance

This ledger preserves the verification established during the completed repository audit. It is not a new full-text review or an independent reproduction of cited experiments. Bibliography identities are distinguished from numerical claims transcribed from the local literature review. No new external performance claims were introduced during final integration.

| Key | Traceable primary record | Verification and limits |
|---|---|---|
| `uci` | https://archive.ics.uci.edu/dataset/849/power+consumption+of+tetouan+city ; DOI 10.24432/C5B034 | Dataset identity, creators and suggested citation checked in prior audit. Suggested year 2018 differs from donation year 2023. Landing-page 52,417 count differs from the local 52,416 data rows. |
| `salam2018` | DOI 10.1109/IRSEC.2018.8703007 ; UCI introductory-paper record | Identity corroborated by UCI and supplied review. IEEE full-text access was blocked; configuration/performance details remain explicitly review-reported. |
| `rose2023` | https://www.atlantis-press.com/proceedings/icacecs-23/125995751 ; DOI 10.2991/978-94-6463-314-6_7 | Publisher metadata checked in prior audit. Numerical values follow the local comparison. The review's optimizer inconsistency remains unresolved. |
| `silva2023` | DOI 10.1016/j.egyr.2023.09.175 ; publisher article S2352484723014208 | Publisher search record corroborates identity/venue/year/pages; direct page access was limited. No configuration-specific metric is invented where the repository comparison has none. |
| `islam2025` | https://link.springer.com/article/10.1007/s11135-024-02043-0 | Publisher metadata/abstract checked. Online 2024, volume year 2025. Abstract covers individual zones and their average; target of the local selected metric row remains unclear. |
| `alsalem2025` | https://www.nature.com/articles/s41598-025-91123-8 | Primary article identity and reported figures checked in prior audit. The zone target and short-lag setup are not equated to the current hourly total. |
| `biswas2026` | DOI 10.1016/j.rineng.2026.110289 | Publisher record corroborates authors, volume and article number. Repository comparison leaves RMSE/horizon unavailable for its selected row; these are retained as unavailable rather than filled from a different description. |
| `bergstra2012` | https://jmlr.org/papers/v13/bergstra12a.html | Official paper record, authors, title and pages support the random-search reference. |
| `chen2016` | https://arxiv.org/abs/1603.02754 | Original author paper supports the XGBoost method citation; it does not supply this project's scores. |
| `lundberg2017` | https://arxiv.org/abs/1705.07874 | Original author paper supports the SHAP attribution framework. The repository's residual-tree implementation determines the scope of its plotted contributions. |
| `tscv` | https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html | Official API documentation supports the expanding-window interface. Actual repository arguments determine this report's folds. |
| `pitfalls` | https://scikit-learn.org/stable/common_pitfalls.html | Official documentation supports training-only fitted preprocessing and pipeline discussion. It does not certify the repository's predictor availability. |

All 12 entries are traceable; primary full texts were not accessible or revalidated for every entry. Exact project numerical evidence comes from saved repository outputs, with the local review used for explicitly identified literature transcriptions. Citation-key resolution is checked by `validate_report.py`; successful Biber processing, when available, provides a separate bibliography-syntax check.

## Final peer-review recheck

The 26 October 2026 final review revisited the UCI, Atlantis Press, Springer, Scientific Reports, JMLR, arXiv and scikit-learn records. Publisher search records corroborated both Elsevier entries; direct article requests returned HTTP 403. The IEEE page required browser verification. Bibliography entries were retained, with no newly asserted full-text verification or invented metadata. The precise scope and direct links are recorded in `FINAL_REVIEW.md`.
