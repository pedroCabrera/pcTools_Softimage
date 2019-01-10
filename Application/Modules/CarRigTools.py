import win32com
from win32com.client import constants as c
import sys , Tools
reload ( Tools )

app = win32com.client.Dispatch( 'XSI.Application' ).Application
XSIMath = win32com.client.Dispatch( 'XSI.Math' )
XSIToolkit = win32com.client.Dispatch( 'XSI.UIToolkit' )
XSIFactory = win32com.client.Dispatch( 'XSI.Factory' )


def RigMasterNull (name,icetree = True,executenode=True,addport=True):
	RIG = app.GetPrim("Null",name)
	RIG.primary_icon = 0
	RIGMASTER = [RIG]
	#Add an IceTree and a Execute Node///Add a port2 for the IceTree
	if icetree == True:
		IceTreeRIG = app.ApplyOp("ICETree", RIG.Name, "siNode", "", "", 0)
		RIGMASTER.append(IceTreeRIG)
		if executenode == True:
			EXECUTErot = app.AddICENode("ICENodes\\ExecuteNode.Preset", IceTreeRIG)		
			app.ConnectICENodes(str(IceTreeRIG)+".Port1", str(EXECUTErot)+".execute")
			RIGMASTER.append(EXECUTErot)
		if addport == True:
			app.AddPortToICENode(str(IceTreeRIG)+".port1", "siNodePortDataInsertionLocationAfter")
	return RIGMASTER 
def CarMovController(RIG,XSIZE,BodyGroupObjs):
	CARmov =RIG.AddNull("CAR_MOV")
	CARmov.primary_icon = 0
	CARmov.Size = XSIZE[1][1]/3.3333
	CARmov.shadow_colour_custom = True
	CARmov.R=1
	CARmov.G=1
	CARmov.shadow_icon = 10
	CARmov.shadow_scaleZ = 5
	CARmov.shadow_scaleX = 8
	CARmov.shadow_scaleY = 2
	#Define the CarBodyContainer
	CARBodyGeo = CARmov.AddNull("CAR_Body")
	CARBodyGeo.primary_icon = 0
	app.SetExpr(CARmov.Name+".null.shadow_offsetY", "("+CARBodyGeo.Name+".kine.local.posy/3)+0.5", "")
	for Obj in BodyGroupObjs:
		app.ParentObj(CARBodyGeo.Name, Obj.Name)
	R = [CARmov,CARBodyGeo]
	return R
def CreateRotationControl(Obj,DIRECTION_WHEELS,parent):
	posObjx = app.GetValue(str(Obj.Name)+".kine.local.posx")
	posObjy = app.GetValue(str(Obj.Name)+".kine.local.posy")
	posObjz = app.GetValue(str(Obj.Name)+".kine.local.posz")
	
	SIZE = Tools.GetBoundingSize(Obj)
	radio = (SIZE[1][1]-SIZE[1][0])/2
	#define a direction controll for each wheel
	DIR = Tools.CreateNullByPose("DIR",parent,posObjx,posObjz)
	DIRECTION_WHEELS.append(DIR)
	
	DIR.shadow_colour_custom = True
	DIR.size = radio
	DIR.primary_icon = 6
	DIR.shadow_icon = 7
	DIR.shadow_offsetY = 2.5
	DIR.shadow_scaleZ = 0.5
	DIR.shadow_scaleY = 0.5
	DIR.shadow_scaleX = 0.5
	#Define a Circle to rotate the whel
	Cv = Tools.AddWheelsCurves(DIR,posObjx,posObjy,radio)
	#Translate the controller to the good position
	posDIRx = app.SetValue(DIR.Name + ".kine.local.posx", posObjx , "")
	posDIRz = app.SetValue(DIR.Name + ".kine.local.posz", posObjz , "")
	app.ParentObj(Cv.Name, Obj.Name)#Parent the object unther the curve
	R = [DIR,Cv]
	return R
def RAYCAST_SURRFACE(DIR,CARmov,Surface):	
	Raycastgrid = CARmov.AddGeometry("Grid","NurbsSurface","Raycast_Surf")#CARmov
	app.SetValue(Raycastgrid.Name + ".visibility.viewvis", False)
	app.SetValue(Raycastgrid.Name + ".surfmsh.geom.subdivu", 1)
	app.SetValue(Raycastgrid.Name + ".surfmsh.geom.subdivv", 1)

	app.FreezeObj(Raycastgrid.Name)

	RaycastLattice = app.GetPrimLattice("Lattice",Raycastgrid,"Raycast_Lattice",Raycastgrid)
	RaycastPrim = RaycastLattice.ActivePrimitive
	size = RaycastPrim.SizeY = 0
	app.SetValue(str(RaycastPrim)+".subdivx", 1)
	app.SetValue(str(RaycastPrim)+".subdivy", 1)
	app.SetValue(str(RaycastPrim)+".subdivz", 1)
	
	CLUSTERS = []
	CLUSTERS.append(RaycastPrim.Geometry.AddCluster(c.siVertexCluster,"RB_CLSTR",[0,2]))
	CLUSTERS.append(RaycastPrim.Geometry.AddCluster(c.siVertexCluster,"RF_CLSTR",(1,3)))
	CLUSTERS.append(RaycastPrim.Geometry.AddCluster(c.siVertexCluster,"LB_CLSTR",(4,6)))
	CLUSTERS.append(RaycastPrim.Geometry.AddCluster(c.siVertexCluster,"LF_CLSTR",(5,7)))

	RAYCAST_NULLS = []
	RAYCAST_cntrs = []
	for clstr in CLUSTERS:
		clstr_Null = Raycastgrid.AddNull(clstr.Name[:2]+"_Raycast")
		clstr_Null.primary_icon = 0
		clstr_Null.shadow_colour_custom = True
		clstr_Null.shadow_icon = 4
		clstr_Null.G = 1
		app.ApplyCns("ObjectToCluster",clstr_Null,clstr)
		RAYCAST_NULLS.append(clstr_Null)
		
		clstr_cntr = Raycastgrid.AddNull(clstr.Name[:2]+"_position_null")
		app.MatchTransform(clstr_cntr, clstr_Null)
		app.ApplyOp("ClusterCenter", clstr.FullName+";"+clstr_cntr.FullName, 0, "siPersistentOperation")
		posX = app.GetValue(str(clstr.Name[:2])+str(DIR.Name[2:])+".kine.local.posx")
		app.MatchTransform(clstr_cntr, str(clstr.Name[:2]+DIR.Name[2:]))
		RAYCAST_cntrs.append(clstr_cntr.Name)

	app.FreezeObj(RaycastLattice, "", "")
	app.DeleteObj(RAYCAST_cntrs)
	
	AddLatticeCompounds(RaycastLattice,Surface)
	return Raycastgrid

