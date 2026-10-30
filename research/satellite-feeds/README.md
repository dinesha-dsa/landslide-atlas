# Satellite inputs for a Raigad forecasting study

This prototype queries official NASA and Copernicus data catalogues. It does not communicate directly with a spacecraft. It does not issue landslide warnings, predict a failure time, or estimate ground displacement.

## Study footprint and current outputs

Fixed WGS84 rectangle: west 73.02°, south 17.8°, east 73.7°, north 18.6°. This southern Raigad pilot rectangle is **not the district boundary** and does not follow dashboard state/district selections. The public snapshot is `docs/data/satellite-feeds.json`. Each run replaces the snapshot with the actual query outcome, including failures; it never presents an old success as a new successful measurement. Retain versioned snapshots for longitudinal research.

* **Sentinel-1 SLC:** public CDSE STAC query for intersecting footprints in the preceding 60 days, newest first, at most 12 records. Includes acquisition and publication times, platform, relative orbit, direction and item source links. Adjacent slices can be from one pass, so record counts are not pass counts. No image downloads or InSAR processing occur.
* **IMERG Early V07:** NASA GES DISC daily directory listing identifies the latest completed half-hour granule listed today or yesterday. A streamed download probe checks access without downloading the file. Authentication failures are explicit; no numerical rainfall is fabricated. No automatic login, credentials or alternative rainfall product is included.
* **Optional actual rainfall import:** an independently downloaded, authorized IMERG Early V07 HDF5 granule can be summarized. The import rejects an unexpected filename, future/incomplete interval, grid shape, or units. It applies dataset scale/offset, masks fill and negative values, and uses cosine-latitude area weights over cells with centres in the pilot rectangle. Mean rate in mm/h and half-hour mean depth in mm are separate fields. This is not a point rain gauge or a district-polygon statistic. Missing cells are reported and never counted as zero.

## Reproduce

Python 3.11 or newer:

```powershell
python -m pip install -r research/satellite-feeds/requirements.txt
python scripts/refresh_satellite_feeds.py
python -m unittest discover -s tests -p "test_satellite*.py"
```

Use GitHub Actions → **Satellite catalogue snapshot** → **Run workflow** to produce a downloadable snapshot artifact. This action does not commit changes or automatically update Pages. Download and review its output, replace `docs/data/satellite-feeds.json`, then commit to publish. There is no scheduled refresh.

For rainfall values, register with [NASA Earthdata](https://urs.earthdata.nasa.gov/), authorize the applicable GES DISC application, and obtain a granule through the official download service under its access terms. Never upload passwords, tokens, `.netrc`, cookies or your raw credential configuration. Keep the downloaded file outside this public repository, then run:

```powershell
python scripts/refresh_satellite_feeds.py --imerg-file "C:\private-data\3B-HHR-E.MS.MRG.3IMERG.YYYYMMDD-SHHMMSS-EHHMMSS.NNNN.V07C.HDF5"
```

The filename above is a template, not a supplied dataset. Only a real correctly named file works. The rainfall source interval and file checksum are recorded separately from the newest catalogue listing. An older import is not relabelled as the newest observation. Review cell completeness and acquisition age before analysis. Snapshots older than 24 hours get a refresh message in the dashboard; that is a display policy, not a validated safety threshold.

## Authoritative documents / access

* [NASA IMERG overview, resolution and timeliness](https://gpm.nasa.gov/data/imerg) and [IMERG technical documentation](https://gpm.nasa.gov/resources/documents/IMERG-technical-documentation): distinguish Early, Late and Final versions; record the exact granule version. Nominal Early latency is about four hours, not instantaneous delivery. A 30-minute timestep does not imply 30-minute availability.
* [NASA Early V07 HDF5 archive](https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHHE.07/): catalogue listings may be public while downloads require Earthdata authentication. Preserve the relevant product citation and data-use guidance.
* [Copernicus STAC documentation](https://documentation.dataspace.copernicus.eu/APIs/STAC.html), [Sentinel-1 product information](https://sentiwiki.copernicus.eu/web/s1-products), [CDSE access and authentication](https://documentation.dataspace.copernicus.eu/APIs/Token.html). A public catalogue response is not authorization to download all listed assets. Retain Copernicus Sentinel attribution and consult current access terms.
* [ISRO MOSDAC API manual](https://www.mosdac.gov.in/downloadapi-manual) and [Bhoonidhi NISAR](https://bhoonidhi.nrsc.gov.in/NISAR/) are follow-up sources, **not connected feeds in this implementation**. Registration, suitability and actual latency must be evaluated separately.

## Next research experiment

1. Select and survey specific slopes, document the landslide inventory dates, completeness and positional uncertainty, and obtain local rain-gauge, soil-moisture/pore-pressure and displacement measurements.
2. Assemble an event-time rainfall history and pre-event antecedent rainfall features. Current half-hour samples alone cannot establish thresholds. Preserve both observation and publication timestamps to prevent future-information leakage. Bias-check IMERG against gauges.
3. Choose Sentinel-1 pairs with compatible relative orbit, direction, burst overlap, polarization and suitable baselines. Download with an authorized CDSE account. Process a time series with precise orbits, DEM/topographic correction, atmospheric correction and coherence/layover/shadow masks. Assess whether vegetation and slope geometry permit reliable line-of-sight displacement. Catalogue timestamps alone are not deformation observations.
4. Define the target (for example, event in a specified mapped slope during the next 24 hours), train only on inputs available at issue time, and test held-out monsoon seasons and locations. Report missed events, false alarms, precision/recall, calibration, uncertainty and usable lead time against rainfall-only and persistence baselines.
5. Validate prospectively with field observations and institutional review before any operational public alerting. A satellite-only system cannot promise the precise time and location of every landslide.

No trained forecasting model, warning threshold, field deployment, rainfall ingestion credential, full IMERG time series, or InSAR result is supplied by this prototype.
