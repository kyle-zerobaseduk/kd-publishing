"""Stable image paths, with an optional edition version to invalidate old caches."""


def asset_stem(book):
    version = book.get('assetVersion')
    return book['id'] + (f'-{version}' if version else '')


def cover_path(book):
    return book.get('coverImage') or f'assets/covers/{asset_stem(book)}.webp'


def preview_path(book, page):
    # Optional previewStem keeps already-published preview filenames stable.
    return f'assets/previews/{book.get("previewStem") or asset_stem(book)}-{page}.webp'
