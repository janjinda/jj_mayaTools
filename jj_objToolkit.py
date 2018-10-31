"""
JJ Obj Toolkit is a simple set of tools for easier manipulation with Obj files in Maya.

Author: Jan Jinda
Email: janjinda@janjinda.com
Version: 1.0.0
"""

# Usual imports
import maya.cmds as cmds
import os
import re


class ObjToolkit(object):

    def __init__(self):
        """Defining initial variables for file dialog."""

        self.caption = None
        self.fileMode = None
        self.okCaption = None

    def dialogOpen(self):
        """Open dialog based on requirements."""

        self.dialogPath = cmds.fileDialog2(fileMode=self.fileMode, caption=self.caption, dialogStyle=2,
                                           okCaption=self.okCaption, fileFilter="Waveform OBJ (*.obj *.OBJ)")[0]

    def importObj(self, *args):
        """Main import function"""
        # Import command
        self.importedFile = cmds.file(self.filePath, i=True, type="OBJ", ignoreVersion=True, renameAll=True,
                                      mergeNamespacesOnClash=False, options="mo=0", pr=True, returnNewNodes=True)

        # Get file name create temp geo name
        fileName = re.sub('[^0-9a-zA-Z]', '_', (self.filePath.split('/')[-1])[0:-4])
        geoName = fileName + "_polySurface1"

        # Create list of a type of each node created on import
        typeList = []
        for item in self.importedFile:
            objType = cmds.objectType(item)
            typeList.append(objType)

        # Combine selection and type list
        combineList = zip(self.importedFile, typeList)
        combineDict = dict(combineList)

        # Find keys with chosen values and removes sufficient keys from the dictionary
        for key in combineDict.keys():
            itemType = ['transform', 'mesh', 'groupId']
            if combineDict[key] in itemType:
                del combineDict[key]

        # Delete all objects which remained in the dictionary
        cmds.delete(combineDict.keys())

        # Assign initialShadingGroup to imported object
        cmds.sets(geoName, forceElement='initialShadingGroup')
        cmds.polySoftEdge(geoName, angle=30)
        cmds.delete(geoName, constructionHistory=True)

        # Rename all imported geometries based on filename
        self.newGeoName = ("%s" % fileName)

        if not self.newGeoName in cmds.ls():
            self.newGeoName = cmds.rename(geoName, self.newGeoName)
        else:
            self.newGeoName = cmds.rename(geoName, ("%s_01" % self.newGeoName))

        # Add new geo to the list
        self.newGeoList.append(self.newGeoName)

    def exportObj(self, *args):
        """Main export function."""
        # Export command
        cmds.file('%s/%s.%s' % (self.dialogPath, self.fileName, 'obj'), force=False,
                  options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', type='OBJexport', es=True)

    def importSingle(self, *args):
        """"Imports a single Obj file."""
        # Set dialog properties
        self.caption = "Single OBJ import"
        self.fileMode = 1  # 1 returns single file, 2 returns directory
        self.okCaption = "Import"

        # Open dialog and store filepath for usage in import function
        self.dialogOpen()
        self.filePath = self.dialogPath

        # Run main import function
        self.newGeoList = []
        self.importObj()
        cmds.select(clear=True)

        cmds.select(self.newGeoList)

    def importBatch(self, *args):
        """Imports all Obj files."""
        # Set dialog properties
        self.caption = "Batch OBJ import"
        self.fileMode = 2  # 1 returns single file, 2 returns directory
        self.okCaption = "Import"

        # Open dialog and store filepath for usage in import function
        self.dialogOpen()
        # List files in the folder obtained from dialog
        self.dirItems = [each for each in os.listdir(self.dialogPath) if
                         each.endswith('.obj') or each.endswith('.OBJ')]

        # Run the import function for every file in the folder
        self.newGeoList = []
        for item in self.dirItems:
            self.filePath = os.path.join(self.dialogPath, item)
            self.importObj()

        cmds.select(self.newGeoList)

    def importSingleBShape(self, *args):
        """Imports a single Obj, applies it as a blend shape on previously selected geometry."""
        sel = cmds.ls(selection=True)
        # Check if just one object is selected
        if len(sel) == 1:
            # Perform import function
            self.importSingle()
            # Blend between selected and imported geo
            blend = cmds.blendShape(self.newGeoName, sel)[0]
            cmds.setAttr('%s.%s' % (blend, self.newGeoName), 1)
            cmds.delete(self.newGeoName)
            cmds.delete(sel, constructionHistory=True)
            cmds.select(sel)

    def importBatchBShape(self, *args):
        """Imports entire directory of Obj files, applies it them as a blend shape based on geometry names."""
        # Perform batch import function
        self.importBatch()

        for geo in self.newGeoList:
            # Find equivalent geo in the scene for every imported geo and blend 
            blend = cmds.blendShape(geo, geo[0:-3])[0]
            cmds.setAttr('%s.%s' % (blend, geo), 1)
            cmds.delete(geo)
            cmds.delete(geo[0:-3], constructionHistory=True)

    def exportSingle(self, *args):
        """Exports selected geometry."""
        # Set dialog properties
        self.caption = "Single OBJ export"
        self.fileMode = 2
        self.okCaption = "Export"

        self.dialogOpen()

        # Filter non geo objects from selection
        sel = cmds.ls(selection=True, long=False)
        self.validGeos = []
        for geo in sel:
            if cmds.objectType(cmds.listRelatives(geo, shapes=True)[0]) == 'mesh':
                self.validGeos.append(geo)

        cmds.select(self.validGeos)
        self.fileName = self.validGeos[0]

        # Run main export function
        self.exportObj()

    def exportBatch(self, *args):
        """Exports all selected geometries as a Obj files."""
        # Set dialog properties
        self.caption = "Batch OBJ export"
        self.fileMode = 3
        self.okCaption = "Export"
        sel = cmds.ls(selection=True, long=False)

        self.dialogOpen()

        # Filter non geo objects from selection
        self.validGeos = []
        for geo in sel:
            if cmds.objectType(cmds.listRelatives(geo, shapes=True)[0]) == 'mesh':
                self.validGeos.append(geo)

        # Run main export function
        for geo in self.validGeos:
            cmds.select(geo)
            self.fileName = geo
            self.exportObj()

        cmds.select(self.validGeos)


class ObjToolkitUI(object):
    """Creates toolkit dialog using Maya UI."""

    windowName = "ObjToolkitUI"

    def __init__(self):
        self.toolkit = ObjToolkit()

        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName, title="JJ Obj Toolkit")

        self.buildUI()

    def buildUI(self):
        columnMain = cmds.columnLayout(rowSpacing=10)

        cmds.frameLayout(label='Import', collapsable=False)
        cmds.columnLayout(rowSpacing=2)

        iSingleBtn = cmds.button(label="Import Single OBJ", w=175, h=25, c=self.toolkit.importSingle)
        iBatchBtn = cmds.button(label="Import Batch OBJ", w=175, h=25, c=self.toolkit.importBatch)
        iSingleBSBtn = cmds.button(label="Import Single OBJ as bShape", w=175, h=25, c=self.toolkit.importSingleBShape)
        iBatchBSBtn = cmds.button(label="Import Batch OBJ as bShape", w=175, h=25, c=self.toolkit.importBatchBShape)

        cmds.setParent(columnMain)

        cmds.frameLayout(label='Export', collapsable=False)
        cmds.columnLayout(rowSpacing=2)

        eSingleBtn = cmds.button(label="Export Single OBJ", w=175, h=25, c=self.toolkit.exportSingle)
        eBatchBtn = cmds.button(label="Export Batch OBJ", w=175, h=25, c=self.toolkit.exportBatch)


def showUI():
    """Function to open toolkit window. Maya UI or Qt can be chosen using parameter."""

    # maya cmds UI
    ui = ObjToolkitUI()
    cmds.showWindow(ui.windowName)

    return ui
