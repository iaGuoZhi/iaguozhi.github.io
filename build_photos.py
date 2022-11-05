import pathlib
from typing import Iterator, Sequence

import markdown
import markdown.extensions.fenced_code
import pymdownx.magiclink
import frontmatter
import jinja2

import highlighting
import witchhazel
import PIL.Image

THUMBNAIL_SIZE = (1024, 768)

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates/photos'),
)


thumbnail_dir = pathlib.Path("./docs/photos/thumbnails")
photos_dir = pathlib.Path("./docs/photos/photos")

def thumbnail(photo_path):
    thumbnail_path = thumbnail_dir / photo_path
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

    im = PIL.Image.open(photos_dir / photo_path)
    im.thumbnail(THUMBNAIL_SIZE)
    im.save(str(thumbnail_path))

    im.close()


def get_sources() -> Iterator[pathlib.Path]:
    return pathlib.Path('.').glob('photos/*.md')


def parse_source(source: pathlib.Path) -> frontmatter.Post:
    post = frontmatter.load(str(source))
    return post


def process_photo(photo: frontmatter.Post) -> frontmatter.Post:
    photo_path = photo.get('path')
    thumbnail(photo_path)
    return photo


def generate_index():
    photos = []
    sources = get_sources()

    for source in sources:
        photo = parse_source(source)
        photo = process_photo(photo)
        photos.append(photo)

    photos.sort(key=lambda x: x["date"], reverse=True)
    template = jinja_env.get_template('index.html')
    rendered = template.render(photos=photos)
    pathlib.Path("./docs/photos/index.html").write_text(rendered)


def main():
    generate_index()


if __name__ == '__main__':
    main()
