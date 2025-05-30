# [included in BP singlefile]
# [!not included in BP singlefile - start]
# -*- coding: utf8 -*-
# ***************************************************************************
# *   Copyright (c) 2024 Maarten Vroegindeweij & Jonathan van der Gouwe	  *
# *   maarten@3bm.co.nl & jonathan@3bm.co.nl								*
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)	*
# *   as published by the Free Software Foundation; either version 2 of	 *
# *   the License, or (at your option) any later version.				   *
# *   for detail see the LICENCE text file.								 *
# *																		 *
# *   This program is distributed in the hope that it will be useful,	   *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of		*
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the		 *
# *   GNU Library General Public License for more details.				  *
# *																		 *
# *   You should have received a copy of the GNU Library General Public	 *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA																   *
# *																		 *
# ***************************************************************************


"""This module provides tools for exporting geometry to Speckle"""

__title__ = "speckle"
__author__ = "Maarten & Jonathan"
__url__ = "./exchange/speckle.py"

from abstract.interval import Interval
from abstract.matrix import Matrix
from abstract.segmentation import Meshable, TesselationSettings
from abstract.serializable import Serializable

# from construction.datum import Grid, GridSystem
from construction.annotation import ColumnTag
from construction.datum import GridLine, Grid
from construction.panel import Panel
from construction.void import Void
from construction.wall import Wall

# from exchange.Trimesh_dep import Trimesh
from abstract.vector import Point, Vector
from geometry.mesh import Mesh
from geometry.rect import Rect
from packages.text import Text
from geometry.solid import Extrusion
from geometry.surface import Surface
from project.fileformat import BuildingPy
from geometry.curve import Line
from geometry.curve import PolyCurve, Polygon
from geometry.curve import Arc
from abstract.vector import Vector
from geometry.plane import Plane
from packages.helper import flatten
from construction.beam import Beam

# [!not included in BP singlefile - end]

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.transports.server import ServerTransport
from specklepy.api import operations

from specklepy.objects import Base as SpeckleObject
from specklepy.objects.geometry import Point as SpecklePoint
from specklepy.objects.geometry import Line as SpeckleLine
from specklepy.objects.geometry import Mesh as SpeckleMesh
from specklepy.objects.geometry import Polyline as SpecklePolyLine
from specklepy.objects.geometry import Vector as SpeckleVector
from specklepy.objects.geometry import Plane as SpecklePlane
from specklepy.objects.geometry import Arc as SpeckleArc
from specklepy.objects.geometry import Box as SpeckleBox
from specklepy.objects.other import DisplayStyle as SpeckleDisplayStyle
from specklepy.objects.primitive import Interval as SpeckleInterval
from specklepy.objects.other import Text as SpeckleText
from specklepy.objects.geometry import Extrusion as SpeckleExtrusion


def to_speckle(self: BuildingPy, streamid, commitstring=None):
    try:
        import specklepy
    except ImportError:
        print("Installing requirement: specklepy")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "specklepy"])
        import specklepy
    from exchange.speckle import translateObjectsToSpeckleObjects, TransportToSpeckle

    speckleobj = translateObjectsToSpeckleObjects(self, self.objects)
    TransportToSpeckle(self.speckleserver, streamid, speckleobj, commitstring)


BuildingPy.to_speckle = to_speckle


def CreateStream(serverurl, name, description):
    # Create new stream/project in Speckle Server
    client = SpeckleClient(host=serverurl)
    account = get_default_account()
    client.authenticate_with_account(account)
    streamid = client.stream.create(name, description, True)
    return streamid


