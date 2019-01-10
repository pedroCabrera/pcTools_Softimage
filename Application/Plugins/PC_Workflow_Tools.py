import win32com 
from win32com.client import constants as c
import Tools
from Tools import *
reload ( Tools )
app = Application
null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "PEDRITO"
	in_reg.Name = "PC_WorkFlow_Tools"
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterCommand("PC_Add_To_Partition_MultiPass","PC_Add_To_Partition_MultiPass")
	in_reg.RegisterCommand("PC_Set_Camera_MultiPass","PC_Set_Camera_MultiPass")
	in_reg.RegisterCommand("PC_Arnold_Framebuffer_Manager","PC_Arnold_Framebuffer_Manager")
	in_reg.RegisterCommand("PC_Custom_Framebuffer_Manager","PC_Custom_Framebuffer_Manager")
	in_reg.RegisterCommand("PC_Store_Custom_Channel","PC_Store_Custom_Channel")
	in_reg.RegisterCommand("PC_MultiPass_Capture","PC_MultiPass_Capture")
	in_reg.RegisterCommand("PC_SetPlayControlFromPass","PC_SetPlayControlFromPass")
	in_reg.RegisterCommand("PC_SendRendertoMuster","PC_SendRendertoMuster")
	
	in_reg.RegisterEvent("PC_ChangePassEvent",c.siOnEndPassChange)
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	app.LogMessage(str(strPluginName) + str(" has been unloaded."),c.siVerbose)
	return true
	
def PC_ChangePassEvent_OnEvent( in_ctxt ):
	Application.PC_SetPlayControlFromPass()
	return true
	
def PC_Add_To_Partition_MultiPass_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true
def PC_Set_Camera_MultiPass_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true

	return true
def PC_Arnold_Framebuffer_Manager_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = "Create Arnold Framebuffers"
	oCmd.ReturnValue = true
	return true
def PC_Custom_Framebuffer_Manager_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = "Create Custom Framebuffers"
	oCmd.ReturnValue = true
	return true	
def PC_Store_Custom_Channel_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true	
def PC_MultiPass_Capture_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true	
def PC_SetPlayControlFromPass_Init(in_ctxt):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true	

def PC_Add_To_Partition_MultiPass_Execute(  ):

	app.LogMessage("Add_To_Partition_MultiPass_Execute called",c.siVerbose)
	

	scene = app.ActiveProject.ActiveScene
	sceneobj = app.EnumElements(scene)
	AllPasses = []
	AllPartitions = []
	Partitions = []
	Objects =  []
	ObjectsName =[]
	Passes = win32com.client.Dispatch( "XSI.Collection" )
	selection = win32com.client.Dispatch( "XSI.Collection" )
	selection.AddItems (app.Selection)
	for element in selection:
		if element.BranchFlag == 1:
			for obj in element.FindChildren2('','','',True):
				Objects.append(obj)
				ObjectsName.append(obj.name)
		else:
			Objects.append(element)
			ObjectsName.append(element.name)
	objCount = len(Objects)
	if objCount == 0:
		app.LogMessage( "Selecciona al menos un objeto",2)
	else:
		for Pass in scene.Passes:
			AllPasses.append(Pass)
			for partition in Pass.Partitions:
				AllPartitions.append(partition)
		PARTITIONS = []								
		for element in AllPartitions:
			if element.PartitionType == 1:
				if element not in Partitions:
					Partitions.append(element.name)
		for i, v in enumerate(Partitions):
			PARTITIONS.append(v)
			PARTITIONS.append(i)

		prop = app.ActiveSceneRoot.AddProperty ("CustomProperty", False, "")
		existpartition = prop.AddParameter3('Partition_Name1',c.siString)
		usenew = prop.AddParameter3('New',c.siBool,)
		newpartition = prop.AddParameter3('Partition_Name2',c.siString)
		allpasses = prop.AddParameter3('All_Passes',c.siBool,)
		create = prop.AddParameter3('Create',c.siBool,)
		addtoBG = prop.AddParameter3('addtoBG',c.siBool,)
		Layout=prop.PPGLayout
		Layout.Clear()
		Layout.AddEnumControl('Partition_Name1',PARTITIONS,'Partition Name',c.siControlCombo)
		Layout.AddItem('New','New Partition')
		Layout.AddItem('Partition_Name2','Partition Name')
		Layout.AddItem('All_Passes','All Passes')
		Layout.AddItem('Create','Create if not exist')
		Layout.AddItem('addtoBG','Add To Bacground ObjectPartition if not exist')
		Layout.SetViewSize( 500, 250 );
		
		cancelado = app.InspectObj(prop,'','Add To Partition',4,False)

		if not cancelado:
			if app.GetValue(usenew) == True:
				partition = app.GetValue(newpartition)
			else:
				partition = app.GetValue(existpartition)
				partition = PARTITIONS[int(partition)*2]
			if app.GetValue(allpasses) == True:
				for Pass in AllPasses:
					Passes.AddItems(Pass)
			else:
				for obj in selection:
					if obj.type == "Pass":
						Passes.AddItems (obj)
			if partition == "":
				app.LogMessage( "No se ha Escrito Ninguna Particion",2)
			else:	
				passCount = Passes.Count
				if passCount == 0:
					Passes.AddItems(scene.ActivePass)
				for eachPass in Passes:
					for element in app.EnumelEments(eachPass):
						if element.type == "Partitions":
							partitions = app.EnumelEments(element)
							if str(eachPass) + "." + partition in str(partitions):
								app.MoveToPartition(str(eachPass) + "." + partition, Objects, eachPass)
								print 'En el pase ' + str(eachPass.name) + ' la particion ' + str(partition) + ' ya existia y se han añadido a ella:' + str(ObjectsName)
							else:
								if usenew.Value == True:
									app.CreatePartition(str(eachPass), str(partition))
									app.MoveToPartition(str(eachPass) + "." + partition, Objects, eachPass)
									print 'En el pase ' + str(eachPass.name) + ' se ha ceado la particion ' + str(partition) + ' y se han añadido a ella:' + str(ObjectsName)	
								else:
									if create.Value == True:
										app.CreatePartition(str(eachPass), str(partition))
										app.MoveToPartition(str(eachPass) + "." + partition, Objects, eachPass)
										print 'En el pase ' + str(eachPass.name) + ' se ha ceado la particion ' + str(partition) + ' y se han añadido a ella:' + str(ObjectsName)		
									else:
										if addtoBG.Value== True:
											app.MoveToPartition(str(eachPass) + ".background_objects_partition", Objects, eachPass)
											print 'En el pase ' + str(eachPass.name) + ' se han añadido a la particion background_objects_partition:' + str(ObjectsName)
										else:
											print 'En el pase ' + str(eachPass.name) + ' no se han movido de su particion:' + str(ObjectsName)
		app.DeleteObj(prop)
	return true
