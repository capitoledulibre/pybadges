# Copyright 2025 Toulibre
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import csv
import dataclasses
import io
import itertools
import sys
from typing import Iterable

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from pybadges.config import Config
from pybadges.iterators import peekable


@dataclasses.dataclass
class Person:
    frontside: str
    backside: str
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
                if keep_ratio:
                    width, height = size
                    ratio = min(width / img.width, height / img.height)
                    size = round(ratio * img.width), round(ratio * img.height)
                img = img.resize(size)

            self._img[filename] = img
            return img.copy()


loader = ImageLoader()


class Printer:
    def __init__(self, config: Config):
        self.config = config

    def make_document(self, persons: list[Person], output: str) -> None:
        pages = self.make_pages(persons)

        print(f"Writing PDF.")
        pages[0].save(
            output,
            save_all=True,
            append_images=pages[1:],
            dpi=(self.config.dpi, self.config.dpi),
        )

    def make_pages(self, persons: Iterable[Person]) -> list[Image.Image]:
        pages = []
        it = peekable(iter(persons))

        while not it.empty():
            pages.extend(self.make_page(it))

        return pages

    def make_page(self, persons: Iterable[Person]) -> list[Image.Image]:
        """Make one page and its backpage."""
        c = self.config  # alias
        nb_badges_height = (c.page.height + c.inner_margin) // (
            c.badge.height + c.inner_margin
        )
        nb_badges_width = (c.page.width + c.inner_margin) // (
            c.badge.width + c.inner_margin
        )

        if nb_badges_height == 0 or nb_badges_width == 0:
            raise ValueError("Invalid config: cannot fit a single badge on a page.")

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

        def make_coord(column: int, row: int) -> tuple[int, int]:
            return (
                margin_left + column * (c.badge.width + c.inner_margin),
                margin_top + row * (c.badge.height + c.inner_margin),
            )

        frontpage = Image.new("RGBA", c.page.size(), color="#f0f0f0")
        # We iterate in (row, col) because we want to fill rows first
        front_positions = [
            make_coord(col, row)
            for row, col in itertools.product(
                range(nb_badges_height), range(nb_badges_width)
            )
        ]

        if c.frontside_only:
            for front_pos, person in zip(front_positions, persons):
                frontpage.paste(self.make_badge(person), front_pos)
            return [frontpage]

        else:
            backpage = Image.new("RGBA", c.page.size(), color="#f0f0f0")

            back_positions = [
                make_coord(col, row)
                for row, col in itertools.product(
                    range(nb_badges_height), reversed(range(nb_badges_width))
                )
            ]

            for front_pos, back_pos, person in zip(
                front_positions, back_positions, persons
            ):
                frontpage.paste(self.make_badge(person), front_pos)
                if not c.frontside_only:
                    backpage.paste(self.make_badge(person, backside=True), back_pos)

            return [frontpage, backpage]

    def make_badge(self, person: Person, backside: bool = False) -> Image.Image:
        print("Badge:", person, file=sys.stderr)
        c = self.config  # alias

        background = person.frontside if not backside else person.backside
        resize = c.badge.size() if c.resize else None
        badge = loader.get(background, resize)

        if backside and not c.text_on_both_sides:
            return badge

        draw_text(
            badge,
            person.name,
            c.name.vertical_offset,
            c.name.size(),
            c.name.font_name,
            c.name.font_size,
            c.name.color,
            multiline=True,
        )
        if person.lastname:
            draw_text(
                badge,
                person.lastname,
                c.lastname.vertical_offset,
                c.lastname.size(),
                c.lastname.font_name,
                c.lastname.font_size,
                c.lastname.color,
            )
        if person.group:
            vertical_offset = c.group.vertical_offset
            if not person.lastname:
                vertical_offset += c.lastname.vertical_offset_if_null

            draw_text(
                badge,
                person.group,
                vertical_offset,
                c.group.size(),
                c.group.font_name,
                c.group.font_size,
                c.group.color,
            )

        if person.logo:
            vertical_offset = c.logo.vertical_offset
            if not person.lastname:
                vertical_offset += c.lastname.vertical_offset_if_null

            logo = loader.get(person.logo, c.logo.size(), keep_ratio=True)
            pos = round((badge.width - logo.width) / 2), vertical_offset
            badge.paste(logo, pos, logo)

        return badge


def draw_text(
    img: Image.Image,
    text: str,
    y: int,
    bbox: tuple[int, int],
    fontname: str,
    fontsize: int = 18,
    color: str = "#000000",
    multiline=False,
) -> None:
    """Draw text on an image. The text is centered on the image and vertically offset of `y` dots.
    fontsize is adjusted to fit the text into the given size.

    :param img: image to draw on
    :param text: text to write
    :param y: vertical offset in dots
    :param bbox: maximum size of the text. fontsize is adjusted to fit into it.
    :param fontsize: maximum font size for the text. Actual font size may be lower to fit `text` into `size`.
    :param color: color of the text as #rgb. Eg. "#ff0000" for red.
    :param multiline: try to split the text in multiple lines to fit bbox.
    """
    canvas = ImageDraw.Draw(img)

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
