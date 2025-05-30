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

"""This module provides tools for annotations like text, label, dimension, dimension tick etc"""


__title__ = "annotation"
__author__ = "Maarten & Jonathan"
__url__ = "./objects/annotation.py"

import math

from abstract.vector import Point, Vector

from packages.text import Text

from geometry.curve import Line, PolyCurve

from abstract.matrix import CoordinateSystem

# [!not included in BP singlefile - end]

# Maarten


class TickMark:
    # Dimension Tick Mark
    def __init__(self):
        self.name = None

        self.curves = []

    @staticmethod
    def by_curves(name, curves):
        TM = TickMark()
        TM.name = name
        TM.curves = curves
        return TM


TMDiagonal = TickMark.by_curves(
    "diagonal", [Line(start=Point(-100, -100, 0), end=Point(100, 100, 0))]
)


class DimensionType:
    def __init__(self):
        self.name = None

        self.font = None
        self.text_height = 2.5
        self.tick_mark: TickMark = TMDiagonal
        self.line_extension = 100

    @staticmethod
    def by_name_font_textheight_tick_mark_extension(
        name: str,
        font: str,
        text_height: float,
        tick_mark: TickMark,
        line_extension: float,
    ):
        DT = DimensionType()
        DT.name = name
        DT.font = font
        DT.text_height = text_height
        DT.tick_mark = tick_mark
        DT.line_extension = line_extension
        return DT


DT2_5_mm = DimensionType.by_name_font_textheight_tick_mark_extension(
    "2.5 mm", "calibri", 2.5, TMDiagonal, 100
)

DT1_8_mm = DimensionType.by_name_font_textheight_tick_mark_extension(
    "1.8 mm", "calibri", 2.5, TMDiagonal, 100
)


class Dimension:
    def __init__(self, start: Point, end: Point, dimension_type) -> None:

        self.start: Point = start
        self.text_height = 100
        self.end: Point = end
        self.scale = 0.1  # text
        self.dimension_type: DimensionType = dimension_type
        self.curves = []
        self.length: float = Line(start=self.start, end=self.end).length
        self.text = None
        self.geom()

    @staticmethod
    def by_startpoint_endpoint_offset(
        start: Point, end: Point, dimension_type: DimensionType, offset: float
    ):
        DS = Dimension()
        DS.start = start
        DS.end = end
        DS.dimension_type = dimension_type
        DS.geom()
        return DS

    def geom(self):
        # baseline
        baseline = Line(start=self.start, end=self.end)
        midpoint_text = baseline.mid
        direction = baseline.direction
        tick_mark_extension_point_1 = (
            self.start - direction * self.dimension_type.line_extension
        )
        tick_mark_extension_point_2 = (
            self.end + direction * self.dimension_type.line_extension
        )
        x = direction
        y = Vector.rotate(x, math.radians(90))
        z = Vector.z_axis
        cs_new_start = CoordinateSystem.by_origin_unit_axes(self.start, [x, y, z])
        cs_new_mid = CoordinateSystem.by_origin_unit_axes(midpoint_text, [x, y, z])
        cs_new_end = CoordinateSystem.by_origin_unit_axes(self.end, [x, y, z])
        self.curves.append(
            Line(tick_mark_extension_point_1, self.start)
        )  # extention_start
        self.curves.append(Line(tick_mark_extension_point_2, self.end))  # extention_end
        self.curves.append(Line(self.start, self.end))  # baseline
        # erg vieze oplossing. #Todo
        crvs = Line(
            start=self.dimension_type.tick_mark.curves[0].start,
            end=self.dimension_type.tick_mark.curves[0].end,
        )

        self.curves.append(
            cs_new_start * self.dimension_type.tick_mark.curves[0]
        )  # dimension tick start
        self.curves.append(cs_new_end * crvs)  # dimension tick end
        self.text = Text(
            text=str(round(self.length)),
            font_family=self.dimension_type.font,
            cs=cs_new_mid,
            height=self.text_height,
        ).write()

    def write(self, project):
        for i in self.curves:
            project.objects.append(i)
        for j in self.text:
            project.objects.append(j)


