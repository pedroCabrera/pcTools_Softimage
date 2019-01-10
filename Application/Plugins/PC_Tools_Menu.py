import win32com.client
from win32com.client import constants
import sys
app = Application
null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "PEDRITO"
	in_reg.Name = "PC_Tools_Menu"
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterMenu( constants.siMenuMainTopLevelID , "PC Tools", true )
	in_reg.RegisterMenu( constants.siMenuTbRenderRenderID , "PC Render Tools", true )
	in_reg.RegisterMenu( constants.siMenuTbRenderPassPartitionID  , "PC Partition Tools", true )
	in_reg.RegisterMenu( constants.siMenuICENodeContextID,'PC_Multi_Compound_Exporter_Menu',False)
	in_reg.RegisterMenu(constants.siMenuMainFileSceneID,"PC_Multi_Model_Exporter_Menu",false,false)
	in_reg.RegisterMenu(constants.siMenuMainFileSceneID,"PC_Multi_Model_Importer_Menu",false,false)
	in_reg.RegisterMenu(constants.siMenuTbGetPrimitiveCurveID,"PC_Ice Curve",false,false)
	
	in_reg.RegisterMenu(constants.siMenuVMCameraID,"Gradient Bg",false,false)

	##XPOP MENU
	in_reg.RegisterCommand("pcXpopMenu","pcXpopMenu")
	
	##SHOTGUN_MENU
	in_reg.RegisterMenu( constants.siMenuMainTopLevelID , "Shotgun", true )

	
	#RegistrationInsertionPoint - do not remove this line
	##Append Workwgroup
	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	app.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true
	
def PC_Multi_Compound_Exporter_Menu_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	cmd = oMenu.AddCallbackItem2("PC_Multi_Compound_Exporter","OnPC_Multi_Compound_ExporterMenuClicked")
	return true
def GradientBg_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCallbackItem("Set Gradient Bg","OnSetGradientMenuClicked")	
	return true
def OnSetGradientMenuClicked( in_ctxt ):
	app.InspectObj("preferences.agGradientBackground")

def PCRenderTools_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem("PC_Arnold Framebuffer Manager","PC_Arnold_Framebuffer_Manager")
	oMenu.AddCommandItem("PC_Custom Framebuffer Manager","PC_Custom_Framebuffer_Manager")
	oMenu.AddCommandItem("PC_Store Custom Channel","PC_Store_Custom_Channel")
	return true
	
def PCPartitionTools_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem("PC_Add To Partition MultiPass","PC_Add_To_Partition_MultiPass")
	oMenu.AddCommandItem("PC_Set Camera MultiPass","PC_Set_Camera_MultiPass")
	oMenu.AddCommandItem("PC_MultiPass Capture","PC_MultiPass_Capture")
def PC_Multi_Model_Exporter_Menu_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem("PC_Multi Model Exporter","PC_Multi_Model_Exporter")
def PC_Multi_Model_Importer_Menu_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem("PC_Multi Model Importer","PC_Multi_Model_Importer")
def PC_IceCurve_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	oMenu.AddCommandItem("PC_Ice Curve","PC_Ice_Curve")
	
def Shotgun_Init( in_ctxt):
	oMenu = in_ctxt.Source
	###tasks####
	tasksMenu=oMenu.AddSubMenu("Tasks")
	tasksMenu.AddCommandItem("Render Passes Template","PC_Create_Template_Task_From_Passes")