def PC_Set_Camera_MultiPass_Execute(  ):

	app.LogMessage("Set_Camera_MultiPass_Execute called",c.siVerbose)

	scene = app.ActiveProject.ActiveScene
	sceneRoot = scene.Root.Children
		
	AllCameras = []
	AllPasses = []

	Cameras = app.ActiveSceneRoot.FindChildren( '', "camera" )

	for i,cam in enumerate(Cameras):
		AllCameras.append(cam.name)
		AllCameras.append(i)
	for Pass in scene.Passes:
		AllPasses.append(Pass.name)
		
	
	prop = app.ActiveSceneRoot.AddProperty ("CustomProperty", False, "PC_Set Camera Multipass")
	
	All = prop.AddParameter3('All_Passes',c.siBool)
	
	for Pass in AllPasses:
		Passparam = prop.AddParameter3(Pass,c.siBool)

	Cam = prop.AddParameter3('Camera',c.siString)
		
	Layout=prop.PPGLayout
	Layout.Clear()

	Layout.AddEnumControl('Camera',AllCameras,'Select Camera',c.siControlCombo)
	Layout.AddItem('All_Passes','All Passes',c.siControlCheck)
	
	for Pass in AllPasses:
		Layout.AddItem(Pass,Pass,c.siControlCheck)
	Layout.Language = "Python"
	Layout.Logic = cameraLogic

	cancelado = app.InspectObj(prop,'','Set Camera',4,False)
	if not cancelado:
		Camera = app.GetValue(Cam)
		Camera = AllCameras[int(Camera)*2]
		TruePasses=[]
		FalsePasses=[]
		All = app.GetValue(All)
		if All == True:
			TruePasses = AllPasses
		else:
			for param in prop.Parameters:
				if param.value == True:
					TruePasses.append(param.name)
				elif param.value == False:
					FalsePasses.append(param.name)
		for Pass in TruePasses:
			app.SetValue('Passes.'+Pass+'.Camera',Camera)
			print 'En el Pase ' + str(Pass) + ' se ha añadido la Camara '+str(Camera)+' para Render'	# 
	app.DeleteObj (prop)		

	return true

