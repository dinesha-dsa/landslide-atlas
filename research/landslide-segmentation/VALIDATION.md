# Validation record

Checked 30 October 2026 with Python 3.12 on Windows.

- Ran `python prepare_resources.py --baseline --preview` with a fresh output directory. All four sample hashes matched the manifest; both image/mask pairs passed shape, finite-value and binary-label checks. A preview was generated.
- Downloaded the upstream code archive at the pinned commit and verified ZIP integrity and presence of its license. No upstream code was executed.
- The three optional paper PDFs were downloaded and parsed in the local resource preparation step (43, 17 and 16 pages); their checksums are recorded in resources.json. Paper content is not bundled in Git.
- Existing dashboard checks: `node --test tests/core.test.js`, seven test groups passed.

No training, GPU check, benchmark score, external geographic evaluation or prospective prediction was performed. These checks establish resource access and sample format, not scientific model performance. Full-dataset archives were not downloaded. Remote resources may become unavailable or change; checksum mismatches require investigation.
