# Data attribution and reuse

The MIT code licence does **not** relicense the bundled source data. Keep each source's attribution, linked terms and notices with reused data or figures. Administrative boundaries are a research snapshot and not an official current representation.

## NASA COOLR report points

Source: [NASA Landslide Viewer and COOLR](https://landslides.nasa.gov/) and the [NASA public report-point service](https://gis.earthdata.nasa.gov/portal/rest/services/Landslides/COOLR_Reports_Points/MapServer/0). The snapshot queries `country_name = 'India'`; report coordinates are joined to the boundary snapshots. It is not a census or a set of independently verified events.

NASA describes COOLR as openly accessible and downloadable. Original records include news and citizen-science contributions. Preserve `source_name`, `source_url` and available contributor citations; linked external works retain their own rights. No news article text, photographs or third-party satellite imagery is bundled. Public availability is not a grant of ownership over all linked content.

Cite: Juang, C. S., Stanley, T. A., and Kirschbaum, D. B. (2019). Using citizen science to expand the global map of landslides: Introducing the Cooperative Open Online Landslide Repository (COOLR). *PLOS ONE*, 14(7), e0218657. [DOI](https://doi.org/10.1371/journal.pone.0218657).

## State / UT boundaries

[geoBoundaries India ADM1 metadata](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/) reports **Creative Commons Attribution 2.5 India**, with DataMeet India community and Election Commission of India as original sources. [Licence](https://creativecommons.org/licenses/by/2.5/in/). Year represented is reported as 2011; the dataset contains later administrative names. This inconsistency is retained in provenance, not represented as a current official map.

## District boundaries

[geoBoundaries India ADM2 metadata](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM2/) reports **Open Data Commons Open Database License 1.0**, sourced from Pathways Data Pvt. Ltd. and lgdirectory.gov.in, year represented 2021. [ODbL](https://opendatacommons.org/licenses/odbl/1-0/). The adapted district boundary database is offered under those same terms, separately from the MIT code. Preserve attribution and applicable share-alike obligations when distributing adapted databases or produced works.

The district metadata declares 736 units; the upstream simplified GeoJSON contains 735 features. No missing polygon was invented. Original names, including Raigarh in Maharashtra, are retained in the data. They may differ from current spellings or administrative names.

For both boundary layers: further simplification uses a 300 m tolerance in EPSG:6933; topology is preserved per feature, not guaranteed between adjacent features. District parent state is assigned by greatest polygon overlap; report regions use point intersections. Coordinates are rounded to four decimal places. These transformations are unsuitable for survey or legal boundary determination. No area-normalized risk statistics are computed.

Cite: Runfola et al. (2020). geoBoundaries: A global database of political administrative boundaries. *PLOS ONE*, 15(4), e0231866. [DOI](https://doi.org/10.1371/journal.pone.0231866).

## Local contributions and exports

Contributors must provide a source URL, source name and licence/permission statement. This is a self-declaration, not verification by the application. Local data stay in browser storage until the user exports or shares them. User imports do not become NASA data. Preserve mixed-source attribution and source licences in exported CSV, GeoJSON, project files and figure captions.

Generated figures include a brief attribution and embedded provenance; cite the relevant sources in the paper as well. The atlas does not establish permission to publish sensitive field locations. Review your own data before sharing.

## Excluded materials

The [segmentation research module](research/landslide-segmentation/README.md) links to Landslide4Sense (Zenodo DOI 10.5281/zenodo.10463239, CC BY 4.0), its IBM-NASA sample mirror at a pinned revision, HR-GLDD (DOI 10.5281/zenodo.7189381, CC BY 4.0), and original research papers. Downloaded samples, PDFs and upstream code archives are ignored and are not bundled in this repository. Cite dataset and paper authors and preserve the original terms. The official Landslide4Sense baseline code has its own MIT license, retained in its downloadable archive. CAS is linked as a further resource; its complete files and license have not been audited here. The repository MIT license covers our preparation code and guide, not third-party data or papers.

The unpublished review manuscript, co-author contact details, journal PDFs, GSI-attributed mirror records, exact pilot training points and trained model are deliberately excluded from this repository. The pilot section reports aggregate exploratory results with limitations; it does not distribute a national model or substitute NASA reports for its original inventory.
