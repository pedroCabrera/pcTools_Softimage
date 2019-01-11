import win32com.client , os , Tools , struct
from win32com.client import constants as c
from Tools import *

XSIToolkit = win32com.client.Dispatch( 'XSI.UIToolkit' )
import Tools
reload ( Tools )
app = Application

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "PEDRITO"
	in_reg.Name = "PC_Basic_Tools"
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("PC_Instances_To_Model","PC_Instances_To_Model")
	in_reg.RegisterCommand('PC_ConvertModelsToNulls','PC_ConvertModelsToNulls')
	in_reg.RegisterCommand("PC_Nurbs_To_Curves","PC_Nurbs_To_Curves")
	in_reg.RegisterCommand("PC_Curve_By_Nulls","PC_Curve_By_Nulls")
	in_reg.RegisterCommand("PC_Custom_Thickness","PC_Custom_Thickness")
	in_reg.RegisterCommand("PC_Multi_Compound_Exporter","PC_Multi_Compound_Exporter")
	in_reg.RegisterCommand("PC_Multi_Model_Exporter","PC_Multi_Model_Exporter")
	in_reg.RegisterCommand("PC_Multi_Model_Importer","PC_Multi_Model_Importer")
	in_reg.RegisterCommand("PC_Create_Point_Cloud_From_Positions","PC_Create_Point_Cloud_From_Positions")
	in_reg.RegisterCommand("PC_Set_Particle_Colored_Shape","PC_Set_Particle_Colored_Shape")
	#RegistrationInsertionPoint - do not remove this line
	
	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	app.LogMessage(str(strPluginName) + str(" has been unloaded."),c.siVerbose)
	return true
	
def PC_ConvertModelsToNulls_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Curve_By_Nulls_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Nurbs_To_Curves_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Custom_Thickness_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Multi_Compound_Exporter_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Multi_Model_Exporter_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	print oCmd.Arguments
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Multi_Model_Importer_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	print oCmd.Arguments
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Create_Point_Cloud_From_Positions_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Instances_To_Model_Init(in_ctxt):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true
def PC_Set_Particle_Colored_Shape_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true

def PC_Instances_To_Model_Execute( ):
	sel = app.Selection
	count = app.Selection.Count
	selection = [sel[i] for i in range(count) if str(app.ClassName(sel[i])) == 'Model' and sel[i].ModelKind == 2]
	for i in selection:
	    d = app.Duplicate("B:"+str(i.InstanceMaster))
	    app.MatchTransform(d, i)
	    if i.Parent.Name != app.ActiveProject.ActiveScene.Root.Name:
	        app.ParentObj(i.Parent, d)
	    app.DeleteObj(i)
def PC_ConvertModelsToNulls_Execute( ):
	Selection = app.Selection
	Models = []
	Nulls = []
	for element in Selection:
		if element.Type == '#model':
			Models.append(element)
	for element in Models:
		Children = []
		for e in  element.Children:
			Children.append(e)
		Null =app.GetPrim("Null")
		Children.append(Null)
		Nulls.append(Null)
		Parent = [Null]
		Parent.append(element.Parent)
		app.ParentObjects(Children)
		app.ParentObjects(Parent)
		X , Y , Z = element.Parameters('posx') , element.Parameters('posy') , element.Parameters('posz')
		name = element.Parameters('name')
		NX , NY , NZ = Null.Parameters('posx') , Null.Parameters('posy') , Null.Parameters('posz')
		Nname = Null.Parameters('name')
		NX.Value = X.Value
		NY.Value = Y.Value
		NZ.Value = Z.Value
		Nname.Value = name.Value + '_Null'
	app.CreateGroup('New Nulls From Models',Nulls)
	D = MsgBox('Delete Original Models?','Delete')
	if D == 1:
		app.DeleteObj(Models)
		
