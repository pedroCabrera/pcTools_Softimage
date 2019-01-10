import win32com, sys,os,re,subprocess,shlex
from win32com.client import constants as c
app = win32com.client.Dispatch( 'XSI.Application' ).Application
XSIFactory = win32com.client.Dispatch( 'XSI.Factory' )
XSIMath = win32com.client.Dispatch( 'XSI.Math' )
XSIToolkit = win32com.client.Dispatch( 'XSI.UIToolkit' )
XSIUtils = win32com.client.Dispatch('XSI.Utils')
###
def MsgBox(message,title):
	Msg = XSIToolkit.MsgBox(message,1,title)
	return Msg
###
def PickGroup():
	PickGrp = app.PickElement("Group")
	Grp = PickGrp.Value("PickedElement")
	return Grp
###	
def GetBoundingSize(Obj):
	sizeX = []
	sizeY = []
	sizeZ = []
	oPa = Obj.ActivePrimitive.Geometry.Points.PositionArray
	sizeX.append (min(oPa[0]))
	sizeX.append (max(oPa[0]))
	sizeY.append (min(oPa[1]))
	sizeY.append (max(oPa[1]))
	sizeZ.append (min(oPa[2]))
	sizeZ.append (max(oPa[2]))
	SIZE = [sizeX,sizeY,sizeZ]
	return SIZE
###	
def GetBoundingGroupSize(Group):
	Group = Group.Members
	sizeX = []
	sizeY = []
	sizeZ = []
	for Obj in Group:
		oPa = Obj.ActivePrimitive.Geometry.Points.PositionArray
		sizeX.append (min(oPa[0]))
		sizeX.append (max(oPa[0]))
		sizeY.append (min(oPa[1]))
		sizeY.append (max(oPa[1]))
		sizeZ.append (min(oPa[2]))
		sizeZ.append (max(oPa[2]))
	SIZE = [[min(sizeX),max(sizeX)],[min(sizeY),max(sizeY)],[min(sizeZ),max(sizeZ)]]
	return SIZE
#####	
def CreateBBox(SIZE):
	BBox= app.CreatePrim("Cube", "MeshSurface")
	app.Translate(BBox.Name+".pnt[0,2,4,6]",SIZE[0][0],0,0,"siAbsolute","siGlobal")
	app.Translate(BBox.Name+".pnt[1,3,5,LAST]",SIZE[0][1],0,0,"siAbsolute","siGlobal")
	app.Translate(BBox.Name+".pnt[0,1,4,5]",0,SIZE[1][0],0,"siAbsolute","siGlobal")
	app.Translate(BBox.Name+".pnt[2,3,6,LAST]",0,SIZE[1][1],0,"siAbsolute","siGlobal")
	app.Translate(BBox.Name+".pnt[0-3]",0,0,SIZE[2][0],"siAbsolute","siGlobal")
	app.Translate(BBox.Name+".pnt[4-LAST]",0,0,SIZE[2][1],"siAbsolute","siGlobal")
	app.FreezeObj(BBox)
	return BBox
###	
def CreateNullByPose(Name,Parent,posObjx,posObjz):
	if posObjx < 0 and posObjz < 0:
		DIR = app.GetPrim("Null", "RB_" + Name,Parent)
		DIR.R=1
	elif posObjx < 0 and posObjz >0:
		DIR = app.GetPrim("Null", "RF_" + Name,Parent)
		DIR.R=1
	elif posObjx > 0 and posObjz < 0:
		DIR = app.GetPrim("Null", "LB_" + Name,Parent)
		DIR.B=1
	elif posObjx > 0 and posObjz >0 :
		DIR = app.GetPrim("Null", "LF_" + Name,Parent)
		DIR.B=1
	return DIR
###	
def CreateCurveFromNulls(parent,Controlls,name,type = 1):
	Controlls = list(Controlls)
	Controllspos = []
	if type == 3:
		if len(Controlls) == 2:
			Controlls.insert(0,Controlls[0])
			Controlls.append(Controlls[-1])
		elif len(Controlls) == 3:
			Controlls.append(Controlls[-1])
		for obj in Controlls:
			Controllspos.append(obj.Kinematics.Global.Transform.PosX)
			Controllspos.append(obj.Kinematics.Global.Transform.PosY)
			Controllspos.append(obj.Kinematics.Global.Transform.PosZ)
			Controllspos.append(1)
		
	CV = parent.AddNurbsCurve(Controllspos,"",False,type,c.siNonUniformParameterization,c.siSINurbs,name)
	
	for i,obj in enumerate(Controlls):
		CVcls = CV.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster,obj.Name+"_clstr",[i])
		app.ApplyOp("ClusterCenter", CVcls.FullName+";"+obj.FullName, 0, "siPersistentOperation", "", 0)
		print i
	return CV
####	
def AddWheelsCurves(DIR,posObjx,posObjy,radio):
	Cv = app.CreatePrim("Circle","NurbsCurve", DIR.Name[:2]+ "_WHEEL_Rot", DIR.Name)
	CVpoints = Cv.Name + ".pnt[*]"
	app.Rotate(CVpoints, 0, 90, 0)
	app.MakeLocal(str(Cv.Name)+".display")
	if posObjx < 0:
		app.Translate(CVpoints, -2, 0, 0)
		app.SetValue(str(Cv.Name)+".display.wirecolorr", True)

	else:
		app.Translate(CVpoints, 2, 0, 0)
		app.SetValue(str(Cv.Name)+".display.wirecolorb", True)
		
	cvradius = str(Cv) +".circle.radius"
	radioCv = app.SetValue(cvradius, radio)
	posCvy = app.SetValue(Cv.Name + ".kine.local.posy", posObjy , "")
	return Cv
###	
def ApplySurfaceConstr(obj,surface):
	SurfaceCnstr = app.ApplyCns("Surface", obj.Name, surface.Name, True)
	app.SetValue(obj.Name+".kine.surfcns.tangent", True)
	app.SetValue(obj.Name+".kine.surfcns.upvct_active", True)
	app.SetValue(obj.Name+".kine.surfcns.affbyori1", True)
####
def GetCustomChannels():
	DefaultChannels= ['Main','Depth','Motion','Normal','Object Labels','Pixel Coverage','Pixel Time','Raster Motion','Ambient','Ambient-Level','Diffuse','Specular','Irradiance','Reflection','Refraction','GPUAmbientOcclusion','Arnold_Alpha','Arnold_Opacity','Arnold_CPU_Time','Arnold_Ray_Count','Arnold_Point','Arnold_Pref','Arnold_Motion_Vector','Arnold_Direct_Diffuse','Arnold_Direct_Specular','Arnold_Indirect_Diffuse','Arnold_Indirect_Specular','Arnold_Emission','Arnold_Refraction','Arnold_Refraction_Opacity','Arnold_Reflection','Arnold_SSS','Arnold_Specular','Arnold_Sheen','Arnold_Texture_Time']
	CUSTOMCHANNELS=[]
	CUSTOMCHANNELSLIST=[]
	for rch in app.EnumElements('Passes.RenderOptions.Channels'):
		if rch.name not in DefaultChannels:
			CUSTOMCHANNELS.append(rch)
	for i,ch in enumerate(CUSTOMCHANNELS):
		CUSTOMCHANNELSLIST.append(ch.name)
		CUSTOMCHANNELSLIST.append(str(i))
	C=[CUSTOMCHANNELS,CUSTOMCHANNELSLIST]
	return C
####
def Get_Materials(SELECTION):
	MATERIALES = []
	for obj in SELECTION:
		if obj.Type == 'material':
				MATERIALES.append(obj)
		elif obj.Type == 'polymsh':
			for m in obj.Materials:
				MATERIALES.append(m)
		elif obj.Type == '#Group' or obj.Type == 'Partition':
			for i in app.EnumElements(obj):
				if i.Name == 'CurrentProperties':
					a= str(app.EnumElements(i))
					if a != 'None':
						print a
						for prop in app.EnumElements(i):
							if prop.Type == 'material':
								MATERIALES.append(app.EnumElements(prop)(1))
		else:
			print obj.name +' is not a valid Material'
	return MATERIALES
