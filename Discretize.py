from __future__ import division # allows floating point division from integers
import FreeCAD, Part, math
import os, dummy, FreeCADGui
from FreeCAD import Base
from pivy import coin

path_curvesWB = os.path.dirname(dummy.__file__)
path_curvesWB_icons =  os.path.join( path_curvesWB, 'Resources', 'icons')

class Discretization:
    def __init__(self, obj , edge):
        ''' Add the properties '''
        FreeCAD.Console.PrintMessage("\nDiscretization class Init\n")
        obj.addProperty("App::PropertyLinkSub",      "Edge",      "Discretization",   "Edge").Edge = edge
        obj.addProperty("App::PropertyEnumeration",  "Algorithm",    "Method",   "Discretization Method").Algorithm=["Number","Distance","Deflection"]
        obj.addProperty("App::PropertyInteger",      "Number",    "Method",   "Number of edge points").Number = 10
        obj.addProperty("App::PropertyFloat",        "Distance",  "Method",   "Distance between edge points").Distance=1.0
        obj.addProperty("App::PropertyFloat",        "Deflection","Method",   "Distance for deflection Algorithm").Deflection=1.0
        obj.addProperty("App::PropertyFloat",        "ParameterFirst",     "Parameters",   "Start parameter").ParameterFirst=0.0
        obj.addProperty("App::PropertyFloat",        "ParameterLast",      "Parameters",   "End parameter").ParameterLast=1.0
        obj.addProperty("App::PropertyVectorList",   "Points",    "Discretization",   "Points")
        obj.addProperty("Part::PropertyPartShape",   "Shape",     "Discretization",   "Shape")
        obj.Proxy = self
        #obj.Samples = (20,2,1000,10)
        obj.Points = []
        obj.Algorithm = "Number"
        self.edge = None
        self.setEdge(obj)
        self.execute(obj)

        
    def selectedEdgesToProperty(self, obj, edge):
        objs = []
        for o in edge:
            if isinstance(o,tuple) or isinstance(o,list):
                if o[0].Name != obj.Name:
                    objs.append(tuple(o))
            else:
                for el in o.SubElementNames:
                    if "Edge" in el:
                        if o.Object.Name != obj.Name:
                            objs.append((o.Object,el))
        if objs:
            obj.Edge = objs
            FreeCAD.Console.PrintMessage(str(edge) + "\n")
            FreeCAD.Console.PrintMessage(str(obj.Edge) + "\n")


    def setEdge( self, obj):
        o = obj.Edge[0]
        e = obj.Edge[1][0]
        n = eval(e.lstrip('Edge'))
        self.edge = o.Shape.Edges[n-1]
        obj.ParameterFirst = obj.ParameterFirst #self.edge.FirstParameter
        obj.ParameterLast = obj.ParameterLast   #self.edge.LastParameter

    def buildPoints(self, obj):
        if   obj.Algorithm == "Number":
            obj.Points = self.edge.discretize( Number = obj.Number,         First = obj.ParameterFirst, Last = obj.ParameterLast)
        elif obj.Algorithm == "Distance":
            obj.Points = self.edge.discretize( Distance = obj.Distance,     First = obj.ParameterFirst, Last = obj.ParameterLast)
        elif obj.Algorithm == "Deflection":
            obj.Points = self.edge.discretize( Deflection = obj.Deflection, First = obj.ParameterFirst, Last = obj.ParameterLast)
        #FreeCAD.Console.PrintMessage(str(len(obj.CombPoints))+" Comb points\n")   #+str(obj.CombPoints)+"\n\n")

    def execute(self, obj):
        FreeCAD.Console.PrintMessage("\n* Discretization : execute *\n")
        self.setEdge( obj)
        self.buildPoints( obj)
        obj.Shape = Part.Compound([Part.Vertex(i) for i in obj.Points])

    def onChanged(self, fp, prop):
        #print fp
        if not fp.Edge:
            return
        if prop == "Edge":
            FreeCAD.Console.PrintMessage("Discretization : Edge changed\n")
            self.setEdge( fp)
        if prop == "Algorithm":
            FreeCAD.Console.PrintMessage("Discretization : Algorithm changed\n")
            if fp.Algorithm == "Number":
                fp.setEditorMode("Number", 0)
                fp.setEditorMode("Distance", 2)
                fp.setEditorMode("Deflection", 2)
            elif fp.Algorithm == "Distance":
                fp.setEditorMode("Number", 2)
                fp.setEditorMode("Distance", 0)
                fp.setEditorMode("Deflection", 2)
            elif fp.Algorithm == "Deflection":
                fp.setEditorMode("Number", 2)
                fp.setEditorMode("Distance", 2)
                fp.setEditorMode("Deflection", 0)
        if prop == "Number":
            if fp.Number <= 1:
                fp.Number = 2
            FreeCAD.Console.PrintMessage("Discretization : Number changed to "+str(fp.Number)+"\n")
        if prop == "Distance":
            if fp.Distance <= 0.0:
                fp.Distance = 0.001
            FreeCAD.Console.PrintMessage("Discretization : Distance changed to "+str(fp.Distance)+"\n")
        if prop == "Deflection":
            if fp.Deflection <= 0.0:
                fp.Deflection = 0.001
            FreeCAD.Console.PrintMessage("Discretization : Deflection changed to "+str(fp.Deflection)+"\n")
        if prop == "ParameterFirst":
            if fp.ParameterFirst < self.edge.FirstParameter:
                fp.ParameterFirst = self.edge.FirstParameter
            FreeCAD.Console.PrintMessage("Discretization : ParameterFirst changed to "+str(fp.ParameterFirst)+"\n")
        if prop == "ParameterLast":
            if fp.ParameterLast > self.edge.LastParameter:
                fp.ParameterLast = self.edge.LastParameter
            FreeCAD.Console.PrintMessage("Discretization : ParameterLast changed to "+str(fp.ParameterLast)+"\n")
        #self.execute(fp) # Infinite loop
            
    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None


class discretize:
    def parseSel(self, selectionObject):
        res = []
        for obj in selectionObject:
            if obj.HasSubObjects:
                subobj = obj.SubObjects[0]
                if issubclass(type(subobj),Part.Edge):
                    res=(obj.Object,[obj.SubElementNames[0]])
            else:
                res=(obj.Object,["Edge1"])
        return res

    def Activated(self):
        s = FreeCADGui.Selection.getSelectionEx()
        edges = self.parseSel(s)
        #FreeCAD.Console.PrintMessage(str(edges) + "\n")
        #combSelected = self.findComb(s)
        #if not combSelected:
            #obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython","Comb") #add object to document
            #Comb(obj,edges)
            #ViewProviderComb(obj.ViewObject)
        #else:
            #self.appendEdges(combSelected, edges)
        obj=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Discretized_Curve") #add object to document
        Discretization(obj,edges)
        obj.ViewObject.Proxy = 0
        obj.ViewObject.PointSize = 4.00000
        #ViewProviderDiscretization(obj.ViewObject)
        FreeCAD.ActiveDocument.recompute()
            
    def GetResources(self):
        return {'Pixmap' : path_curvesWB_icons+'/discretize.svg', 'MenuText': 'Discretize', 'ToolTip': 'Discretizes edge or wire'}

FreeCADGui.addCommand('Discretize', discretize())


