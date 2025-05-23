# [included in BP singlefile]
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


"""This module provides tools for familys/objects"""

__title__ = "plane"
__author__ = "Maarten & Jonathan"
__url__ = "./objects/objectcollection.py"

from abstract.serializable import Serializable
from abstract.vector import Point, Vector
from geometry.curve import Line, PolyCurve, Rect
from geometry.surface import Surface
from geometry.solid import Extrusion
from exchange.DXF import ReadDXF

# [!not included in BP singlefile - end]
# EVERYWHERE FOR EACH OBJECT A ROTATION/POSITION
# Make sure that the objects can be merged!


class WurksRaster3d(Serializable):
    def __init__(self):

        self.bottom = None
        self.top = None
        self.name = "x"
        self.lines = None

    def by_line(self, lines: Line, bottom: float, top: float):
        self.bottom = Vector(0, 0, bottom)
        self.top = Vector(0, 0, top)
        self.lines = lines

        surfList = []
        for line in self.lines:
            pts = []
            pts.append(Point.translate(line.start, self.bottom))
            pts.append(Point.translate(line.end, self.bottom))
            pts.append(Point.translate(line.end, self.top))
            pts.append(Point.translate(line.start, self.top))
            project.objects.append(Surface(PolyCurve.by_points(pts)))
            surfList.append(Surface(PolyCurve.by_points(pts)))

        print(f"{len(surfList)}* {self.__class__.__name__} has been created")


class WurksPedestal:
    def __init__(self):
        self.topfilename = "temp\\jonathan\\pedestal_top.dxf"
        self.basefilename = "temp\\jonathan\\pedestal_foot.dxf"
        self.diameter = 10
        self.topheight = 3
        self.baseheight = 3
        self.cache = {}
        self.top_dxf = None
        self.base_dxf = None

    def load_dxf(self, filename):
        if filename in self.cache:
            return self.cache[filename]
        else:
            dxf = ReadDXF(filename).polycurve
            self.cache[filename] = dxf
            return dxf

    def load_top_dxf(self):
        if self.top_dxf is None:
            self.top_dxf = self.load_dxf(self.topfilename)
        return self.top_dxf

    def load_base_dxf(self):
        if self.base_dxf is None:
            self.base_dxf = self.load_dxf(self.basefilename)
        return self.base_dxf

    def by_point(self, points, height, rotation=None):
        if isinstance(points, Point):
            points = [points]

        top = self.load_top_dxf()
        base = self.load_base_dxf()

        for point in points:
            topcenter = Point.difference(top.centroid(), point)
            translated_top = top.translate(Point.to_vector(topcenter))
            project.objects.append(
                Extrusion.by_polycurve_height(translated_top, self.topheight, 0)
            )

            frame = Rect(
                Vector(
                    x=(translated_top.centroid().x) - (self.diameter / 2),
                    y=(translated_top.centroid().y) - (self.diameter / 2),
                    z=point.z - self.topheight,
                ),
                self.diameter,
                self.diameter,
            )
            project.objects.append(
                Extrusion.by_polycurve_height(
                    frame, height - self.baseheight - self.topheight, 0
                )
            )

            basecenter = Point.difference(base.centroid(), point)
            translated_base = base.translate(Point.to_vector(basecenter))
            project.objects.append(
                Extrusion.by_polycurve_height(translated_base, self.baseheight, -height)
            )

        print(f"{len(points)}* {self.__class__.__name__} has been created")

    pass  # pootje, voet diameter(vierkant), verstelbare hoogte inregelen,


class WurksComputerFloor:  # centerpoint / rotation / panel pattern / ply
    pass  # some type of floor object


class WurksFloorFinish:
    pass  # direction / pattern / ect


class WorkPlane:
    def __init__(self):
        self.length = None
        self.width = None
        self.points = []

    def create(self, length: float = None, width: float = None) -> str:
        self.length = length or 1000
        self.width = width or 1000
        rect = Rect(Vector(0, 0, 0), self.length, self.width)
        for pt in rect.points:
            self.points.append(pt)
        project.objects.append(rect)
        print(f"1* {self.__class__.__name__} has been created")
        return Rect(Vector(0, 0, 0), self.length, self.width)

    pass  # pootje, voet diameter(vierkant), verstelbare hoogte inregelen,


WorkPlane = WorkPlane()
# rotation(Vector)/#volume/#scale