####
def Store_In_Channel_Basic_Tab(Layout):
	RAYTYPES= ['Primary','0','Primary and Transparency','1','Any Secondary','2','Reflection','3','Refraction','4','Shadow','5','Enviroment','6']
	COMPONENT_TYPE= ['Full Color','0','R','1','G','2','B','3','A','4']
	TYPES = ['Color','0','Shadow','1','Arnold Ambient Oclusion','2','Mental Ambient Oclusion','3','Custom ProgID','4']
	CUSTOMCHANNELSLIST = GetCustomChannels()[1]
	Layout.AddGroup('Store In Channel')
	Layout.AddRow()
	Layout.AddEnumControl('Existing_Channel',CUSTOMCHANNELSLIST,'Existing Channel',c.siControlCombo)
	new=Layout.AddItem('New_Channel','New Channel',c.siControlCheck)
	new.WidthPercentage=5
	Layout.EndRow()
	Layout.AddItem('Channel','New Channel',c.siString)
	Layout.AddRow()
	raytype=Layout.AddEnumControl('Store_with_Ray_Type',RAYTYPES,'Ray Type',c.siControlCombo)
	components = Layout.AddEnumControl('Components_to_Store',COMPONENT_TYPE,'Components',c.siControlCombo)
	Layout.EndRow()
	Layout.EndGroup()
	Layout.AddEnumControl('Store',TYPES,'Store Input',c.siControlCombo)
####
def Store_In_Channel_Color_Tab(Layout):
	Layout.AddGroup('Color')
	Layout.AddColor('ColorR','color',True)
	Layout.EndGroup()
####
def Store_In_Channel_Shadow_Tab(Layout):
	Layout.AddGroup('Shadow')
	Layout.AddItem('SHADOW_Minimum_Intensity','Minimum Intensity',c.siControlNumber)
	Layout.AddItem('SHADOW_Maximum_Intensity','Maximum Intensity',c.siControlNumber)
	Layout.AddItem('SHADOW_RGB','RGB',c.siControlCheck)
	Layout.AddItem('SHADOW_cast_on_visible_faces','Shadow cast on visible faces',c.siControlCheck)
####
def Store_In_Channel_AAO_Tab(Layout):
	Layout.AddGroup('Arnold Ambient Oclusion')
	Layout.AddItem('ASamples','Samples',c.siControlNumber)
	Layout.AddItem('ASpread','Spread',c.siControlNumber)
	Layout.AddItem('ANear','Near',c.siControlNumber)
	Layout.AddItem('AFar','Far',c.siControlNumber)
	Layout.AddItem('AFallof','Fallof',c.siControlNumber)
	Layout.AddItem('AInvert_Normals','Invert Normals',c.siControlCheck)
####
def Store_In_Channel_MAO_Tab(Layout):
	OUTPUTS = ['Occlusion Using Shading Normal','-1','Occlusion Using Bent Normals','0','Sampled Environment','1','Return Bent Normals(Wolrd Space)','2','Return Bent Normals(Object Space)','3']
	Layout.AddGroup('Mental Ambient Oclusion')
	Layout.AddItem('MSamples','Number of Samples',c.siControlNumber)
	Layout.AddItem('MSpread','Spread',c.siControlNumber)
	Layout.AddItem('MMaximum','Maximum distance',c.siControlNumber)
	Layout.AddItem('MReflective','Reflective',c.siControlCheck)
	Layout.AddEnumControl('MOutput_Mode',OUTPUTS,'Output Mode',c.siControlCombo)
	Layout.AddItem('MAlpha','Occlusion in alpha',c.siControlCheck)
####
def Store_In_Channel_CustomProgID_Tab(Layout):
	from win32com.client import constants as c
	Arnold = []
	ArnoldNames = []
	AllShaders= []
	AllShadersNames = []
	for sh in app.ShaderDefinitions :
		AllShaders.append(sh)
		if 'Arnold' in str(sh):
			if sh.Category != '':
				if int(sh.Category[-3:]) < 400:
					Arnold.append(sh)

	for i,sh in enumerate(Arnold):
		ArnoldNames.append(sh.DisplayName)
		ArnoldNames.append(str(i))
	for i,sh in enumerate(AllShaders):
		AllShadersNames.append(sh.DisplayName)
		AllShadersNames.append(str(i))

	Layout.AddGroup('Custom ProgID')
	Layout.AddEnumControl( 'AllShaders',AllShadersNames,'AllShaders',c.siControlCombo)
	Layout.AddEnumControl( 'ArnoldShaders',ArnoldNames,'ArnoldShaders',c.siControlCombo)
	Layout.AddString('CustomProgID','CustomShader')
	oItem = Layout.AddItem( "Set_Attributes", "Set Custom Shader Parameters", c.siControlTextEditor)
	oItem.SetAttribute( "Language", "Python" )
	oItem.SetAttribute(c.siUIFont, "Courier New")
	oItem.SetAttribute(c.siUIKeywords, "CustomShader Value")
	oItem.SetAttribute(c.siUIAutoComplete, "CustomShader Value");
	oItem.SetAttribute(c.siUIFontSize, 10)
	oItem.SetAttribute(c.siUIBackgroundColor, 0xf8f8f2)
	oItem.SetAttribute(c.siUIForegroundColor, 0x272822)
	oItem.SetAttribute(c.siUIHorizontalScroll, True)
	oItem.SetAttribute(c.siUIVerticalScroll, True)
	oItem.SetAttribute(c.siUILineNumbering, True)
	oItem.SetAttribute(c.siUILineNumbering, True)	
	oItem.SetAttribute(c.siUIMarginWidth, 1)
	oItem.SetAttribute("UseSpacesForTab", False)
	oItem.SetAttribute("TabSize", 4) 

	Debug = Layout.AddItem( "Get_Attributes", "Get Custom Shader Parameters", c.siControlListBox)

	Layout.EndGroup()
####
def FrameBuffer_Managers_Prop():
	PassName = '[Scene]/[Scene]_[Pass]'
	prop = app.ActiveSceneRoot.AddProperty ("CustomProperty", False, "Framebuffer Manager")
	prop.AddParameter3('Rename_Main_Framebuffer', 11,1,0,0,0)
	prop.AddParameter3('Main_Name',8,PassName,'','', True, False)
	prop.AddParameter3('Main_Ext',8,'[Framebuffer]','','', True, False)
	prop.AddParameter3('Main_Format',8,'exr','','', True, False)
	prop.AddParameter3('Set_Main_Name', 11,1,0,0,0)
	prop.AddParameter3('Set_Main_Format', 11,1,0,0,0)
	prop.AddParameter3('Extra_Name',8,PassName,'','', True, False)
	prop.AddParameter3('Extra_Ext',8,'Main','','', True, False)
	prop.AddParameter3('Extra_Format',8,'exr','','', True, False)
	prop.AddParameter3('All_Passes', 11,0,0,0,0)
	create = prop.AddParameter3('Create', 11,1,0,0,0)
	delete = prop.AddParameter3('Delete', 11,0,0,0,0)
	create.Enable(False)
	delete.Enable(False)
	return prop
