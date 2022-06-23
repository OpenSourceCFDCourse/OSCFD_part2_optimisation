from FreeCAD import Vector
import Part

v0 = Part.Vertex(0,0,0)
v1 = Part.Vertex(0,100,0)
v2 = Part.Vertex(400,100,0)
v3 = Part.Vertex(400,-600,0)
v4 = Part.Vertex(300,-600,0)
v5 = Part.Vertex(300,0,0)

inlet = Part.LineSegment(v0.Point,v1.Point)
outlet = Part.LineSegment(v3.Point,v4.Point)
line1 = Part.LineSegment(v1.Point,v2.Point)
line2 = Part.LineSegment(v2.Point,v3.Point)
line3 = Part.LineSegment(v4.Point,v5.Point)
line4 = Part.LineSegment(v5.Point,v0.Point)

extrudeVector = Vector(0,0,10)

inletFace = inlet.toShape().extrude(extrudeVector)
outletFace = outlet.toShape().extrude(extrudeVector)

inletFace.exportStl('inlet.stl',1)
outletFace.exportStl('outlet.stl',1)

walls = Part.Compound([line1.toShape(),line2.toShape(),line3.toShape(),line4.toShape()])
wallFaces = walls.extrude(extrudeVector)
wallFaces.exportStl('walls.stl',1)

exit(0)
