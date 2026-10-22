"""Reproducible small cover derivatives; originals remain unchanged."""
import json
from pathlib import Path
from PIL import Image
from book_assets import cover_path

ROOT = Path(__file__).resolve().parents[1]
for book in json.loads((ROOT/'catalogue/books.json').read_text()):
    source = ROOT / cover_path(book)
    with Image.open(source) as image:
        image.resize((370, round(image.height * 370 / image.width)), Image.Resampling.LANCZOS).save(
            ROOT/'assets/responsive'/f'{source.stem}-370.webp', quality=82, method=6)
print('Generated 370px cover derivatives without modifying originals')