def PC_Nurbs_To_Curves_Execute(  ):
	Application.LogMessage("PC_Nurbs_To_Curves_Execute called",c.siVerbose)
	Options=['U','V','ALL']
	XSIDialog =XSIFactory.CreateObject("XSIDial.XSIDialog")
	Objects = app.Selection
	Nurbs =[]
	for Object in Objects:
		if Object.Type == 'surfmsh':
			Nurbs.append(Object)
	if Nurbs == []:
		print 'Select At least One Nurbs'
	else:
		B = XSIDialog.Combo( 'Select Type', Options )
		if B == 0:
			option = 'u'
		elif B == 1:
			option ='v'
		else:
			option = 'All'
		if B != -1:
			a=XSIFactory.CreateObject('CustomColor')
			Color = app.InspectObj(a,'select curve color','color',4)
			CR,CG,CB= a.parameters(0),a.parameters(1),a.parameters(2)
			r,g,b=CR.Value,CG.Value,CB.Value
			if Color != True:
				for Nurb in Nurbs:
					if option == 'All':
						CVops=[]
						cv1 =app.ApplyGenOp("CrvExtract", "", Nurb.fullname +'.knotcrvv[*]')
						cv2 =app.ApplyGenOp("CrvExtract", "", Nurb.fullname +'.knotcrvu[*]')
						CVops.append(cv1)
						CVops.append(cv2)
						for CV in CVops:
							for element in CV:
								cv = element.parent.parent
								app.MakeLocal(cv.name+'.display', "siDefaultPropagation")
								cv.name = Nurb.name + '_CV_1'
								D = cv.Properties('Display')
								R,G,B = D.Parameters('wirecolorr'),D.Parameters('wirecolorg'),D.Parameters('wirecolorb')
								R.Value,G.Value,B.Value = r,g,b
								app.ParentObj(Nurb, cv )
					else:
						cvop=app.ApplyGenOp("CrvExtract", "", Nurb.fullname +'.knotcrv' + option + '[*]','','','')
						for element in cvop:
							cv = element.parent.parent
							app.MakeLocal(cv.name+'.display', "siDefaultPropagation")
							cv.name = Nurb.name + '_CV_1'
							D = cv.Properties('Display')
							R,G,B = D.Parameters('wirecolorr'),D.Parameters('wirecolorg'),D.Parameters('wirecolorb')
							R.Value,G.Value,B.Value = r,g,b
							app.ParentObj(Nurb, cv )
	return true
def PC_Curve_By_Nulls_Execute(  ):
	Controlls = app.Selection
	parent = Application.ActiveProject.ActiveScene.Root
	PPG = Curve_By_Nulls_InitialPPG()
	if PPG != None:
		type,close = PPG
		if type == 2:
			CV = Curve_By_Nulls_CreateCurveFromNulls(parent,Controlls,"CV",close,1)
			Application.ApplyGenOp("CrvFit", "", CV, 0, "siPersistentOperation", "siHideGenOpInputs", "")
		else:
			CV = Curve_By_Nulls_CreateCurveFromNulls(parent,Controlls,"CV",close,type)
		Curve_By_Nulls_FIRSTPPG()	
	return CV
	
def PC_Custom_Thickness_Execute(  ):

	Application.LogMessage("PC_Custom_Thickness_Execute called",c.siVerbose)
	O= app.Selection
	PolyIndex =[]
	for o in O:
		if o.Type == 'polySubComponent':
			subComponent = o.SubComponent
			Object = subComponent.Parent3DObject
			selectedPolygonIndex = subComponent.ElementArray
			PolyIndex.append(selectedPolygonIndex)
		elif o.Type == 'polymsh':
			Object = o
			PolyIndex = 'All'
		ICETree= app.ApplyIceOp('PC_Custom Thickness',o)
		if PolyIndex == 'All':
			Compound=app.AddICENode("GetDataNode", ICETree)
			app.SetValue(str(Compound)+'.reference', "self.PolygonIndex", "")
			app.ConnectICENodes(str(ICETree)+'.PC_Custom_Thickness.Polygon_Index', str(Compound)+'.value')
		else:
			Compound=app.AddICENode("StringToArray", ICETree)
			PolyIndex = str(PolyIndex).replace('[','').replace(']','').replace('(','').replace(')','')
			app.SetValue(str(Compound)+'.Value_string', str(PolyIndex))
			app.ConnectICENodes(str(ICETree)+'.PC_Custom_Thickness.Polygon_Index', str(Compound)+'.Result')
			app.SetValue(str(ICETree)+'.PC_Custom_Thickness.Duplicate_Polygons', False)
		app.InspectObj(ICETree,'','',3)
	app.ActivateObjectSelTool()
	# 
	return true

