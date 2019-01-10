import win32com.client
from win32com.client import constants as c
import sys
import Tools
import CarRigTools as CarRigT
reload( Tools )
reload( CarRigT )

app = Application
null = None
false = 0
true = 1
def XSILoadPlugin( in_reg ):
	in_reg.Author = "PEDRITO"
	in_reg.Name = "PC_Rigging_Tools"
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("PC_Auto_Rigging_Car","PC_Auto_Rigging_Car")
	in_reg.RegisterCommand("PC_Path_Rig","PC_Path_Rig")
	#RegistrationInsertionPoint - do not remove this line
	
	oPrefs = app.Preferences
	oAutoInspect = oPrefs.SetPreferenceValue("Interaction.autoinspect", False)
	

	return true
def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),c.siVerbose)
	return true

def PC_Auto_Rigging_Car_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true
def PC_Path_Rig_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true

def PC_Auto_Rigging_Car_Execute(  ):

	Application.LogMessage("PC_Auto_Rigging_Car_Execute called",c.siVerbose)
	
	##Start by pikking the geometry groups
	PickTheBody = Tools.MsgBox("Pick the Body Group","PICK THE BODY")
	if PickTheBody != 2 and  3:	
		BodyGroup = Tools.PickGroup()
		XSIZE = Tools.GetBoundingGroupSize(BodyGroup)
		PickTheWheels = Tools.MsgBox("Pick the Wheels GROUP","PICK THE WHEELS")
		if PickTheWheels != 2 and 3:
			WheelGroup = Tools.PickGroup()
			BodyGroupObjs=BodyGroup.Members
			WheelGroupObjs=WheelGroup.Members
			
			#Create A Null for the Rig whith an ice tree
			RIGMASTER = CarRigT.RigMasterNull("CAR_RIG",True,True,True)
			RIG = RIGMASTER[0]
			IceTreeRIG = RIGMASTER[1]
			EXECUTErot = RIGMASTER[2]
			EXECUTErotPort = 1
			
			#Create a Null fot MoveControl and one for the geometry
			CarMove = CarRigT.CarMovController(RIG,XSIZE,BodyGroupObjs)
			CARmov = CarMove[0]
			CARBodyGeo = CarMove[1]
				
			DIRECTION_WHEELS = []
			
			for Obj in WheelGroupObjs:
				RotationControls = CarRigT.CreateRotationControl(Obj,DIRECTION_WHEELS,CARmov)
				DIR = RotationControls[0]
				Cv = RotationControls[1]
				#Add the IceCompounds to rotate the wheel
				#CarRigT.AddRotationCompounds(IceTreeRIG,EXECUTErotPort,DIR,Cv,EXECUTErot)
				#EXECUTErotPort = EXECUTErotPort + 1
				
			#Create a compound with all the Rotatio Nodes	
			#ROTATION_WHEELS = app.CreateICECompoundNode(str(IceTreeRIG)+".*","ROTATION_WHEELS")
			
			#Set the Raycast Mode
			PickTheGround = Tools.MsgBox("Do you want to constrain on a surface or various?Just Pick a GROUP whit IT!","SELECT A GROUP whit SURFACE TO CONSTRAIN")
			if PickTheGround != 2 and 3:
				Surface = Tools.PickGroup()
				EXECUTEposport = 1
				rycst = CarRigT.RAYCAST_SURRFACE(DIR,CARmov,Surface)#Create a surface, a lattice whith clusters ald nulls and an ICETREE
				CarRigT.ApplyRaycast(DIRECTION_WHEELS,IceTreeRIG,EXECUTEposport)#Create the nodes to drive the wheels position with the nulls Raycast
				Tools.ApplySurfaceConstr(CARBodyGeo,rycst)
				#Translate all the body objs to the inial ZEROZERO because of the surfcnstr
				for Obj in BodyGroupObjs:
					Application.Translate(Obj, 0, 0, 0,"siAbsolute","siGlobal")
					
			#Create a Model with the car and groups	
			L=[RIG,WheelGroup,BodyGroup,Surface]
			s=app.SelectObj(L)
			RIG_mdl=app.CreateModel(s, "CAR_RIG_MDL", "", "")
		return true
	# 
	return true
