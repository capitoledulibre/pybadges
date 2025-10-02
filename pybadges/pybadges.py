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
import os
import itertools
import sys
import re
import qrcode

from typing import Iterable

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from pybadges.config import Config
from pybadges.iterators import peekable

VCARD = """
BEGIN:VCARD
VERSION:4.0
N:{};{};
FN:{} {}
ORG:{}
EMAIL:{}
REV:20241030T195243Z
END:VCARD
"""

@dataclasses.dataclass
class Person:
    frontside: str
    backside: str
    name: str
    lastname: str = ""
    group: str = ""
    logo: str = ""
    email: str = ""


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

def make_document(config: Config, persons: list[Person], output: str, qrcodes_path: str) -> None:
    # Sort persons for optimal printing layout
    sorted_persons = sort_persons_for_printing(persons)

    # Generate qrCodes
    sorted_persons_with_qrcodes = generate_qrcodes(sorted_persons, qrcodes_path)
    
    # Use the sorted list directly with make_pages
    pages = make_pages(config, sorted_persons_with_qrcodes)

    pages[0].save(
        output, save_all=True, append_images=pages[1:], dpi=(config.dpi, config.dpi)
    )

# Modify the make_pages function to respect our sorted order
def make_pages(config: Config, persons: Iterable[Person]) -> list[Image.Image]:
    """Make pages with persons in the exact order provided."""
    c = config
    persons_list = list(persons)  # Convert to list to ensure we can index
    
    # Calculate how many badges per page
    badges_per_page = 4  # Assuming 2x2 layout
    
    # Calculate margins
    margin_top = (c.page.height - 2 * c.badge.height - c.inner_margin) // 2
    margin_left = (c.page.width - 2 * c.badge.width - c.inner_margin) // 2
    
    # Define positions for badges on page (top-left, top-right, bottom-left, bottom-right)
    positions = [
        (margin_left, margin_top),  # top-left
        (margin_left + c.badge.width + c.inner_margin, margin_top),  # top-right
        (margin_left, margin_top + c.badge.height + c.inner_margin),  # bottom-left
        (margin_left + c.badge.width + c.inner_margin, margin_top + c.badge.height + c.inner_margin)  # bottom-right
    ]
    
    # For backside, we need to mirror positions horizontally
    back_positions = [
        (margin_left + c.badge.width + c.inner_margin, margin_top),  # top-right becomes top-left
        (margin_left, margin_top),  # top-left becomes top-right
        (margin_left + c.badge.width + c.inner_margin, margin_top + c.badge.height + c.inner_margin),  # bottom-right becomes bottom-left
        (margin_left, margin_top + c.badge.height + c.inner_margin)  # bottom-left becomes bottom-right
    ]
    
    pages = []
    
    # Create pages with 4 badges each
    for i in range(0, len(persons_list), badges_per_page):
        page_persons = persons_list[i:i+badges_per_page]
        
        # Create front page
        frontpage = Image.new("RGB", c.page.size(), color=0xF0F0F0)
        for j, person in enumerate(page_persons):
            if j < len(positions):
                frontpage.paste(make_badge(config, person), positions[j])
        
        pages.append(frontpage)
        
        # Create back page if needed
        if not c.frontside_only:
            backpage = Image.new("RGB", c.page.size(), color=0xF0F0F0)
            for j, person in enumerate(page_persons):
                if j < len(back_positions):
                    backpage.paste(make_badge(config, person, backside=True), back_positions[j])
            
            pages.append(backpage)
    
    return pages

