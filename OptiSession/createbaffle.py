from FreeCAD import Vector
import Part

b0 = Part.Vertex(250,50,0)
b1 = Part.Vertex(340,50,0)
b2 = Part.Vertex(350,-20,0)

weight = 1
extrudeVector = Vector(0,0,10)

bsplineBaffle = Part.BSplineCurve()
bsplineBaffle.increaseDegree(2)
bsplineBaffle.setPole(1,b0.Point,1)
bsplineBaffle.setPole(2,b1.Point,weight)
bsplineBaffle.setPole(3,b2.Point,1)

wallBaffle = bsplineBaffle.toShape().extrude(extrudeVector)
wallBaffle.exportStl('wallBaffle.stl',1)

exit(0)