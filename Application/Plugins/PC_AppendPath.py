import win32com.client
import shutil, string, os
from win32com.client import constants
import sys,os
null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
	in_reg.Author = "Pedrito"
	in_reg.Name = "PC_AAappendPath"
	in_reg.Major = 1
	in_reg.Minor = 0

	#Instert Modules Folder in Python Path and prints Avaliable Modules
	AddonLocation = in_reg.OriginPath
	workgroupLibFolder = str(AddonLocation).replace('Plugins','Modules')


	os.environ["OPENCV_DIR"]=workgroupLibFolder+'\vc10'
	os.environ["PATH"]=os.environ['OPENCV_DIR']+'''\bin'''+';'+os.environ["PATH"]
	if workgroupLibFolder not in sys.path :
		sys.path.append( workgroupLibFolder )
		print workgroupLibFolder +' has been added to Python Path'

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true
	

