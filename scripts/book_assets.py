"""Stable image paths, with an optional edition version to invalidate old caches."""


def asset_stem(book):
    version = book.get('assetVersion')
    return book['id'] + (f'-{version}' if version else '')


def cover_path(book):
    return book.get('coverImage') or f'assets/covers/{asset_stem(book)}.webp'


def preview_path(book, page):
    return f'assets/previews/{asset_stem(book)}-{page}.webp'
