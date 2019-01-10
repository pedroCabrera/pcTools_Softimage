import win32com.client
from win32com.client import constants
import Tools
from Tools import *
from Tools import *
reload ( Tools )

null = None
false = 0
true = 1
PC_PRIMS=['PC_Cubesphere','PC_Disc','PC_Polygon','PC_Basic_Gear']
def XSILoadPlugin( in_reg ):
	in_reg.Author = "Pedrito"
	in_reg.Name = "PC_Primitives"
	in_reg.Major = 1
	in_reg.Minor = 0
	
	for prim in PC_PRIMS:
		in_reg.RegisterCommand(prim,prim)
	in_reg.RegisterCommand("PC_Ice_Curve","PC_Ice_Curve")
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true


def PC_Cubesphere_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Disc_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Polygon_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Basic_Gear_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Ice_Curve_Init (in_ctxt):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Cubesphere_Execute(  ):

	Application.LogMessage("Primitives_Execute called",constants.siVerbose)

	app = Application
	Comp = 'PC_Cubesphere'
	Cubesphere = app.GetPrim("EmptyPolygonMesh", Comp, "", "")
	Ice = app.ApplyIceOp(Comp)
	app.InspectObj(Ice)	
	return true
def PC_Disc_Execute(  ):

	Application.LogMessage("Primitives_Execute called",constants.siVerbose)
	app = Application
	Comp = 'PC_Disc'
	Cubesphere = app.GetPrim("EmptyPolygonMesh", Comp, "", "")
	Ice = app.ApplyIceOp(Comp)
	app.InspectObj(Ice)	
	return true
def PC_Polygon_Execute(  ):

	Application.LogMessage("Primitives_Execute called",constants.siVerbose)

	app = Application
	Comp = 'PC_Polygon'
	Cubesphere = app.GetPrim("EmptyPolygonMesh", Comp, "", "")
	Ice = app.ApplyIceOp(Comp)
	app.InspectObj(Ice)	
	return true
def PC_Basic_Gear_Execute(  ):

	Application.LogMessage("Primitives_Execute called",constants.siVerbose)

	app = Application
	Comp = 'PC_Basic Gear'
	Cubesphere = app.GetPrim("EmptyPolygonMesh", Comp, "", "")
	Ice = app.ApplyIceOp(Comp)
	app.InspectObj(Ice)	
	return true
def PC_Ice_Curve_Execute():

	oRoot = Application.ActiveSceneRoot
	cv = oRoot.AddNurbsCurve(None, None, 0, 1)
	Application.AddStaticICEAttribute(str(cv)+'.crvlist', "__PCVPositions", "siComponentDataTypeFloat", "siComponentDataContextSingleton", "siComponentDataStructureDynamicArray")
	Application.AddStaticICEAttribute(str(cv)+'.crvlist', "__PCVpcvNB", "siComponentDataTypeLong", "siComponentDataContextSingleton", "siComponentDataStructureDynamicArray")
	Application.AddStaticICEAttribute(str(cv)+'.crvlist', "__PCVDegree", "siComponentDataTypeLong", "siComponentDataContextSingleton", "siComponentDataStructureDynamicArray")
	Application.AddStaticICEAttribute(str(cv)+'.crvlist', "__PCVClosed", "siComponentDataTypeLong", "siComponentDataContextSingleton", "siComponentDataStructureDynamicArray")

	cv.Name = "PC_ICE_CV"
	try:
		Scop = XSIFactory.CreateScriptedOp("PC_ICE_CV", "", "XSI.SIPython")
	except:
		Scop = XSIFactory.CreateScriptedOp("PC_ICE_CV", "", "Python")
	Scop.AddOutputPort(cv.ActivePrimitive)
	
	Scop.AddInputPort(cv.ActivePrimitive)
	
	Scop.AlwaysEvaluate = 1

	Scop.Code = PC_ICE_CV_LOGIC
	Scop.Connect(None,2)
	Application.SelectObj(cv)
	ICETree = Application.ApplyICEop("PC_Set PC CV Data",cv,cv,"siUnspecified")
	LINARRAY = Application.AddICECompoundNode("Build Linearly Interpolated Array", ICETree)
	Application.SetPortType(str(LINARRAY)+".End", "siComponentDataTypeVector3")
	Application.SetValue(str(ICETree)+'.PC_Set_PC_CV_Data.Reference', "self", "")
	Application.ConnectICENodes(str(ICETree)+'.PC_Set_PC_CV_Data.ControlPoints', str(LINARRAY)+".Result")
	Application.SetValue(str(LINARRAY)+".End_x", 20, "")
	Application.SetValue(str(LINARRAY)+".End_y", 20, "")
	Application.InspectObj(str(ICETree)+'.PC_Set_PC_CV_Data')
	Application.InspectObj(ICETree)
	Application.SelectObj(cv)
	Application.OpenView("ICE Tree",False)
	
	return true
