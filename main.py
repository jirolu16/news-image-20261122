"""Render the one-page newspaper for Sunday 22 November 2026.

Entry point for the make.fun bounty "news-image-20261122": sum up one
day of world news in a single image. The page is drawn entirely with
PIL -- no photographs, no downloaded art, no network -- so the picture
is self-contained and legible to a judge who sees nothing else.

Layout, top to bottom:
  masthead   "THE WORLD IN ONE DAY" with the Sunday date line
  lead       the COP31 climate summit collapsing in Antalya
  panels     Hormuz tanker strikes; a drone hits a Kyiv suburb block;
             the Sinaloa cartel capture; markets slide into correction
  wide       the candy-factory fire in Cikande, Indonesia
  briefs     a dark "ALSO THAT DAY" strip with four one-line stories

Running this file writes entry.png into the directory named by the
MAKEFUN_OUTPUT_DIR environment variable (default "/output").
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- page
PAGE = 1024            # the page is square, PAGE x PAGE pixels
MARGIN = 32            # white border kept around the printed area
PAPER = (246, 241, 230)
CARD = (255, 253, 246)
LEAD_TINT = (238, 229, 208)

# ----------------------------------------------------------------- ink
BLACK = (26, 24, 20)
BODY_INK = (50, 46, 40)
GREY = (94, 88, 78)
CARD_EDGE = (118, 110, 94)
RED = (148, 38, 28)
STRIP_INK = (224, 218, 202)      # pale text on the black briefs strip

# ------------------------------------------------------- lead motif band
BAND = (30, 40, 34)              # deep green-black, summit-hall dark
POLE = (196, 188, 168)
FLAG_RED = (178, 60, 44)
FLAG_GOLD = (206, 158, 52)
FLAG_BLUE = (70, 104, 148)
FLAG_GREEN = (84, 128, 84)

# ------------------------------------------------------------- content
DATE_LINE = "SUNDAY 22 NOVEMBER 2026"

LEAD_KICKER = "ANTALYA · CLIMATE SUMMIT"
LEAD_HEADLINE = "COP31 COLLAPSES"
LEAD_DECK = "UN talks end with nothing signed, two days past deadline"
LEAD_BODY = (
    "The UN climate summit in Antalya, Turkey ended on Sunday with no "
    "agreement after the European Union and other countries rejected a "
    "final draft text that never once mentioned fossil fuels. Two days "
    "past its deadline, the talks broke up with nothing signed."
)

PANELS = [
    (
        "STRAIT OF HORMUZ · THE GULF",
        "Iran strikes tankers at Hormuz",
        "Iran struck three oil tankers near the Strait of Hormuz and "
        "hit an industrial site in Bahrain, injuring two people, as "
        "the crisis in the Gulf widened.",
    ),
    (
        "DYMER · UKRAINE",
        "Drone hits Kyiv apartment block",
        "A Russian drone struck a five-storey apartment building in "
        "Dymer, north of Kyiv. Fourteen people were missing as rescue "
        "teams searched the rubble.",
    ),
    (
        "SINALOA · MEXICO",
        "Cartel boss captured in Sinaloa",
        "Mexican special forces captured cartel leader 'El Chapo "
        "Isidro' (Fausto Isidro Meza Flores). Eleven people were "
        "killed in the raid, among them four soldiers.",
    ),
    (
        "NEW YORK · MARKETS",
        "Markets slide into correction",
        "The AI sell-off deepened: the S&P 500 fell 3.7% and the "
        "Nasdaq 5.3% as the rout spread from Wall Street to Japan "
        "and Korea.",
    ),
]

WIDE_KICKER = "CIKANDE · INDONESIA"
WIDE_HEADLINE = "Factory fire in Indonesia: dozens missing"
WIDE_BODY = (
    "Fire tore through a candy factory in Cikande, Banten. Three "
    "workers were confirmed dead and dozens more were still "
    "unaccounted for as rescuers searched the ruins."
)

BRIEFS = [
    "After an eight-year journey, the BepiColombo spacecraft enters "
    "orbit around Mercury",
    "Boat carrying mourners to a funeral capsizes in Nigeria; at "
    "least 24 dead",
    "Drone-hit Russian cargo ship Sparta II burns for a second day "
    "in the Gulf of Finland",
    "Israeli settlers torch vehicles in four West Bank villages; "
    "Israel opens an inquiry",
]

# --------------------------------------------------------------- fonts
NOTO_DIR = "/usr/share/fonts/truetype/noto"
DEJAVU_DIR = "/usr/share/fonts/truetype/dejavu"


def _face(noto_name, dejavu_name):
    """Path of the preferred Noto face, or its DejaVu stand-in."""
    path = os.path.join(NOTO_DIR, noto_name)
    if os.path.isfile(path):
        return path
    return os.path.join(DEJAVU_DIR, dejavu_name)


SERIF_BLACK = _face("NotoSerif-Black.ttf", "DejaVuSerif-Bold.ttf")
SERIF_BOLD = _face("NotoSerif-Bold.ttf", "DejaVuSerif-Bold.ttf")
SANS_BOLD = _face("NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf")
SANS = _face("NotoSans-Regular.ttf", "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text_width(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def fit_font(draw, text, path, size, floor, max_width):
    """Shrink from `size` towards `floor` until the text fits."""
    while size > floor and text_width(draw, text, font(path, size)) > max_width:
        size -= 2
    return font(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap, measured in pixels against the real font."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if text_width(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, x, y, text, fnt, colour, max_width, leading):
    """Draw wrapped text from (x, y); return y below the last line."""
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=colour)
        y += leading
    return y


def draw_centred(draw, cx, y, text, fnt, colour):
    draw.text((cx - text_width(draw, text, fnt) / 2, y), text,
              font=fnt, fill=colour)


# ------------------------------------------------------------- drawing
def masthead(draw):
    """Newspaper name, tagline and the red date line."""
    content_w = PAGE - 2 * MARGIN
    draw_centred(draw, PAGE / 2, 20,
                 "ONE PAGE  ·  ONE DAY  ·  THE WHOLE WORLD",
                 font(SANS_BOLD, 17), GREY)
    draw.line([(MARGIN, 44), (PAGE - MARGIN, 44)], fill=BLACK, width=2)
    name = "THE WORLD IN ONE DAY"
    draw_centred(draw, PAGE / 2, 50, name,
                 fit_font(draw, name, SERIF_BLACK, 54, 30, content_w),
                 BLACK)
    draw_centred(draw, PAGE / 2, 106, DATE_LINE,
                 fit_font(draw, DATE_LINE, SERIF_BLACK, 30, 20, content_w),
                 RED)
    draw.line([(MARGIN, 142), (PAGE - MARGIN, 142)], fill=BLACK, width=4)
    draw.line([(MARGIN, 149), (PAGE - MARGIN, 149)], fill=BLACK, width=1)


def flags_motif(draw, x0, y0, x1, y1):
    """A row of summit flags; the last pole stands snapped and bare.

    The talks ended with nothing agreed, so the final flag never made
    it up its pole: the pole leans, its top half fallen to the floor.
    """
    draw.rectangle([x0, y0, x1, y1], fill=BAND)
    floor_y = y1 - 7
    draw.line([(x0, floor_y), (x1, floor_y)], fill=POLE, width=2)
    colours = [FLAG_BLUE, FLAG_GOLD, FLAG_GREEN, FLAG_RED, FLAG_BLUE]
    span = x1 - x0
    for i, colour in enumerate(colours):
        px = x0 + span * (0.10 + 0.16 * i)
        top = y0 + 7
        draw.line([(px, top), (px, floor_y)], fill=POLE, width=3)
        draw.rectangle([px + 2, top + 2, px + 34, top + 17], fill=colour)
    # the broken pole: stub still standing, top half lying on the floor
    bx = x0 + span * 0.90
    draw.line([(bx, y0 + 22), (bx + 3, floor_y)], fill=POLE, width=3)
    draw.line([(bx + 8, floor_y - 3), (bx + 34, floor_y - 1)],
              fill=POLE, width=3)
    draw.rectangle([bx + 10, floor_y - 12, bx + 30, floor_y - 4],
                   fill=FLAG_GOLD)


def lead_story(draw):
    """The tinted lead block: kicker, headline, deck, body, motif."""
    top, bottom = 157, 404
    inner_w = PAGE - 2 * MARGIN - 32
    draw.rectangle([MARGIN, top, PAGE - MARGIN, bottom],
                   fill=LEAD_TINT, outline=BLACK, width=2)
    draw.text((MARGIN + 16, top + 10), LEAD_KICKER,
              font=font(SANS_BOLD, 17), fill=RED)
    y = top + 36
    y = draw_wrapped(draw, MARGIN + 16, y, LEAD_HEADLINE,
                     fit_font(draw, LEAD_HEADLINE, SERIF_BLACK, 47, 30,
                              inner_w),
                     BLACK, inner_w, 54)
    y = draw_wrapped(draw, MARGIN + 16, y + 2, LEAD_DECK,
                     font(SERIF_BOLD, 21), RED, inner_w, 26)
    y = draw_wrapped(draw, MARGIN + 16, y + 6, LEAD_BODY,
                     font(SANS, 18), BODY_INK, inner_w, 23)
    band_top = bottom - 46
    assert y <= band_top - 6, f"lead text reaches motif: {y} > {band_top}"
    flags_motif(draw, MARGIN + 2, band_top, PAGE - MARGIN - 2, bottom - 2)


def story_card(draw, box, kicker, headline, body):
    """One bordered panel; the assert keeps every word on the page."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=CARD, outline=CARD_EDGE, width=2)
    inset = 14
    inner_w = (x1 - x0) - 2 * inset
    y = y0 + 8
    draw.text((x0 + inset, y), kicker, font=font(SANS_BOLD, 15), fill=RED)
    y += 21
    y = draw_wrapped(draw, x0 + inset, y, headline,
                     font(SERIF_BOLD, 23), BLACK, inner_w, 27)
    y = draw_wrapped(draw, x0 + inset, y + 3, body,
                     font(SANS, 17), BODY_INK, inner_w, 21)
    assert y <= y1 - 6, f"panel overflow: '{headline}' ends {y}, box {y1}"