def PC_Store_Custom_Channel_Execute(  ):
	ADSHADER = app.CreateShaderFromProgID
	SELECTION = win32com.client.Dispatch( "XSI.Collection" )
	SELECTION.AddItems (app.SELECTION)

	if len(SELECTION) > 0:
		MATERIALES =  Get_Materials(SELECTION)
		if len(MATERIALES)>0:
			TYPES = ['Color','0','Shadow','1','Arnold Ambient Oclusion','2','Mental Ambient Oclusion','3','Custom ProgID','4']

			PROP = app.ActiveSceneRoot.AddProperty ("CustomProperty", False, "")
			###Add Parameters ###
			###BASICS###
			NEW_CHANNEL = PROP.AddParameter3('New_Channel',11,False, '', '', False,False)
			EXISTING_CHANNEL = PROP.AddParameter3('Existing_Channel',8,'', '', '', False,False)
			CHANEL_PARAM = PROP.AddParameter3('Channel',8,'My Custom Channel', '', '', False,False)
			CHANEL_PARAM.Enable(False)
			RAY_TYPE = PROP.AddParameter3('Store_with_Ray_Type',8,'0', '', '', False,False)
			COMPONENT = PROP.AddParameter3('Components_to_Store',8,'0', '', '', False,False)
			TYPE = PROP.AddParameter3('Store',8,0, '', '', False,False)
			####COLOR
			ColorR,ColorG,ColorB,ColorA = PROP.AddParameter3('ColorR',5,0, 0, 1, False,False),PROP.AddParameter3('ColorG',5,0, 0, 1, False,False),PROP.AddParameter3('ColorB',5,0, 0, 1, False,False),PROP.AddParameter3('ColorA',5,0, 0, 1, False,False)
			###SHADOW
			SHADOW_MIN = PROP.AddParameter3('SHADOW_Minimum_Intensity',5,0, 0, 1, False,False)
			SHADOW_MAX = PROP.AddParameter3('SHADOW_Maximum_Intensity',5,1, 0, 1, False,False)
			SHADOW_RGB = PROP.AddParameter3('SHADOW_RGB',11,False, '', '', False,False)
			SHADOW_CAST = PROP.AddParameter3('SHADOW_cast_on_visible_faces',11,False, '', '', False,False)
			###Arnold AO
			ASAMPLES = PROP.AddParameter3('ASamples',5,3, 0, 16, False,False)
			ASPREAD = PROP.AddParameter3('ASpread',5,1, 0, 1, False,False)
			ANEAR = PROP.AddParameter3('ANear',5,0, 0, 100, False,False)
			AFAR = PROP.AddParameter3('AFar',5,100, 0, 200, False,False)
			AFALLOFF = PROP.AddParameter3('AFallof',5,0, 0, 1, False,False)
			AINVERT = PROP.AddParameter3('AInvert_Normals',11,False, '', '', False,False)
			###Mental AO
			MSAMPLES = PROP.AddParameter3('MSamples',5,16, 0, 1000, False,False)
			MSPREAD = PROP.AddParameter3('MSpread',5,0.8, 0, 1, False,False)
			MMAXIMUM = PROP.AddParameter3('MMaximum',5,0, 0, 20, False,False)
			MREFLECTIVE = PROP.AddParameter3('MReflective',11,False, '', '', False,False)
			MOUTPUT = PROP.AddParameter3('MOutput_Mode',8,'0', '', '', False,False)
			MALPHA = PROP.AddParameter3('MAlpha',11,False, '', '', False,False)
			####Custom ProgId
			PROGIDARNOLDLIST= PROP.AddParameter3('ArnoldShaders',8,'', '', '', False,False)
			PROGIDLIST= PROP.AddParameter3('AllShaders',8,'', '', '', False,False)
			WRITE =  PROP.AddParameter3('WriteProgID',11,True, '', '', False,False)
			PROGID = PROP.AddParameter3('CustomProgID',8,'ArnoldCoreShaders.utility.1.0', '', '', False,False)
			PROGIDPARAMS =  PROP.AddParameter3('Set_Attributes',8,PROGIDPARAMSEXPLAIN , '', '', False,False)
			PROGIDGETP =  PROP.AddParameter3('Get_Attributes',8,'' , '', '', False,False)
			###Set Layout ###
			Layout = PROP.PPGLayout
			Layout.Clear()
			Store_In_Channel_Basic_Tab(Layout)
			Store_In_Channel_Color_Tab(Layout)
			Layout.Language = "Python"
			Layout.Logic = CustomChannelLogic
			
			cancelado = app.InspectObj(PROP,'','Store Color In Channel',4,False)
			
			if not cancelado:
				CUSTOMCHANNELS,CUSTOMCHANNELSLIST = GetCustomChannels()
				if NEW_CHANNEL.Value == True:
					CHANNEL_NAME = CHANEL_PARAM.Value 
				else:
					if EXISTING_CHANNEL.Value != '': 
						CHANNEL_NAME = CUSTOMCHANNELS[int(EXISTING_CHANNEL.Value)].Name
					else:
						CHANNEL_NAME = ''
				if CHANNEL_NAME != '':
					Exist = False
					for CHANEL in app.EnumElements('Passes.RenderOptions.Channels'):
						if CHANNEL_NAME.lower() == CHANEL.Name.lower():
							Exist = True
							ExistingChannel = CHANEL
					if Exist == True:
						RCHANEL = ExistingChannel.Name
					else:
						RCHANEL = app.CreateRenderChannel(CHANNEL_NAME, "siRenderChannelColorType", "")
					for MATERIAL in MATERIALES:
						SURFACE = MATERIAL.surface
						SHADER = SURFACE.Source.Parent
						SHADER_OUTPUT = SURFACE.Source
						if 'Color4Passthrough' in SHADER.ProgID:
							COLORPASS = SHADER
						else:
							COLORPASS = ADSHADER("SIUtilityShaders.Color4Passthrough.1.0",str(MATERIAL), "Color4_Passthrough")
							COLORPASS.input.Source = SHADER_OUTPUT
							SURFACE.Source = COLORPASS
							
						STORECOLOR = ADSHADER("Softimage.sib_color_storeinchannel.1.0", str(MATERIAL), "Store_Color_in_Channel")
						STORECOLOR.Name,STORECOLOR.channel,STORECOLOR.raytype,STORECOLOR.component = 'Store_'+RCHANEL,RCHANEL,int(RAY_TYPE.Value),int(COMPONENT.Value)
						
						app.SIAddArrayElement(str(COLORPASS.channels))
						ITEM = app.EnumElements(COLORPASS.Channels)(len(app.EnumElements(COLORPASS.Channels))-1)
						ITEM.Source = STORECOLOR
						##COLOR
						if TYPE.Value ==  '0':
							STORECOLOR.input.red,STORECOLOR.input.green,STORECOLOR.input.blue,STORECOLOR.input.alpha= ColorR.Value,ColorG.Value,ColorB.Value,ColorA.Value
						##SHADOW
						if TYPE.Value ==  '1':
							SHADOW = ADSHADER("Softimage.sib_illum_shadowmaterial.1.0", str(MATERIAL), "Shadow")
							SHADOW.min,SHADOW.max,SHADOW.rgb,SHADOW.shadowvisible = SHADOW_MIN.Value,SHADOW_MAX.Value,SHADOW_RGB.Value,SHADOW_CAST.Value
							STORECOLOR.input.Source = SHADOW
						##AAO	
						if TYPE.Value ==  '2':
							AO = ADSHADER("ArnoldCoreShaders.ambient_occlusion.1.0", str(MATERIAL), "Arnold_Ambient_Oclusion")
							AO.samples,AO.spread,AO.near_clip,AO.far_clip,AO.falloff,AO.invert_normals = ASAMPLES.Value,ASPREAD.Value,ANEAR.Value,AFAR.Value,AFALLOFF.Value,AINVERT.Value
							STORECOLOR.input.Source = AO
						##MAO	
						if TYPE.Value ==  '3':
							AO = ADSHADER("Softimage.XSIAmbientOcclusion.1.0", str(MATERIAL), "Mental_Ambient_Oclusion")
							AO.samples,AO.spread,AO.max_distance,AO.reflective,AO.output_mode,AO.occlusion_in_alpha =MSAMPLES.Value,MSPREAD.Value,MMAXIMUM.Value,MREFLECTIVE.Value,MOUTPUT.Value,MALPHA.Value
							STORECOLOR.input.Source = AO
						##CUSTOMPROGID
						if TYPE.Value == '4':
							CustomShader = ADSHADER(PROGID.Value,str(MATERIAL),'')
							exec PROGIDPARAMS.Value
							STORECOLOR.input.Source = CustomShader
				else:
					app.LogMessage('Insert a valid Fbuffer',4)
			app.DeleteObj(PROP)
		
		else:
			app.LogMessage ('Select at least one Valid Material Container',4)
			app.LogMessage ('Valid Objects are: Geometries, Materials, Groups, Partitions',4)
	else:
		app.LogMessage ('Select at least one Valid Material Container',4)
		app.LogMessage ('Valid Objects are: Geometries, Materials, Groups, Partitions',4)


