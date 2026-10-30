"""Download and inspect public research examples; does not train any model."""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone

import h5py
import numpy as np
import requests

ROOT = Path(__file__).resolve().parent


def download(entry, output):
    destination = output / entry['path']
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = entry.get('sha256')
    if destination.exists() and expected:
        if hashlib.sha256(destination.read_bytes()).hexdigest() == expected:
            return {**entry, 'bytes': destination.stat().st_size}
    temporary = destination.with_suffix(destination.suffix + '.part')
    try:
        digest = hashlib.sha256()
        with requests.get(entry['source'], stream=True, timeout=(30, 180)) as response:
            response.raise_for_status()
            with temporary.open('wb') as handle:
                for chunk in response.iter_content(1024 * 1024):
                    handle.write(chunk)
                    digest.update(chunk)
        checksum = digest.hexdigest()
        if expected and checksum != expected:
            raise ValueError('SHA-256 mismatch: ' + entry['path'])
        if destination.suffix == '.pdf':
            with temporary.open('rb') as handle:
                if handle.read(4) != b'%PDF':
                    raise ValueError('Response is not a PDF: ' + entry['path'])
        temporary.replace(destination)
        # Keep the stable source URL; signed CDN redirect URLs are intentionally omitted.
        return {**entry, 'sha256': checksum, 'bytes': destination.stat().st_size}
    finally:
        temporary.unlink(missing_ok=True)


def inspect_pair(output, number):
    with h5py.File(output / f'samples/image_{number}.h5', 'r') as handle:
        image = handle['img'][:]
    with h5py.File(output / f'samples/mask_{number}.h5', 'r') as handle:
        mask = handle['mask'][:]
    if image.shape != (128, 128, 14) or mask.shape != (128, 128):
        raise ValueError(f'Unexpected image/mask shapes for pair {number}')
    if not np.isfinite(image).all() or not np.isfinite(mask).all():
        raise ValueError(f'Non-finite values in pair {number}')
    labels = np.unique(mask).tolist()
    if not set(labels).issubset({0, 1}):
        raise ValueError(f'Non-binary mask in pair {number}')
    return dict(sample=number, image_shape=list(image.shape), mask_shape=list(mask.shape),
                image_dtype=str(image.dtype), labels=labels, positive_pixels=int(mask.sum()))


def preview(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with h5py.File(output / 'samples/image_1.h5') as handle:
        image = handle['img'][:]
    with h5py.File(output / 'samples/mask_1.h5') as handle:
        mask = handle['mask'][:]
    rgb = image[:, :, [3, 2, 1]].astype(float)
    lo, hi = np.percentile(rgb, (2, 98), axis=(0, 1))
    rgb = np.clip((rgb - lo) / np.maximum(hi - lo, 1e-6), 0, 1)
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), constrained_layout=True)
    axes[0].imshow(rgb)
    axes[0].set_title('RGB (2–98% display stretch)')
    axes[1].imshow(mask, cmap='gray', vmin=0, vmax=1)
    axes[1].set_title('Provided landslide mask')
    axes[2].imshow(image[:, :, 12], cmap='terrain')
    axes[2].set_title('Provided slope channel')
    for axis in axes:
        axis.axis('off')
    fig.suptitle('Landslide4Sense training sample — not Maharashtra; not a prediction')
    fig.savefig(output / 'sample_preview.png', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'downloads')
    parser.add_argument('--papers', action='store_true', help='Also download three linked PDFs (~43 MB)')
    parser.add_argument('--baseline', action='store_true', help='Also download a pinned upstream code archive (~4 MB); never execute it')
    parser.add_argument('--preview', action='store_true', help='Render a labelled training-example PNG')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'resources.json').read_text(encoding='utf-8'))
    selected = [e for e in manifest['files'] if e['kind'] == 'sample'
                or (args.papers and e['kind'] == 'paper')
                or (args.baseline and e['kind'] == 'baseline')]
    args.output.mkdir(parents=True, exist_ok=True)
    report = dict(retrieved_utc=datetime.now(timezone.utc).isoformat(), files=[], checks=[], failures=[])
    report_path = args.output / 'download_report.json'
    try:
        for entry in selected:
            try:
                report['files'].append(download(entry, args.output))
                print('Verified:', entry['path'], flush=True)
            except Exception as error:
                report['failures'].append(dict(path=entry['path'], error=str(error)))
                raise
        for number in (1, 2):
            report['checks'].append(inspect_pair(args.output, number))
        if args.preview:
            preview(args.output)
        print('Two image/mask pairs passed shape, finite-value and binary-label checks.')
    finally:
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
