# Verification record

Checked locally on 30 October 2026.

- Seven Node.js test groups passed: filters and undated handling; coordinates/dates/provenance; CSV parsing and formula escaping; polygon holes and border ambiguity; grid count conservation; actual snapshot counts, IDs and sampled spatial joins.
- JavaScript syntax checks passed.
- Browser verified: Maharashtra default resolves source diacritics; Maharashtra has 79 reports in this snapshot; the Maharashtra source district named Raigarh has eight; All India has 1,741.
- A future-year selection produced the empty-data state after checking responsive input events.
- Map PNG (2700 × 1800) and SVG downloaded successfully. Timeline PNG (2100 × 1170) downloaded and was visually inspected. These dimensions are 3× the vector view boxes, not a claim of sensor resolution or print DPI.
- A clearly labelled synthetic QA-only contribution was added locally, a note saved, and both survived a reload. Importing its saved project again added zero duplicate records. The temporary contribution and its note were then removed; the source dataset was never changed.
- No browser console errors were reported during these checks.
- Desktop rendering visually inspected. Responsive CSS is included; a separate mobile-device run has not been performed.
- Public publication scope is this app directory only. Download caches, test output, credentials, manuscripts, author email records, journal PDFs and the third-party GSI mirror are excluded.

GitHub publication verified: the public repository contains the expected 20 files. The Actions test job passed; the deployed site and source manifest returned HTTP 200 at https://dinesha-dsa.github.io/landslide-atlas/. Live browser loading displayed the expected 79 Maharashtra reports. The source ledger preserves the upstream 736-declared / 735-downloaded district discrepancy.

Model-availability regression checked: Kerala and Pune show no model and hide the pilot panel; Maharashtra overall shows pilot results only; Raigarh shows a partial-area pilot; India overall shows no national model. This changes display and scope communication, not the underlying data or model coverage.
# Satellite-input prototype (2026-10-30)

Queried official CDSE STAC for Sentinel-1 SLC footprints intersecting the fixed southern Raigad rectangle in the preceding 60 days: 9 records returned in the initial snapshot. Latest listed acquisition: 2026-10-24 01:02 UTC. These are catalogue metadata, not processed radar observations or displacement estimates.

NASA GES DISC IMERG Early V07 directory listing succeeded; numerical download probe returned HTTP 401. Initial snapshot therefore has no rainfall measurement. The older PMM OpenSearch endpoint returned HTML instead of the documented JSON and is not used. No substituted precipitation product or inferred values are published.

Validation: four Python tests cover half-open half-hour timing, midnight rollover, rate/depth conversion, fill masking, all-missing handling, unknown units and future intervals. Eight Node test groups cover existing explorer behaviour and timestamp freshness display. HDF5 tests use synthetic fixtures only; the import has not yet been validated on an authorized real IMERG granule. Local browser inspection confirmed source status rendering and readable responsive layout. The public JSON includes source-query URLs and hashes, acquisition/publication times for radar, and the rainfall download access outcome. Refresh is manual, not an operational monitoring service.

# Seven-priority development start (2026-10-30)

Executed a source-checksummed audit of all 1,741 bundled NASA COOLR reports: 79 Maharashtra reports, all with a reported date, and 6 inside the fixed pilot rectangle. These remain unverified candidate reports, not deduplicated authoritative events or eligible forecast labels. Saved the candidate CSV, audit JSON and a year-count SVG; no hazard trend is inferred.

Executed a separately labelled synthetic benchmark of 1,500 unit-day examples, with explicit 2021 training, 2022 validation and 2023 test roles and storm groups kept within partitions. Compared terrain-only/rainfall-only logistic baselines, combined logistic, Random Forest, histogram gradient boosting and training prevalence. Saved synthetic inputs, predictions, metrics, grouped confidence intervals, environment/input fingerprints and a reliability SVG. No Maharashtra model was trained. No field sensor installation, external communications or new data agreements occurred.

Nine forecasting tests passed: temporal feature integration, source availability cutoffs, missing/overlapping/incomplete rainfall, invalid rainfall, valid partitions, grouped-event leakage, unverified outcomes, late training outcomes, validation threshold choice and duplicate issue rejection. Existing Node tests also pass. Browser QA verified seven cards, no horizontal overflow at the narrow preview size, and explicit synthetic-only figure labelling. The draft protocol is not preregistered; it still needs team/domain approval, real verified outcomes, an external geography design and prospective monitoring.

