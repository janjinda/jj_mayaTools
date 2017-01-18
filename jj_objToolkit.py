import maya.cmds as mc
from PySide import QtCore, QtGui
import os
import re


class ObjToolkit(object):
    def __init__(self):

        """ This is a class comment"""

        self.newGeoList = []
        self.dirItems = []
        self.suffix = '_geo'
        self.caption = None
        self.fileMode = None
        self.okCaption = None
        self.filePath = None
        self.fileName = None
        self.geoName = None
        self.newGeoName = None
        self.selection = []
        self.importedFile = []

    def dialogPop(self):

        # Opens dialog based on functions settings

        self.filePath = mc.fileDialog2(fileMode=self.fileMode, caption=self.caption, dialogStyle=2,
                                       okCaption=self.okCaption, fileFilter="Waveform OBJ (*.obj *.OBJ)")

    def importSingle(self, *args):

        # Defines single file import variables and runs dialogPop function

        self.caption = "Single OBJ import"
        self.fileMode = 1  # 1 returns single file, 2 returns directory
        self.okCaption = "Import"

        self.dialogPop()

        self.importedFile = mc.file(self.filePath, i=True, type="OBJ", ignoreVersion=True, renameAll=True,
                                    mergeNamespacesOnClash=False, options="mo=0", pr=True, returnNewNodes=True)

        for name in self.filePath:
            lastName = name.split("/")[-1]

        self.fileName = lastName[0:-4]
        self.fileName = re.sub('[^0-9a-zA-Z]', '_', self.fileName)
        self.geoName = self.fileName + "_polySurface1"

        self.cleanup()

        self.rename()

        mc.select(clear=True)

    def importBatch(self, *args):

        # Defines directory import variables and runs dialogPop function

        self.caption = "Batch OBJ import"
        self.fileMode = 2  # 1 returns single file, 2 returns directory
        self.okCaption = "Import"

        self.dialogPop()

        self.dirItems += [each for each in os.listdir(self.filePath[0]) if
                          each.endswith('.obj') or each.endswith('.OBJ')]

        for each in self.dirItems:
            self.importedFile = mc.file(('%s/%s' % (self.filePath[0], each)), i=True, type="OBJ", ignoreVersion=True,
                                        renameAll=True,
                                        mergeNamespacesOnClash=False, options="mo=0", pr=True, returnNewNodes=True)

            self.fileName = each[0:-4]
            self.fileName = re.sub('[^0-9a-zA-Z]', '_', self.fileName)
            self.geoName = self.fileName + "_polySurface1"

            self.cleanup()

            self.rename()

            self.newGeoList.append(self.newGeoName)

            mc.select(clear=True)

    def importSingleBShape(self, *args):

        self.selection = mc.ls(selection=True)

        self.importSingle()
        blend = mc.blendShape(self.newGeoName, self.selection)[0]
        mc.setAttr('%s.%s' % (blend, self.newGeoName), 1)
        mc.delete(self.newGeoName)
        mc.delete(self.selection, constructionHistory=True)

    def importBatchBShape(self, *args):

        self.importBatch()

        for geo in self.newGeoList:
            blend = mc.blendShape(geo, geo[0:-1])[0]
            mc.setAttr('%s.%s' % (blend, geo), 1)
            mc.delete(geo)
            mc.delete(geo[0:-1], constructionHistory=True)

    def exportBatch(self, *args):

        self.caption = "Batch OBJ export"
        self.fileMode = 3
        self.okCaption = "Export"
        self.selection = mc.ls(selection=True)

        self.dialogPop()

        for geo in self.selection:
            mc.select(geo)
            mc.file('%s/%s.%s' % (self.filePath[0], geo[0:-4], 'obj'), force=True,
                    options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', type='OBJexport', es=True)

    def cleanup(self):

        typeList = []

        # Creates list of a type of each node created on import

        for item in self.importedFile:
            objType = mc.objectType(item)
            typeList.append(objType)

        # Combines selection and type list

        combineList = zip(self.importedFile, typeList)
        combineDict = dict(combineList)

        # Finds keys with chosen values and removes sufficient keys from the dictionary

        for key in combineDict.keys():
            itemType = ['transform', 'mesh', 'groupId']
            if combineDict[key] in itemType:
                del combineDict[key]

        # Deletes all objects which remained in the dictionary

        mc.delete(combineDict.keys())

        # Assigns initialShadingGroup to imported object

        mc.sets(self.geoName, forceElement='initialShadingGroup')
        mc.polySoftEdge(self.geoName, angle=30)
        mc.delete(self.geoName, constructionHistory=True)

    def rename(self):

        self.newGeoName = mc.rename(self.geoName, '%s%s' % (self.fileName, self.suffix))


class ObjToolkitUI(object):
    windowName = "ObjToolkitUI"

    def __init__(self):
        self.toolkit = ObjToolkit()

        if mc.window(self.windowName, query=True, exists=True):
            mc.deleteUI(self.windowName)

        mc.window(self.windowName, title="JJ Obj Toolkit")

        self.buildUI()

    def buildUI(self):
        columnMain = mc.columnLayout(rowSpacing=10)

        mc.frameLayout(label='Import', collapsable=False)
        mc.columnLayout(rowSpacing=2)

        iSingleBtn = mc.button(label="Import Single OBJ", w=175, h=25, c=self.toolkit.importSingle)
        iBatchBtn = mc.button(label="Import Batch OBJ", w=175, h=25, c=self.toolkit.importBatch)
        iSingleBSBtn = mc.button(label="Import Single OBJ as bShape", w=175, h=25, c=self.toolkit.importSingleBShape)
        iBatchBSBtn = mc.button(label="Import Batch OBJ as bShape", w=175, h=25, c=self.toolkit.importBatchBShape)

        mc.setParent(columnMain)

        mc.frameLayout(label='Export', collapsable=False)
        mc.columnLayout(rowSpacing=2)

        eBatchBtn = mc.button(label="Export Batch OBJ", w=175, h=25, c=self.toolkit.exportBatch)


class ObjToolkitUIQt(QtGui.QDialog):

    def __init__(self):

        super(ObjToolkitUIQt, self).__init__()

        self.setWindowTitle('OBJ Toolkit')
        self.toolkit = ObjToolkit()

        self.buildUI()

    def buildUI(self):
        layout = QtGui.QVBoxLayout(self)

        iSingleBtn = QtGui.QPushButton('Import Single OBJ')
        iSingleBtn.clicked.connect(self.toolkit.importSingle)
        layout.addWidget(iSingleBtn)

        iBatchBtn = QtGui.QPushButton('Import Batch OBJ')
        iBatchBtn.clicked.connect(self.toolkit.importBatch)
        layout.addWidget(iBatchBtn)

        iSingleBSBtn = QtGui.QPushButton('Import Single OBJ as bShape')
        iSingleBSBtn.clicked.connect(self.toolkit.importSingleBShape)
        layout.addWidget(iSingleBSBtn)

        iBatchBSBtn = QtGui.QPushButton('Import Batch OBJ as bShape')
        iBatchBSBtn.clicked.connect(self.toolkit.importBatchBShape)
        layout.addWidget(iBatchBSBtn)

        eBatchBtn = QtGui.QPushButton('Export Batch OBJ')
        eBatchBtn.clicked.connect(self.toolkit.exportBatch)
        layout.addWidget(eBatchBtn)


def showUI(type="cmds"):
    if type == "cmds":

        # maya cmds UI
        ui = ObjToolkitUI()
        mc.showWindow(ui.windowName)

    elif type == "qt":

        # Qt UI
        ui = ObjToolkitUIQt()
        ui.show()

    return ui