def convert_to_speckle_object(
    self: BuildingPy, building_py_object: Serializable, target_class: type = None
) -> SpeckleObject:
    # detect the type of the building py object and convert it to a speckle object
    if isinstance(building_py_object, Interval):
        converted_object = SpeckleInterval(
            start=building_py_object.start, end=building_py_object.end
        )
    elif isinstance(building_py_object, Vector):
        converted_object = (target_class or SpeckleVector).from_coords(
            building_py_object.x,
            building_py_object.y,
            building_py_object.z if len(building_py_object) > 2 else 0,
        )
    elif isinstance(building_py_object, Plane):
        converted_object = SpecklePlane(
            origin=convert_to_speckle_object(building_py_object.Origin),
            normal=convert_to_speckle_object(building_py_object.Normal),
            xdir=convert_to_speckle_object(building_py_object.v1),
            ydir=convert_to_speckle_object(building_py_object.v2),
        )

    elif isinstance(building_py_object, Mesh):
        converted_object = SpeckleMesh(
            vertices=[axis for vert in building_py_object.vertices for axis in vert],
            faces=[
                index
                for face in building_py_object.faces
                # length, index 1, index 2, index ... length for example: 3, 0, 1, 2
                for index in ([len(face)] + face)
            ],
            name=building_py_object.name,
            colors=[color for color in building_py_object.colors],
            textureCoordinates=[],
        )

    elif isinstance(building_py_object, PolyCurve):
        speckle_points = [
            convert_to_speckle_object(self, point)
            for point in building_py_object.points
        ]
        converted_object = SpecklePolyLine.from_points(speckle_points)
        try:
            converted_object.area = building_py_object.area()
            converted_object.length = PolyCurve.length(building_py_object)
            converted_object.closed = building_py_object.closed
        except Exception as e:
            print(e)

    elif isinstance(building_py_object, Line):
        display_style = SpeckleDisplayStyle()
        display_style.color = -854423
        display_style.linetype = "Continuous"
        display_style.lineweight = 0.25
        converted_object = SpeckleLine(
            start=convert_to_speckle_object(building_py_object.start),
            end=convert_to_speckle_object(building_py_object.end),
        )
        converted_object.length = building_py_object.length
        converted_object.color = 0
        converted_object.displayStyle = display_style

    elif isinstance(building_py_object, Polygon) or isinstance(
        building_py_object, PolyCurve
    ):
        speckle_points = [
            convert_to_speckle_object(point) for point in building_py_object
        ]
        speckle_polyline = SpecklePolyLine.from_points(points=speckle_points)
        speckle_polyline.closed = building_py_object.isClosed
        speckle_polyline.area = building_py_object.area
        speckle_polyline.length = building_py_object.length
        speckle_polyline.curveCount = len(building_py_object.curves)
        speckle_polyline.pointCount = len(building_py_object.points)

    elif isinstance(building_py_object, Panel):
        colrs = building_py_object.colorlst
        converted_object = SpeckleMesh(
            vertices=building_py_object.extrusion.verts,
            faces=building_py_object.extrusion.faces,
            colors=colrs,
            name=building_py_object.name,
            textureCoordinates=[],
        )
    elif isinstance(building_py_object, Matrix):
        converted_object = SpecklePlane(
            origin=convert_to_speckle_object(
                self, building_py_object.origin, SpecklePoint
            ),
            normal=convert_to_speckle_object(
                self,
                (
                    building_py_object.get_axis(2).normalized
                    if building_py_object.dimensions >= 3
                    else Vector.z_axis
                ),
            ),
            xdir=convert_to_speckle_object(
                self, building_py_object.get_axis(0).normalized
            ),
            ydir=convert_to_speckle_object(
                self, building_py_object.get_axis(1).normalized
            ),
        )
    elif isinstance(building_py_object, ColumnTag):
        converted_object = SpeckleText(
            plane=convert_to_speckle_object(
                self, building_py_object.transform, SpecklePlane
            ),
            value=building_py_object.text,
            height=building_py_object.text_height,
        )
    # elif isinstance(building_py_object, Face):
    # 	all_vertices = []
    # 	all_faces = []
    # 	all_colors = []
    # 	for index in range(len(building_py_object.PolyCurveList)):
    # 		all_vertices.append(building_py_object.mesh[index].verts)
    # 		all_faces.append(building_py_object.mesh[index].faces)
    # 		all_colors.append(building_py_object.colorlst[index])
    # 	all_vertices = flatten(all_vertices)
    # 	all_faces = flatten(all_faces)
    # 	all_colors = flatten(all_colors)
    # 	speckle_objects.append(SpeckleMesh(
    # 								  vertices=all_vertices,
    # 								  faces=all_faces,
    # 								  colors=all_colors,
    # 								  name=building_py_object.name[index],
    # 								  units= project.units
    # 								  ))
    elif isinstance(building_py_object, Surface):
        all_vertices = []
        all_faces = []
        all_colors = []

        if len(building_py_object.inner_Surface) > 0:
            for each in building_py_object.inner_Surface:
                converted_object = SpeckleMesh(
                    surface_type="Inner_Surface",
                    vertices=each.verts,
                    faces=each.faces,
                    name=building_py_object.type,
                    textureCoordinates=[],
                )
        converted_object = SpeckleMesh(
            surface_type="Outer_Surface",
            vertices=building_py_object.outer_Surface.verts,
            faces=building_py_object.outer_Surface.faces,
            name=building_py_object.type,
            textureCoordinates=[],
            colors=building_py_object.colorlst,
        )

    # elif isinstance(building_py_object, Beam):
    #    try:
    #        if building_py_object.comments.type == "Scia_Params":
    #            converted_object = SpeckleMesh(
    #                vertices=building_py_object.extrusion.verts,
    #                faces=building_py_object.extrusion.faces,
    #                colors=building_py_object.colorlst,
    #                name=building_py_object.name,
    #                textureCoordinates=[],
    #                Scia_Id=building_py_object.comments.id,
    #                Scia_Justification=building_py_object.comments.perpendicular_alignment,
    #                Scia_Layer=building_py_object.comments.layer,
    #                Scia_Rotation=building_py_object.comments.lcs_rotation,
    #                Scia_Staaf=building_py_object.comments.name,
    #                Scia_Type=building_py_object.comments.cross_section,
    #                Scia_Node_Start=building_py_object.comments.start_node,
    #                Scia_Node_End=building_py_object.comments.end_node,
    #                Revit_Rotation=str(building_py_object.comments.revit_rot),
    #                Scia_Layer_Type=building_py_object.comments.layer_type,
    #                BuildingPy_XJustification=building_py_object.comments.Xjustification,
    #                BuildingPy_YJustification=building_py_object.comments.Yjustification,
    #            )
    #        else:
    #            converted_object = SpeckleMesh(
    #                vertices=building_py_object.extrusion.verts,
    #                faces=building_py_object.extrusion.faces,
    #                colors=building_py_object.colorlst,
    #                name=building_py_object.name,
    #                textureCoordinates=[],
    #            )
    #    except:
    #        # converted_object = SpeckleMesh(
    #        # 								vertices=building_py_object.extrusion.verts,
    #        # 								faces=building_py_object.extrusion.faces,
    #        # 								colors = building_py_object.colorlst,
    #        # 								name = building_py_object.profileName,
    #        # 								textureCoordinates = [])
    elif isinstance(building_py_object, Extrusion) or isinstance(
        building_py_object, Void
    ):
        clrs = [4294901760, 4294901760, 4294901760, 4294901760, 4294901760]

        # if void, color red.

        converted_object = SpeckleMesh(
            vertices=building_py_object.verts,
            faces=building_py_object.faces,
            colors=clrs,
            name=(
                "Void"
                if isinstance(building_py_object, Void)
                else building_py_object.name
            ),
            textureCoordinates=[],
        )

        if isinstance(building_py_object.parameters, dict):
            building_py_object.parameters = [building_py_object.parameters]

        for param in building_py_object.parameters:
            for param, value in param.items():
                try:
                    param_name = int(param)
                except ValueError:
                    param_name = param
                setattr(converted_object, str(param_name), value)
    elif isinstance(building_py_object, Wall):
        clrs = []
        converted_object = SpeckleMesh(
            vertices=building_py_object.verts,
            faces=building_py_object.faces,
            colors=clrs,
            name=building_py_object.name,
            textureCoordinates=[],
        )
    elif isinstance(building_py_object, Arc):
        converted_object = ArcToSpeckleArc(building_py_object)
    # when converting to speckle extrusion, we'd still need to provide the mesh.
    # elif isinstance(building_py_object, Extrusion):
    #    converted_object = SpeckleExtrusion()
    # elif isinstance(building_py_object, Beam):
    #    return convert_to_speckle_object(building_py_object.extrusion)
    elif isinstance(building_py_object, Rect):
        converted_object = SpeckleBox(
            basePlane=convert_to_speckle_object(
                self, Matrix.translate(building_py_object.center)
            ),
            xSize=convert_to_speckle_object(
                self,
                Interval(start=building_py_object.p0.x, end=building_py_object.p1.x),
            ),
            ySize=convert_to_speckle_object(
                self,
                Interval(start=building_py_object.p0.y, end=building_py_object.p1.y),
            ),
        )
        if len(building_py_object.p0) >= 3:
            converted_object.zsize = convert_to_speckle_object(
                self,
                Interval(start=building_py_object.p0.z, end=building_py_object.p1.z),
            )
    elif isinstance(building_py_object, Meshable):
        settings = TesselationSettings()
        mesh = building_py_object.to_mesh(settings)
        mesh.name = building_py_object.name
        return convert_to_speckle_object(self, mesh)
    else:
        raise NotImplementedError(
            f"{building_py_object.__class__.__name__} cannot yet be converted to speckle"
        )
    converted_object.units = self.units
    converted_object.applicationId = self.applicationId
    # converted_object.name = typeof(converted_object)
    # converted_object.domain =
    # converted_object.id = building_py_object.
    return converted_object