def PC_Multi_Compound_Exporter_Execute( ):
	app.LogMessage("PC_Multi_Compound_Exporter_Execute called",c.siVerbose)
	N = Application.Selection

	if len(N)==0:
		app.LogMessage ('Select at least 1 Valid Compound',2)
	else:
		###Create Property And Parameters###	
		prop = app.ActiveSceneRoot.AddProperty('CustomProperty',False,'Compound Properties')
		newname = prop.addParameter3('Set New Name',11,False,'','',False)
		name = prop.addParameter3('CompoundName',8)
		newcategory = prop.addParameter3('Set New Category',11,False,'','',False)
		category = prop.addParameter3('Category',8)
		newtask = prop.addParameter3('Set New Task',11,False,'','',False)
		task = prop.addParameter3('Task',8)
		export = prop.addParameter3('export',11,False,'','',False)
		path = prop.addParameter3('Path',8)
		r,g,b = prop.addParameter3('R',5),prop.addParameter3('G',5),prop.addParameter3('B',5)
		#####PPG Layout And Logic######
		PPG=prop.PPGLayout
		PPG.AddGroup('Name')
		PPG.AddRow()
		nn = PPG.AddString('CompoundName','Name',0)
		snn = PPG.AddItem('Set_New_Name','Active')
		snn.WidthPercentage = 20
		nn.WidthPercentage = 75
		PPG.EndRow()
		PPG.EndGroup()
		PPG.AddGroup('Category')
		PPG.AddRow()
		nc = PPG.AddString('Category','Category',0)
		snc = PPG.AddItem('Set_New_Category','Active')
		snc.WidthPercentage = 20
		nc.WidthPercentage = 75
		PPG.EndRow()
		PPG.EndGroup()
		PPG.AddGroup('Task')
		PPG.AddRow()
		nt = PPG.AddString('Task','Task',0)
		snt = PPG.AddItem('Set_New_Task','Active')
		snt.WidthPercentage = 20
		nt.WidthPercentage = 75
		PPG.EndRow()
		PPG.EndGroup()
		PPG.AddGroup('Export')
		PPG.AddRow()
		PPG.AddItem('export','Export')
		PPG.addItem('Path','Path',c.siControlFolder)
		PPG.EndRow()
		PPG.EndGroup()
		PPG.AddColor('R','',True)
		PPG.Language = "Python"
		######
		###Do it####
		Cancelado =app.InspectObj(prop,'','Compound Properties',4,False)
		if not Cancelado:
			for n in N:
				Cp = Application.GetICECompoundProperties(n)
				Name = name.Value if newname.value == True else Cp[0]
				Cat = category.Value if newcategory.Value == True else Cp[1]
				Task = task.Value if newtask.Value == True else Cp[2]

				rgb = (b.Value*255,g.Value*255,r.Value*255)
				color =  struct.pack('BBB',*rgb).encode('hex')
				print Name + ' : ' + Cat + ' : ' +Task
				#app.EditICECompoundProperties(n, Name, Cat, Task)
				app.EditICECompoundProperties(n, Name, Cat, Task, "", "", "", "", "", "", "", color, "", "")
				if export.value == True:
					print path.value
					app.ExportICECompoundNode(n, path.value + '\\' + Name + '.xsicompound')
		app.DeleteObj(prop)


	return true