def PC_Path_Rig_Execute(  ):
	Application.LogMessage("PC_Path_Rig_Execute called",c.siVerbose)
	def Groups (curve,Listaobj,RIG):
		GRP_Curve = app.CreateGroup("GRP_Curve",curve,RIG)
		GRP_Cnstr = app.CreateGroup("GRP_Constrained",Listaobj,RIG)
		app.CopyPaste(GRP_Curve, "", RIG, 1)
		app.CopyPaste(GRP_Cnstr, "", RIG, 1)
	def Layout(prop):
		oLayout =prop.PPGLayout
		oLayout.Clear()
		oLayout.Language = "Python"
		oLayout.AddRow();
		oLayout.AddItem("Active")
		oLayout.AddItem("Lock")
		oLayout.EndRow();
		oLayout.AddItem("path__")
		oLayout.AddItem("offset")
		oLayout.AddRow();
		oLayout.AddItem("tangency")
		oLayout.AddItem("up_vector")
		oLayout.EndRow();
		oLayout.AddRow();
		oLayout.AddGroup("Tangency",True,50)
		oLayout.AddRow();
		oLayout.AddButton("tX","X")
		oLayout.AddButton("tY","Y")
		oLayout.AddButton("tZ","Z")
		oLayout.EndRow();
		oLayout.AddRow();
		oLayout.AddButton("tnX","-X")
		oLayout.AddButton("tnY","-Y")
		oLayout.AddButton("tnZ","-Z")
		oLayout.EndRow();
		oLayout.EndGroup();
		oLayout.AddGroup("UpVector",True,50)
		oLayout.AddRow();
		oLayout.AddButton("uX","X")
		oLayout.AddButton("uY","Y")
		oLayout.AddButton("uZ","Z")
		oLayout.EndRow();
		oLayout.AddRow();
		oLayout.AddButton("unX","-X")
		oLayout.AddButton("unY","-Y")
		oLayout.AddButton("unZ","-Z")
		oLayout.EndRow();
		oLayout.EndGroup();
		oLayout.EndRow();
		oLayout.AddRow();
		oLayout.AddButton("INSPECT","INSPECT")
		oLayout.AddButton("RERIG","RERIG")
		oLayout.AddButton("DELETE_RIG","DELETE_RIG")
		oLayout.AddButton("INVERT","INVERT_CURVE")
		oLayout.EndRow();
		oLayout.Logic = Tools.PathRigLogic
	def PC_Path_Rig(Lista):
		VARS=[]
		if not Lista:
			XSIUIToolkit.MsgBox("Por Favor seleccione al menos un objeto",0,"SELECCIONE ALGUN OBJETO")
		else:
			message = XSIUIToolkit.MsgBox("Pick a curve to be the path",1,"SELECT THE PATH")
			print message
			if message == 1:
				RIG = Application.ActiveSceneRoot.AddModel("","PC_Path_Rig")
				app.SetValue(str(RIG) + ".visibility.viewvis",False)
				pickelement = app.PickElement("curve","pick a curve for the path","")
				Curve = pickelement.Value("PickedElement")
				oPrefs = Application.Preferences
				oAutoInspect = oPrefs.SetPreferenceValue("Interaction.autoinspect", False);
				#Añadimos Custom property and params
				rigProp = RIG.AddProperty ("CustomProperty", False, "PC_Path_Rig")
				pActive = rigProp.AddParameter3("Active",11,True)
				pLock = rigProp.AddParameter3("Lock",11,True)
				pPath = rigProp.AddParameter3("path_%",4,0,0,100)
				app.EditParameterDefinition(pPath, "path_%", 4, 0, 300, 0, 100, "path_%", "path_%")
				pOffset = rigProp.AddParameter3("offset",4,1,-100,100)
				pTangency = rigProp.AddParameter3("tangency",11,True)
				pUpVector = rigProp.AddParameter3("up_vector",11,True)
				pInvert = rigProp.AddParameter3("INVERT",11,False)
				#Start Loop
				for element in Selection:
					elementkine = str(element)+".kine.pathcns"
					elementactive = str(elementkine) + ".active"
					elementlocked = str(elementkine) + ".lockcnsed"
					elementperc = str(elementkine) +".perc"#porcentaje del path
					elementtang = str(elementkine) + ".tangent"#tangencia
					elementdir = str(elementkine) +".dir"#direccion de la tangencia
					elementupv = str(elementkine)+".upvct_active"#up vector
					index = Lista.index(str(element.Name))#multiplicador del path en funcion de su indice
					offset = str(pOffset)+ "*" + "-"+ str(index) #offset para funcion
					pathexpr = str(pPath) + "+" + str(offset)#expresion para en cada path
					app.ApplyCns("Path", element, Curve, "")#Creal el path constrain
					app.SetExpr( elementperc, str(pathexpr), "")#Crea la expresion para el %
					app.SetExpr(elementtang,str(pTangency),"")#Crea la expresion para on/off tangency
					app.SetExpr(elementupv,str(pUpVector),"")#Crea la expresion para on/off UpV
					app.SetExpr(elementactive,str(pActive),"")
				Layout(rigProp)
				app.InspectObj(rigProp,"","",3)
				VARS = [Curve,RIG.Name]
		return VARS
	#codigo
	Selection = app.Selection
	Listaobj = []
	for element in Selection:
		Listaobj.append(element.FullName)
	VARS = PC_Path_Rig(Listaobj)
	if VARS != []:
		Groups(VARS[0],Listaobj,VARS[1])
		app.SelectObj(Listaobj)
	# 
	return true