def GridLineToLines(self: BuildingPy, GridLine):
    SpeckleLines = []
    for line in GridLine.line:
        SpeckleLines.append(convert_to_speckle_object(self, line))
    return SpeckleLines


def GridToLines(self: BuildingPy, Grid):
    SpeckleLines = []
    for line_x in Grid.gridsX:
        SpeckleLines.append(GridLineToLines(self, line_x))
    for line_j in Grid.gridsY:
        SpeckleLines.append(GridLineToLines(self, line_j))
    return SpeckleLines


def ArcToSpeckleArc(arc: Arc):
    speckle_plane = SpecklePlane(
        origin=convert_to_speckle_object(arc.plane.Origin),
        normal=convert_to_speckle_object(arc.plane.Normal),
        xdir=convert_to_speckle_object(arc.plane.vector_1),
        ydir=convert_to_speckle_object(arc.plane.vector_2),
    )

    start_point = convert_to_speckle_object(arc.start)
    mid_point = convert_to_speckle_object(arc.mid)
    end_point = convert_to_speckle_object(arc.end)

    radius = arc.radius
    start_angle = arc.startAngle
    end_angle = arc.endAngle
    angle_radians = arc.angle_radian
    area = arc.area
    length = arc.length
    speckle_interval = convert_to_speckle_object(Interval(start=0, end=1))

    spArc = SpeckleArc(
        startPoint=start_point,
        midPoint=mid_point,
        endPoint=end_point,
        domain=speckle_interval,
        plane=speckle_plane,
        radius=radius,
        startAngle=start_angle,
        endAngle=end_angle,
        angleRadians=angle_radians,
        area=area,
        length=length,
    )

    return spArc