def PC_Multi_Model_Exporter_Execute(  ):

	Application.LogMessage("PC_Multi_Model_Exporter_Execute called",c.siVerbose)
	# 
	Selection = app.Selection
	if len(Selection) > 0:
		prop = app.ActiveProject.ActiveScene.Root.Addproperty('CustomProperty', False , 'Ruta')
		prop.addParameter3('Ruta Export',8)
		Layout = prop.PPGLayout
		Layout.addItem('Ruta_Export','Ruta_Export',c.siControlFolder)
		cancelado = app.InspectObj(prop,'','RUTA',4,False )
		if not cancelado:
			Ruta = prop.parameters('Ruta_Export').Value
			print Ruta
			for i in Selection:
				app.ExportModel(i.name, str(Ruta)+"\\"+str(i.name)+'.emdl', "", "")
		app.DeleteObj(prop)	# 
	else:
		app.LogMessage('Select at least one Valid Object',2)
	return true
def PC_Multi_Model_Importer_Execute(  ):

	Application.LogMessage("PC_Multi_Model_Importer_Execute called",c.siVerbose)

	prop = app.ActiveProject.ActiveScene.Root.Addproperty('CustomProperty', False , 'Ruta')
	for i in ['Path','Folders','Files','Import']:
		prop.addParameter3(i,8)
	Mimporter =  Application.GetCommandByScriptingName('ImportModel')
	for i in Mimporter.Arguments:
		TEST = [True for match in ['Parent','Reference','ShareOptions']  if match in str(i)]
		if TEST:
			if type(i.Value) is bool:
				prop.addParameter3('M'+str(i),11,0,0,1,False,False)
			elif type(i.Value) is int:
				prop.addParameter3('M'+str(i),8,'65535')
				prop.addParameter3('M'+str(i)+'info',8,'Share all objects: Image sources/clips, materials and material libraries, layers and partitions')
			else:
				prop.addParameter3('M'+str(i),8)
	Oimporter =  Application.GetCommandByScriptingName('OBJImport')
	for i in Oimporter.Arguments:
		TEST = [True for match in ['FileName']  if match in str(i)]
		if not TEST:
			if type(i.Value) is bool:
				v = 1
				if str(i.Name) == 'UserNormal':
					v = 0
				prop.addParameter3('O'+str(i),11,v,0,1,False,False)
			elif type(i.Value) is int:
				if str(i) == 'Group':
					prop.addParameter3('O'+str(i),8,'1')
				if str(i) == 'hrc':
					prop.addParameter3('O'+str(i),8,'0')
			else:
				prop.addParameter3(str(i),8)
	dotImporter = Application.GetValue('dotXSIImportOptions')
	prop.addParameter3('dotParent',8)
	for dot in Application.EnumElements(dotImporter):
		if 'Path' not in dot.Name:
			prop.addParameter3('dot'+str(dot.Name),11,dot.Value,0,1,False,False)

	Layout = prop.PPGLayout

	P=Layout.addItem('Path','Path',c.siControlFolder)
	P.SetAttribute(c.siUINoLabel,True)

	Layout.AddGroup('Files')
	Layout.AddRow()
	Layout.AddGroup('Folders')
	FO=Layout.addItem('Folders','Folders',c.siControlListBox)
	Layout.EndGroup()
	Layout.AddGroup('Files')
	FI=Layout.addItem('Files','Files',c.siControlListBox)
	Layout.EndGroup()
	for i in [FO,FI]:
		i.SetAttribute(c.siUICY,200)   
		i.SetAttribute(c.siUIMultiSelectionListBox,True)
		i.SetAttribute(c.siUINoLabel,True)  
	Layout.EndRow()
	Layout.EndGroup()

	Layout.AddRow()
	Layout.AddSpacer(2,0)
	Layout.AddButton('AddToList')
	Layout.AddButton('RemoveFromList')
	Layout.EndRow()

	Layout.AddGroup('Import Paths')
	IMPORT=Layout.addItem('Import','',c.siControlListBox)
	IMPORT.SetAttribute(c.siUICY,100) 
	IMPORT.SetAttribute(c.siUINoLabel,True)  
	IMPORT.SetAttribute(c.siUIMultiSelectionListBox,True)
	Layout.EndGroup()

	Layout.AddTab('Models')
	for i in Mimporter.Arguments:
		TEST = [True for match in ['Parent','Reference','ShareOptions']  if match in str(i)]
		if TEST:
			if type(i.Value) is bool:
				Layout.addItem('M'+str(i),str(i),c.siControlCheck)
			elif type(i.Value) is int:
				I=Layout.addItem('M'+str(i),str(i),c.siControlCombo)
				I.UIItems = ['None','0','Images','1','Materials','2','Layers','4','Partitions','8','All','65535']
				II = Layout.addItem('M'+str(i)+'info','info',c.siControlStatic)
				II.SetAttribute(c.siUICX,350)
				II.SetAttribute(c.siUICY,200)

			else:
				Layout.AddRow()
				Layout.addItem('M'+str(i),str(i),c.siControlString)
				Layout.AddButton('MPickParent','PickParent')
				Layout.EndRow()
	Layout.AddTab('Objs')
	for i in Oimporter.Arguments:
		TEST = [True for match in ['FileName']  if match in str(i)]
		if not TEST:
			if type(i.Value) is int:
				if str(i) == 'Group':
					Layout.AddGroup('Group')
					I=Layout.addItem('O'+str(i),str(i),c.siControlRadio)
					I.UIItems = ['Import as clusters','0','Import as objects','1']
					I.SetAttribute(c.siUINoLabel,True)  
					Layout.EndGroup()
				if str(i) == 'hrc':
					Layout.AddGroup('Hierachy')
					I=Layout.addItem('O'+str(i),str(i),c.siControlRadio)
					I.UIItems =  ['No Hierachy','0','Null as Parent','1','Model as Parent','2']
					I.SetAttribute(c.siUINoLabel,True)  
					Layout.EndGroup()
			elif str(i.Name) == 'UserNormal':
				Layout.addItem('O'+str(i),'Import Normals as UserNormal',c.siControlCheck)
	for i in Oimporter.Arguments:
		if type(i.Value) is bool and str(i) != 'UserNormal':
			if 'Material' in str(i):
				Layout.AddGroup('Material')
			Layout.addItem('O'+str(i),str(i),c.siControlCheck)
			if 'UVwrapping' in str(i):
				Layout.EndGroup()
	Layout.AddTab('dotXsi')
	Layout.AddRow()
	Layout.addItem('dotParent','Parent',c.siControlString)
	Layout.AddButton('dotPickParent','PickParent')
	Layout.EndRow()
	for dot in Application.EnumElements(dotImporter):
		if 'Path' not in dot.Name:
			Layout.addItem('dot'+dot.Name.replace(' ','_').replace('(','_').replace(')','_'),dot.Name,c.siControlCheck)

	Layout.Language = 'Python'
	Layout.Logic = MultiImporterLogic

	def Multi_Model_Importer_Inspect ():
		cancelado = app.InspectObj(prop,'','RUTA',4,False)
		if not cancelado:
			Index = [i*2 for i in range (len(IMPORT.UIItems)/2)]
			IMPORTOBJS = [list(IMPORT.UIItems)[a] for a in Index]
			if len(IMPORTOBJS) > 0:
				Margs= []
				for i in Mimporter.Arguments:
					try:
						Margs.append(prop.Parameters('M'+str(i)).Value)
					except:
						continue
				Oargs= []
				for i in Oimporter.Arguments:
					try:
						Oargs.append(prop.Parameters('O'+str(i)).Value)
					except:
						continue
				dotargs = []		
				for dot in Application.EnumElements(dotImporter):
					if 'Path' not in dot.Name:
						dot.Value = prop.Parameters('dot'+dot.Name.replace(' ','_').replace('(','_').replace(')','_')).Value
				for obj in IMPORTOBJS:
					fileName, fileExtension = os.path.splitext(obj)
					if fileExtension == '.emdl':
						objs = app.ImportModel(obj, Margs[0], Margs[1],'', '', Margs[2], '' )
					if fileExtension.lower() == '.obj':
						objs = app.ObjImport(obj, int(Oargs[0]), int(Oargs[1]), Oargs[2],  Oargs[3], Oargs[4], Oargs[5])
					if fileExtension ==  '.xsi' :
						objs = app.ImportDotXSI(obj,prop.Parameters('dotParent').Value)
					if fileExtension == '.fbx':
						objs = app.FBXImport(obj)
			else:
				Message = XSIToolkit.MsgBox('No item added to import list',5 ,'Error')
				if Message == 4:
					Multi_Model_Importer_Inspect()
		return 

	Multi_Model_Importer_Inspect()

	app.DeleteObj(prop)	

