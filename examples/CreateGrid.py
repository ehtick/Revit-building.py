import sys
import os
from ezdxf import readfile, DXFStructureError, DXFValueError


from project.fileformat import *
from geometry.curve import *
from abstract.vector import Point
from geometry.surface import *
from exchange.DXF import *
from exchange.IFC import *
from construction.beam import *
from construction.datum import *

GridA = Grid.by_startpoint_endpoint(Line(start=Point(-1000, 0, 0), end=Point(10000, 0, 0)), "A")

ifc_project = CreateIFC()

ifc_project.add_project("My Project")
ifc_project.add_site("My Site")
ifc_project.add_building("Building A")
ifc_project.add_storey("Ground Floor")
ifc_project.add_storey("G2Floor")

translateObjectsToIFC(project.objects, ifc_project)

ifc_project.export("grids.ifc")