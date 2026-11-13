"""Create the free printable colouring pages from private interior PDFs.

Run: python scripts/generate_free_colouring_pages.py /path/to/private/source/directory
Each page's art stream is copied unchanged from the finished interior; only a small
attribution line is added in the bottom margin. Source PDFs never enter the repository.
"""
import io
import json
import sys
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {b['id']: b for b in json.loads((ROOT / 'catalogue/books.json').read_text())}


def main(source_dir):
    for item in json.loads((ROOT / 'content/free-colouring-pages.json').read_text())['items']:
        title = BOOKS[item['bookId']]['shortTitle']
        page = PdfReader(Path(source_dir) / item['sourcePdf']).pages[item['interiorPage'] - 1]
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        overlay = io.BytesIO()
        c = canvas.Canvas(overlay, pagesize=(width, height))
        c.setFillColor(Color(0.35, 0.35, 0.35))
        c.setFont('Helvetica', 7.5)
        c.drawCentredString(width / 2, 20, f'© K.D.Publishing · From {title} · Free for personal use. Please don\u2019t resell.')
        c.save()
        overlay.seek(0)
        writer = PdfWriter()
        added = writer.add_page(page)
        added.merge_page(PdfReader(overlay).pages[0])
        writer.compress_identical_objects()
        writer.add_metadata({'/Title': f'{title} – free colouring page', '/Author': 'K.D.Publishing',
                             '/Subject': 'Free for personal use. Please do not resell.'})
        with open(ROOT / item['pdf'], 'wb') as handle:
            writer.write(handle)
        image = pdfium.PdfDocument(str(ROOT / item['pdf']))[0].render(scale=680 / width).to_pil().convert('L')
        image.save(ROOT / item['thumbnail'], 'WEBP', quality=82, method=6)
        print(item['pdf'], image.size)


if __name__ == '__main__':
    main(sys.argv[1])