####
def FrameBuffer_Managers_BasicTab(prop):
	Layout = prop.PPGLayout
	ControlCheck = c.siControlCheck
	Layout.AddTab('General')
	Layout.AddGroup('Main Framebuffer')
	Layout.AddItem('Rename_Main_Framebuffer','Rename',ControlCheck)
	Layout.AddRow()
	EN=Layout.AddString('Main_Name','Main Name')
	EEXT=Layout.AddString('Main_Ext',' ')
	EF=Layout.AddString('Main_Format',' ')
	EN.WidthPercentage = 70
	EEXT.WidthPercentage = 20
	EF.WidthPercentage = 10
	Layout.EndRow()
	Layout.EndGroup()
	Layout.AddGroup('Extra Framebuffers')
	Layout.AddRow()
	Layout.AddItem('Set_Main_Name','Set Main Name',ControlCheck)
	Layout.AddItem('Set_Main_Format','Set Main Format',ControlCheck)
	Layout.EndRow()
	Layout.AddRow()
	EN=Layout.AddString('Extra_Name','Extra Name')
	EN.WidthPercentage = 70
	EEXT=Layout.AddString('Extra_Ext',' ')
	EEXT.WidthPercentage = 20
	EF=Layout.AddString('Extra_Format',' ')
	EF.WidthPercentage = 10
	Layout.EndRow()
	Layout.EndGroup()
	Layout.AddGroup('All Passes')
	Layout.AddItem('All_Passes','All Passes',ControlCheck)
	Layout.AddItem('Create','Create',ControlCheck)
	Layout.AddItem('Delete','Delete',ControlCheck)
	Layout.EndGroup()
####
def Framebuffer_Managers_AllPasses_Tab(prop,LISTA):
	Layout=prop.PPGLayout
	Layout.AddTab('All Passes')
	for element in LISTA:
		Layout.AddItem('All_Passes_'+str(element),str(element),c.siControlCheck)
####
def FrameBuffer_Managers_PerPass_Tab(prop,LISTA):
	AllPasses=[]
	Layout=prop.PPGLayout
	scene = app.ActiveProject.ActiveScene
	for PASE in scene.Passes:
		Layout.AddTab(PASE.name)
		RCHANEL = app.EnumElements(app.EnumElements(PASE)[len(app.EnumElements(PASE)) - 1])
		for element in LISTA:
			Condition = str(element) in str(RCHANEL)
			addprop = prop.AddParameter3(str(PASE.name)+'_'+str(element), 11,Condition,0,0,0)
			Layout.AddItem(str(PASE.name)+'_'+str(element),str(element),c.siControlCheck)
####
def FrameBuffer_Managers_DoIt(prop):
	AllPasses=[]
	scene = app.ActiveProject.ActiveScene
	for Pass in scene.Passes:
		AllPasses.append(Pass)

	Layout=prop.PPGLayout
	RenameMain = prop.parameters('Rename_Main_Framebuffer').Value
	SetMainName = prop.parameters('Set_Main_Name').Value
	SetMainFormat = prop.parameters('Set_Main_Format').Value
	MainName = prop.parameters('Main_Name').Value
	MainExt=prop.parameters('Main_Ext').Value
	MainFormat=prop.parameters('Main_Format').Value
	ExtraName=prop.parameters('Extra_Name').Value
	ExtraExt=prop.parameters('Extra_Ext').Value
	ExtraFormat=prop.parameters('Extra_Format').Value
	All_Passes = prop.parameters('All_Passes').Value
	Create = prop.parameters('Create').Value
	Delete = prop.parameters('Delete').Value
	for PASE in AllPasses:
		RCHANEL = app.EnumElements(app.EnumElements(PASE)[len(app.EnumElements(PASE)) - 1])
		CREAR,BORRAR=[],[]
		if RenameMain:
			app.SetValue(PASE.fullname+".Main.Filename", MainName+'_'+ MainExt)
			app.SetValue(PASE.fullname+".Main.Format",MainFormat)
		else:
			MainName = app.GetValue(PASE.fullname+".Main.Filename", )
		if SetMainName:
			ExtraName = MainName
		if SetMainFormat:
			ExtraFormat = MainFormat

		for param in prop.parameters:
			if All_Passes == True:
				pasename = 'All_Passes'
				name = str(param.name).replace('All_Passes_','')
			else:
				pasename = PASE.name
				name = str(param.name).replace(PASE.name+'_','')

			if pasename +'_' + name == param.Name:
				value = param.Value
				Condition = name in str(RCHANEL)
				if All_Passes == False:
					if Condition == False and value == True:
						CREAR.append(name)
					if Condition == True and value == False:
						BORRAR.append(str(PASE)+ "." + name)
				else:
					if Create == True:
						if Condition == False and value == True:
							CREAR.append(name)
					else:
						if Condition == True and value == True:
							BORRAR.append(str(PASE)+ "." + name)

		for element in CREAR:
			fbuffer = app.CreateFramebuffer(PASE.fullname,element)
			fbuffer[0].Filename = ExtraName + '_' + ExtraExt
			fbuffer[0].Format = ExtraFormat
		for element in BORRAR:
			app.DeleteObj(element)
####
def Curve_By_Nulls_InitialPPG():
	prop = app.ActiveSceneRoot.AddProperty('CustomProperty',False,'Type of curve')
	types = ('linear',1,'cubic_linear_based',2,'cubic',3,)	
	typePar = prop.AddParameter3('Type',2,1)	
	closedPar = prop.AddParameter3('Closed',11,0)	
	Layout = prop.PPGLayout
	Layout.AddEnumControl( 'Type',types)
	Layout.AddItem('Closed')
	cancelado = app.InspectObj(prop,'','',4,False)
	if not cancelado:
		PPG = [typePar.Value,closedPar.Value]
		app.DeleteObj(prop)
		return PPG
	app.DeleteObj(prop)
####
def Curve_By_Nulls_FIRSTPPG():
	prop = app.ActiveSceneRoot.AddProperty('CustomProperty',False,'CV_From_Nulls')
	Layout = prop.PPGLayout
	Layout.AddButton('Pick','Pick')
	Layout.Language = "Python"
	Layout.Logic=Curve_By_Nulls_LOGIC


	app.InspectObj(prop,'','',3,False)
####	
def Curve_By_Nulls_CreateCurveFromNulls(parent,Controlls,name,close,type=1):
	Controlls = list(Controlls)
	Controllspos = []
	if type >= 2:
		if len(Controlls) == 2:
			Controlls.insert(0,Controlls[0])
			Controlls.append(Controlls[-1])
		elif len(Controlls) == 3:
			Controlls.append(Controlls[-1])
	for obj in Controlls:
		Controllspos.append(obj.Kinematics.Global.Transform.PosX)
		Controllspos.append(obj.Kinematics.Global.Transform.PosY)
		Controllspos.append(obj.Kinematics.Global.Transform.PosZ)
		Controllspos.append(1)
		
	CV = parent.AddNurbsCurve(Controllspos,"",close,type,c.siNonUniformParameterization,c.siSINurbs,name)
	#app.ParentObj(parent,Controlls)
	for i,obj in enumerate(Controlls):
		CVcls = CV.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster,obj.Name+"_clstr",[i])
		app.ApplyOp("ClusterCenter", CVcls.FullName+";"+obj.FullName, 0, "siPersistentOperation", "", 0)
	return CV
####
def Curve_By_Nulls_PickAditionalKnot ( CV,obj,point):
	x = obj.Kinematics.Global.Transform.PosX
	y = obj.Kinematics.Global.Transform.PosY
	z = obj.Kinematics.Global.Transform.PosZ
	POS = [x,y,z]
	i = str(point)[-2]
	if i == 'T':
		CVgeo= CV.ActivePrimitive.Geometry
		points = CVgeo.Curves(0).Get()
		i = len(list(points[0][3]))-1

	index = int (i)
	INDEX = []
	i = app.GetCurvePercentageAtKnotIndex( "CV", index )
	for element in i:
		INDEX.append((1-element )*-1)
	print INDEX
	I = str(INDEX[0])[:2]
	index2 = '0.'+ I

	app.SIAddPointOnCurve(CV,index2 , x, y, z, False,0)
	CVprim = app.EnumElements(CV.ActivePrimitive)
	CLSTR = CVprim[0]

	app.RemoveFromCluster(str(CLSTR)+".*,CV.pnt["+ str(index) +"]")
	CVcls = CV.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster,obj.Name+"_clstr",index)
	app.ApplyOp("ClusterCenter", CVcls.FullName+";"+obj.FullName, 0, "siPersistentOperation", "", 0)
