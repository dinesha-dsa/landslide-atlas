# Landslide Atlas — India research workspace

**Live dashboard:** https://dinesha-dsa.github.io/landslide-atlas/  
**Source repository:** https://github.com/dinesha-dsa/landslide-atlas

A GitHub Pages static dashboard with India state/UT and district selection, attributable NASA COOLR report points, local observations and notes, and reproducible research figures.

## What works

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

Obtain an authoritative dated landslide inventory and survey footprint; collect pre-event covariates and field checks; evaluate whole-event and district holdouts; quantify calibration and decision benefit where identifiable. Shared backend storage, review roles and automated model execution would need a separate authenticated service. They are not provided by GitHub Pages or this version of the app.