# New function to create a page with specific persons in order
def make_page_with_persons(config: Config, persons: list[Person]) -> list[Image.Image]:
    """Make one page and its backpage with specific persons in the given order."""
    c = config
    nb_badges_height = 2  # Assuming 2x2 layout
    nb_badges_width = 2
    
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

    # Define positions in order: top-left, top-right, bottom-left, bottom-right
    positions = [
        (margin_left, margin_top),  # top-left
        (margin_left + c.badge.width + c.inner_margin, margin_top),  # top-right
        (margin_left, margin_top + c.badge.height + c.inner_margin),  # bottom-left
        (margin_left + c.badge.width + c.inner_margin, margin_top + c.badge.height + c.inner_margin)  # bottom-right
    ]
    
    frontpage = Image.new("RGB", c.page.size(), color=0xF0F0F0)
    
    if c.frontside_only:
        for pos, person in zip(positions, persons):
            frontpage.paste(make_badge(config, person), pos)
        return [frontpage]
    else:
        backpage = Image.new("RGB", c.page.size(), color=0xF0F0F0)
        
        # For backpage, we need to mirror positions horizontally
        back_positions = [
            (margin_left + c.badge.width + c.inner_margin, margin_top),  # top-right becomes top-left
            (margin_left, margin_top),  # top-left becomes top-right
            (margin_left + c.badge.width + c.inner_margin, margin_top + c.badge.height + c.inner_margin),  # bottom-right becomes bottom-left
            (margin_left, margin_top + c.badge.height + c.inner_margin)  # bottom-left becomes bottom-right
        ]
        
        for pos, person in zip(positions, persons):
            frontpage.paste(make_badge(config, person), pos)
        
        for back_pos, person in zip(back_positions, persons):
            if not c.frontside_only:
                backpage.paste(make_badge(config, person, backside=True), back_pos)
        
        return [frontpage, backpage]

def make_badge(config: Config, person: Person, backside: bool = False) -> Image.Image:
    # print("Badge:", person, file=sys.stderr)
    c = config  # 6 times shorter to type

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
        c.name.color_as_int(),
        multiline=True,
    )

    if (not backside and person.lastname) or (backside and not person.logo):
        draw_text(
            badge,
            person.lastname,
            c.lastname.vertical_offset,
            c.lastname.size(),
            c.lastname.font_name,
            c.lastname.font_size,
            c.lastname.color_as_int(),
        )

    if (not backside and person.group) or (backside and not person.logo):
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
            c.group.color_as_int(),
        )

    if backside and person.logo:
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

def natural_sort_key(s: str) -> list:
    """
    Create a key for natural sorting where numbers in strings are treated as numbers.
    This ensures "Name 1" < "Name 2" < "Name 11" < "Name 023"
    """
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', s)]

def sort_persons_for_printing(persons: list[Person]) -> list[Person]:
    """
    Sort persons by group, lastname, and name with natural sorting,
    then arrange them so that when printed (4 badges per page), 
    the badges follow alphabetical order across pages in each position.
    
    For example, with 16 persons and 4 badges per page:
    - Position 1: persons[0], persons[4], persons[8], persons[12]
    - Position 2: persons[1], persons[5], persons[9], persons[13]
    - Position 3: persons[2], persons[6], persons[10], persons[14]
    - Position 4: persons[3], persons[7], persons[11], persons[15]
    """
    if not persons:
        return []
    
    # First sort by frontside, then lastname, then name with natural sorting
    alpha_sorted = sorted(
        persons, 
        key=lambda p: (
            natural_sort_key(p.frontside),
            natural_sort_key(p.lastname),
            natural_sort_key(p.name)
        )
    )
    
    # Calculate number of pages needed
    badges_per_page = 4
    num_pages = (len(alpha_sorted) + badges_per_page - 1) // badges_per_page
    
    # Create a new sorted list for pagination - this is the key change
    sorted_persons = []
        
    # Process complete sets of pages
    for iteration in range(num_pages):
        for i in range(badges_per_page):
            index = i * num_pages + iteration 
            if index >= len(alpha_sorted):
                break  # Exit the inner loop if index is out of bounds
            sorted_persons.append(alpha_sorted[index])
    
    # Display the final sorted list (optimized for printing)
    # print("\nFinal sorted persons (optimized for printing):", file=sys.stderr)
    # for i, person in enumerate(sorted_persons):
    #     page_num = i // badges_per_page + 1
    #     position = i % badges_per_page + 1
    #     print(f"  {i+1}. Page {page_num}, Position {position}: Frontside: {person.frontside}, Name: {person.name} {person.lastname}", file=sys.stderr)
    
    return sorted_persons

def generate_qrcodes(persons: list[Person], qrcodes_path: str) -> list[Person]:
    for person in persons:  
        if person.name and person.lastname:
            vcard = VCARD.format(person.lastname, person.name, person.name, person.lastname, person.group, person.email)
            # print(vcard)
            img = qrcode.make(vcard)
            type(img)  # qrcode.image.pil.PilImage
            img_path = os.path.join(qrcodes_path, person.name + "-" + person.lastname + ".png")
            person.logo = img_path 
            # print(img_path)
            img.save(img_path, "PNG")

    return persons