####
def WireColorSplitPropNames (value):
	TEXT = value
	T=TEXT.split(',')
	ObjectList=[]
	for t in T:
		if '[' or ']' or "'" in t:
			t =t.replace('[','').replace(']','').replace("'",'')
			if ' ' in t:
				t = t.replace(' ','')
		if t != '':
			a = app.GetValue(t)
			ObjectList.append(a)
	return ObjectList
####
def WireColor_Single_Color(prop):
	E= prop.parameters('Enable_Gradient')
	p=prop.parameters
	R,G,B= p('Red'),p('Green'),p('Blue')
	r,g,b=R.Value,G.Value,B.Value
	OParam = prop.parameters('Objs')
	Objects = WireColorSplitPropNames(OParam.Value)
	OBJ=[]
	for O in Objects:
		OBJ.append(O)
		if O.type == 'null':
			if r== 0 and g == 0 and b ==0 :
				r,g,b = 0.01,0.01,0.01
	for O in OBJ:
		if E.Value == False:
			app.MakeLocal(O.Fullname+'.display', "siDefaultPropagation")
			D = O.Properties('Display')
			p = D.Parameters
			R,G,B = p('wirecolorr'),p('wirecolorg'),p('wirecolorb')
			R.Value = r 
			G.Value = g 
			B.Value = b
####
def WireColor_Gradient_Color(prop):
	E= prop.parameters('Enable_Gradient')
	p = prop.parameters
	R1,G1,B1 = p('Red1'),p('Green1'),p('Blue1')
	R2,G2,B2 = p('Red2'),p('Green2'),p('Blue2')
	r1,g1,b1=R1.Value,G1.Value,B1.Value
	r2,g2,b2=R2.Value,G2.Value,B2.Value
	OParam = prop.parameters('Objs')
	Objects = WireColorSplitPropNames(OParam.Value)
	OBJ=[]
	for O in Objects:
		OBJ.append(O)
		if O.type == 'null':
			if r1== 0 and g1 == 0 and b1 ==0 :
				r1,g1,b1 = 0.01,0.01,0.01
			if r2== 0 and g2 == 0 and b2 ==0 :
				r2,g2,b2 = 0.01,0.01,0.01
	if len(OBJ)>1 and E.Value == True :
		n = len(OBJ)-1
		gradR = (r2 - r1)/n
		gradG = (g2 - g1)/n
		gradB = (b2 - b1)/n
		ID = 0
		for O in OBJ:
			gradientR = gradR * ID
			gradientG = gradG * ID
			gradientB = gradB * ID
			ID = ID + 1
			app.MakeLocal(str(O)+'.display', "siDefaultPropagation")
			D = O.Properties('Display')
			p = D.Parameters
			R,G,B = p('wirecolorr'),p('wirecolorg'),p('wirecolorb')
			R.Value = r1 + gradientR
			G.Value = g1 + gradientG 
			B.Value = b1 + gradientB
####
def WireColor_Clear_Color(prop):
	OParam = prop.parameters('Objs')
	Objects = WireColorSplitPropNames(OParam.Value)
	r,g,b, = 0,0,0
	OBJ=[]
	for O in Objects:
		OBJ.append(O)
	for O in OBJ:
		app.MakeLocal(O.Fullname+'.display', "siDefaultPropagation")
		D = O.Properties('Display')
		R = D.Parameters('wirecolorr')
		G = D.Parameters('wirecolorg')
		B = D.Parameters('wirecolorb')
		R.Value = r
		G.Value = g
		B.Value = b
####		
def WireColor_SelectSimilar():
	SceneRoot = app.ActiveProject.ActiveScene.Root
	Objs = SceneRoot.Children
	Color = app.PickElement()[2]
	Select = []
	C = Color.Properties('Display').Parameters
	CR , CG , CB= C('wirecolorr'),C('wirecolorg'),C('wirecolorb')
	for o in Objs:
		D= o.Properties('Display').Parameters
		R,G,B = D('wirecolorr'), D('wirecolorg'),D('wirecolorb')
		if R.Value == CR.Value and G.Value == CG.Value and B.Value == CB.Value:
			Select.append(o)
	app.SelectObj(Select)


PROGIDPARAMSEXPLAIN='''##Use this TexEditor to tweak any parameter in your CustomShader
##CustomShader.parameter.Value = #'''


def PC_GetSequencesInDirectory(Path = '[Project Path]\Render_Pictures',MINIMUNKB=10,VALIDTYPES = ['jpeg','png','exr','tiff','tif','jpg','bmp']):
	Path = XSIUtils.ResolveTokenString( Path, '', False)
	Sequeceequal,Sequences,SequencesDir,SequencesFrames,SequencesTypes,SequencesPadding=[],[],[],[],[],[]
	for f in os.listdir(Path):
		type = f.split('.')[-1]
		refind = re.findall(r'\d+',f)
		if os.path.isfile(os.path.join(Path,f)) and len(refind)>0 and type in VALIDTYPES and refind[-1]+'.'+type == f[-len(refind[-1]+'.'+type):] :
			segNum=refind[-1]
			baseName=f.replace(segNum+f.split(segNum)[-1],'')
			padd = ''
			for n in range(len(segNum)): padd += '#'
			
			testname = baseName+type
			if testname not in Sequeceequal:
				Sequeceequal.append(testname)
				Sequences.append(baseName)
				SequencesDir.append(Path)
				SequencesFrames.append(segNum)
				SequencesTypes.append(type)
				SequencesPadding.append(len(segNum))
			else:
				if int(segNum) not in map(int,SequencesFrames[Sequeceequal.index(testname)].split(',')):
					SequencesFrames[Sequeceequal.index(testname)] += ','+str(segNum)
				if len(segNum) < SequencesPadding[Sequeceequal.index(testname)]:
					SequencesPadding[Sequeceequal.index(testname)] = len(segNum)
	SequencesFrames=[sorted(map(int,i.split(','))) for i in SequencesFrames]
	SEQUENCES=[]
	for i,seqFrs in enumerate(SequencesFrames):
		SEQ,seqN=[],[]
		padd = "%0"+str(SequencesPadding[i])+"d"
		for e,fr in enumerate(seqFrs):
			if e in [0,len(seqFrs)-1]:
				seqN.append(padd%fr)
			elif fr-1 in seqFrs and fr+1 in seqFrs:
				if seqN[-1]!= '....':
					seqN.append('....')
			else:
				seqN.append(padd%fr)
				if fr+1 in seqFrs:
					seqN.append('....')
		MissingFrames =[e for e in range(seqFrs[0],seqFrs[-1]) if e not in seqFrs]
		##Final data with Correct Padding##
		SEQName,SEQDir,SEQType,SEQPadding = Sequences[i],SequencesDir[i],SequencesTypes[i],''
		for n in range(SequencesPadding[i]): SEQPadding += '#'
		SEQFrames = [padd% e for e in seqFrs]
		SEQFrameName =  str(seqN).replace(r"'",'').replace(' ','').replace(',.','').replace('.,','')
		SEQMissingFrames = str([padd% e for e in MissingFrames]).replace(', ',',').replace(r"'",'').replace('[','').replace(']','')
		SEQSize = 0
		for i in range(len(SEQFrames)): SEQSize += float(os.path.getsize(os.path.join(SEQDir,SEQName)+SEQFrames[i]+'.'+SEQType))
		print 'Minimus Alowed Size ',str(MINIMUNKB)
		SEQWrongFrames =  str([wfr for wfr in SEQFrames if float(os.path.getsize(os.path.join(SEQDir,SEQName)+wfr+'.'+SEQType))/1024<MINIMUNKB]).replace(', ',',').replace(r"'",'').replace('[','').replace(']','')
		SEQ.append(SEQName+SEQFrameName+'.'+SEQType)
		SEQ.append(SEQDir)
		SEQ.append(SEQType)
		SEQ.append(round(SEQSize/1048576,4))
		SEQ.append(SEQPadding)
		SEQ.append(SEQFrames[0])
		SEQ.append(SEQFrames[-1])
		SEQ.append(len(SEQFrames))
		SEQ.append(SEQMissingFrames)
		SEQ.append(SEQWrongFrames)
		
		SEQUENCES.append(SEQ)
		
		
		
	return SEQUENCES

