from abstract.vector import Vector
from project.fileformat import BuildingPy
from geometry.rect import Rect

project = BuildingPy("BoundingBoxes from Revit", "1")
bb = Rect()

height = 3675

bb = Rect.centered_at_origin(Vector(7350, 8550))

project.objects.append(bb)


project.to_speckle("29a6c39880")
