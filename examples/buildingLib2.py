




from library.profile import data as jsondata



project = BuildingPy("Library Profiles","0")

# Export all steelprofiles to Speckle
lst = []
for item in jsondata:
    for i in item.values():
        lst.append(i[0]["synonyms"][0])

names = [
    "HEA200",
    "HEB200",
    "HEM200",
    "IPE200",
    "200AA",
    "HD320/300",
    "DIN20",
    "DIE20",
    "DIL20",
    "DIR20",
    "UNP200",
    "Buis219.1/10",
    "INP200",
   # "T100",
    "UPE200",
   # "UAP200",
    "L200/200/16",
    "L200/100/10",
    "S100x15",
    "R50",
    "K200/200/10",
    "K200/100/10"
    ]

height = 2000
x = 0
y = 0
spacing = 2000
row = 5

rownumb = 0
rowcolum = 5
for i in names:
    if rownumb == rowcolum:
        rowcolum = rowcolum + 5
        y = y + spacing
        x = 0
    prof = i[:3]
    print(i)
    fram = Beam.by_startpoint_endpoint(Point(x, y, 0), Point(x, y+1, height), i, i, BaseSteel).write(project)
    ColumnTag.by_beam(fram).write(project)
    x = x + spacing
    rownumb = rownumb + 1

#Cold Formed C
nm = "C150/50/2"
C = Beam.by_startpoint_endpoint(Point(-1000,-1001,0),Point(-1000,-1000,height),CProfile(nm,50,150,3,5,10),nm,0,BaseSteel).write(project)
ColumnTag.by_beam(C).write(project)

#Cold Formed C with lips
nm = "CWL150/50/10/2"
CWL = Beam.by_startpoint_endpoint(Point(0,-1001,0),Point(0,-1000,height),CProfileWithLips(nm,50,150,20,3,5,10),nm,0,BaseSteel).write(project)
ColumnTag.by_beam(CWL).write(project)

#Cold Formed L
nm = "CF_L100/50/3/3"
CWL = Beam.by_startpoint_endpoint(Point(1000,-1001,0),Point(1000,-1000,height),LProfileColdFormed(nm,50,100,3,3,5,15),nm,0,BaseSteel).write(project)
ColumnTag.by_beam(CWL).write(project)

#Cold Formed Sigma with lips
nm = "CF_Sigma150 / 50 / 10 / 1"
CWL = Beam.by_startpoint_endpoint(Point(2000,-1001,0),Point(2000,-1000,height),SigmaProfileWithLipsColdFormed(nm,50, 150, 1, 3, 10, 60, 35, 15,10),nm,0,BaseSteel).write(project)
ColumnTag.by_beam(CWL).write(project)

#Cold Formed Z
nm = "CF_Z200/100/2"
CWL = Beam.by_startpoint_endpoint(Point(3000,-1001,0),Point(3000,-1000,height),ZProfileColdFormed(nm,100,200,2,3),nm,0,BaseSteel).write(project)
ColumnTag.by_beam(CWL).write(project)

#Cold Formed Z with lips
nm = "CF_ZL150/100/1"
CWL = Beam.by_startpoint_endpoint(Point(4000,-1001,0),Point(4000,-1000,height),ZProfileWithLipsColdFormed(nm,100,150,1,3,10),nm,0,BaseSteel).write(project)
ColumnTag.by_beam(CWL).write(project)

project.to_speckle("a5d97a353d")