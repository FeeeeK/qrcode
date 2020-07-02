#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from io import BytesIO

from MyQR.mylibs import theqrmodule
from PIL import Image


# Positional parameters
#   words: str
#
# Optional parameters
#   version: int, from 1 to 40
#   level: str, just one of ('L','M','Q','H')
#   picutre: str, a filename of a image
#   colorized: bool
#   constrast: float
#   brightness: float
#
# See [https://github.com/sylnsfar/qrcode] for more details!
def run(
    words,
    version=1,
    level="H",
    picture=None,
    colorized=False,
    contrast=1.0,
    brightness=1.0,
):

    supported_chars = r"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ··,.:;+-*/\~!@#$%^&`'=<>[]()?_{}|"

    # check every parameter
    if not isinstance(words, str) or any(i not in supported_chars for i in words):
        raise ValueError("Wrong words! Make sure the characters are supported!")
    if not isinstance(version, int) or version not in range(1, 41):
        raise ValueError("Wrong version! Please choose a int-type value from 1 to 40!")
    if not isinstance(level, str) or len(level) > 1 or level not in "LMQH":
        raise ValueError(
            "Wrong level! Please choose a str-type level from {'L','M','Q','H'}!"
        )

    def combine(ver, qr_name, bg_name, colorized, contrast, brightness):
        from MyQR.mylibs.constant import alig_location
        from PIL import ImageEnhance, ImageFilter

        qr = Image.open(qr_name)
        qr = qr.convert("RGBA") if colorized else qr

        bg0 = Image.open(bg_name).convert("RGBA")
        bg0 = ImageEnhance.Contrast(bg0).enhance(contrast)
        bg0 = ImageEnhance.Brightness(bg0).enhance(brightness)

        left = (bg0.size[0] - qr.size[0]) // 4
        top = (bg0.size[1] - qr.size[1]) // 4
        right = (bg0.size[0] + qr.size[0]) // 4
        bottom = (bg0.size[1] + qr.size[1]) // 4

        bg0 = bg0.crop((left, top, right, bottom))
        bg0 = bg0.resize((qr.size[0] - 24, qr.size[1] - 24))

        bg = bg0 if colorized else bg0.convert("1")

        aligs = []
        if ver > 1:
            aloc = alig_location[ver - 2]
            for a in range(len(aloc)):
                for b in range(len(aloc)):
                    if not (
                        (a == b == 0)
                        or (a == len(aloc) - 1 and b == 0)
                        or (a == 0 and b == len(aloc) - 1)
                    ):
                        for i in range(3 * (aloc[a] - 2), 3 * (aloc[a] + 3)):
                            for j in range(3 * (aloc[b] - 2), 3 * (aloc[b] + 3)):
                                aligs.append((i, j))

        for i in range(qr.size[0] - 24):
            for j in range(qr.size[1] - 24):
                if not (
                    (i in (18, 19, 20))
                    or (j in (18, 19, 20))
                    or (i < 24 and j < 24)
                    or (i < 24 and j > qr.size[1] - 49)
                    or (i > qr.size[0] - 49 and j < 24)
                    or ((i, j) in aligs)
                    or (i % 3 == 1 and j % 3 == 1)
                    or (bg0.getpixel((i, j))[3] == 0)
                ):
                    qr.putpixel((i + 12, j + 12), bg.getpixel((i, j)))

        qr_name = BytesIO()
        qr.resize((qr.size[0] * 3, qr.size[1] * 3)).save(qr_name, format="png")
        return qr_name

    tempdir = os.path.join(os.path.expanduser("~"), ".myqr")

    try:
        save_name = BytesIO()
        ver, qr_name = theqrmodule.get_qrcode(version, level, words, save_name)

        if picture and picture[-4:] == ".gif":
            import imageio

            im = Image.open(picture)

            im.save(os.path.join(tempdir, "0.png"))
            while True:
                try:
                    seq = im.tell()
                    im.seek(seq + 1)
                    im.save(os.path.join(tempdir, "%s.png" % (seq + 1)))
                except EOFError:
                    break

            imsname = []
            for s in range(seq + 1):
                bg_name = os.path.join(tempdir, "%s.png" % s)
                imsname.append(
                    combine(
                        ver, qr_name, bg_name, colorized, contrast, brightness, tempdir
                    )
                )

            ims = [imageio.imread(pic) for pic in imsname]
            qr_name = BytesIO()
            imageio.mimsave(qr_name, ims)
        elif picture:
            qr_name = combine(ver, qr_name, picture, colorized, contrast, brightness)
        elif qr_name:
            qr = Image.open(qr_name)
            qr_name = BytesIO()
            qr.resize((qr.size[0] * 3, qr.size[1] * 3)).save(qr_name, format="png")

        return ver, level, qr_name

    except:
        raise
