from maya import cmds
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

        self.filePath = cmds.fileDialog2(fileMode=self.fileMode, caption=self.caption, dialogStyle=2,
                                         okCaption=self.okCaption, fileFilter="Waveform OBJ (*.obj *.OBJ)")

    def importSingle(self, *args):

        # Defines single file import variables and runs dialogPop function

        self.caption = "Single OBJ import"
        self.fileMode = 1  # 1 returns single file, 2 returns directory
        self.okCaption = "Import"

        self.dialogPop()

        self.importedFile = cmds.file(self.filePath, i=True, type="OBJ", ignoreVersion=True, renameAll=True,
                                      mergeNamespacesOnClash=False, options="mo=0", pr=True, returnNewNodes=True)

        for name in self.filePath:
            lastName = name.split("/")[-1]

        self.fileName = lastName[0:-4]
        self.fileName = re.sub('[^0-9a-zA-Z]', '_', self.fileName)
        self.geoName = self.fileName + "_polySurface1"

        self.cleanup()

        self.rename()

        cmds.select(clear=True)

    def importBatch(self, *args):

        # Defines directory import variables and runs dialogPop function

        self.caption = "Batch OBJ import"
        self.fileMode = 2  # 1 returns single file, 2 returns directory
        self.okCaption = "Import"

        self.dialogPop()

        self.dirItems += [each for each in os.listdir(self.filePath[0]) if
                          each.endswith('.obj') or each.endswith('.OBJ')]

        for each in self.dirItems:
            self.importedFile = cmds.file(('%s/%s' % (self.filePath[0], each)), i=True, type="OBJ", ignoreVersion=True,
                                          renameAll=True,
                                          mergeNamespacesOnClash=False, options="mo=0", pr=True, returnNewNodes=True)

            self.fileName = each[0:-4]
            self.fileName = re.sub('[^0-9a-zA-Z]', '_', self.fileName)
            self.geoName = self.fileName + "_polySurface1"

            self.cleanup()

            self.rename()

            self.newGeoList.append(self.newGeoName)

            cmds.select(clear=True)

    def importSingleBShape(self, *args):

        self.selection = cmds.ls(selection=True)

        self.importSingle()
        blend = cmds.blendShape(self.newGeoName, self.selection)[0]
        cmds.setAttr('%s.%s' % (blend, self.newGeoName), 1)
        cmds.delete(self.newGeoName)
        cmds.delete(self.selection, constructionHistory=True)

    def importBatchBShape(self, *args):

        self.importBatch()

        for geo in self.newGeoList:
            blend = cmds.blendShape(geo, geo[0:-1])[0]
            cmds.setAttr('%s.%s' % (blend, geo), 1)
            cmds.delete(geo)
            cmds.delete(geo[0:-1], constructionHistory=True)

    def exportBatch(self, *args):

        self.caption = "Batch OBJ export"
        self.fileMode = 3
        self.okCaption = "Export"
        self.selection = cmds.ls(selection=True)

        self.dialogPop()

        for geo in self.selection:
            cmds.select(geo)
            cmds.file('%s/%s.%s' % (self.filePath[0], geo[0:-4], 'obj'), force=True,
                      options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', type='OBJexport', es=True)

    def cleanup(self):

        typeList = []

        # Creates list of a type of each node created on import

        for item in self.importedFile:
            objType = cmds.objectType(item)
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

        cmds.delete(combineDict.keys())

        # Assigns initialShadingGroup to imported object

        cmds.sets(self.geoName, forceElement='initialShadingGroup')
        cmds.polySoftEdge(self.geoName, angle=30)
        cmds.delete(self.geoName, constructionHistory=True)

    def rename(self):

        self.newGeoName = cmds.rename(self.geoName, '%s%s' % (self.fileName, self.suffix))


class ObjToolkitUI(object):
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

        eBatchBtn = cmds.button(label="Export Batch OBJ", w=175, h=25, c=self.toolkit.exportBatch)


class ObjToolkitUIQt(QtGui.QDialog):

    def __init__(self):

        super(ObjToolkitUIQt, self).__init__()

        self.setWindowTitle('OBJ Toolkit')
        self.toolkit = ObjToolkit()

        self.settings = QtCore.QSettings('JJ', 'jjObjToolkit')
        geometry = self.settings.value('geometry', '')
        self.restoreGeometry(geometry)

        self.buildUI()

    def closeEvent(self, event):
        geometry = self.saveGeometry()
        self.settings.setValue('geometry', geometry)
        super(ObjToolkitUIQt,self).closeEvent(event)

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
        cmds.showWindow(ui.windowName)

    elif type == "qt":

        # Qt UI
        ui = ObjToolkitUIQt()
        ui.show()

    return ui