def PC_Arnold_Framebuffer_Manager_Execute(  ):
	app.SITOA_CreateRenderChannels()
	LISTA = ["Depth","Arnold_Direct_Diffuse","Arnold_Indirect_Diffuse","Arnold_Direct_Specular","Arnold_Indirect_Specular",'Arnold_Motion_Vector',"Arnold_Emission","Arnold_Alpha","Arnold_Opacity","Arnold_Refraction",'Arnold_Refraction_Opacity',"Arnold_Reflection","Arnold_SSS"]
	prop = FrameBuffer_Managers_Prop()
	FrameBuffer_Managers_BasicTab(prop)
	for element in LISTA:
		prop.AddParameter3('All_Passes_'+str(element), 11,0,0,0,0)
	FrameBuffer_Managers_PerPass_Tab(prop,LISTA)
	Layout = prop.PPGLayout
	Layout.Language = 'Python'
	Layout.Logic=ArnoldFbufferLogic
	Cancelado = app.InspectObj ( prop ,"", "Arnold Framebuffer Manager", c.siModal, False )
	if not Cancelado:
		FrameBuffer_Managers_DoIt(prop)
	app.DeleteObj (prop)		
	return true
def PC_Custom_Framebuffer_Manager_Execute(  ):
	CUSTOMCHANNELS=GetCustomChannels()[0]
	LISTA=[]
	for ch in CUSTOMCHANNELS:
		LISTA.append(ch.name)
	prop = FrameBuffer_Managers_Prop()
	FrameBuffer_Managers_BasicTab(prop)
	for element in LISTA:
		prop.AddParameter3('All_Passes_'+str(element), 11,0,0,0,0)
	FrameBuffer_Managers_PerPass_Tab(prop,LISTA)
	Layout = prop.PPGLayout
	Layout.Language = 'Python'
	Layout.Logic=CustomFbufferLogic
	Cancelado = app.InspectObj ( prop ,"", "Custom Framebuffer Manager", c.siModal, False )
	if not Cancelado:
		FrameBuffer_Managers_DoIt(prop)
	app.DeleteObj (prop)		
	return true