def PCTools_Init( in_ctxt ):
	oMenu = in_ctxt.Source
	################
	##Tools Submenu##
	ToolsMenu=oMenu.AddSubMenu("Tools")
	##Properties##
	PPGMenu = ToolsMenu.AddSubMenu('Properties')
	PPGMenu.AddCallbackItem("PC_Wire Color","OnPC_Wire_ColorMenuClicked")
	PPGMenu.AddCallbackItem("PC_Utility Buttons","OnUtility_ButtonsMenuClicked")
	PPGMenu.AddCallbackItem("Xtreme Renamer","OnXTRM_Renamer_ToolClicked")
	##Utilities##
	UTMenu = ToolsMenu.AddSubMenu('Utilities')
	UTMenu.AddCommandItem("PC_Convert Models To Nulls","PC_ConvertModelsToNulls")
	UTMenu.AddCommandItem("PC_Ass Geo Switcher","PC_Ass_Geo_Switcher")
	UTMenu.AddCommandItem("PC_Multi Compound Exporter","PC_Multi_Compound_Exporter")
	##Multi Pass##
	PassMenu = ToolsMenu.AddSubMenu('Multi Pass Tools')
	PassMenu.AddCommandItem("PC_Set Camera MultiPass","PC_Set_Camera_MultiPass")
	PassMenu.AddCommandItem("PC_Add To Partition MultiPass","PC_Add_To_Partition_MultiPass")
	PassMenu.AddCommandItem("PC_MultiPass Capture","PC_MultiPass_Capture")
	##Render##
	RenderMenu = ToolsMenu.AddSubMenu('Render Tools')
	RenderMenu.AddCommandItem("PC_Arnold Framebuffer Manager","PC_Arnold_Framebuffer_Manager")
	RenderMenu.AddCommandItem("PC_Custom Framebuffer Manager","PC_Custom_Framebuffer_Manager")
	RenderMenu.AddCommandItem("PC_Store Custom Channel","PC_Store_Custom_Channel")
	#####################
	##Pimitives Submenu##
	PrimMenu=oMenu.AddSubMenu("Primitives")
	
	PC_PRIMS=['PC_Cubesphere','PC_Disc','PC_Polygon','PC_Basic_Gear']
	for prim in PC_PRIMS:
		PrimMenu.AddCommandItem(prim,prim)
	#########	
	##Polymesh Submenu##
	PolyMenu=oMenu.AddSubMenu("Polymesh")
	
	PolyMenu.AddCommandItem("PC_Custom Thickness","PC_Custom_Thickness")
	############
	##PointCloud Submenu##
	PCloudMenu=oMenu.AddSubMenu("Point Cloud")
	
	PCloudMenu.AddCommandItem("PC_Create_Point_Cloud_From_Positions","PC_Create_Point_Cloud_From_Positions")
	PCloudMenu.AddCommandItem("PC_Set_Particle_Colored_Shape","PC_Set_Particle_Colored_Shape")
	#############
	##Curves Submenu##
	CvMenu=oMenu.AddSubMenu("Curves")
	
	CvMenu.AddCommandItem("PC_Nurbs To Curves","PC_Nurbs_To_Curves")
	CvMenu.AddCommandItem("PC_Curve By Nulls","PC_Curve_By_Nulls")
	############
	##Rigging Submenu##
	RigMenu=oMenu.AddSubMenu("Rigging")
	
	RigMenu.AddCommandItem("PC_Path Rig","PC_Path_Rig")
	RigMenu.AddCommandItem("PC_Auto Rigging Car","PC_Auto_Rigging_Car")
	
	
	return true
	
def OnPC_Wire_ColorMenuClicked( in_ctxt ):
	sp= app.ActiveProject.ActiveScene.Root.Properties
	SceneProp=[]
	for element in sp:
		SceneProp.append(element.name)
	if 'PC_Wire_Color' in SceneProp :
		app.InspectObj('PC_Wire_Color','','',3)
	else:
		app.AddProp("PC_Wire_Color",'Scene_Root')
	return 1
def OnUtility_ButtonsMenuClicked( in_ctxt ):
		sp= app.ActiveProject.ActiveScene.Root.Properties
		SceneProp=[]
		for element in sp:
			SceneProp.append(element.name)
		if 'Utility_Buttons' in SceneProp :
			app.InspectObj('Utility_Buttons','','',3)
		else:
			app.AddProp("Utility_Buttons",'Scene_Root')
		return 1
def OnXTRM_Renamer_ToolClicked( in_ctxt ):
		SceneRoot = app.ActiveSceneRoot
		SceneRoot.AddProperty("XTRM_Renamer")
		app.InspectObj("XTRM_Renamer")
def OnPC_Multi_Compound_ExporterMenuClicked(in_ctxt):
		N = in_ctxt.GetAttribute("Target")
		OLD = [i for i in app.Selection]
		app.DeselectAll()
		for n in N:
			if 'Operator' in str(n.Categories):
				app.AddToSelection(n)
		app.PC_Multi_Compound_Exporter()
		app.SelectObj(OLD)

def pcXpopMenu_Init(in_ctxt):
	oCmd = in_ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = true
	return true	
