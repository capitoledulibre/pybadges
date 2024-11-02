import csv
import dataclasses
import io
import itertools
import sys
from typing import Iterable

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from config import Config
from iterators import peekable


DPI = 300


def mm2dots(mm: float) -> int:
    """Convert millimeters to dots."""
    return round(mm / 25.4 * DPI)


@dataclasses.dataclass
class Person:
    name: str
    lastname: str = ""
    group: str = ""
    logo: str = ""


class ImageLoader:
    def __init__(self) -> None:
        self._img = {}

    def get(
        self,
        filename: str,
        size: tuple[int, int] | None = None,
        keep_ratio: bool = False,
    ) -> Image.Image:
        try:
            return self._img[filename].copy()
        except KeyError:
            img = Image.open(filename).convert("RGBA")
            if size is not None:
                width, height = size
                if keep_ratio:
                    ratio = min(width / img.width, height / img.height)
                    size = round(ratio * img.width), round(ratio * img.height)
                img = img.resize(size)

            self._img[filename] = img
            return img.copy()


loader = ImageLoader()


def make_document(
    config: Config, persons: list[Person], output: str, background: str
) -> None:
    pages = make_pages(config, persons, background)

    pages[0].save(output, save_all=True, append_images=pages[1:], dpi=(DPI, DPI))


def make_pages(
    config: Config, persons: Iterable[Person], background: str
) -> list[Image.Image]:
    pages = []
    it = peekable(iter(persons))

    while not it.empty():
        pages.append(make_page(config, it, background))

    return pages


def make_page(
    config: Config, persons: Iterable[Person], background: str
) -> Image.Image:
    c = config  # 6 times shorter to type
    page = Image.new("RGB", c.page.size(), color=0xF0F0F0)

    nb_badges_height = c.page.height // (c.badge.height + c.inner_margin)
    nb_badges_width = c.page.width // (c.badge.width + c.inner_margin)

    margin_top = (
        c.page.height
        - nb_badges_height * c.badge.height
        - (nb_badges_height - 1) * c.inner_margin
    ) // 2

    margin_left = (
        c.page.width
        - nb_badges_width * c.badge.width
        - (nb_badges_width - 1) * c.inner_margin
    ) // 2

    positions = itertools.product(range(nb_badges_height), range(nb_badges_width))

    for pos, person in zip(positions, persons):
        badge = make_badge(config, background, person)
        pos = (
            margin_left + pos[1] * (c.badge.width + c.inner_margin),
            margin_top + pos[0] * (c.badge.height + c.inner_margin),
        )
        page.paste(badge, pos)

    return page


def make_badge(config: Config, background: str, person: Person) -> Image.Image:
    print("Badge:", person, file=sys.stderr)
    c = config  # 6 times shorter to type
    badge = loader.get(background)

    if person.logo:
        logo = loader.get(person.logo, c.group.size(), keep_ratio=True)
        pos = round((badge.width - logo.width) / 2), c.group.vertical_offset
        badge.paste(logo, pos, logo)

    draw_text(
        badge,
        person.name,
        c.name.vertical_offset,
        c.name.size(),
        c.name.font_size,
        c.name.color_as_int(),
        multiline=True,
    )
    if person.lastname:
        draw_text(
            badge,
            person.lastname,
            c.lastname.vertical_offset,
            c.lastname.size(),
            c.lastname.font_size,
            c.lastname.color_as_int(),
        )
    if person.group and not person.logo:
        draw_text(
            badge,
            person.group,
            c.group.vertical_offset,
            c.group.size(),
            c.group.font_size,
            c.group.color_as_int(),
        )

    return badge


def draw_text(
    img: Image.Image,
    text: str,
    y: int,
    bbox: tuple[int, int],
    fontsize: int = 18,
    color: int = 0x000000,
    multiline=False,
) -> None:
    """Draw text on an image. The text is centered on the image and vertically offset of `y` dots.
    fontsize is adjusted to fit the text into the given size.

    :param img: image to draw on
    :param text: text to write
    :param y: vertical offset in dots
    :param bbox: maximum size of the text. fontsize is adjusted to fit into it.
    :param fontsize: maximum font size for the text. Actual font size may be lower to fit `text` into `size`.
    :param multiline: try to split the text in multiple lines to fit bbox.
    """
    canvas = ImageDraw.Draw(img)

    # TODO: softcode font
    fontname = "DejaVuSans.ttf"

    while True:
        font = ImageFont.truetype(fontname, fontsize)

        # NOTE: poor algorithm because it repeats itself a lot between reducing
        # size and wrapping text
        if multiline:
            text = wrap_text(font, text, bbox[0])

        _, _, width, height = canvas.multiline_textbbox((0, 0), text, font)

        if width > bbox[0] or height > bbox[1]:
            fontsize -= 8
        else:
            break

    # `font` is at the right size

    # Position text in the horizontal center of the image.
    # anchor is set to middle (horiz.) and top (vert.)
    # See https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
    pos = (img.width / 2, y)
    canvas.multiline_text(pos, text, fill=color, font=font, anchor="ma", align="center")


def wrap_text(font: ImageFont.FreeTypeFont, text: str, max_width: int) -> str:
    words = text.split()
    if not words:
        words = [""]
    lines = []
    line = new_line = words[0]
    for word in words[1:]:
        new_line += " " + word

        _, _, width, height = font.getbbox(new_line)

        if width > max_width:
            lines.append(line)
            new_line = line = word
        else:
            line = new_line

    lines.append(line)

    return "\n".join(lines)


def parse_persons(ifd: io.StringIO) -> list[Person]:
    persons = []
    for row in csv.reader(ifd, skipinitialspace=True):
        persons.append(Person(*row))

    return persons


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=argparse.FileType("rb"),
        metavar="TOML",
        required=True,
        help="Config toml file. See README.md for format.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=argparse.FileType("r"),
        metavar="CSV",
        required=True,
        help="Input csv file. See README.md for format.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("wb"),
        metavar="PDF",
        required=True,
        help="output pdf file",
    )
    parser.add_argument(
        "-b", "--background", required=True, help="background image for the badge"
    )

    args = parser.parse_args()

    config = Config.from_toml(args.config)
    make_document(config, parse_persons(args.input), args.output, args.background)

    # TODO: recto-verso
    # TODO: background in CSV