def PC_MultiPass_Capture_Execute(  ):
	PASSES =[Pass for Pass in app.Selection if Pass.Type == 'Pass']
	if len(PASSES) > 0:
		SCENERATE = app.GetValue("PlayControl.Rate")
		ViewportCapture = app.Dictionary.GetObject("ViewportCapture")
		projectPath= Application.ActiveProject.path
		currpath = app.GetValue("ViewportCapture.FileName")
		splitPath = currpath.split('\\')
		if splitPath[0] == 'Render_Pictures':
			splitPath[0] = '[Project Path]/Render_Pictures'
		currpath= '\\'.join(splitPath[:-1])
		currpath = XSIUtils.ResolveTokenString(currpath,0,False)
		prop = app.ActiveSceneRoot.AddProperty ("CustomProperty", False, "")
		Path = prop.AddParameter3('Path',8,currpath)
		Format = prop.AddParameter3('Format',8,'.jpeg')
		Padd = prop.AddParameter3('Padding',8,'.#')
		Width = prop.AddParameter3('Width',3,720,0,100000,False,False)
		Height = prop.AddParameter3('Height',3,720/1.777,0,100000,False,False)
		Height.Enable( False )
		OVerrHeight = prop.AddParameter3('OVerrHeight',11,False,0,1,False,False)
		FRate = prop.AddParameter3('FRate',5,SCENERATE,0,100000,False,False)
		Launch = prop.AddParameter3('Launch',11,True,0,1,False,False) 
		OpenGL = prop.AddParameter3('OpenGL',11,False,0,1,False,False) 
		Layout = prop.PPGLayout
		Layout.Clear()

		Layout.AddGroup('Path')
		PA=Layout.addItem('Path','Path',c.siControlFolder)
		PA.SetAttribute(c.siUINoLabel,True)
		Layout.AddRow()
		Layout.AddSpacer(1,0)
		P=Layout.addItem('Padding','Padding',c.siString)
		P.LabelMinPixels = 5
		P.SetAttribute(c.siUICX,50)
		F=Layout.addItem('Format','Format',c.siString)
		F.LabelMinPixels = 10
		F.SetAttribute(c.siUICX,70)
		Layout.EndRow()
		Layout.EndGroup()

		Layout.AddRow()
		Layout.AddGroup('Size')
		Layout.AddRow()
		Layout.AddStaticText('Image Size:')
		W=Layout.addItem('Width','',c.siControlNumber)
		Layout.AddStaticText('X')
		H=Layout.addItem('Height','',c.siControlNumber)
		Layout.AddStaticText('Override Camera Pict Ratio',100,50)
		O=Layout.addItem('OVerrHeight','',c.siControlCheck)
		Layout.EndRow()
		Layout.EndGroup()
		#Layout.AddSpacer(0.01,0.01)
		Layout.EndRow()

		Layout.AddRow()

		G=Layout.AddGroup()
		G.SetAttribute(c.siUIShowFrame,False)
		Layout.AddRow()
		Layout.AddStaticText('Launch Flipbook When Done',200)
		L=Layout.addItem('Launch','',c.siControlCheck)
		Layout.EndRow()
		Layout.AddRow()
		Layout.AddStaticText('OpenGL Anti-Aliasing',200)
		OP=Layout.addItem('OpenGL','',c.siControlCheck)
		Layout.EndRow()
		Layout.EndGroup()

		Layout.AddGroup()
		Layout.AddRow()
		Layout.AddStaticText('Frame Rate:')
		FR=Layout.addItem('FRate','',c.siControlNumber)
		Layout.EndRow()
		Layout.EndGroup()

		Layout.EndRow()

		for P in [W,H,FR,O,L,OP]:
			P.SetAttribute(c.siUINoLabel,True)
			P.SetAttribute(c.siUINoSlider,True)
			P.SetAttribute(c.siUICX,50)
			P.LabelMinPixels = 1

		Layout.SetViewSize(500,300)

		cancelado = app.InspectObj(prop,'','MultiCapture',4,False)
		if not cancelado:
			vm=app.Desktop.ActiveLayout.FindView('vm')
			viewport = vm.GetAttributeValue('focusedviewport')
			initcam= vm.GetAttributeValue('activecamera:'+viewport)
			Path,Format,Width,FRate,Padding,Launch,OpenGL = Path.Value,Format.Value,Width.Value,FRate.Value,Padd.Value,Launch.Value,OpenGL.Value
			for Pass in PASSES:
				app.SetCurrentPass(Pass)
				vm.SetAttributeValue('activecamera:'+viewport,'Render Pass')
				Start,End = Pass.FrameStart.Value,Pass.FrameEnd.Value
				Cam = app.ActiveSceneRoot.FindChild(str(Pass.Camera.Value))
				Height = Width / Cam.aspect.Value
				for i in app.EnumElements(ViewportCapture):
					if i.name == 'Start Frame':
						i.Value = Start
					if i.name == 'End Frame':
						i.Value = End
					if i.name == 'File Name':
						i.Value = Path+'\\'+Pass.name+Format
					if i.name == 'Width':
						i.Value = Width
					if i.name == 'Height':
						i.Value = Height
					if i.name == 'Frame Rate':
						i.Value = FRate
					if i.name == 'Padding':
						i.Value = '(fn)'+Padding+'(ext)'
					if i.name == 'Launch Flipbook':
						i.Value = Launch
					if i.name == 'OpenGL Anti-Aliasing':
						if OpenGL == True:
							i.Value = 16
						else:
							i.Value = 1
				app.CaptureViewport(ord(viewport)%32,0)
			vm.SetAttributeValue('activecamera:'+viewport,initcam)
		app.DeleteObj(prop)
	else:
		app.LogMessage( "Selecciona al menos un Pase",2)