def PC_Create_Point_Cloud_From_Positions_Execute(  ):

	#Application.LogMessage("PC_Create_Point_Cloud_From_Positions_Execute called",c.siVerbose)
	OBJ = []
	O = app.Selection
	for o in O:
		OBJ.append(o)
		ALLCOLORS = []
		GROUPS = []

	##Find Diffetent Colors##
	for o in OBJ:
		C = o.Properties('Display')
		R , G , B = C.Parameters('wirecolorr').Value , C.Parameters('wirecolorg').Value , C.Parameters('wirecolorb').Value
		COLOR=[R,G,B]
		if COLOR not in ALLCOLORS:
			ALLCOLORS.append(COLOR)
			
	##Create Group for each different Color##		
	for color in ALLCOLORS:
		Select = []
		CR , CG , CB = color[0] , color[1] , color[2]
		for o in OBJ:
			D= o.Properties('Display')
			R , G , B = D.Parameters('wirecolorr').Value , D.Parameters('wirecolorg').Value , D.Parameters('wirecolorb').Value
			if R == CR and G == CG and B == CB:
				Select.append(o)
		app.SelectObj(Select)
		Group = app.CreateGroup()
		GROUPS.append(Group)
		app.DeselectAll()
		
	##Create PoinCloud And ICE TREE##
	PCloud = app.GetPrim("PointCloud", "PC_Point Cloud from Positions", "", "")
	ICETree = app.ApplyOp("ICETree", PCloud)
	app.SetValue(str(ICETree)+'.Name', "PC_Positions to Point Cloud", "")

	Execute = app.AddICENode("$XSI_DSPRESETS\\ICENodes\\ExecuteNode.Preset", ICETree)
	app.ConnectICENodes(str(ICETree) +'.port1', str(Execute)+'.execute')
	port , c = 0 , -1

	Compounds = []
	ColorCompounds = []
	Compounds.append(Execute)
	
	for g in GROUPS:
		Positions = []
		Rotations = []
		for a in g.Members:
			X , Y , Z = a.Parameters('posx').Value , a.Parameters('posy').Value , a.Parameters('posz').Value
			RX , RY , RZ = a.Parameters('rotx').Value , a.Parameters('roty').Value , a.Parameters('rotz').Value
			pos = [X,Y,Z]
			rot = [RX,RY,RZ]
			Positions.append(pos)
			Rotations.append(rot)
		Pos = str(Positions).replace('[','').replace(']','').replace('(','').replace(')','')
		Rot = str(Rotations).replace('[','').replace(']','').replace('(','').replace(')','')
		c , port = c + 1 , port + 1
		R,G,B = ALLCOLORS[c][0],ALLCOLORS[c][1],ALLCOLORS[c][2]
		if port > 1:
			Application.AddPortToICENode(str(Execute)+'.port'+str(port-1), "siNodePortDataInsertionLocationAfter")
		##Add Compounds##
		Addpoint = app.AddICENode("$XSI_DSPRESETS\\ICENodes\\AddPointNode.Preset", ICETree)
		PosArray = app.AddICENode("StringToArray", ICETree)
		RotArray = app.AddICENode("StringToArray", ICETree)
		SetColor = app.AddICECompoundNode("PC_Set Particle Colored Shape", ICETree)
		SetOri = app.AddICECompoundNode("PC_Orientate Points from Array", ICETree)
		##Make Conections##
		app.ConnectICENodes(str(Execute) +'.port'+ str(port), str(Addpoint)+'.add')
		app.ConnectICENodes(str(Addpoint)+'.positions1', str(PosArray)+'.Result')
		app.ConnectICENodes(str(SetOri)+'.New_Pos', str(PosArray)+'.Result')
		app.ConnectICENodes(str(SetOri)+'.Rotation_Array', str(RotArray)+'.Result')
		app.ConnectICENodes(str(Addpoint)+'.oncreation1', str(SetColor)+'.Execute')
		
		app.AddPortToICENode(str(Addpoint)+'.oncreation1', "siNodePortDataInsertionLocationAfter")
		app.ConnectICENodes(str(Addpoint)+'.oncreation2', str(SetOri)+'.Execute_on_Emit')

		##Set Init Values##
		app.SetValue(str(PosArray)+'.Value_string', Pos, "")
		app.SetValue(str(RotArray)+'.Value_string', Rot, "")
		app.SetValue(str(SetColor)+'.Color_red', R)
		app.SetValue(str(SetColor)+'.Color_green', G)
		app.SetValue(str(SetColor)+'.Color_blue', B)
		
		Compounds.append(Addpoint)
		Compounds.append(PosArray)
		Compounds.append(SetColor)
		Compounds.append(RotArray)
		ColorCompounds.append(SetColor)
		
	COMPOUND = app.CreateICECompoundNode(Compounds,'Init Groups')
	for c in ColorCompounds:
		color = app.AddExposedParamToICECompoundNode(str(c)+'.Color', COMPOUND)
		size = app.AddExposedParamToICECompoundNode(str(c)+'.Size', COMPOUND)
		shape = app.AddExposedParamToICECompoundNode(str(c)+'.Shape', COMPOUND)
		custom = app.AddExposedParamToICECompoundNode(str(c)+'.Use_Custom', COMPOUND)
		ref = app.AddExposedParamToICECompoundNode(str(c)+'.Reference', COMPOUND)
		index = app.AddExposedParamToICECompoundNode(str(c)+'.Index', COMPOUND)
		app.CreateLayoutGroupInICECompoundNode(COMPOUND, [color.Name, size.Name, shape.Name,custom.Name,ref.Name,index.Name], "")
	app.InspectObj(COMPOUND)
	app.DeleteObj(GROUPS)
	return true
def PC_Set_Particle_Colored_Shape_Execute(  ):

	Application.LogMessage("PC_Set_Particle_Colored_Shape called",c.siVerbose)
	
	P = app.PickElement(c.siPointFilter)[2]
	app.SelectObj(P)
	O = app.Selection
	for o in O:
		if o.Type == 'pntSubComponent':
			subComponent = o.SubComponent
			Object = subComponent.Parent3DObject
			selectedPointIndex = subComponent.ElementArray
			print selectedPointIndex
			
	ICETree = Application.ApplyICEOp("PC_Set Particle Colored Shape", Object)
	PointIndex = str(selectedPointIndex).replace('(','').replace(')','').replace('[','').replace(']','')
	Compound= app.AddICECompoundNode("PC_Test Particle Index In String Array",ICETree)
	app.SetValue(str(Compound)+'.Value_string', str(PointIndex))
	app.ConnectICENodes(str(ICETree)+'.PC_Set_Particle_Colored_Shape.Filter', str(Compound)+'.Result')
	app.InspectObj(ICETree)
	return true