class BeamTag:
    def __init__(self):
        # Dimensions in 1/100 scale

        self.scale = 0.1
        self.cs: CoordinateSystem = CoordinateSystem()
        self.offset_x = 500
        self.offset_y = 100
        self.font_family = "calibri"
        self.text: str = "text"
        self.text_curves = None
        self.text_height = 100

    def __textobject(self):
        # cstextnew = cstext.translate(self.textoff_vector_local)
        self.text_curves = Text(
            text=self.text,
            font_family=self.font_family,
            height=self.text_height,
            cs=self.cs,
        ).write

    def by_cs_text(self, coordinate_system: CoordinateSystem, text):
        self.cs = coordinate_system
        self.text = text
        self.__textobject()
        return self

    def write(self, project):
        for x in self.text_curves():
            project.objects.append(x)
        return self

    @staticmethod
    def by_frame(frame):
        tag = BeamTag()
        frame_vector = frame.vector_normalised
        x = frame_vector
        y = Vector.rotate(x, math.radians(90))
        z = Vector.Z_Axis
        vx = Vector.scale(frame_vector, tag.offset_x)
        frame_width = PolyCurve.bounds(frame.curve)[4]
        vy = Vector.scale(y, frame_width * 0.5 + tag.offset_y)
        origintext = Point.translate(frame.start, vx)
        origintext = Point.translate(origintext, vy)
        csnew = CoordinateSystem(origintext, x, y, z)
        tag.cs = csnew
        tag.text = frame.name
        tag.__textobject()
        return tag


class ColumnTag:
    def __init__(self):
        # Dimensions in 1/100 scale

        self.width = 700
        self.height = 500
        self.factor = 3  # hellingsfacor leader
        self.scale = 0.1  # voor tekeningverschaling
        self.position = (
            "TL"  # TL, TR, BL, BR Top Left Top Right Bottom Left Bottom Right
        )
        self.transform: CoordinateSystem = CoordinateSystem()

        # self.textoff_vector_local: Vector = Vector(1,1,1)
        self.font_family = "calibri"
        self.curves = []
        # self.leadercurves()
        self.text: str = "text"
        self.text_height = 100
        self.text_offset_factor = 5
        self.textoff_vector_local: Vector = Vector(
            self.height / self.factor,
            self.height + self.height / self.text_offset_factor,
            0,
        )
        self.text_curves = None
        # self.textobject()

    def __leadercurves(self):
        self.startpoint = Point(0, 0, 0)
        self.midpoint = Point.translate(
            self.startpoint, Vector(self.height / self.factor, self.height, 0)
        )
        self.endpoint = Point.translate(self.midpoint, Vector(self.width, 0, 0))
        for line in [
            Line(start=self.startpoint, end=self.midpoint),
            Line(start=self.midpoint, end=self.endpoint),
        ]:
            self.curves.append(self.transform * line)

    def __textobject(self):

        cstextnew = CoordinateSystem.translate(self.textoff_vector_local) * self.transform
        self.text_curves = Text(
            text=self.text,
            font_family=self.font_family,
            height=self.text_height,
            cs=cstextnew,
        ).write

    def by_cs_text(self, coordinate_system: CoordinateSystem, text):
        self.transform = coordinate_system
        self.text = text
        self.__leadercurves()
        self.__textobject()
        return self


    @staticmethod
    def by_beam(beam, position="TL"):
        tag = ColumnTag()
        tag.position = position
        tag.transform = CoordinateSystem.translate(beam.start)
        tag.text = beam.name
        tag.__leadercurves()
        tag.__textobject()
        return tag


# class Label:
# class LabelType:
# class TextType:
