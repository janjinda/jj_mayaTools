"""
JJ Obj Toolkit is a simple set of tools for easier manipulation with Obj files in Maya.

Author: Jan Jinda
Email: janjinda@janjinda.com
Version: 1.0.0
"""

# Usual imports
import maya.cmds as cmds
import re


def dialog(fileMode, diaCaption, okCaption):
    """Open dialog based on requirements."""

    dialogPath = cmds.fileDialog2(fileMode=fileMode, caption=diaCaption, okCaption=okCaption,
                                  dialogStyle=2, fileFilter="Waveform OBJ (*.obj *.OBJ)")

    return dialogPath


def importObj(dialogPath):
    """Main import function"""
    # Import command
    selectedFiles = cmds.file(dialogPath, i=True, type="OBJ", ignoreVersion=True, renameAll=True,
                              mergeNamespacesOnClash=False, options="mo=0, lo=0", pr=True, returnNewNodes=True)

    # Get file name create temp geo name
    fileName = re.sub('[^0-9a-zA-Z]', '_', (dialogPath.split('/')[-1])[0:-4])
    tempGeoName = fileName + "_polySurface1"

    # Create list of a type of each node created on import
    typeList = []
    for i in selectedFiles:
        typeList.append(cmds.objectType(i))

    # Combine selection and type list
    combineDict = dict(zip(selectedFiles, typeList))

    # Find keys with chosen values and removes sufficient keys from the dictionary
    for key in combineDict.keys():
        exclusionType = ['transform', 'mesh', 'groupId']
        if combineDict[key] in exclusionType:
            del combineDict[key]

    # Delete all objects which remained in the dictionary
    cmds.delete(combineDict.keys())

    # Assign initialShadingGroup to imported object
    cmds.sets(tempGeoName, forceElement='initialShadingGroup')
    cmds.polySoftEdge(tempGeoName, angle=30)
    cmds.delete(tempGeoName, constructionHistory=True)

    # Rename all imported geometries based on filename
    newGeo = ("%s" % fileName)

    if newGeo not in cmds.ls():
        newGeo = cmds.rename(tempGeoName, newGeo)
    else:
        newGeo = cmds.rename(tempGeoName, ("%s_01" % newGeo))

    return newGeo


def exportObj(dialogPath, fileName):
    """Main export function."""
    # Export command
    cmds.file('%s/%s.%s' % (dialogPath, fileName, 'obj'), force=False,
              options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', type='OBJexport', es=True)
    return fileName


# noinspection PyUnusedLocal
def importSingle(*args):
    """Imports all Obj files."""
    dialogPath = dialog(fileMode=1, diaCaption="Single OBJ Import", okCaption="Import")
    newGeo = importObj(dialogPath[0])
    cmds.select(clear=True)
    print newGeo
    return newGeo


# noinspection PyUnusedLocal
def importBatch(*args):
    """Import selected Obj files"""
    dialogPath = dialog(fileMode=4, diaCaption="Batch OBJ Import", okCaption="Import")

    newGeoList = []
    for i in dialogPath:
        newGeo = importObj(i)
        newGeoList.append(newGeo)

    cmds.select(clear=True)
    return newGeoList


def bSCreate(source, target):
    blendS = cmds.blendShape(source, target)[0]
    cmds.setAttr('%s.%s' % (blendS, source), 1)
    cmds.delete(source)

    return blendS


# noinspection PyUnusedLocal
def importSingleBS(*args):
    origGeoList = cmds.ls(selection=True)
    blendSList = []

    if len(origGeoList) == 1:
        newGeo = importSingle()
        blendSList = [bSCreate(source=newGeo, target=origGeoList[0])]
        cmds.select(origGeoList)

    bSControlCreate(blendSList=blendSList, origGeoList=origGeoList)

    return origGeoList, blendSList


# noinspection PyUnusedLocal
def importBatchBS(*args):
    newGeoList = importBatch()
    origGeoList = []
    blendSList = []

    for i in newGeoList:
        origGeoList.append(i[:-3])
        blendS = bSCreate(source=i, target=i[:-3])
        blendSList.append(blendS)

    bSControlCreate(blendSList=blendSList, origGeoList=origGeoList)

    return origGeoList, blendSList


# noinspection PyUnusedLocal
def exportSingle(*args):
    dialogPath = dialog(fileMode=2, diaCaption="Single OBJ Export", okCaption="Export")

    selection = cmds.ls(selection=True)
    validGeo = []

    for i in selection:
        if cmds.objectType(cmds.listRelatives(i, shapes=True)[0]) == 'mesh':
            validGeo.append(i)

    fileName = validGeo[0]
    exportObj(dialogPath=dialogPath, fileName=fileName)

    return fileName


# noinspection PyUnusedLocal
def exportBatch(*args):
    selection = cmds.ls(selection=True)
    dialogPath = dialog(fileMode=2, diaCaption="Batch OBJ Export", okCaption="Export")

    validGeo = []
    for i in selection:
        if cmds.objectType(cmds.listRelatives(i, shapes=True)[0]) == 'mesh':
            validGeo.append(i)

    for i in validGeo:
        cmds.select(i)
        fileName = i
        exportObj(dialogPath=dialogPath, fileName=fileName)

    cmds.select(validGeo)

    return validGeo


def buildUI():
    columnMain = cmds.columnLayout(rowSpacing=10)

    cmds.frameLayout(label='Import', collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.button(label="Import Single OBJ", w=175, h=25, c=importSingle)
    cmds.button(label="Import Batch OBJ", w=175, h=25, c=importBatch)
    cmds.button(label="Import Single OBJ as bShape", w=175, h=25, c=importSingleBS)
    cmds.button(label="Import Batch OBJ as bShape", w=175, h=25, c=importBatchBS)

    cmds.setParent(columnMain)

    cmds.frameLayout(label='Import Options', labelWidth=175, collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.checkBox('deleteCHCheckbox', label='Delete History')

    cmds.setParent(columnMain)

    cmds.frameLayout(label='Export', collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.button(label="Export Single OBJ", w=175, h=25, c=exportSingle)
    cmds.button(label="Export Batch OBJ", w=175, h=25, c=exportBatch)


def showUI():
    windowName = "ObjToolkitUI"

    if cmds.window(windowName, query=True, exists=True):
        cmds.deleteUI(windowName)

    cmds.window(windowName, title="JJ OBJ Toolkit")

    buildUI()

    cmds.showWindow(windowName)


# noinspection PyUnusedLocal
def bSControlCreate(blendSList, origGeoList, *args):
    bSControlLoc = None
    bsControlAttr = None

    if not testCheckboxes():

        bSControlLoc = cmds.spaceLocator(n="bs_ctrl")[0]

        availableAttrs = cmds.listAttr(bSControlLoc, keyable=True)

        for i in availableAttrs:
            cmds.setAttr('%s.%s' % (bSControlLoc, i), lock=True, keyable=False)

        bsControlAttr = cmds.addAttr(bSControlLoc, shortName='bsAmount', longName='Blend_Shapes_Amount', defaultValue=1.0,
                                     minValue=0, maxValue=1, keyable=True)
        for i in blendSList:
            cmds.connectAttr('%s.bsAmount' % bSControlLoc, '%s.envelope' % i)

    else:
        cmds.delete(origGeoList, ch=True)

    return bSControlLoc, bsControlAttr


def testCheckboxes():
    deleteCHCheckboxV = cmds.checkBox('deleteCHCheckbox', query=True, value=True)

    return deleteCHCheckboxV
