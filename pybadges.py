import csv
import dataclasses
import io
import itertools
import sys
from typing import Iterable

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from iterators import peekable


DPI = 300


def mm2dots(mm: float) -> int:
    """Convert millimeters to dots."""
    return round(mm / 25.4 * DPI)


# NOTE: Adapt contants to the desired layout
BADGE_HEIGHT = mm2dots(147)
BADGE_WIDTH = mm2dots(104)
INNER_MARGIN = mm2dots(1)

SIZE_NAME = round(BADGE_WIDTH * 0.9), round(BADGE_HEIGHT / 6)
SIZE_LASTNAME = round(BADGE_WIDTH * 0.9), round(BADGE_HEIGHT / 7)
SIZE_GROUP = round(BADGE_WIDTH * 0.9), round(BADGE_HEIGHT / 8)

FONT_SIZE_NAME = 256
FONT_SIZE_LASTNAME = 172
FONT_SIZE_GROUP = 136

PAGE_HEIGHT = mm2dots(297)
PAGE_WIDTH = mm2dots(210)


@dataclasses.dataclass
class Person:
    name: str
    lastname: str = ""
    group: str = ""
    logo: str = ""

    # NOTE: Adapt contants to the desired layout
    def positions(self) -> tuple[int, int, int]:
        name_y = mm2dots(66)
        lastname_y = mm2dots(88)
        group_y = mm2dots(105)
        if not self.lastname:
            group_y = mm2dots(100)

        return name_y, lastname_y, group_y


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


def make_document(persons: list[Person], output: str, background: str) -> None:
    pages = make_pages(persons, background)

    pages[0].save(output, save_all=True, append_images=pages[1:], dpi=(DPI, DPI))


def make_pages(persons: Iterable[Person], background: str) -> list[Image.Image]:
    pages = []
    it = peekable(iter(persons))

    while not it.empty():
        pages.append(make_page(it, background))

    return pages


def make_page(persons: Iterable[Person], background: str) -> Image.Image:
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), color=0xF0F0F0)

    nb_badges_height = PAGE_HEIGHT // (BADGE_HEIGHT + INNER_MARGIN)
    nb_badges_width = PAGE_WIDTH // (BADGE_WIDTH + INNER_MARGIN)

    margin_top = (
        PAGE_HEIGHT
        - nb_badges_height * BADGE_HEIGHT
        - (nb_badges_height - 1) * INNER_MARGIN
    ) // 2

    margin_left = (
        PAGE_WIDTH
        - nb_badges_width * BADGE_WIDTH
        - (nb_badges_width - 1) * INNER_MARGIN
    ) // 2

    positions = itertools.product(range(nb_badges_width), range(nb_badges_height))

    for pos, person in zip(positions, persons):
        badge = make_badge(background, person)
        pos = (
            margin_left + pos[0] * (BADGE_WIDTH + INNER_MARGIN),
            margin_top + pos[1] * (BADGE_HEIGHT + INNER_MARGIN),
        )
        page.paste(badge, pos)

    return page


def make_badge(background: str, person: Person) -> Image.Image:
    print("Badge:", person, file=sys.stderr)
    badge = loader.get(background)

    name_y, lastname_y, group_y = person.positions()

    if person.logo:
        logo = loader.get(person.logo, SIZE_GROUP, keep_ratio=True)
        pos = round((badge.width - logo.width) / 2), group_y
        badge.paste(logo, pos, logo)

    draw_text(badge, person.name, name_y, SIZE_NAME, FONT_SIZE_NAME, multiline=True)
    if person.lastname:
        draw_text(badge, person.lastname, lastname_y, SIZE_LASTNAME, FONT_SIZE_LASTNAME)
    if person.group and not person.logo:
        draw_text(badge, person.group, group_y, SIZE_GROUP, FONT_SIZE_GROUP)

    return badge


def draw_text(
    img: Image.Image,
    text: str,
    y: int,
    bbox: tuple[int, int],
    fontsize: int = 18,
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

    # TODO: softcode text color
    white = 0xFFFFFF
    black = 0x000000

    # Position text in the horizontal center of the image.
    # anchor is set to middle (horiz.) and top (vert.)
    # See https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
    pos = (img.width / 2, y)
    canvas.multiline_text(pos, text, fill=black, font=font, anchor="ma", align="center")


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
        "-i",
        "--input",
        type=argparse.FileType("r"),
        metavar="CSV",
        required=True,
        help="input csv file",
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

    make_document(parse_persons(args.input), args.output, args.background)
