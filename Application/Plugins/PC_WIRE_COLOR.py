import win32com.client
from win32com.client import constants as c
import Tools
from Tools import *
reload (Tools)
null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "PEDRITO"
	in_reg.Name = "PC_Wire_Color"
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterProperty("PC_Wire_Color")
	return true
def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),c.siVerbose)
	return true
	
def AddMultiParameter3(prop,lista,type):
	params = []
	for i in lista:
		p = prop.AddParameter3(str(i),type)
		params.append(p)
	return params
	
def PC_Wire_Color_Define( in_ctxt ):
	prop = in_ctxt.Source
	objs = [str(i.fullname) for i in Application.Selection]
	print objs
	Objs = prop.AddParameter3('Objs',8,str(objs))
	AddMultiParameter3(prop,['Red','Green','Blue'],5)
	Gradient = prop.AddParameter3('Enable_Gradient',11)
	AddMultiParameter3(prop,['Red1','Green1','Blue1'],5)
	AddMultiParameter3(prop,['Red2','Green2','Blue2'],5)
	return true
def PC_Wire_Color_DefineLayout( in_ctxt ):
	Layout = in_ctxt.Source
	Layout.Clear()
	Layout.AddGroup('Color')
	Layout.AddGroup('Single Color')
	Layout.AddItem('Red','Sigle Color',c.siControlRGB )
	Layout.EndGroup()
	Layout.AddGroup('Gradient',True,)
	Layout.AddItem('Enable_Gradient','Enable Gradient',c.siControlCheck )
	Layout.AddItem('Red1','First Color',c.siControlRGB )
	Layout.AddItem('Red2','Second Color',c.siControlRGB )
	Layout.EndGroup()
	Layout.AddButton('Clear','Clear Color')
	Layout.EndGroup()
	Layout.AddGroup('Selection',True,)
	Layout.AddRow()
	Layout.AddButton('Update')
	Layout.AddButton('Select')
	Layout.AddButton('SelectSimilar')
	Layout.EndRow()
	Layout.EndGroup()
	return true
def PC_Wire_Color_OnInit():
	Application.LogMessage("PC_Wire_Color_OnInit called",c.siVerbose)
	
#########
def PC_Wire_Color_Enable_Gradient_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	if prop.parameters('Enable_Gradient').Value == True:
		WireColor_Gradient_Color(prop)
	else:
		WireColor_Single_Color(prop)
def PC_Wire_Color_Clear_OnClicked():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Clear_Color(prop)
def PC_Wire_Color_SelectSimilar_OnClicked():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_SelectSimilar()
def PC_Wire_Color_Update_OnClicked():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	OParam = prop.parameters('Objs')
	OBJS=Application.Selection
	objs=[str(O.fullname) for O in OBJS]
	OParam.Value = [str(objs) if len(objs)>= 1 else ''][0]
	if prop.parameters('Enable_Gradient').Value == True:
		WireColor_Gradient_Color(prop)
	else:
		WireColor_Single_Color(prop)
	Application.DeselectAll()
def PC_Wire_Color_Select_OnClicked():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	OParam = prop.parameters('Objs')
	ObjectList=	WireColorSplitPropNames(OParam.Value)
	Application.SelectObj(ObjectList)
def PC_Wire_Color_Red_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Single_Color(prop)
def PC_Wire_Color_Green_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Single_Color(prop)
def PC_Wire_Color_Blue_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Single_Color(prop)
def PC_Wire_Color_Red1_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Gradient_Color(prop)			
def PC_Wire_Color_Green1_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Gradient_Color(prop)			
def PC_Wire_Color_Blue1_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Gradient_Color(prop)			
def PC_Wire_Color_Red2_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Gradient_Color(prop)			
def PC_Wire_Color_Green2_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Gradient_Color(prop)			
def PC_Wire_Color_Blue2_OnChanged():
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	WireColor_Gradient_Color(prop)			
def PC_Wire_Color_OnClosed( ):
	Application.LogMessage("PC_Wire_Color_OnClosed called",c.siVerbose)
	prop = Application.ActiveProject.ActiveScene.Root.Properties('PC_Wire_Color')
	Application.DeleteObj(prop)
