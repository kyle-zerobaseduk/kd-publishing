"""Generate deliberately reduced web imagery from the approved local PDFs.

Usage: python scripts/generate_assets.py ../assets_source ../project_sources
Source PDFs stay outside this repository; only the small WebP exports are committed.
"""
import json
import sys
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
books = json.loads((ROOT / 'catalogue/books.json').read_text())
sources = [Path(p).resolve() for p in sys.argv[1:]]


def find(name):
    matches = [p for directory in sources for p in directory.rglob('*' + name) if p.is_file() and not '.openai-download-' in p.name]
    if not matches:
        raise FileNotFoundError(name)
    if len(matches) > 1:
        raise ValueError(f'Ambiguous source: {name}: {matches}')
    return matches[0]


def image(page, width):
    zoom = min(1.55, width / page.rect.width * 1.25)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def save_web(im, destination, width):
    im.thumbnail((width, 1300), Image.Resampling.LANCZOS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    im.save(destination, format='WEBP', quality=78, method=6)
    assert max(im.size) <= 1300


for book in books:
    ident = book['id']
    if book['coverSource']:
        pdf = fitz.open(find(book['coverSource']))
        page = pdf[0]
        im = image(page, 1050)
        if page.rect.width / page.rect.height > 1.15:
            # KDP wrap: back, spine, front. Keep only the right-hand front panel.
            front_points = 576 if 'football-coach' in ident or ident == 'season-planner' else 612
            left = round(im.width * (1 - front_points / page.rect.width))
            im = im.crop((left, 0, im.width, im.height))
        save_web(im, ROOT / 'assets/covers' / f'{ident}.webp', 740)
    pdf = fitz.open(find(book['interiorSource']))
    for number in book['previewPages']:
        if not 1 <= number <= len(pdf):
            raise ValueError(f'{ident}: invalid page {number} of {len(pdf)}')
        im = image(pdf[number - 1], 950)
        save_web(im, ROOT / 'assets/previews' / f'{ident}-{number}.webp', 850)
print(f'Exported web images for {len(books)} books')
