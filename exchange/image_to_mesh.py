# [!not included in BP singlefile - start]
# -*- coding: utf8 -*-
# ***************************************************************************
# *   Copyright (c) 2024 Maarten Vroegindeweij & Jonathan van der Gouwe      *
# *   maarten@3bm.co.nl & jonathan@3bm.co.nl                                *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************


"""This module provides tools for image handling"""

import sys
from pathlib import Path
import urllib.request
from PIL import Image

__title__ = "image"
__author__ = "Joas"
__url__ = "./abstract/image.py"

# [!not included in BP singlefile - end]

# example 1 = imagePyB().by_file("C:/Users/JoasHollander/Documents/GitHub/building.py/temp/bugatti-chiron.jpg", 100, 100, dx=10, dy=10)
# example 2 = imagePyB().by_stream("https://onlinejpgtools.com/images/examples-onlinejpgtools/sunflower.jpg")


class imagePyB:
    # Image to Mesh with colors of pixels
    def __init__(self):
        self.img = None
        self.imgpath = None
        self.imgwidth = None
        self.imgheight = None
        self.dx = None
        self.dy = None
        self.dz = None
        self.pixels = None
        self.facenr = -1
        self.numberofpixels = 0
        self.vertx = 0
        self.verty = 0
        self.vertz = 0
        self.name = None
        self.kleurcode_rijen = []
        self.pixellist = []
        self.vert = []
        self.faces = []
        self.colorlst = []
        self.xfactor = 0
        self.yfactor = 0

    @staticmethod
    def rgb_to_int(rgb):
        r, g, b = [max(0, min(255, c)) for c in rgb]
        return (255 << 24) | (r << 16) | (g << 8) | b

    def by_file(self, imgpath, imgwidth=None, imgheight=None, dx=0, dy=0, dz=0):
        self.imgpath = imgpath
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.img = Image.open(self.imgpath)
        self.pixels = self.img.load()
        self.vertx += dx
        self.verty += dy
        self.vertz += dz

        if imgwidth is None:
            self.imgwidth = self.img.width
            self.xfactor = 1
        else:
            self.imgwidth = imgwidth
            self.xfactor = 1 / self.img.width * imgwidth

        if imgheight is None:
            self.imgheight = self.img.height
            self.yfactor = 1
        else:
            self.imgheight = imgheight
            self.yfactor = 1 / self.img.height * imgheight

        for y in range(self.img.height):
            rij_kleurcodes = []
            for x in range(self.img.width):
                rij_kleurcodes.append(self.pixels[x, y])
            self.kleurcode_rijen.append(rij_kleurcodes)

        for kleurcode_rij in self.kleurcode_rijen:
            for kleurcode in kleurcode_rij:
                self.pixellist.append(kleurcode)

        for i in self.pixellist:
            self.faces.append(4)
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.vertx += self.xfactor
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.verty -= self.yfactor
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.vertx -= self.xfactor
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.vertx += self.xfactor
            self.verty += self.yfactor
            self.numberofpixels += 1

            if self.numberofpixels == len(rij_kleurcodes):
                self.vertx = 0 + dx
                self.verty -= self.yfactor
                self.numberofpixels = 0

        for i in self.pixellist:
            argbint_color = self.rgb_to_int(i)
            self.colorlst.append(argbint_color)
            self.colorlst.append(argbint_color)
            self.colorlst.append(argbint_color)
            self.colorlst.append(argbint_color)
            # self.colorlst = None
        return self

    def by_stream(self, imgpath, imgwidth=None, imgheight=None, dx=0, dy=0, dz=0):
        self.imgpath = imgpath
        urllib.request.urlretrieve(self.imgpath, "img.png")
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.img = Image.open("img.png")
        self.pixels = self.img.load()
        self.vertx += dx
        self.verty += dy
        self.vertz += dz

        if imgwidth is None:
            self.imgwidth = self.img.width
            self.xfactor = 1
        else:
            self.imgwidth = imgwidth
            self.xfactor = 1 / self.img.width * imgwidth

        if imgheight is None:
            self.imgheight = self.img.height
            self.yfactor = 1
        else:
            self.imgheight = imgheight
            self.yfactor = 1 / self.img.height * imgheight

        for y in range(self.img.height):
            rij_kleurcodes = []
            for x in range(self.img.width):
                rij_kleurcodes.append(self.pixels[x, y])
            self.kleurcode_rijen.append(rij_kleurcodes)

        for kleurcode_rij in self.kleurcode_rijen:
            for kleurcode in kleurcode_rij:
                self.pixellist.append(kleurcode)

        for i in self.pixellist:
            self.faces.append(4)
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.vertx += self.xfactor
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.verty -= self.yfactor
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.vertx -= self.xfactor
            self.vert.append(self.vertx)
            self.vert.append(self.verty)
            self.vert.append(self.vertz)
            self.facenr += 1
            self.faces.append(self.facenr)
            self.vertx += self.xfactor
            self.verty += self.yfactor
            self.numberofpixels += 1

            if self.numberofpixels == len(rij_kleurcodes):
                self.vertx = 0 + dx
                self.verty -= self.yfactor
                self.numberofpixels = 0

        for i in self.pixellist:
            argbint_color = self.rgb_to_int(i)
            self.colorlst.append(argbint_color)
            self.colorlst.append(argbint_color)
            self.colorlst.append(argbint_color)
            self.colorlst.append(argbint_color)
        return self