def pcXpopMenu_Execute():
	popup = Application.XPOP()
		

	popup.AddHeader( "Tools", 0x8844CC)
	##Properties##
	PPGMenu = popup.AddSubMenu('Properties')
	PPGMenu.AddItem("PC_Wire Color","OnPC_Wire_ColorMenuClicked('')")
	PPGMenu.AddItem("PC_Utility Buttons","OnUtility_ButtonsMenuClicked('')")
	PPGMenu.AddItem("Xtreme Renamer","OnXTRM_Renamer_ToolClicked('')")
	##Utilities##
	UTMenu = popup.AddSubMenu('Utilities')
	UTMenu.AddItem("PC_Convert Models To Nulls","Application.PC_ConvertModelsToNulls()")
	UTMenu.AddItem("PC_Ass Geo Switcher","Application.PC_Ass_Geo_Switcher()")
	UTMenu.AddItem("PC_Multi Compound Exporter","Application.PC_Multi_Compound_Exporter()")
	##Multi Pass##
	PassMenu = popup.AddSubMenu('Multi Pass Tools')
	PassMenu.AddItem("PC_Set Camera MultiPass","Application.PC_Set_Camera_MultiPass()")
	PassMenu.AddItem("PC_Add To Partition MultiPass","Application.PC_Add_To_Partition_MultiPass()")
	PassMenu.AddItem("PC_MultiPass Capture","Application.PC_MultiPass_Capture()")
	##Render##
	RenderMenu = popup.AddSubMenu('Render Tools')
	RenderMenu.AddItem("PC_Arnold Framebuffer Manager","Application.PC_Arnold_Framebuffer_Manager()")
	RenderMenu.AddItem("PC_Custom Framebuffer Manager","Application.PC_Custom_Framebuffer_Manager()")
	RenderMenu.AddItem("PC_Store Custom Channel","Application.PC_Store_Custom_Channel()")


	popup.AddHeader( "Modeling", 0x8844CC)
	##Pimitives Submenu##
	PrimMenu=popup.AddSubMenu("Primitives")
	PC_PRIMS=[["PC_Cubesphere",'Application.PC_Cubesphere()'],["PC_Disc",'Application.PC_Disc()'],["PC_Polygon",'Application.PC_Polygon()'],["PC_Basic_Gear",'Application.PC_Basic_Gear()']]
	for prim in PC_PRIMS:
		PrimMenu.AddItem(prim[0],prim[1])
	#########	
	##Polymesh Submenu##
	PolyMenu=popup.AddSubMenu("Polymesh")
	PolyMenu.AddItem("PC_Custom Thickness","Application.PC_Custom_Thickness()")
	############
	##PointCloud Submenu##
	PCloudMenu=popup.AddSubMenu("Point Cloud")
	PCloudMenu.AddItem("PC_Create_Point_Cloud_From_Positions","Application.PC_Create_Point_Cloud_From_Positions()")
	PCloudMenu.AddItem("PC_Set_Particle_Colored_Shape","Application.PC_Set_Particle_Colored_Shape()")
	#############
	##Curves Submenu##
	CvMenu=popup.AddSubMenu("Curves")
	CvMenu.AddItem("PC_Nurbs To Curves","Application.PC_Nurbs_To_Curves()")
	CvMenu.AddItem("PC_Curve By Nulls","Application.PC_Curve_By_Nulls()")

	popup.AddHeader( "Rigging", 0x8844CC)
	##Rigging Submenu##
	RigMenu=popup.AddSubMenu("Rigging")
	RigMenu.AddItem("PC_Path Rig","Application.PC_Path_Rig()")
	RigMenu.AddItem("PC_Auto Rigging Car","Application.PC_Auto_Rigging_Car()")

 
	#submenu1.AddItem( "&Cube", "Application.SetGlobal('icon','Cube')");	
	#submenu1.SetIcon( Application.GetGlobal("icon") )
	
	
		
	popup.origin_y = 74 # mousepointer is on "Clean-up" initially
	
	exec(popup.Track())
	return 1

def toggleGlobal(str):
	if Application.GetGlobal(str):
		Application.SetGlobal(str, 0)
	else:
		Application.SetGlobal(str, 1)

def handler(i):
	if i==1:
		Application.LogMessage("Tea")
	else:
		Application.LogMessage("Coffee")
	return 1