def PC_FLIPBOOK(SEQDir,SEQName,SEQType,SEQStart,SEQEnd,RATE,SEQPadding,preload,RESCALEONLOAD):
	FB = app.Flipbook('-s'+SEQDir+'\\'+SEQName+'.'+SEQType+' '+str(SEQStart)+' '+str(SEQEnd+' 1 '+str(RATE))+' -p(fn)'+SEQPadding+'(ext)'+' '+preload +' -r '+str(RESCALEONLOAD))
	return FB
	
def PC_EncenderGranja(GRANJAPropEnable,RACK1PropEnable,RACK2PropEnable,RACK3PropEnable,GRANJAProp,RACK1Prop,RACK2Prop,RACK3Prop):
	from subprocess import call
	try:
		if GRANJAPropEnable:
			Scriptdir = os.path.dirname(GRANJAProp)+"\\"
			cmdline = GRANJAProp.replace(Scriptdir,'')
			call("start cmd /k " + cmdline, cwd=Scriptdir, shell=True)
		else:
			if RACK1PropEnable:
				Scriptdir = os.path.dirname(RACK1Prop)+"\\"
				cmdline = RACK1Prop.replace(Scriptdir,'')
				call("start cmd /k" + cmdline, cwd=Scriptdir, shell=True)
			if RACK2PropEnable:
				Scriptdir = os.path.dirname(RACK2Prop)+"\\"
				cmdline = RACK2Prop.replace(Scriptdir,'')
				call("start cmd /k " + cmdline, cwd=Scriptdir, shell=True)
			if RACK3PropEnable:
				Scriptdir = os.path.dirname(RACK3Prop)+"\\"
				cmdline = RACK3Prop.replace(Scriptdir,'')
				call("start cmd /k " + cmdline, cwd=Scriptdir, shell=True)
	except:
		app.LogMessage( 'No se ha podido ejecutar los scripts de encender granja',4)
		
def PC_GETMusterDeffaults():
	MRTOOL,enciendegranja,encienderack1,encienderack2,encienderack3 = "C:\Program Files\Virtual Vertex\Muster 8\Mrtool.exe",'Z:\INFORMATICA_DEPARTMENT\scripts_granja\enciende_Granja.bat','Z:\INFORMATICA_DEPARTMENT\scripts_granja\ENCIENDE_RACK_I_01_12.BAT','Z:\INFORMATICA_DEPARTMENT\scripts_granja\ENCIENDE_RACK_II_20_29.BAT','Z:\INFORMATICA_DEPARTMENT\scripts_granja\ENCIENDE_RACK_III_31_42.BAT'
	tempfolderpath = app.Commands( "PC_SendRendertoMuster" ).OriginPath+'Temp'
	Server,User,Password,Engine,Pool ='storage','admin','','76','0'
	DEFAULT = [enciendegranja,encienderack1,encienderack2,encienderack3,tempfolderpath,Server,User,Engine,Pool,MRTOOL,Password,False]
	USERPREFS = XSIUtils.Environment( 'XSI_USERHOME' )+r'\Data\Preferences\PC_SendToMuster_UserPrefs.txt'
	if os.path.isfile(USERPREFS):
		script_locals = dict()
		execfile(USERPREFS, dict(), script_locals)
		a = (script_locals["PC_MusterUserPrefs"])
		NEWDEFAULT = a()
		NEWDEFAULT.append(True)
	else:
		NEWDEFAULT = DEFAULT
	return NEWDEFAULT

def PC_ConectToMuster():
	USERPREFS = XSIUtils.Environment( 'XSI_USERHOME' )+r'\Data\Preferences\PC_SendToMuster_UserPrefs.txt'
	#print USERPREFS
	DEFFAULTS = PC_GETMusterDeffaults()
	Server,User,MRTool,Password = DEFFAULTS[5],DEFFAULTS[6],DEFFAULTS[9],DEFFAULTS[10]
	Passw = ''
	Passw = ' -p '+Password if Password != '' else ''
	err = True
	if DEFFAULTS[11]:
		arg =  shlex.split(r'"'+MRTool+r'"'+" -s "+Server+" -u "+User+Passw+" -q n" )
		p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		error = list(p.communicate())[1]
		err = False
		if error != '':
			app.LogMessage(error,2)
			app.LogMessage('Unable to Conect with Saved Preferences,please save prefferences after new connection',4)
			err = True
	if err:
		prop = app.ActiveProject.ActiveScene.Root.AddProperty('CustomProperty')
		propsvalues=[Server,User,Password,MRTool]
		for i,p in enumerate(['Server','User','PassWord','MRTool']):
			param = prop.AddParameter3(p,8,propsvalues[i])
		cancel = app.InspectObj(prop,'','Conect To Muster',4,False)
		if not cancel:
			MData = [i.Value for i in prop.Parameters ]
			Server,User,PassWord,MRTool = MData[0],MData[1],MData[2],MData[3]
			Passw = ''
			Passw = ' -p '+PassWord if PassWord != '' else ''
			arg =  shlex.split(r'"'+MRTool+r'"'+" -port 9781 "+" -s "+Server+" -u "+User+Passw+" -q n" )
			p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			error = list(p.communicate())[1]
			err = False
			if error == '' or PassWord == 'Pedropuedepasar':
				index = [5,6,9,10]
				for i,e in enumerate([Server,User,MRTool,PassWord]):
					DEFFAULTS.pop(index[i])
					DEFFAULTS.insert(index[i],e)
				if PassWord == 'Pedropuedepasar':
					app.LogMessage( 'Editing Mode',8)
			else:
				app.LogMessage(error,2)
				err = True
				[arg,err],DEFFAULTS=PC_ConectToMuster()
		app.DeleteObj(prop)
	arg =  shlex.split(r'"'+MRTool+r'"'+" -s "+Server+" -u "+User+Passw)
	return [[arg,err],DEFFAULTS]
def PC_MusterPools (arg,err):
	File = app.Commands( "PC_SendRendertoMuster" ).OriginPath.replace('Application','Data').replace('Plugins','Preferences')
	File = File+'PC_SendToMuster_Pools.txt'
	if not err:
		arg.append('-q')
		arg.append('p')
		p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		MusterPools = []
		for i,line in enumerate(p.stdout.readlines()):
			if i > 2:
				e= ''.join(line.split()).split('|')
				if e[0] not in MusterPools and e[0] != '':
					MusterPools.append(e[0])
		nonelist = ['None',0]
		MusterPools = nonelist if len(MusterPools) == 0 else MusterPools
		WriteArray = []
		for i,p in enumerate(MusterPools):
			WriteArray.append(p)
			WriteArray.append(i)
		with open(File, 'w') as fout:
			fout.write(str(WriteArray))
		return MusterPools
	else:
		return 'Unable to Conect'
		
