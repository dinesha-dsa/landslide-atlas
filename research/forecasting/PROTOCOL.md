# Draft protocol v0.1 — not preregistered or approved

## Question and hypothesis

Does antecedent rainfall improve 24-hour landslide forecasts over terrain-only and prevalence baselines for independently monitored Maharashtra slope units when actual input availability is respected? Does any gain persist in a held-out season and an external district? The latency-aware combination is a candidate contribution; no claim of being the first is made. Current code implements a temporal benchmark; external-district and prospective studies remain to be designed and run.

## Target and units

Primary target: at least one independently verified rainfall-triggered **shallow landslide** initiating in a fixed mapped slope unit during `(issue_utc, issue_utc + 24 h]`. Freeze the geomorphic landslide definition and polygon membership rule before labelling. Deep-seated movement and rockfalls are separate outcomes. Forecasts are at unit level, not exact time/location predictions. Store UTC internally and display IST with explicit zone if needed. One issue per unit per day for the initial study; choose issue hour according to input latency and operational use before analysis.

A positive label requires reviewed source evidence and a bounded time interval assignable to the target window. A date-only report cannot be treated as an exact event time. Events straddling window boundaries are excluded from the primary analysis or analysed in a prespecified timing-uncertainty sensitivity analysis. A negative label requires documented surveillance/survey coverage sufficient to support no observed qualifying event in that unit/window. Unknown outcomes remain unknown, not zero. Separate time of event from time of reporting and time verification became available.

## Development and independent evaluation

* Select Raigad development units after inventory/coverage appraisal. Choose a second district only after confirming compatible data, terrain and survey processes. No district has yet been reserved as an independent test set.
* Freeze datasets, feature list, storm grouping and partition dates in a versioned configuration. Training seasons precede validation seasons; untouched test seasons follow them. Earlier labels must have been available before later partition issue dates. Apply a purge based on label windows and storm duration. Keep the same landslide episode and associated storm out of multiple partitions. Input histories can overlap legitimately in chronological forecasting; future labels or future observations cannot enter training.
* Tune hyperparameters, calibration and decision thresholds only within training/validation data. Do not choose a preferred model or novelty based on test performance. The starter uses fixed modest model settings and validation-only thresholds. A final study must add nested blocked tuning if needed and freeze the settings before test evaluation.
* Compare training prevalence, terrain-only logistic, rainfall-only logistic, a local empirical rainfall threshold, combined logistic, Random Forest and gradient boosting. The empirical threshold comparator is specified but not yet implemented because no local verified event/rainfall history exists. Add soil moisture or InSAR only as a separately evaluated feature set with documented availability and missingness. Missing InSAR does not imply stable ground.
* Report event counts, monitored unit-days, event prevalence, survey completeness and class balance in every split. Report PR-AUC/average precision, ROC-AUC, recall, precision, false alarms per monitored unit-day, Brier score and reliability plots. Select alert utility with domain partners before operational use. The starter's 5:1 miss/false-alarm cost is illustrative. Evaluate grouped uncertainty and uncertainty from rainfall bias/event timing; do not treat adjacent pixels as independent events.
* External transfer must use an untouched geography and explicit buffer/terrain-domain assessment. Evaluate without retuning first; report a separately identified adaptation experiment if local recalibration is used. No such result is currently available.

## Latency and prospective phase

Record input observation start/end, first accessible publication time, retrieval time, product version and any revision. Hindcasts must use a defensible as-issued archive; later final rainfall or reanalysis is an oracle/sensitivity comparison, not operational input. Future rainfall forecasts, if added, require provider issue time, lead time, valid time and archived forecast version. Current code uses antecedent observed rainfall only; it does not ingest numerical weather forecasts.

After independent retrospective review, freeze one candidate and log timestamped forecasts prospectively in shadow mode for a complete suitable monitored season. Store unavailable predictions and outages rather than dropping them. Verify events independently of predictions. Report actual issue-to-event lead time only for events with adequate timing; a 24 h target is not automatically a 24 h warning lead. Decide sample sufficiency from event counts and interval widths; a single monsoon does not guarantee adequate evidence. No public warning dissemination is authorized by this protocol.

## Release and research integrity

Protocol approval, author roles, study-site permissions, source permissions, privacy review, labelling adjudication and prospective study registration remain pending. Archive protocol changes and distinguish exploratory from prespecified analyses. Before submission, independently reproduce results and check current literature to establish the precise contribution. Software tests and synthetic metrics cannot substitute for field evidence or publication review.
