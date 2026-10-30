# Landslide Atlas — India research workspace

**Live dashboard:** https://dinesha-dsa.github.io/landslide-atlas/  
**Source repository:** https://github.com/dinesha-dsa/landslide-atlas

A GitHub Pages static dashboard with India state/UT and district selection, attributable NASA COOLR report points, local observations and notes, and reproducible research figures.

## Research starter: deep learning and Maharashtra evaluation

See [the landslide segmentation research module](research/landslide-segmentation/README.md) for a reproducible sample downloader, verified image/mask checks, research-paper PDF links, official baseline code access, full-dataset manifests and a proposed Maharashtra evaluation protocol.

Run [the research sample demonstration on GitHub Actions](https://github.com/dinesha-dsa/landslide-atlas/actions/workflows/research-demo.yml) to generate a training-example preview and verification report without installing Python locally. The module guide includes an attributed example image and instructions for running it in a fork.

This module helps scholars begin a Landslide4Sense/U-Net reproduction. It provides data preparation and study guidance; no deep learning model has been trained or evaluated here. Segmentation of visible landslide footprints does not establish future susceptibility or warning performance. The module runs locally in Python and is separate from the dashboard's exploratory Raigad pilot.

## What works

- A red-highlighted future-prediction research objective, explicitly labelled as proposed and unvalidated, with pre-event data and independent temporal-testing requirements. Red emphasis marks the objective, not geographic hazard predictions.

- A four-minute English video guide with synthetic narration, 24 caption cues, eight seekable chapters, a complete transcript and downloadable MP4/captions. Open **Video guide** in the dashboard navigation. The video explains evidence limits and the research demonstration; it is not model output.

- State/UT and district selection using dated geoBoundaries geometry snapshots.
- A snapshot of 1,741 NASA COOLR India report points; event-year, undated-record and trigger filters.
- An interactive geographic map with pan, zoom and a report-count grid. The grid is **not susceptibility**.
- Four analytical figures: dated reports through time, triggers, reporting geography and evidence completeness.
- Map/chart exports as vector SVG and 3×-resolution PNG. SVG metadata embeds the filters, selected record IDs and source ledger.
- Filtered CSV and GeoJSON, a reproduction manifest, and import/export of a local research project JSON.
- Source-required observation entry, CSV/Point-GeoJSON import, and notes on individual records. Contributions and notes persist in the same browser; they do not silently change source records.
- A source ledger with download URLs, transformations, citations, boundary dates, licences and original-download SHA-256 hashes.
- Selection-aware model availability: other states/districts explicitly show no trained model; all-India shows no national model. The southern Raigad pilot results appear only for Maharashtra overall or its Raigarh/Raigad district, with partial-area limits.

## Run locally

No JavaScript dependencies or API keys are needed. From this directory:

```text
python -m http.server 8765 --directory docs
```

Open `http://localhost:8765`. Serve over HTTP; opening `index.html` directly with `file://` can block dataset loading.

Run checks with Node.js 22 or later:

```text
npm test
```

Or `node --test tests/core.test.js` if npm is unavailable. The automated checks cover filtering, date/coordinate validation, CSV escaping, geometry membership, spatial assignments and snapshot integrity.

## Publish with GitHub Pages

1. Create a repository named `landslide-atlas` in your GitHub account. Upload **this directory's contents only**, preserving `.github/workflows/pages.yml`. Do not upload the surrounding manuscript workspace.
2. Use `main` as the default branch. In **Settings → Pages → Build and deployment**, choose **GitHub Actions** as the source.
3. Push a change or manually run **Test and deploy research atlas** from the Actions tab. After successful deployment, use the Pages URL returned by GitHub. A repository URL by itself does not render HTML as a website.

The included workflow tests the code and uploads only `docs/`. It requires no personal access token in the repository. If using the CLI with an authenticated account, a typical first publication is:

```text
git init -b main
git add .
git commit -m "Add source-linked landslide research atlas"
gh repo create landslide-atlas --public --source . --remote origin --push
```

Then enable the Pages Actions source in Settings. Repository creation and live deployment still require an authenticated GitHub account; do not claim a live URL until the deployment succeeds.

## Research interpretation

This is an observation explorer, not a hazard warning system or validated susceptibility product. The 1,741 records are repository reports, not necessarily distinct events. Zero reports can reflect missing reporting. Locations, dates and category labels can be uncertain. Counts are not normalized for area, population, reporting effort or surveyed coverage. There is no model for every state or district.

Boundaries retain source names and differing vintages. Maharashtra's `Raigarh` name refers to the source snapshot's district label; users looking for Raigad should select that entry. ADM2 metadata declares 736 units while the simplified download contains 735; the app preserves the actual geometries and documents the discrepancy.

The public NASA reports differ from the GSI-attributed mirror used by the original terrain-only Raigad pilot. The public app does not redistribute that mirror, exact training points, model files or unreviewed manuscripts.

## Collaboration and storage

GitHub Pages is static hosting. Added observations and notes are stored locally under `landslide-atlas-session-v1`; there is no server database and no shared live editing. Use **Save project JSON** and have a colleague import that file to merge contributions. Project imports preserve record IDs so repeated import does not duplicate those records. Generic CSV/GeoJSON imports are added as new local contributions and are not automatically deduplicated.

Browser storage can be cleared by the browser or user. Export projects as a backup. To propose a reviewed public data update, open an issue or pull request in the repository with source, permission and validation evidence. Do not post personal or sensitive field information publicly.

## Refresh the snapshot

`scripts/prepare_data.py` requires Python, `requests` and `geopandas` (the parent workspace's Python environment already includes these). It retrieves source metadata and point records by object-ID batches, checks the returned counts, and computes region joins. Downloads are cached in ignored `.cache/`. For a deliberate refresh, move the cache to a backup location, rerun the script and inspect changed counts, source terms, metadata, schemas and geometry. Do not replace failed downloads with fabricated observations.

The manifest records the preparation time. Upstream URL and original-response hashes allow auditing the cached inputs. The Git commit and exported manifest identify a published snapshot; downloads are not automatically refreshed by the public website.

## Attribution

See [DATA_LICENSES.md](DATA_LICENSES.md) and [the source ledger](docs/data/manifest.json). Code is MIT; NASA contributions and boundary datasets retain their own terms. In particular the adapted district boundary database remains under ODbL, separately from the application code.

## Next research steps

### Maintain the narrated guide

The published guide is `docs/media/research-tour.mp4` (about 2.4 MB). Chapter text is in `docs/media/research-tour.json`; timed captions, chapter metadata and provenance are alongside it. To rebuild on Windows with Microsoft Zira Desktop installed, install `Pillow` and `imageio-ffmpeg` in a separate Python environment, then run `python scripts/build_research_tour.py`. The script invokes Windows System.Speech through `scripts/generate_tour_voice.ps1`; it needs no external speech service or API key. Inspect slide layout, encoded duration, audio stream and captions after rebuilding. If chapter text/timing changes, update the static chapter controls and transcript in `docs/index.html` to match the generated metadata. Build intermediates remain in ignored `.cache/research-tour/`.

Obtain an authoritative dated landslide inventory and survey footprint; collect pre-event covariates and field checks; evaluate whole-event and district holdouts; quantify calibration and decision benefit where identifiable. Shared backend storage, review roles and automated model execution would need a separate authenticated service. They are not provided by GitHub Pages or this version of the app.
# Satellite-input research prototype

The [Raigad satellite module](research/satellite-feeds/README.md) adds official NASA IMERG and Sentinel-1 SLC catalogue checks, timestamped provenance, and optional authorized rainfall-file import. Open **Satellite inputs** in the dashboard. It is a fixed pilot rectangle, independent of explorer filters. No forecasting skill or radar-derived displacement is claimed. Rainfall download authentication and missing measurements are shown explicitly. A manual Actions workflow produces a refresh artifact for review; it does not update the website automatically.

# Seven-priority forecasting research programme

Open **Research plan** in the dashboard or the [forecasting starter](research/forecasting/README.md). Development has started across inventory verification, historical rainfall, a defined target, baselines, independent evaluation, field planning and reproducibility. The executed inventory audit identifies 79 Maharashtra candidate reports (6 in the pilot rectangle), with zero independently verified forecast labels. The separate 1,500-row synthetic benchmark checks software only. Field monitoring and validated Maharashtra forecasts remain pending. Use the included templates, draft protocol and manual GitHub research workflow to continue.

