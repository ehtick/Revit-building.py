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


"""This module provides tools for the modelling of wall components."""

__title__ = "door"
__author__ = "Maarten & Jonathan"
__url__ = "./objects/wall.py"

import sys


from geometry.solid import Extrusion



# [!not included in BP singlefile - end]

class Wall:
	def __init__(self):
		
		self.name = None
		self.verts = None
		self.faces = None
		# self.polycurve = None or self.profile
		self.parms = None


	@classmethod
	def by_mesh(self, verts=list, faces=list):
		wall = Wall()
		wall.verts = [vertex * project.scale for vertex in verts]
		wall.faces = list(faces)
		return wall

	def __str__(self) -> str:
		return f"{self.type}(Name={self.name})"