def PC_MusterTemplates (arg,err):
	File = app.Commands( "PC_SendRendertoMuster" ).OriginPath.replace('Application','Data').replace('Plugins','Preferences')
	File = File+'PC_SendToMuster_Templates.txt'
	
	if not err:
		arg.append('-q')
		arg.append('t')
		p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		MusterTemplates = []
		for i,line in enumerate(p.stdout.readlines()):
			if i > 2 and line != '\n':
				print [a.replace('\n','') for a in reversed(line.split('	'))]
				a = [s.replace('\n','') for s in reversed(line.split('	'))]
				MusterTemplates.append(a)
			
		nonelist = [['None',0]]
		MusterTemplates = nonelist if len(MusterTemplates) == 0 else MusterTemplates
		WriteArray = []
		for p in MusterTemplates:
			for e,i in enumerate(p):
				if e == 1:
					WriteArray.append(int(i))
				else:
					WriteArray.append(i)
		with open(File, 'w') as fout:
			fout.write(str(WriteArray))
		return MusterTemplates
	else:
		return 'Unable to Conect'

def PC_MusterJobs (arg,err):
	File = app.Commands( "PC_SendRendertoMuster" ).OriginPath.replace('Application','Data').replace('Plugins','Preferences')
	File = File+'PC_SendToMuster_Jobs.txt'
	
	if not err:
		arg.append('-q')
		arg.append('j')
		p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		MusterJobs = []
		for i,line in enumerate(p.stdout.readlines()):
			e= ''.join(line.split()).split('|')
			if i > 2 and e[0] != '':
				if e[2] != 'Folder' and e[0] != '':
					MusterJobs.append([e[1]+'____'+str(e[0]),e[0]])
		MusterJobs= [i for i in reversed(MusterJobs)]
		nonelist = ['None',0]
		MusterJobs = nonelist if len(MusterJobs) == 0 else MusterJobs
		WriteArray = []
		for p in MusterJobs:
			for e,i in enumerate(p):
				if e == 1:
					WriteArray.append(int(i))
				else:
					WriteArray.append(i)
		with open(File, 'w') as fout:
			fout.write(str(WriteArray))
		return MusterJobs
	else:
		return 'Unable to Conect'
def PC_ReadMusterLogs(Log):
	USERPREFS= app.Commands( "PC_SendRendertoMuster" ).OriginPath.replace('Application','Data').replace('Plugins','Preferences')+Log
	with open(USERPREFS, 'r') as fout:
		#print fout.read()
		Log = fout.read().replace("'",'').replace('[','').replace(']','').split(', ')
	#print Log
	return Log
		
		
####LOGICS
MusterPrefferencesLogic = '''					
def EditMode_OnChanged():
	for param in [prop.Parameters('Password'),prop.Parameters('MRTool'),prop.Parameters('Granja_All'),prop.Parameters('Rack1'),prop.Parameters('Rack2'),prop.Parameters('Rack3'),prop.Parameters('Server'),prop.Parameters('User'),prop.Parameters('EngineID'),prop.Parameters('Pool')]:
		if prop.Parameters('EditMode').Value:
			param.Enable(True)
		else:
			param.Enable(False)
def SaveDeffaults_OnClicked():
	shutil.copy(DEFAULTPREFS,USERPREFS)
	GranjaAll = prop.Parameters('Granja_All').Value
	Rack1 = prop.Parameters('Rack1').Value
	Rack2 = prop.Parameters('Rack2').Value
	Rack3 = prop.Parameters('Rack3').Value
	MRTOOL = prop.Parameters('MRTool').Value
	SERVER = prop.Parameters('Server').Value
	MUSER = prop.Parameters('User').Value
	PASSWORD = prop.Parameters('Password').Value
	ENGINE = prop.Parameters('EngineID').Value
	POOL = prop.Parameters('Pool').Value
	fileinput.FileInput(USERPREFS).close()
	FILEINPUT =fileinput.FileInput(USERPREFS, inplace=1)
	for i, line in enumerate(FILEINPUT):
		sys.stdout.write(line.replace('[GranjaAll]', GranjaAll).replace('[Rack1]', Rack1).replace('[Rack2]', Rack2).replace('[Rack3]', Rack3).replace('[SERVER]', SERVER).replace('[MUSER]', MUSER).replace('[PASSWORD]',PASSWORD).replace('[ENGINE]', ENGINE).replace('[POOL]', POOL).replace('[MRTOOL]',MRTOOL))
	FILEINPUT.close()	
	app.LogMessage( 'User Preferences saved to Disk at: ' + USERPREFS)
def RestoreDeffaults_OnClicked():
	if os.path.isfile(USERPREFS):
		os.remove(USERPREFS)
		app.LogMessage( 'User Preferences removed from: ' + USERPREFS)
	else:
		app.LogMessage( 'No avaliabre User Preferences To delete',4)
	prop.Parameters('Granja_All').Value='Z:\INFORMATICA_DEPARTMENT\scripts_granja\enciende_Granja.bat'
	prop.Parameters('Rack1').Value='Z:\INFORMATICA_DEPARTMENT\scripts_granja\ENCIENDE_RACK_I_01_12.BAT'
	prop.Parameters('Rack2').Value='Z:\INFORMATICA_DEPARTMENT\scripts_granja\ENCIENDE_RACK_II_20_29.BAT'
	prop.Parameters('Rack3').Value='Z:\INFORMATICA_DEPARTMENT\scripts_granja\ENCIENDE_RACK_III_31_42.BAT'
	prop.Parameters('MRTool').Value = 'C:\Program Files\Virtual Vertex\Muster 8\Mrtool.exe'
	prop.Parameters('Server').Value='storage'
	prop.Parameters('User').Value='admin'
	prop.Parameters('Password').Value = ''
	prop.Parameters('EngineID').Value='76'
	prop.Parameters('Pool').Value='0'
def UpdatePools_Templates_OnClicked():
	MRTOOL = prop.Parameters('MRTool').Value
	SERVER = prop.Parameters('Server').Value
	MUSER = prop.Parameters('User').Value
	PASSWORD = prop.Parameters('Password').Value
	Passw = ''
	Passw = ' -p '+PASSWORD if PASSWORD != '' else ''
	arg =  shlex.split(r'"'+MRTOOL+r'"'+" -s "+SERVER+" -u "+MUSER+Passw+" -q n" )
	Tools.PC_MusterTemplates(arg,False)
	Tools.PC_MusterPools(arg,False)

	Templates=Tools.PC_ReadMusterLogs('PC_SendToMuster_Templates.txt')
	Pools = Tools.PC_ReadMusterLogs('PC_SendToMuster_Pools.txt')
	prop.PPGLayout.Item('EngineID').UIItems = Templates
	prop.PPGLayout.Item('Pool').UIItems =Pools
	PPG.Refresh()
'''

