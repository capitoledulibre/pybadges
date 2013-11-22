#!/usr/bin/env python

# Licensed under the WTFPL license, http://sam.zoy.org/wtfpl/.

import cairo
import pango
import pangocairo
import os.path
import sys
import optparse

__version__ = '0.1'

BADGE_HEIGHT = 66
BADGE_WIDTH  = 96

PAGE_HEIGHT = 297
PAGE_WIDTH = 210

INNER_MARGIN = 3

TEXT_COLOR = (1, 1, 1)

def convert_mm_to_dots(mm):
    return float(mm) / 25.4 * 72

def draw_text(ctx, pc, text, base_font_sz, y, text_width, text_height,
              area_width, multiline=False):
    font_sz = base_font_sz
    while font_sz > 6:
        name_fd = pango.FontDescription("Ubuntu")
        name_fd.set_size(font_sz * pango.SCALE)
        layout = pc.create_layout()
        layout.set_font_description(name_fd)
        layout.set_text(text)
        layout.set_alignment(pango.ALIGN_CENTER)
        if multiline:
            layout.set_width(int(convert_mm_to_dots(text_width) * pango.SCALE))

        if layout.get_size()[0] > (convert_mm_to_dots(text_width) * pango.SCALE):
            font_sz -= 1
            continue

        if layout.get_size()[1] > (convert_mm_to_dots(text_height) * pango.SCALE):
            font_sz -= 1
            continue

        # draw
        text_x, text_y, text_w, text_h = layout.get_extents()[1]
        x = (convert_mm_to_dots(area_width) / 2) - (text_w/2.0)/pango.SCALE - int(float(text_x)/pango.SCALE)
        y = y + (convert_mm_to_dots(text_height)/2) - (text_h/2.0)/pango.SCALE - int(float(text_y)/pango.SCALE)
        ctx.move_to(x, y)
        pc.show_layout(layout)
        break


def draw_badge(ctx, width, height, description, background_image):
    im = cairo.ImageSurface.create_from_png(background_image)

    ctx.save()
    ctx.rectangle(0, 0, convert_mm_to_dots(width),
                  convert_mm_to_dots(height))
    ctx.scale(float(convert_mm_to_dots(width)) / im.get_width(),
              float(convert_mm_to_dots(height)) / im.get_height())
    ctx.set_source_surface(im)
    ctx.fill()
    ctx.restore()

    ctx.set_source_rgb(0.9, 0.9, 0.9)
    ctx.rectangle(0, 0, convert_mm_to_dots(width),
                  convert_mm_to_dots(height))
    ctx.stroke()

    if len(description) == 0:
        return

    name = description[0].strip()

    if len(description) > 1:
        company = description[1].strip()
    else:
        company = ''

    if len(description) > 2:
        role = description[2].strip()
    else:
        role = ''

    if name and company and role:
        name_y = 5
        company_y = 60
        role_y = 80
    elif name and company and not role:
        name_y = 10
        company_y = 70
    elif name and not company and role:
        name_y = 10
        role_y = 70
    elif name and not company and not role:
        name_y = 30

    ctx.set_source_rgb(TEXT_COLOR[0], TEXT_COLOR[1], TEXT_COLOR[2])
    pc = pangocairo.CairoContext(ctx)

    if name:
        draw_text(ctx, pc, name,    18, name_y, width * 0.9, height / 3, width, True)
    if company:
        draw_text(ctx, pc, company, 16, company_y, width * 0.9, height / 7, width)
    if role:
        draw_text(ctx, pc, role,    14, role_y, width * 0.9, height / 7, width)

def generate_document(input_csv, output_pdf, background_image):
    surface = cairo.PDFSurface(output_pdf,
                               convert_mm_to_dots(PAGE_WIDTH),
                               convert_mm_to_dots(PAGE_HEIGHT))

    nb_badges_height = PAGE_HEIGHT / (BADGE_HEIGHT + INNER_MARGIN)
    nb_badges_width  = PAGE_WIDTH / (BADGE_WIDTH + INNER_MARGIN)

    margin_top_bottom = (PAGE_HEIGHT - \
                             nb_badges_height * BADGE_HEIGHT - \
                             (nb_badges_height - 1) * INNER_MARGIN) / 2

    margin_left_right = (PAGE_WIDTH - \
                             nb_badges_width * BADGE_WIDTH - \
                             (nb_badges_width - 1) * INNER_MARGIN) / 2

    import csv
    csvFile = csv.reader(open(input_csv, 'rb'), delimiter=',')

    ctx = cairo.Context(surface)

    row = 0
    col = 0

    for badge in csvFile:
        ctx.save()
        ctx.translate(convert_mm_to_dots(margin_left_right + col * (BADGE_WIDTH + INNER_MARGIN)),
                      convert_mm_to_dots(margin_top_bottom + row * (BADGE_HEIGHT + INNER_MARGIN)))
        draw_badge(ctx, BADGE_WIDTH, BADGE_HEIGHT, badge, background_image)
        ctx.restore()

        col += 1
        if col == nb_badges_width:
            col = 0
            row += 1
        if row == nb_badges_height:
            col = 0
            row = 0
            surface.show_page()

    surface.finish()

def main():
    usage = '%prog -o output-pdf -i input-csv -b background-image'
    parser = optparse.OptionParser(usage=usage,
                                   version='%%prog %s' % __version__)
    parser.add_option('-o', dest='output_pdf', metavar='OUTPUT_PDF',
                      help='specify the location of the output PDF.')
    parser.add_option('-i', dest='input_csv', metavar='INPUT_CSV',
                      help='specify the location of the input CSV.')
    parser.add_option('-b', dest='background_image', metavar='BACKGROUND_IMAGE',
                      help='specify the location of the background image.')
    (options, args) = parser.parse_args()
    if len(args):
        parser.print_help()
        return 1

    if not options.output_pdf:
        parser.error("Missing output PDF")
    if not options.input_csv:
        parser.error("Missing input CSV")
    if not options.background_image:
        parser.error("Missing background image")
    if not os.path.exists(options.input_csv):
        parser.error("Input CSV %s does not exist" % options.input_csv)
    if not os.path.exists(options.background_image):
        parser.error("Background image %s does not exist" % options.background_image)

    generate_document(options.input_csv, options.output_pdf, options.background_image)

if __name__ == '__main__':
    sys.exit(main())