def wide_panel(draw):
    """Full-width card for the Indonesia factory fire."""
    top, bottom = 796, 904
    inner_w = PAGE - 2 * MARGIN - 28
    draw.rectangle([MARGIN, top, PAGE - MARGIN, bottom],
                   fill=CARD, outline=CARD_EDGE, width=2)
    draw.text((MARGIN + 14, top + 8), WIDE_KICKER,
              font=font(SANS_BOLD, 15), fill=RED)
    y = draw_wrapped(draw, MARGIN + 14, top + 27, WIDE_HEADLINE,
                     font(SERIF_BOLD, 24), BLACK, inner_w, 28)
    y = draw_wrapped(draw, MARGIN + 14, y + 3, WIDE_BODY,
                     font(SANS, 17), BODY_INK, inner_w, 21)
    assert y <= bottom - 6, f"wide panel overflow: {y} > {bottom}"


def briefs_strip(draw):
    """The black ALSO THAT DAY strip: four briefs in four columns."""
    top, bottom = 912, 1008
    draw.rectangle([MARGIN, top, PAGE - MARGIN, bottom],
                   fill=BLACK, outline=BLACK, width=2)
    draw.text((MARGIN + 14, top + 7), "ALSO THAT DAY",
              font=font(SANS_BOLD, 18), fill=PAPER)
    col_w = (PAGE - 2 * MARGIN - 28 - 24) // 4
    for i, brief in enumerate(BRIEFS):
        bx = MARGIN + 14 + i * (col_w + 8)
        end = draw_wrapped(draw, bx, top + 31, "·  " + brief,
                           font(SANS, 14), STRIP_INK, col_w, 17)
        assert end <= bottom - 4, f"brief {i} overflow: {end} > {bottom}"


def build():
    """Assemble the whole front page and return the PIL image."""
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    draw.rectangle([14, 14, PAGE - 14, PAGE - 14], outline=BLACK, width=3)

    masthead(draw)
    lead_story(draw)

    col_w = (PAGE - 2 * MARGIN - 12) // 2
    left = (MARGIN, MARGIN + col_w)
    right = (MARGIN + col_w + 12, PAGE - MARGIN)
    rows = [(412, 596), (604, 788)]
    for i, (kicker, headline, body) in enumerate(PANELS):
        x0, x1 = left if i % 2 == 0 else right
        y0, y1 = rows[i // 2]
        story_card(draw, (x0, y0, x1, y1), kicker, headline, body)

    wide_panel(draw)
    briefs_strip(draw)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    img = build()
    img.save(target, format="PNG", optimize=True)
    print(f"wrote {target} size={os.path.getsize(target)} "
          f"dims={img.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