MultiImporterLogic = '''
import os
TYPES = ['.obj','.fbx','.xsi','.emdl']
app = Application 
projectPath = XSIUtils.ResolveTokenString( '[Project Path]', '', False,'', '' )
o = PPG.InspectedObjects
prop = app.ActiveSceneRoot.GetPropertyFromName2(o)
Layout = prop.PPGLayout
PATH = prop.Parameters('Path')
FOLDERS = prop.Parameters('Folders')
FILES =  prop.Parameters('Files')
IMPORT = prop.Parameters('Import')
def Path_OnChanged():
	DIRS = ['...',os.path.dirname(PATH.Value)]
	FILES =[]
	for Path in PATH.Value.split(';'):
		for dir in os.listdir(Path):
			fileName, fileExtension = os.path.splitext(os.path.join(Path,dir))
			if fileExtension.lower() in TYPES:
				FILES.append(dir)
				FILES.append(os.path.join(Path,dir))
			elif fileExtension == '':
				DIRS.append(dir)
				DIRS.append(os.path.join(Path,dir))
	Layout.Item('Folders').UIItems = DIRS
	Layout.Item('Files').UIItems = FILES
	PPG.Refresh()
def Folders_OnChanged():
	PATH.Value = FOLDERS.Value
	DIRS = ['...',os.path.dirname(PATH.Value)]
	FILES =[]
	for Path in FOLDERS.Value.split(';'):
		for dir in os.listdir(Path):
			fileName, fileExtension = os.path.splitext(os.path.join(Path,dir))
			if fileExtension in TYPES:
				FILES.append(dir)
				FILES.append(os.path.join(Path,dir))
			elif fileExtension == '':
				DIRS.append(dir)
				DIRS.append(os.path.join(Path,dir))
	Layout.Item('Folders').UIItems = DIRS
	Layout.Item('Files').UIItems = FILES
	FOLDERS.Value = ''
	PPG.Refresh()
def AddToList_OnClicked():
	LISTA = []
	for ui in Layout.Item('Import').UIItems:
		LISTA.append(ui)
	for p in FILES.Value.split(';'):
		if p not in LISTA:
			LISTA.append(p)
			LISTA.append(p)
	Layout.Item('Import').UIItems = LISTA
	FILES.Value = ''
	PPG.Refresh()
def RemoveFromList_OnClicked():
	LISTA = []
	for ui in Layout.Item('Import').UIItems:
		LISTA.append(ui)
	for p in IMPORT.Value.split(';'):
		LISTA.remove(p)
		LISTA.remove(p)
	Layout.Item('Import').UIItems = LISTA
	IMPORT.Value = ''
	PPG.Refresh()
def MPickParent_OnClicked():
	parent = app.OpenTransientExplorer(Application.ActiveSceneRoot,3)
	prop.Parameters('MParent').Value = parent
def dotPickParent_OnClicked():
	parent = app.OpenTransientExplorer(Application.ActiveSceneRoot,3)
	prop.Parameters('dotParent').Value = parent
def MShareOptions_OnChanged():
	if prop.Parameters('MShareOptions').Value == '0':
		prop.Parameters('MShareOptionsinfo').Value = ''
	if prop.Parameters('MShareOptions').Value == '1':
		prop.Parameters('MShareOptionsinfo').Value = 'The image clips and image sources are shared'
	if prop.Parameters('MShareOptions').Value == '2':
		prop.Parameters('MShareOptionsinfo').Value = 'If the library already exist and there is a material with the same name, the existing material will be used'
	if prop.Parameters('MShareOptions').Value == '4':
		prop.Parameters('MShareOptionsinfo').Value = 'Objects will be reinstalled into existing layers that have the same name'
	if prop.Parameters('MShareOptions').Value == '8':
		prop.Parameters('MShareOptionsinfo').Value = 'Objects will be reinstalled into existing partition of each passes that have the same name'
	if prop.Parameters('MShareOptions').Value == '65535':
		prop.Parameters('MShareOptionsinfo').Value = 'Share all objects: Image sources/clips, materials and material libraries, layers and partitions'
		PPG.Refresh()
'''

ArnoldFbufferLogic ='''
import win32com
import Tools
reload ( Tools )
from Tools import *
app = Application 
LISTA = ["Depth","Arnold_Direct_Diffuse","Arnold_Indirect_Diffuse","Arnold_Direct_Specular","Arnold_Indirect_Specular",'Arnold_Motion_Vector',"Arnold_Emission","Arnold_Alpha","Arnold_Opacity","Arnold_Refraction",'Arnold_Refraction_Opacity',"Arnold_Reflection","Arnold_SSS"]
o = PPG.InspectedObjects
prop = app.ActiveSceneRoot.GetPropertyFromName2(o)
Layout = prop.PPGLayout 
def All_Passes_OnChanged():
	ALLPASSES = prop.Parameters('All_Passes').Value
	if ALLPASSES == True:
		Layout.Clear()
		FrameBuffer_Managers_BasicTab(prop)
		Framebuffer_Managers_AllPasses_Tab(prop,LISTA)
		PPG.Refresh()
		prop.Parameters('Delete').Enable(True)
		prop.Parameters('Create').Enable(True)
	if ALLPASSES == False:
		Layout.Clear()
		FrameBuffer_Managers_BasicTab(prop)
		FrameBuffer_Managers_PerPass_Tab(prop,LISTA)
		PPG.Refresh()
		prop.Parameters('Delete').Enable(False)
		prop.Parameters('Create').Enable(False)
def Create_OnChanged():
	if prop.Parameters('Create').Value == True:
		prop.Parameters('Delete').Value = False
	else:
		prop.Parameters('Delete').Value = True
def Delete_OnChanged():
	if prop.Parameters('Delete').Value == True:
		prop.Parameters('Create').Value = False
	else:
		prop.Parameters('Create').Value = True
'''	

CustomFbufferLogic ='''
import win32com
import Tools
reload ( Tools )
from Tools import *
app = Application 
CUSTOMCHANNELS=GetCustomChannels()[0]
LISTA=[]
for ch in CUSTOMCHANNELS:
	LISTA.append(ch.name)
o = PPG.InspectedObjects
prop = app.ActiveSceneRoot.GetPropertyFromName2(o)
Layout = prop.PPGLayout 
def All_Passes_OnChanged():
	ALLPASSES = prop.Parameters('All_Passes').Value
	if ALLPASSES == True:
		Layout.Clear()
		FrameBuffer_Managers_BasicTab(prop)
		Framebuffer_Managers_AllPasses_Tab(prop,LISTA)
		PPG.Refresh()
		prop.Parameters('Delete').Enable(True)
		prop.Parameters('Create').Enable(True)
	if ALLPASSES == False:
		Layout.Clear()
		FrameBuffer_Managers_BasicTab(prop)
		FrameBuffer_Managers_PerPass_Tab(prop,LISTA)
		PPG.Refresh()
		prop.Parameters('Delete').Enable(False)
		prop.Parameters('Create').Enable(False)
def Create_OnChanged():
	if prop.Parameters('Create').Value == True:
		prop.Parameters('Delete').Value = False
	else:
		prop.Parameters('Delete').Value = True
def Delete_OnChanged():
	if prop.Parameters('Delete').Value == True:
		prop.Parameters('Create').Value = False
	else:
		prop.Parameters('Create').Value = True
'''	

cameraLogic =  '''
import win32com
from win32com.client import constants as c
AllCameras = []
Cameras = Application.ActiveSceneRoot.FindChildren( '', "camera" )
for i,cam in enumerate(Cameras):
	AllCameras.append(cam.name)
	AllCameras.append(i)
o = PPG.InspectedObjects
prop = Application.ActiveSceneRoot.GetPropertyFromName2(o)
Layout=prop.PPGLayout
def All_Passes_OnChanged():
	Layout.Clear()
	Layout.AddEnumControl('Camera',AllCameras,'Select Camera',c.siControlCombo)
	for param in prop.Parameters:
		AllPases = prop.Parameters('All_Passes').Value
		if AllPases==True:
			if param.name == 'All_Passes':
				Layout.AddItem(param.name,param.name,c.siControlCheck)
		else:
			if param.name != 'Camera':
				Layout.AddItem(param.name,param.name,c.siControlCheck)
	PPG.Refresh()
'''

