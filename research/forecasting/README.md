# Maharashtra forecasting research programme — seven workstreams

**Status: development started across all seven priorities. No validated Maharashtra forecast exists.** Code readiness is separate from data readiness and scientific validation. This package extends the existing inventory explorer, satellite catalogue checks and segmentation sample demonstration; those remain distinct experiments.

## Start here

```powershell
python -m pip install -r research/forecasting/requirements.txt
python research/forecasting/pipeline.py audit
python research/forecasting/pipeline.py demo
python -m unittest discover -s tests -p "test_forecast*.py"
```

The audit uses real bundled NASA COOLR report records. The demo generates **1,500 synthetic slope-day examples** solely to test the software. Its metrics and reliability plot are not evidence of forecasting skill in India. The two outputs have separate folders and explicit interpretation metadata. No synthetic record is added to the atlas inventory.

Use GitHub Actions → **Forecasting research checks** → **Run workflow** to run tests, audit and synthetic benchmark. Download the resulting artifact. It does not update the website or issue alerts. No recurring job is configured.

## Seven priorities, concrete starts, acceptance gates

| Workstream | Implemented start | Evidence still needed before completion |
|---|---|---|
| 1. Verified inventory | Reproducible Maharashtra report audit, candidate CSV, inventory and survey templates | Source access/permission, deduplication, mapped units, independent review, bounded event timing and systematic coverage |
| 2. Historical rainfall | Official satellite access prototype; interval table and availability-aware 24/72/168 h feature builder | Authorized numerical time series, spatial extraction by unit, gauge comparisons and documented bias correction |
| 3. Forecast target | Draft 24 h slope-unit target and timestamp conventions | Team approval, chosen mapped units, evidence that target labels can be observed reliably |
| 4. Benchmarks | Terrain-only and rainfall-only logistic models; combined logistic, Random Forest and histogram gradient boosting; training-prevalence baseline | Real eligible training table, rainfall-threshold comparator, frozen feature/hyperparameter choices |
| 5. Independent evaluation | Temporal/group separation checks, validation-only thresholds, reliability plots, storm-group bootstrap intervals | Multiple suitable seasons, external geography, field verification and prospective shadow testing |
| 6. Field observations | Site screening, instrument and maintenance plan; field and sensor CSV templates | Landowner/institutional permissions, qualified site assessment, installation, calibration and actual measurements |
| 7. Reproducibility | Versioned protocol, CLI, tests, seeded demo, environment and input checksums, manual CI artifact | Reviewed data releases, recorded model artefacts/configurations, independent reproduction and archive DOI |

## Real-data workflow

1. Review `outputs/inventory/maharashtra-candidate-reports.csv`. These reports are leads, not training labels. Populate `templates/event_inventory.csv` and `templates/survey_coverage.csv` through documented evidence review. Keep ambiguous/missing outcomes unknown. A lack of reported events is not a verified negative.
2. Define stable `unit_id` polygons in a reviewed GeoJSON and obtain authorized rainfall grids/gauges. Use the satellite module for product access, then spatially aggregate each interval to each unit. The current satellite importer summarizes the pilot box, **not** individual slope units. Do not relabel that box average as local slope rainfall.
3. Populate `rainfall_intervals.csv` in **mm per interval**, with true publication/availability times and valid-cell fraction. Values from an hourly/half-hourly rate must first be integrated over their actual interval. Do not substitute mm/h for mm. Keep dataset versions separate.
4. Populate `forecast_issues.csv`, then build antecedent features:

```powershell
python research/forecasting/pipeline.py features --issues private/forecast_issues.csv --rainfall private/rainfall_intervals.csv --output private/features.csv
```

The builder requires contiguous, nonoverlapping, fully observed windows, all available by issue time. Incomplete windows produce missing values, never zero. Because near-real-time rainfall is delayed, a window ending at issue time can legitimately be missing. A future extension should explicitly add a lagged-window feature (for example, ending at the latest usable observation) or a separately identified issued weather forecast; do not silently backfill unavailable observations. Daily rainfall cannot simply be split into hourly observations. Reanalysis/final-product reconstructions are separate sensitivity analyses, not operational hindcasts unless actual availability is known.

5. Join independently reviewed outcomes and pre-issue terrain into `benchmark_table.csv`. This join requires scientific review; the software does not automatically invent labels from report dates. `group_id` must cluster related storms/landslide episodes, potentially across units; its definition must be frozen before partitioning. Feature availability and source evidence must be independently audited; the validator cannot prove that a user-supplied table is true.
6. Assign explicit train/validation/test partitions according to `PROTOCOL.md`, then run:

```powershell
python research/forecasting/pipeline.py benchmark --input private/benchmark_table.csv --output private/research-run
```

The validator requires both classes per partition, reviewed coverage and labels, no duplicate unit/issue, a 24 h outcome interval, no shared storm group across partitions, and chronological separation based on outcome availability. Missing or invalid required data stop the benchmark. It does **not** enforce a geographic buffer or perform external transfer testing; those require a separate frozen study design.

Outputs include test predictions, discrimination/error metrics, Brier scores, five-bin reliability plots and storm-group bootstrap intervals (minimum 10 groups; 200 resamples). These intervals condition on the fitted model and omit training/inventory uncertainty. Thresholds minimize an illustrative validation-only cost of `5 × missed events + false alarms`; this is a software experiment setting, not an approved warning policy. Confidence intervals and a visually plausible reliability plot do not establish operational reliability. There is no automatic model selection from test results or public alerting.

Keep restricted or unreleased data in the ignored repository `private/` directory or outside this repository. Do not publish field staff personal information, access credentials or unapproved site details. Public contribution templates have headers only, not fabricated field records.

## Scope and coordination

See [protocol](PROTOCOL.md), [fieldwork plan](FIELDWORK.md), [coordination and release plan](WORKPLAN.md), and [source ledger](SOURCES.md). All seven can advance together, but training depends on verified inventory and predictors; prospective validation depends on a frozen model and monitored outcomes. No collaborators have been contacted, instruments purchased or installed, or external data-access agreements made by this package.