def PC_SetPlayControlFromPass_Execute():
	Start_Frame = Application.GetCurrentPass().FrameStart.Value
	End_Frame = Application.GetCurrentPass().FrameEnd.Value
	Application.SetValue("PlayControl.Key", Start_Frame, "")
	Application.SetValue("PlayControl.In",Start_Frame, "")
	Application.SetValue("PlayControl.Out",End_Frame, "")
def PC_SendRendertoMuster_Execute():
	import os,sys,subprocess,win32com ,fileinput,Tools
	from subprocess import call
	from win32com.client import constants as c
	reload(Tools)
	app = Application
	######SCENE DATA###################################################################
	scene = app.ActiveProject.ActiveScene
	scenename = scene.Parameters('Name').Value
	SceneRenderOutput=app.GetValue("Passes.RenderOptions.OutputDir")
	SceneStart=app.GetValue("Passes.RenderOptions.FrameStart")
	SceneEnd= app.GetValue("Passes.RenderOptions.FrameEnd")
	scenePath = app.ActiveProject.ActiveScene.Parameters('Filename').Value
	#############USER DATA###################################################
	conect= PC_ConectToMuster()
	arg,err = conect[0]
	NEWDEFAULT =conect[1]
	if not err:
		LogsFold = app.Commands( "PC_SendRendertoMuster" ).OriginPath.replace('Application','Data').replace('Plugins','Preferences')
		if not os.path.isfile(LogsFold+'PC_SendToMuster_Templates.txt'):
			PC_MusterTemplates(arg,err)
		if not os.path.isfile(LogsFold+'PC_SendToMuster_Pools.txt'):
			PC_MusterPools(arg,err)
		Templates=PC_ReadMusterLogs('PC_SendToMuster_Templates.txt')
		Pools = PC_ReadMusterLogs('PC_SendToMuster_Pools.txt')
		#Jobs = PC_ReadMusterLogs('PC_SendToMuster_Jobs.txt')
		######PASS DATA############################################################################
		CurrentPass = app.GetCurrentPass()
		SelecteddPasses=[o for o in app.Selection if o.Type == 'Pass']
		PASSES= ['All Passes','0','Current Pass','1','Selected Passes','2'] if len(SelecteddPasses) > 0 else ['All Passes','0','Current Pass','1']
		####PROPERTY PAGE###########################################################PROPERTY PAGE####################################################################################################################################
		prop = scene.Root.AddProperty('CustomProperty',False,'Send To Muster')
		SceneProp=prop.AddParameter3('Scene',8,scenePath,'','',False,True)
		RenderOutputProp=prop.AddParameter3('RenderOutput',8,SceneRenderOutput)
		OverrideName = prop.AddParameter3('OverrideName',11,False,False)
		JobProp=prop.AddParameter3('JobName',8,'[Pass]')
		TypeProp= prop.AddParameter3('Passes',8,'0')
		JobPerPassProp = prop.AddParameter3('JobPerPass',11,True)
		SkipProp= prop.AddParameter3('Skip',11,True)
		OverrideFramesProp = prop.AddParameter3('OverrideFrames',11)
		StartProp= prop.AddParameter3('StartFrame',3,SceneStart)
		EndProp= prop.AddParameter3('EndFrame',2,SceneEnd)
		PaketProp = prop.AddParameter3('PaketSize',2,1,1,100)
		PriorityProp = prop.AddParameter3('Priority',2,90,0,200)
		
		GRANJAPROPS=[]
		for i,param in enumerate(['Granja_AllEnable','Rack1Enable','Rack2Enable','Rack3Enable']):
			v = False if i != 1 else True
			p = prop.AddParameter3(param,11,v)
			GRANJAPROPS.append(p)
		#####USER_EDITABLE_PARAMS##################################################

		EditModeProp = prop.AddParameter3('EditMode',11,0)
		for i,param in enumerate(['Granja_All','Rack1','Rack2','Rack3','Server','User','EngineID','Pool','MRTool','Password']):
			i = i+1 if i>= 4 else i
			p= prop.AddParameter3(param,8,NEWDEFAULT[i],'','',False,False)
			p.Enable(False)
			GRANJAPROPS.append(p)
	
		for param in [StartProp,EndProp,JobProp]:
			param.Enable(False)
		for param in prop.Parameters:
			param.Animatable = False

		#######LAYOUT#################################################################LAYOUT#######################################
		Layout = prop.PPGLayout
		Layout.Language='Python'
		Layout.Clear()
		Layout.AddGroup('Names')
		SC=Layout.AddItem('Scene',)
		SC.SetAttribute(c.siUINoLabel,True)
		Layout.AddRow()
		OF=Layout.AddItem('OverrideName','JobName')
		JN=Layout.AddItem('JobName')
		OF.SetAttribute(c.siUIWidthPercentage,20)
		JN.SetAttribute(c.siUIWidthPercentage,80)
		JN.SetAttribute(c.siUINoLabel,True)
		Layout.EndRow()
		Layout.AddItem('RenderOutput','',c.siControlFolder)
		Layout.EndGroup()
		TYPE=Layout.AddEnumControl('Passes',PASSES)
		Layout.AddItem('JobPerPass')
		Layout.AddGroup('Frames')
		Layout.AddItem('Skip')
		Layout.AddItem('OverrideFrames')
		Layout.AddRow()
		Layout.AddItem('Priority')
		Layout.AddItem('PaketSize')
		Layout.EndRow()
		Layout.AddRow()
		Layout.AddItem('StartFrame')
		Layout.AddItem('EndFrame')
		Layout.EndRow()
		Layout.EndGroup()
		
		Layout.AddGroup('Encender Granja')
		for param in ['Granja_AllEnable','Rack1Enable','Rack2Enable','Rack3Enable']:
			Layout.AddItem(param,param.replace('Enable',''))
		Layout.EndGroup()
		
		
		Layout.AddTab('Settings')
		Layout.AddItem('EditMode')
		Layout.AddGroup('MusterTags')
		for param in ['Server','User','Password']:
			Layout.AddItem(param,param)
		#print Templates
		Layout.AddEnumControl('EngineID',Templates)
		Layout.AddEnumControl('Pool',Pools)
		Layout.EndGroup()
		Layout.AddGroup('RenderFarm')
		for param in ['MRTool','Granja_All','Rack1','Rack2','Rack3']:
			Layout.AddItem(param,param)
		Layout.EndGroup()
		Layout.AddRow()
		for btn in ['SaveDeffaults','RestoreDeffaults','UpdatePools_Templates']:
			Layout.AddButton(btn)
		Layout.EndRow()
		
		Layout.Logic = '''
import os,sys,fileinput,shutil,shlex,Tools
app = Application 
o = PPG.InspectedObjects
prop = app.ActiveSceneRoot.GetPropertyFromName2(o)
selfpath = os.path.dirname(app.Commands( "PC_SendRendertoMuster" ).OriginPath)
path = app.Commands( "PC_SendRendertoMuster" ).OriginPath + 'Temp'
DEFAULTPREFS = os.path.dirname(selfpath)+'\Modules\Deffaults\PC_SendToMuster_DeffaultPrefs.txt'
USERPREFS = XSIUtils.Environment( 'XSI_USERHOME' )+r'\Data\Preferences\PC_SendToMuster_UserPrefs.txt'
def Passes_OnChanged():
	if not prop.Parameters('OverrideName').Value:
		if prop.Parameters('Passes').Value == '0':
			if prop.Parameters('JobPerPass').Value:
				prop.Parameters('JobName').Value = '[Pass]'
			else:
				prop.Parameters('JobName').Value = '[Scene]'
		elif prop.Parameters('Passes').Value == '1':
			prop.Parameters('JobName').Value = str(app.GetCurrentPass().Name)
		elif prop.Parameters('Passes').Value == '2':
			prop.Parameters('JobName').Value = '[Pass]'
	if prop.Parameters('Passes').Value == '0' or prop.Parameters('Passes').Value == '2':
		prop.Parameters('StartFrame').Value = app.GetValue("Passes.RenderOptions.FrameStart")
		prop.Parameters('EndFrame').Value = app.GetValue("Passes.RenderOptions.FrameEnd")
		prop.Parameters('JobPerPass').Enable(True)
	elif prop.Parameters('Passes').Value == '1':
		prop.Parameters('StartFrame').Value = app.GetCurrentPass().FrameStart.Value
		prop.Parameters('EndFrame').Value = app.GetCurrentPass().FrameEnd.Value
	if prop.Parameters('Passes').Value == '1' or prop.Parameters('Passes').Value == '2':
		prop.Parameters('JobPerPass').Enable(False)
		prop.Parameters('JobPerPass').Value = True
def JobPerPass_OnChanged():
	if not prop.Parameters('OverrideName').Value:
		if prop.Parameters('Passes').Value == '0':
			if prop.Parameters('JobPerPass').Value :
				prop.Parameters('JobName').Value = '[Pass]'
			else:
				prop.Parameters('JobName').Value = '[Scene]'
def OverrideName_OnChanged():
	if prop.Parameters('OverrideName').Value:
		prop.Parameters('JobName').Enable(True)
	else:
		prop.Parameters('JobName').Enable(False)
		if prop.Parameters('Passes').Value == '0':
			if prop.Parameters('JobPerPass').Value:
				prop.Parameters('JobName').Value = '[Pass]'
			else:
				prop.Parameters('JobName').Value = '[Scene]'
		elif prop.Parameters('Passes').Value == '1':
			prop.Parameters('JobName').Value = str(app.GetCurrentPass().Name)
		elif prop.Parameters('Passes').Value == '2':
			prop.Parameters('JobName').Value = '[Pass]'
def OverrideFrames_OnChanged():
	if prop.Parameters('OverrideFrames').Value:
		for param in [prop.Parameters('StartFrame'),prop.Parameters('EndFrame')]:
			param.Enable(True)
	else:
		for param in [prop.Parameters('StartFrame'),prop.Parameters('EndFrame')]:
			param.Enable(False)
		if prop.Parameters('Passes').Value == '0' or prop.Parameters('Passes').Value == '2':
			prop.Parameters('StartFrame').Value = app.GetValue("Passes.RenderOptions.FrameStart")
			prop.Parameters('EndFrame').Value = app.GetValue("Passes.RenderOptions.FrameEnd")
		elif prop.Parameters('Passes').Value == '1':
			prop.Parameters('StartFrame').Value = app.GetCurrentPass().FrameStart.Value
			prop.Parameters('EndFrame').Value = app.GetCurrentPass().FrameEnd.Value
def Granja_AllEnable_OnChanged():
		for param in [prop.Parameters('Rack1Enable'),prop.Parameters('Rack2Enable'),prop.Parameters('Rack3Enable')]:
			if prop.Parameters('Granja_AllEnable').Value:
				param.Enable(False)
				param.Value = False
			else:
				param.Enable(True)
				if param.Name == 'Rack1Enable':
					param.Value = True
''' + Tools.MusterPrefferencesLogic					

		#########################################################################################################################################
		Cancel = app.InspectObj(prop,'PC_Send Render to Muster','',4,False)
		if not Cancel:

			##############Get Data from Property#######
			propparams = prop.Parameters
			app.setValue("Passes.RenderOptions.OutputDir",propparams('RenderOutput').Value)
			Passes,PassesNames,passall= [],[],False
			SCENE =  propparams('Scene').Value.replace( r'\\abastor\Comun','Z:')
			SKIP = '-skip on' if propparams('Skip').Value else ''
			StartFrame,EndFrame = propparams('StartFrame').Value,propparams('EndFrame').Value
			PAKETSIZE ,PRIORITY,MRTOOL,SERVER,USER,PASWORD,ENGINE= str(propparams('PaketSize').Value),str(propparams('Priority').Value),propparams('MRTool').Value,propparams('Server').Value,propparams('User').Value,propparams('Password').Value,propparams('EngineID').Value
			Pools = PC_ReadMusterLogs('PC_SendToMuster_Pools.txt')
			POOL = Pools[Pools.index(propparams('Pool').Value)-1]
			#####Try to save Scene########		
			try:	
				if os.path.isfile(propparams('Scene').Value.replace('.scn','.lock')):
					os.remove(propparams('Scene').Value.replace('.scn','.lock'))
				app.SaveSceneAs(SCENE)	
				app.LogMessage( 'Scene saved at: '+SCENE,8)
			except:
				app.LogMessage( 'Not Posible to Save',4)
			######Define Passes##########
			if propparams('Passes').Value == '0':
				if propparams('JobPerPass').Value == True:
					for Pass in scene.Passes:
						Passes.append(Pass)
						PassesNames.append(Pass.Name)
				else:
						PassesNames.append('all')
						passall = True
			elif propparams('Passes').Value == '1':
				Passes.append(CurrentPass)
				PassesNames.append(CurrentPass.Name)
			elif propparams('Passes').Value == '2':
				for Pass in SelecteddPasses:
					Passes.append(Pass)
					PassesNames.append(Pass.Name)
			#####Do The Job Per Pass#####
			for i,PSS in enumerate(PassesNames):
				JOBNAME = XSIUtils.ResolveTokenString(propparams('JobName').Value,0,False,['Pass','Scene'],[PSS,scenename])
				#######Define Start/End Frame#####
				PASS,STARTFRAME,ENDFRAME ='all', str(StartFrame),str(EndFrame)
				if not passall:
					PASS = PSS
					if not propparams('OverrideFrames').Value:
						STARTFRAME,ENDFRAME = str(Passes[i].FrameStart.Value),str(Passes[i].FrameEnd.Value)
				##CUSTOM TOKEN SETUP###
				TOKENS =  ['MRTOOL','SERVER','MUSER','PASWORD','ENGINE','POOL','JOBNAME','FILE','STARTFRAME','ENDFRAME','PAKETSIZE','PASS','SKIP','PRIORITY']
				RESOLVE = [MRTOOL,SERVER,USER,PASWORD,ENGINE,POOL,JOBNAME,SCENE,STARTFRAME,ENDFRAME,PAKETSIZE,PASS,SKIP,PRIORITY]
				###BASIC MUSTER FLAGS###
				TOKENFILE=''' "[MRTOOL]" -port 9781 -s [SERVER] -u [MUSER] -b -e [ENGINE] -pool [POOL] -n "[JOBNAME]" -f "[FILE]" -sf [STARTFRAME] -ef [ENDFRAME] -pk [PAKETSIZE] -pr [PRIORITY] -bf 1 -add  "-pass [PASS] [SKIP]" '''
				RESOLVEDFILE = XSIUtils.ResolveTokenString( TOKENFILE, 0, False, TOKENS, RESOLVE )
				app.LogMessage('sended cmd: '+RESOLVEDFILE,8)
				##SEND JOB
				arg =  shlex.split(RESOLVEDFILE)
				p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				error = list(p.communicate())[1]
				if error != '':
					app.LogMessage(error,2)
				else:
					print 'Job send to Muster as: ',JOBNAME
			##########################################################ENCENDER GRANJA###################################
			PC_EncenderGranja(GRANJAPROPS[0].Value,GRANJAPROPS[1].Value,GRANJAPROPS[2].Value,GRANJAPROPS[3].Value,GRANJAPROPS[4].Value,GRANJAPROPS[5].Value,GRANJAPROPS[6].Value,GRANJAPROPS[7].Value)
		app.DeleteObj(prop)