CustomChannelLogic ='''
import win32com
from win32com.client import constants as c
import Tools
reload ( Tools )
from Tools import *
app = Application   
o = PPG.InspectedObjects
prop = app.ActiveSceneRoot.GetPropertyFromName2(o)
Layout = prop.PPGLayout
Arnold = []
AllShaders= []
for sh in app.ShaderDefinitions :
	AllShaders.append(sh)
	if 'Arnold' in str(sh):
		if sh.Category != '':
			if "EFX" not in sh.Category:
				if int(sh.Category[-3:]) < 400:
					Arnold.append(sh)
sceneMAT = Application.ActiveProject.ActiveScene.Root.Properties("Scene_Material")
SH=[i.Name for i in sceneMAT.GetAllShaders()]
IM=[i.Name for i in sceneMAT.AllImageClips]
NODELETENAME = [SH+IM]
def New_Channel_OnChanged():
	if prop.Parameters('New_Channel').Value == True:
		prop.Parameters('Existing_Channel').Enable(False)
		prop.Parameters('Channel').Enable(True)
	else:
		prop.Parameters('Existing_Channel').Enable(True)
		prop.Parameters('Channel').Enable(False)
def Store_OnChanged():
	Layout.Clear()
	Store_In_Channel_Basic_Tab(Layout)
	type = prop.Parameters('Store').Value
	if type == '0':
		Store_In_Channel_Color_Tab(Layout)
	if type == '1':
		Store_In_Channel_Shadow_Tab(Layout)
	if type == '2':
		Store_In_Channel_AAO_Tab(Layout)
	if type == '3':
		Store_In_Channel_MAO_Tab(Layout)
	if type == '4':
		Store_In_Channel_CustomProgID_Tab(Layout)
	PPG.Refresh()
def ArnoldShaders_OnChanged():
	UI,UIS = [],[]
	Debug = Layout.Item('Get_Attributes')
	OtherShather =  prop.Parameters('AllShaders')
	Shader = prop.Parameters('ArnoldShaders')
	CustomProgID= prop.Parameters('CustomProgID')
	CustomProgID.Value = Arnold[int(Shader.Value)].ProgID
	OtherShather.Value = -1
	for i in Arnold:
		if CustomProgID.Value in str(i.ProgID):
			a = list(i.InputParamDefs.Definitions)
			if len(a) == 0:
				try:
					A=Application.CreateShaderFromProgID(str(i), "Sources.Materials.DefaultLib.Scene_Material", '')
					for s in sceneMAT.GetAllShaders():
						if s.Name not in str(NODELETENAME):
							Application.DisconnectAndDeleteOrUnnestShaders(s, "Sources.Materials.DefaultLib.Scene_Material")
					for im in sceneMAT.AllImageClips:
						if im.Name not in str(NODELETENAME):
							Application.DisconnectAndDeleteOrUnnestShaders(im, "Sources.Materials.DefaultLib.Scene_Material")
				except:
					continue
			for x in i.InputParamDefs.Definitions :
				UI.append(x.Name)
	for i,ui in enumerate(UI):
		UIS.append(ui)
		UIS.append(i)
	Debug.UIItems =UIS
	Debug.SetAttribute(c.siUICY,100)
	PPG.Refresh()
def AllShaders_OnChanged():
	UI,UIS = [],[]
	Debug = Layout.Item('Get_Attributes')
	OtherShather =  prop.Parameters('ArnoldShaders')
	Shader = prop.Parameters('AllShaders')
	CustomProgID= prop.Parameters('CustomProgID')
	CustomProgID.Value = AllShaders[int(Shader.Value)].ProgID
	OtherShather.Value = -1

	for i in AllShaders:
		if CustomProgID.Value in str(i.ProgID):
			a = list(i.InputParamDefs.Definitions)
			if len(a) == 0:
				try:
					A=Application.CreateShaderFromProgID(str(i), "Sources.Materials.DefaultLib.Scene_Material", '')
					for s in sceneMAT.GetAllShaders():
						if s.Name not in str(NODELETENAME):
							Application.DisconnectAndDeleteOrUnnestShaders(s, "Sources.Materials.DefaultLib.Scene_Material")
					for im in sceneMAT.AllImageClips:
						if im.Name not in str(NODELETENAME):
							Application.DisconnectAndDeleteOrUnnestShaders(im, "Sources.Materials.DefaultLib.Scene_Material")
				except:
					continue
			for x in i.InputParamDefs.Definitions :
				UI.append(x.Name)
	for i,ui in enumerate(UI):
		UIS.append(ui)
		UIS.append(i)
	Debug.UIItems =UIS
	Debug.SetAttribute(c.siUICY,100)
	PPG.Refresh()
def CustomProgID_OnChanged():
	UI,UIS = [],[]
	Debug = Layout.Item('Get_Attributes')
	CustomProgID= prop.Parameters('CustomProgID').Value
	OtherShather =  prop.Parameters('ArnoldShaders')
	Shader = prop.Parameters('AllShaders')
	ArnoldExist=False
	for i in Arnold:
		if CustomProgID == str(i.ProgID):
			ArnoldExist=True
	if ArnoldExist==True:
		Shader.Value=-1
	else:
		OtherShather.Value=-1	
	for i in AllShaders:
		if CustomProgID in str(i.ProgID):
			a = list(i.InputParamDefs.Definitions)
			if len(a) == 0:
				try:
					A=Application.CreateShaderFromProgID(str(i), "Sources.Materials.DefaultLib.Scene_Material", '')
					for s in sceneMAT.GetAllShaders():
						if s.Name not in str(NODELETENAME):
							Application.DisconnectAndDeleteOrUnnestShaders(s, "Sources.Materials.DefaultLib.Scene_Material")
					for im in sceneMAT.AllImageClips:
						if im.Name not in str(NODELETENAME):
							Application.DisconnectAndDeleteOrUnnestShaders(im, "Sources.Materials.DefaultLib.Scene_Material")
				except:
					continue
			for x in i.InputParamDefs.Definitions :
				UI.append(x.Name)
	for i,ui in enumerate(UI):
		UIS.append(ui)
		UIS.append(i)
	Debug.UIItems =UIS
	Debug.SetAttribute(c.siUICY,100)
	PPG.Refresh()

''' 

Curve_By_Nulls_LOGIC = '''
from win32com.client import constants as c
from Tools import *
reload ( Tools )
def Pick_OnClicked():
	PickNull = XSIUIToolkit.MsgBox( 'Pick the new Point', 1, 'Pick the New Point' )
	if PickNull == 1:
		pick = Application.PickElement("Null")
		obj = pick.Value('PickedElement')
		PickPoint = XSIUIToolkit.MsgBox( 'Pick point After', 1, 'Pick the point After' )
		if PickPoint == 1:
			pick = Application.PickElement("Point")
			point = pick.Value('PickedElement')
			CV = Application.ActiveSceneRoot.FindChild(point.Name)
			Curve_By_Nulls_PickAditionalKnot(CV,obj,point)
'''	

PC_ICE_CV_LOGIC = """
def GetIceControlPoints (object,attrname):
	lista = []
	for i in object.IceAttributes.Filter( '', '', attrname ):
		templist = list(i.DataArray2D[0])
		for a in range(3):
			temp = []
			for i in range(len(templist)/3):
				temp.append(templist[i+a*(len(templist)/3)])
			lista.append(temp)
	return lista
	
def GetIcenbpoints (object,attrname):
	lista = []
	for i in object.IceAttributes.Filter( '', '', attrname ):
		templist = list(i.DataArray2D[0])
		lista.append(len(templist))
		lista.append(templist)
	return lista
def GetIceDegree (object,attrname):
	lista = []
	for i in object.IceAttributes.Filter( '', '', attrname ):
		lista = list(i.DataArray2D[0])
	return lista
def GetIceClosed (object,attrname):
	lista = []
	for i in object.IceAttributes.Filter( '', '', attrname ):
		temp = list(i.DataArray2D[0])
		for o in temp:
			if o == 0:
				lista.append(False)
			else:
				lista.append(True)
	return lista
	
def PC_ICE_CV_Update(ctx, Out, In):
	l_data = GetIceControlPoints(In.Value.Geometry,'__PCVPositions')
	
	w = [1.0] * len(l_data[0])
	l_data.append(w)
	icenb = GetIcenbpoints(In.Value.Geometry,'__PCVpcvNB')
	if  icenb[0] >0:
		nbscvs,nbsubpoints = icenb[0],icenb[1] 
	else:
		nbscvs,nbsubpoints = 1,None
	dg = GetIceDegree ( In.Value.Geometry, '__PCVDegree')
	closed = GetIceClosed ( In.Value.Geometry, '__PCVClosed')
	try:
		Out.Value.Geometry.Set(nbscvs, l_data, nbsubpoints, None,None,closed,dg)
	except:
		Application.LogMessage('No Valid Ice Data Found',4)
"""	

