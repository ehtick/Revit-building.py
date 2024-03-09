import sys, os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from objects.frame import *
from exchange.IFC import *
from exchange.struct4U import *

tree = ET.parse("C:/Users/Jonathan/Desktop/Struct4U_Export/hal_speckle_test2.xml")
root = tree.getroot()

#convert .xml to buildingpy objects.
obj = []

#LoadGrid and create in Speckle
XYZ = XMLImportNodes(tree)
obj = obj + XMLImportGrids(tree, 1000)
obj.append(XMLImportPlates(tree))

#BEAMS
BeamsFrom = root.findall(".//Beams/From_node_number")
BeamsNumber = root.findall(".//Beams/Number")
BeamsTo = root.findall(".//Beams/To_node_number")
BeamsName = root.findall(".//Beams/Profile_number")
BeamsLayer = root.findall(".//Beams/Layer")
BeamsRotation = root.findall(".//Beams/Angle")

#PROFILES
ProfileNumber = root.findall(".//Profiles/Number")
ProfileName = root.findall(".//Profiles/Profile_name")

#BEAMS
for i, j, k, l, m in zip(BeamsFrom, BeamsTo, BeamsName, BeamsNumber, BeamsRotation):
    profile_name = ProfileName[int(k.text)-1].text
    profile_name = profile_name.split()[0]
    if profile_name == None:
        print(f"No profile name '{profile_name}' found.")
    else:
        start = XYZ[1][XYZ[0].index(i.text)]
        end = XYZ[1][XYZ[0].index(j.text)]
        try:
            pf = Frame.byStartpointEndpointProfileNameShapevector(start, end, profile_name, profile_name + "-" + l.text, Vector2(0,0), float(m.text), BaseSteel, None)
            if pf != None:
                obj.append(pf)
        except Exception as e:
            print(f"Could not translate '{profile_name}'.")

project.objects = obj
#read the objects here.

#from coordinate to coordinate.
# give rotation on axis.

print(project.objects)
project.toIFC("c6e11e74cb")