def AddLatticeCompounds(RaycastLattice,Surface):

	IceTreeLATTICE = app.ApplyOp("ICETree", RaycastLattice.Name, "siNode", "", "", 0)
	RAYCASTnode = app.AddICECompoundNode("PC_RAYCAST_for_lattice", IceTreeLATTICE)
	app.ConnectICENodes(str(IceTreeLATTICE)+".port1" , str(RAYCASTnode)+".Execute")
	
	SurfaceNode = app.AddICENode("GetDataNode", IceTreeLATTICE)
	app.SetValue(str(SurfaceNode) +".reference", Surface.Name, "")
	app.ConnectICENodes(str(RAYCASTnode)+".Surface", str(SurfaceNode)+".value")
def AddRotationCompounds(IceTreeRIG,EXECUTErotPort,DIR,Cv,EXECUTErot):
	cvradius =str(Cv) +".circle.radius"
	RigRuedasNode = app.AddICECompoundNode("PC_ROTATION_WHEEL", IceTreeRIG)

	app.ConnectICENodes(str(EXECUTErot)+".port" + str(EXECUTErotPort), str(RigRuedasNode)+".Execute")

	RadiusNode = app.AddICENode("GetDataNode", IceTreeRIG)
	app.SetValue(str(RadiusNode) +".reference", cvradius, "")
	app.ConnectICENodes(str(RigRuedasNode)+".Radius", str(RadiusNode)+".value")

	DirectionNode = app.AddICENode("GetDataNode", IceTreeRIG)
	app.SetValue(str(DirectionNode)+".reference", DIR.Name, "")
	app.ConnectICENodes(str(RigRuedasNode)+".Direction_Control", str(DirectionNode)+".outname")

	RotationNode = app.AddICENode("GetDataNode", IceTreeRIG)
	app.SetValue(str(RotationNode)+".reference", Cv.Name, "")
	app.ConnectICENodes(str(RigRuedasNode)+".Rotation_Control", str(RotationNode)+".outname")
	
	app.AddPortToICENode(str(EXECUTErot)+".port" + str(EXECUTErotPort), "siNodePortDataInsertionLocationAfter")
def AddPositionCompounds(IceTreeRIG,EXECUTEposport,element,EXECUTEpos):
	PosRaycastnode = app.AddICECompoundNode("PC_RAYCAST_POSTION", IceTreeRIG)
	app.ConnectICENodes(str(EXECUTEpos)+".port" + str(EXECUTEposport), str(PosRaycastnode)+".Execute")
	
	raycastSelfnode = app.AddICENode("GetDataNode", IceTreeRIG)
	app.SetValue(str(raycastSelfnode) +".reference", element.Name, "")
	app.ConnectICENodes(str(PosRaycastnode)+".DIRECTION_WHEEL", str(raycastSelfnode)+".outname")

	raycastNullnode = app.AddICENode("GetDataNode", IceTreeRIG)
	app.SetValue(str(raycastNullnode) +".reference", element.Name[:2]+"_Raycast", "")
	app.ConnectICENodes(str(PosRaycastnode)+".RAYCAST_POS", str(raycastNullnode)+".outname")
	
	app.AddPortToICENode(str(EXECUTEpos)+".port" + str(EXECUTEposport), "siNodePortDataInsertionLocationAfter")
def ApplyRaycast(DIRECTION_WHEELS,IceTreeRIG,EXECUTEposport):
	EXECUTEpos = app.AddICENode("ICENodes\\ExecuteNode.Preset", IceTreeRIG)		
	app.ConnectICENodes(str(IceTreeRIG)+".Port2", str(EXECUTEpos)+".execute")
	for element in DIRECTION_WHEELS:
		AddPositionCompounds(IceTreeRIG,EXECUTEposport,element,EXECUTEpos)				
		EXECUTEposport = EXECUTEposport + 1
		
	COMPOUND_LIST = app.EnumElements(str(IceTreeRIG)+".DescendantNodes")
	POSITION_COMPOUNDS = []
	
	for element in COMPOUND_LIST:
		if element.Name != "ROTATION_WHEELS":
			POSITION_COMPOUNDS.append(element.FullName)
			
	POSITION_RAYCAST = app.CreateICECompoundNode(POSITION_COMPOUNDS,"POSITION_RAYCAST")
