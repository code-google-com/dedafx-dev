#!C:/Python25/python.exe
##    Copyright (C) 2006-2009  Ben Deda
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Ben Deda
##    ben@dedafx.com

# TODO: 
# 1. needs cleanup to make all functions consistent in what path format they expect
# 2. needs doc strings for classes/functions

import win32com.client
import datetime
            
class Alienbrain(object):
    """Main class interface with Alienbrain source control"""
    
    #
    # exceptions used by this class
    #
    class InvalidConverterVersionError(Exception):
        """Invalid Converter version"""
    class ProjectLoadError(Exception):
        """Project failed to load"""
    class AlienbrainInterfaceError(Exception):
        """Alienbrain Interface not found!"""
    class UnsuccessfulCommand(Exception):
        """Ailienbrain command was unsuccessful!"""
        
    class Revision(object):            
            
            # ab returns individual components, so serialization is minimal! EASY!
            def __init__(self):
                self.revNumber = 0
                self.view = ""      #not used in AB, but here to keep it consistent between ab and starteam
                self.branchRev = "" #not used in AB, but here to keep it consistent between ab and starteam
                self.user = ""
                self._revTime = None
                self.comment = None
                
            def __set_revTime__(self, iTime):
                starttime = datetime.datetime(1601, 1,1, 0,0,0)
                #iTime on ab is in nanoseconds, convert to microseconds
                mTime = float(iTime)/10.0
                dd = datetime.timedelta(microseconds=mTime)
                self._revTime = starttime + dd
                
            def __get_revTime__(self):
                return self._revTime
                
            revTime = property( fget=__get_revTime__, fset=__set_revTime__, doc="The Revision timestamp in datetime format." )
    
    def __init__(self, sUsername, sPswd, sProject="", sServer=""):
        
        self.com_nxn = None
        self.com_param = None
        self.project = sProject
        self.server = sServer
        
        try:
            #self.nxn = win32com.client.Dispatch("NxNNamespace")
            self.com_nxn = win32com.client.Dispatch("NxNNamespace.NxNNamespaceHelper")
            self.com_param = win32com.client.Dispatch("NxNXMLHelper.NxNXMLParameter" )
        except:
            raise self.AlienbrainInterfaceError

        
        # login to the project using a read-only user account
        self.com_param.Reset()
        self.com_param.Command = "ProjectLoadEx"
        self.com_param.SetParamIn("Name", self.project) # this is the recommended way to set params, as suggested by Softimage
        self.com_param.SetParamIn("Hostname", self.server)
        
       # if ( sUsername != "" and sPswd != "" ):
        self.com_param.SetParamIn("LogonType", "1")
        self.com_param.SetParamIn("Username", sUsername)
        self.com_param.SetParamIn("Password", sPswd)
                
        self.com_nxn.RunCommand ( self.__getWorkspacePath(), self.com_param.Command, self.com_param.xml )
        if ( self.com_param.WasSuccessful ):
            pass
            #print "SUCCESS: Project loaded"
        else:
            #print "ERROR: Project failed to load"
            raise self.ProjectLoadError
        
    def __del__(self):
        try:
            if self.com_param and self.com_nxn:
                self.com_param.Reset()
                self.com_param.Command = "ProjectUnloadEx"
                self.com_param.SetParamIn("Name", self.project)
                self.com_nxn.RunCommand ( self.__getWorkspacePath(), self.com_param.Command, self.com_param.xml )
               # if self.com_param.WasSuccessful:
               #     print "Alienbrain project unloaded."
               # else:
               #     print "ERROR: ProjectUnloadEx failed!"
        except AttributeError:
            # self.com_param or self.com_nxn is not defined
            pass
        
    def __getWorkspacePath(self, sPath="", bDir=False):
        sPath = sPath.replace("/","\\")
        if ( sPath.startswith("\\\\Workspace\\" + self.project + "\\") ):
            return sPath        
        while ( sPath.startswith("\\") ):
            sPath = sPath[1:]
        while ( sPath.endswith("\\") ):
            sPath = sPath[:-1]
        ret = "\\\\Workspace\\" + self.project + "\\" + sPath
        if bDir:
            ret += "\\"
        return ret
        
          
    def getFilesOfType(self, sExt, sParentPath, recursive=True ):
        files = []
        sParentPath = self.__getWorkspacePath(sParentPath)
        sObjectPath = self.com_nxn.GetFirstChild(sParentPath)
        while sObjectPath != "":
            sPath = sParentPath + "\\" + sObjectPath
            sName = self.com_nxn.GetProperty( sPath, "Name" )
            if ( self.isItemFile(sPath) and sName.find(sExt) == (len(sName) - len(sExt)) ):
                #print sPath
                files.append( sPath )
            else:
                if ( self.isItemFolder( sPath ) and recursive ):
                    #print sPath
                    fl = self.getFilesOfType( sExt, sPath, recursive )
                    files.extend( fl )
            sObjectPath = self.com_nxn.GetNextChild(sParentPath, sObjectPath);
        return files
        
    def getFiles(self, sParentPath, recursive=True ):
        files = []
        sObjectPath = self.com_nxn.GetFirstChild(sParentPath)
        while sObjectPath != "":
            sPath = sParentPath + "\\" + sObjectPath
            if ( self.isItemFile(sPath) ):
                files.append( sPath )
            else:
                if ( self.isItemFolder( sPath ) and recursive ):
                    fl = self.getFiles( sPath, recursive )
                    files.extend( fl )
            sObjectPath = self.com_nxn.GetNextChild(sParentPath, sObjectPath);
        return files
        
    def getLocalPath(self, sPath):
        """Return the local path of the item"""
        sLocalPath = self.com_nxn.GetProperty( sPath, "LocalPath" ); 
        return sLocalPath; 
        
    def isItemShare(self,sPath):
        """Return True or False if this item is a share"""
        sObjectType = self.com_nxn.GetProperty( sPath, "NamespaceType")
        return (sObjectType.find ("\\Workspace\\DbItem\\FileFolder\\File\\Virtual\\Share") == 0 )
        
    def isItemFolder(self,sPath):
        """Return True or False if this item is a directory folder"""
        sObjectType = self.com_nxn.GetProperty( sPath, "NamespaceType")
        return (sObjectType.find ("\\Workspace\\DbItem\\FileFolder\\Folder") == 0 )
        
    def isItemOriginalFile(self,sPath):
        """Return True or False if this item is an original file"""
        return ( self.isItemFile(sPath) and not self.isItemShare(sPath) )
        
    def isItemFile(self,sPath):
        """Return True or False if this item is an original file"""
        sObjectType = self.com_nxn.GetProperty( sPath, "NamespaceType")
        return (sObjectType.find ("\\Workspace\\DbItem\\FileFolder\\File") == 0 )
        
    def itemExists(self,sPath):
        """test to see if the server item exists"""
        return (self.com_nxn.GetProperty( sPath, "Name") != "")
        
    def getShareSource(self,sSharePath):
        if ( self.isItemShare(sSharePath) ):
            return self.com_nxn.GetProperty( sSharePath, "NxNShareTargetPath")
        return sSharePath # it is an original file

    def createShare(self,sShareSource,sDestPath,sNewShareName=""):
        sShare = sShareSource
        if self.isItemShare(sShareSource):
            sShare = self.getShareSource(sShareSource)
            
        #sDestNamspace = self.com_nxn.GetProperty( sDestPath,"NamespaceType")
        if ( sShare != None ):
                    
            self.com_param.Reset()
            sCommand = "NxNShare_Create"
            self.com_param.Command = sCommand
            if ( self.isItemFolder(sDestPath) ):# assumes that the destination path exists
                self.com_param.SetParamIn("ShareFolder",sDestPath)
            self.com_param.SetParamIn("GetLatestVersion", 1)
            
                    
            self.com_nxn.RunCommand( sSharePath, sCommand, self.com_param.XML, false  )
            if self.com_param.WasSuccessful:
                print "share created"
                shareName = self.com_param.ParamOut("SharePath")
                if ( sNewShareName != "" ): # this assumes the new name is of the correct format, "name.ext"
                    #(sNewShareName.rfind(".") == len(sNewShareName)-4)
                    self.com_param.reset()
                    self.com_param.Command = "Rename"
                    self.com_param.SetParamIn( "Name", sNewShareName )
                    
            else:
                #print "FAILED to create share!"
                #raise self.UnsuccessfulCommand
                return False
                
    def getFolderList(self, sParentFolder):
        """get a list of folders contained in the parent directory"""
        folderList = []
        sParentPath = self.__getWorkspacePath(sParentFolder)
        sObjectPath = self.com_nxn.GetFirstChild(sParentPath)
        sObjectType = ""
        while (sObjectPath != ""):
            sName = self.com_nxn.GetProperty(sParentPath+sObjectPath, "Name")
            #sObjectType = self.com_nxn.GetProperty( sParentPath+sObjectPath, "NamespaceType")
            #print (sName)                        
            #if ( sObjectType.find("\\Workspace\\DbItem\\FileFolder\\Folder") == 0 ):
            if self.isItemFolder(sParentPath+sObjectPath):                    
                folderList.append(sName)
                                
            sObjectPath = self.com_nxn.GetNextChild(sParentPath, sObjectPath);
        return folderList
        
       
    def hasOriginalFiles(self, sParentPath, recursive=True):
        """check to see if any of the contained files are not shares, and return true or false"""
        sParentPath = self.__getWorkspacePath(sParentPath)
        sObjectPath = self.com_nxn.GetFirstChild(sParentPath)
        ret = False
        while (sObjectPath != ""):
            sPath = sParentPath+sObjectPath
            if self.isOriginalFile(sPath):
                return True
            else:                                        
                if ( recursive and self.isFolder(sPath) ):                
                    ret = self.hasOriginalFiles( sParentPath+sObjectPath, recursive )
                if ( ret ):
                    return ret
                
            sObjectPath = self.com_nxn.GetNextChild(sParentPath, sObjectPath);
        return False
        
    def diffDirectories(self, sSourceDir, sDestDir, recursive=True, mirror=True):
        """check to make sure that sSourceDir has the same contents of sDestDir, both in naming of the files, subfolders, and linkage if necessary"""

        # recursively walk the source directory
        sObjectPath = self.com_nxn.GetFirstChild(sSourceDir)
        while (sObjectPath != ""):
            sPath = sParentPath + sObjectPath
            
            if ( self.isFolder(sPath) and recursive ):
                # check to see if the directory exists in the destination dir
                self.diffDirectories(sSourceDir, sDestDir, recursive, mirror)
            
            sObjectPath = self.com_nxn.GetNextChild(sSourceDir, sObjectPath);
        
    def checkOut(self, sPath):
        sPath = self.__getWorkspacePath(sPath)
        self.com_param.Reset()
        self.com_param.Command = "CheckOut"
        self.com_param.SetParamIn("ShowDialog", "0")
        
        self.com_nxn.RunCommand ( sPath, self.com_param.Command, self.com_param.xml )
        return self.com_param.WasSuccessful
        
    def getLatest(self, sPath, sTargetPath):
        sPath = self.__getWorkspacePath(sPath)
        self.com_param.Reset()
        self.com_param.Command = "GetLatest"
        self.com_param.SetParamIn("ShowDialog", "0")
        self.com_param.SetParamIn("SmartGet", "1")
        if ( sTargetPath != None ):
            self.com_param.SetParamIn("DestinationPath", sTargetPath)
        self.com_param.SetParamIn("OverwriteWritable", "1")
        self.com_param.SetParamIn("OverwriteCheckedOut", "1")
        self.com_param.SetParamIn("OverwriteChangedReadonly", "1")
                
        self.com_nxn.RunCommand ( sPath, self.com_param.Command, self.com_param.xml )
        return self.com_param.WasSuccessful
        
    def addLabel(self, sPath, sLabel):
        if( sLabel == None or sPath == None ):
            return False
            
        sPath = self.__getWorkspacePath(sPath)
        sPath = self.getShareSource(sPath)
        self.com_param.Reset()
        self.com_param.Command = "VC_AddLabel"
        self.com_param.SetParamIn("Name", sLabel)
        self.com_param.SetParamIn("Comment", sLabel)
        self.com_param.SetParamIn("ShowDialog", "0")
                        
        self.com_nxn.RunCommand ( sPath, self.com_param.Command, self.com_param.xml )
        return self.com_param.WasSuccessful
        
    def hasLabel(self, sPath, sLabel):
        sPath = self.__getWorkspacePath(sPath)
        sPath = self.getShareSource(sPath)
        sHistory = sPath+"\\History"
        sChild = self.com_nxn.GetFirstChild(sHistory)
        #print sHistory, sChild
        while (sChild != "" ):
            if ( sChild == sLabel ):
                #print "label found!"
                return True
            sChild = self.com_nxn.GetNextChild(sHistory, sChild);
        self.com_param.Reset()
        self.com_param.Command = "VC_ShowHistory"
        self.com_nxn.RunCommand ( sPath, self.com_param.Command, self.com_param.xml )
        return False
        
    def getHistory(self, sPath):
        sPath = self.__getWorkspacePath(sPath)
        sPath = self.getShareSource(sPath)
        sHistory = sPath + "\\History"
        sChild = self.com_nxn.GetFirstChild(sHistory)
        hist = []
        while (sChild != "" ):
            rev = Alienbrain.Revision()
            rev.revNumber = self.com_nxn.GetProperty( sHistory+"\\"+sChild, "VersionControl_Number")
            rev.user = self.com_nxn.GetProperty( sHistory+"\\"+sChild, "VersionControl_User")
            rev.revTime = self.com_nxn.GetProperty( sHistory+"\\"+sChild, "VersionControl_Time")
            rev.comment = self.com_nxn.GetProperty( sHistory+"\\"+sChild, "VersionControl_Comment")
            hist.append(rev)
            sChild = self.com_nxn.GetNextChild(sHistory, sChild);
            
        return hist
        
    def getVersionNumber(self, sPath):
        return self.com_nxn.GetProperty( self.__getWorkspacePath(sPath), "NxN_VersionNumber")
        
    def getComment(self, sPath):
        return self.com_nxn.GetProperty( self.__getWorkspacePath(sPath), "VersionControl_Comment")
        
    def getVersion(self, sPath, sLabel, sTargetPath):
        """label and targetpath are required, and targetpath must be a dir and end with a backslash"""
        # if sPath is a directory, recursively get a file list to operate on individually
        sPath = self.__getWorkspacePath(sPath)
        files = []
        if ( self.isItemFolder(sPath) ):
            files.extend( self.getFiles(sPath) )
        else :
            files.append(sPath)
            
        for p in files:
            fs = p[len(sPath):p.rfind("\\")]
            if ( self.hasLabel(p, sLabel) ):                  
                self.com_param.Reset()
                self.com_param.Command = "VC_GetVersion"
                self.com_param.SetParamIn("Label", sLabel)
                self.com_param.SetParamIn("DestinationPath", sTargetPath+fs+"\\")
                self.com_param.SetParamIn("ShowDialog", "0")
                self.com_param.SetParamIn("OverwritePolicy", "1")
                self.com_param.SetParamIn("OverwritePolicyWritable", "1")
                self.com_param.SetParamIn("OverwritePolicyReadonlyChanged", "1")

                self.com_nxn.RunCommand ( p, self.com_param.Command, self.com_param.xml )
        return self.com_param.WasSuccessful
        
    def getProperty(self, sPath, sProperty):
        """get a named property for the path item
        
        return '' if the property is empty or not defined on this object"""
        return self.com_nxn.GetProperty( self.__getWorkspacePath(sPath), sProperty) 
    
    def getCustomAttributes(self, sPath):
        """get the custom attributes on the object"""
        attribs = []
        sPath = self.__getWorkspacePath(sPath)
        p = self.getProperty(sPath, "_NXN_Attributes_Custom")
        pa = p.split('|')
        for i in pa:
            ia = i.split(',')
            val = self.getProperty(sPath, ia[0])
            attribs.append((ia,val))
        return attribs
    
def getCatalogImages(alienbrain, rootdir):        
    files = ab.getFilesOfType('.jpg', rootdir)
    catfiles = []
    for f in files:
        s = '_cat.jpg'
        if f.find(s) == (len(f) - len(s)):
            catfiles.append(f)
    return catfiles
    
if __name__ == "__main__":
    scInterface = Alienbrain( "username", "pswd", "ProjectName", "Server")
    if not scInterface.getLatest("\\\\Workspace\\myProject\\someFolder\\someFile.txt", "c:\\someLocalPath\\someFile.txt" ):
        print "failed to get latest!"
    if not scInterface.addLabel("\\\\Workspace\\myProject\\someFolder\\someFile.txt", "label_set_by_python_script" ):
        print "add label failed!"
    
    
    p = scInterface.getCustomAttributes("\\\\Workspace\\ProjectName\\FolderName1\\SubFolder2\\somefile.txt")
    
    print "_NXN_Attributes_Custom"
    for i in p:
        print "  ", i
    
    
        

            

    