import sys, os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from construction.frame import *
from exchange.scia import *

from exchange.struct4U import *

from construction.analytical import *
from project.fileformat import project


filepath = f"{os.getcwd()}\\temp\\Scia\\Examples buildingpy\\_1.xml"

project = BuildingPy("TempCommit", "0")

LoadXML(filepath, project)

# print(project.objects)
# print(len(project.objects))
project.toSpeckle("c6e11e74cb")

#send the loadxml objects back
#so after send return the project.objects (start and end coords)