def translateObjectsToSpeckleObjects(self: BuildingPy, building_py_objects: list):
    speckle_objects: list[SpeckleObject] = []
    for building_py_object in building_py_objects:
        if isinstance(building_py_object, Text):
            for polycurves in building_py_object.write():
                polycurve = convert_to_speckle_object(self, polycurves)
                speckle_objects.append(polycurve)
        elif isinstance(building_py_object, GridLine):
            for converted_line in GridToLines(self, building_py_object):
                speckle_objects.append(converted_line)
        elif isinstance(building_py_object, Grid):
            for converted_line in GridToLines(building_py_object):
                speckle_objects.append(converted_line)

        else:
            speckle_objects.append(convert_to_speckle_object(self, building_py_object))

    return speckle_objects


def TransportToSpeckle(
    host: str, streamid: str, SpeckleObjects: list, messageCommit: str
):
    client = SpeckleClient(host=host)
    account = get_default_account()
    client.authenticate_with_account(account)
    streamid = streamid

    class SpeckleExport(SpeckleObject):
        elements = None

    obj = SpeckleExport(elements=SpeckleObjects)
    transport = ServerTransport(client=client, stream_id=streamid)
    hash = operations.send(base=obj, transports=[transport])

    commit_id = client.commit.create(
        stream_id=streamid,
        object_id=hash,
        message=messageCommit,
    )

    print(f"View commit: https://{host}/streams/{streamid}/commits/{commit_id}")
    return commit_id
