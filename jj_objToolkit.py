"""
JJ Obj Toolkit is a simple set of tools for easier manipulation with Obj files in Maya.

Author: Jan Jinda
Email: janjinda@janjinda.com
Version: 0.0.8
"""

# Usual imports
import maya.cmds as cmds
import re

version = "0.9.5"


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
        newGeo = cmds.rename(tempGeoName, ("%s_obj" % newGeo))

    return newGeo


def exportObj(dialogPath, fileName):
    """Main export function."""
    # Export command
    cmds.file('%s/%s.%s' % (dialogPath, fileName, 'obj'), force=False,
              options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', type='OBJexport', es=True)

    return fileName


def bSCreate(source, target):
    blendS = cmds.blendShape(source, target)[0]
    cmds.setAttr('%s.%s' % (blendS, source), 1)
    cmds.delete(source)

    return blendS


def bSControlCreate(blendSList, origGeoList, *args):
    bSControlLoc = None
    bsControlAttr = None

    if not testCheckboxes():

        bSControlLoc = cmds.spaceLocator(n="bShape_ctrl")[0]

        availableAttrs = cmds.listAttr(bSControlLoc, keyable=True)

        for i in availableAttrs:
            cmds.setAttr('%s.%s' % (bSControlLoc, i), lock=True, keyable=False)

        bsControlAttr = cmds.addAttr(bSControlLoc, shortName='bsAmount', longName='Blend_Shapes_Amount',
                                     defaultValue=1.0,
                                     minValue=0, maxValue=1, keyable=True)
        for i in blendSList:
            cmds.connectAttr('%s.bsAmount' % bSControlLoc, '%s.envelope' % i)

    else:
        cmds.delete(origGeoList, ch=True)

    return bSControlLoc, bsControlAttr


def importSingle(*args):
    """Imports all Obj files."""
    newGeos = []
    dialogPath = dialog(fileMode=1, diaCaption="Single OBJ Import", okCaption="Import")

    if dialogPath:
        newGeos = [importObj(dialogPath[0])]
        cmds.select(clear=True)

        print "%s OBJs were imported." % len(newGeos),

    return newGeos


def importBatch(*args):
    """Import selected Obj files"""
    newGeos = []
    dialogPath = dialog(fileMode=4, diaCaption="Batch OBJ Import", okCaption="Import")

    if dialogPath:
        for i in dialogPath:
            newGeo = importObj(i)
            newGeos.append(newGeo)
        cmds.select(clear=True)

        print "%s OBJs were imported." % len(newGeos),

    return newGeos


def importSingleBS(*args):
    newGeos = []
    origGeos = cmds.ls(selection=True)
    blendSList = []
    bSControlLoc = None

    if len(origGeos) == 1:
        newGeos = importSingle()

        if newGeos:
            source = newGeos[0]
            target = origGeos[0]

            if cmds.polyEvaluate(source, v=True) == cmds.polyEvaluate(target, v=True):
                blendSList = [bSCreate(source=source, target=target)]
                bSControlLoc = bSControlCreate(blendSList=blendSList, origGeoList=origGeos[0])[0]
                cmds.select(bSControlLoc)

            print "%s OBJs were imported. %s OBJs were blend shaped." % (len(newGeos), len(blendSList)),

    return newGeos, blendSList, bSControlLoc


def importBatchBS(*args):
    sceneGeos = cmds.listRelatives(cmds.ls(type='mesh'), parent=True)
    validGeos = []
    newGeos = importBatch()
    blendSList = []
    bSControlLoc = None

    if newGeos:
        for i in newGeos:
            origGeo = i.replace('_obj', '')
            if origGeo in sceneGeos:
                validGeos.append(origGeo)
                blendS = bSCreate(source=i, target=origGeo)
                blendSList.append(blendS)

        if blendSList:
            bSControlLoc = bSControlCreate(blendSList=blendSList, origGeoList=validGeos)[0]

        if bSControlLoc:
            print "%s OBJs imported. %s OBJs blend shaped. bs_ctrl created." % (len(newGeos), len(blendSList)),
        else:
            print "%s OBJs imported. %s OBJs blend shaped. History deleted." % (len(newGeos), len(blendSList)),

    return newGeos, blendSList, bSControlLoc


def exportSingle(*args):
    selection = cmds.ls(selection=True)
    dialogPath = dialog(fileMode=2, diaCaption="Single OBJ Export", okCaption="Export")
    validGeos = []

    if dialogPath:
        for i in selection:
            allMeshes = cmds.listRelatives(cmds.listRelatives(i, allDescendents=True, type='mesh'), parent=True)

            for ii in allMeshes:
                validGeos.append(ii)

        fileName = validGeos[0]
        exportObj(dialogPath=dialogPath[0], fileName=fileName)
        print ('%s geometries exported to OBJ.' % len(validGeos)),

    return validGeos


def exportBatch(*args):
    selection = cmds.ls(selection=True)
    dialogPath = dialog(fileMode=2, diaCaption="Batch OBJ Export", okCaption="Export")
    validGeos = []

    if dialogPath:
        for i in selection:
            allMeshes = cmds.listRelatives(cmds.listRelatives(i, allDescendents=True, type='mesh'), parent=True)

            for ii in allMeshes:
                validGeos.append(ii)

        for i in validGeos:
            cmds.select(i)
            fileName = i
            exportObj(dialogPath=dialogPath[0], fileName=fileName)

        cmds.select(validGeos)

        print ('%s OBJ exported.' % len(validGeos)),

    return validGeos


def buildUI():

    mainColor = [0.0438, 0.4032, 0.553]
    width = 150

    columnMain = cmds.columnLayout(rowSpacing=10)

    cmds.frameLayout(label='Import OBJ', backgroundColor=mainColor, collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.button(label="Import Single", w=width, h=25, c=importSingle)
    cmds.button(label="Import Batch", w=width, h=25, c=importBatch)
    cmds.button(label="Import Single as bShape", w=width, h=25, c=importSingleBS)
    cmds.button(label="Import Batch as bShape", w=width, h=25, c=importBatchBS)

    cmds.setParent(columnMain)

    cmds.frameLayout(label='Import Options', collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.checkBox('deleteCHCheckbox', label='Delete History', width=width)

    cmds.setParent(columnMain)

    cmds.frameLayout(label='Export OBJ', backgroundColor=mainColor, collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.button(label="Export Single", w=width, h=25, c=exportSingle)
    cmds.button(label="Export Batch", w=width, h=25, c=exportBatch)

    cmds.setParent(columnMain)

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, (width/2)), (2, (width/2))])
    cmds.text(label='Jan Jinda', align='left')
    cmds.text(label='')
    cmds.text(label='<a href="http://janjinda.com">janjinda.com</a>', hyperlink=True, align='left')
    cmds.text(label=('v%s' % version), align='right')


def showUI():
    windowName = "ObjToolkitUI"

    if cmds.window(windowName, query=True, exists=True):
        cmds.deleteUI(windowName)

    cmds.window(windowName, title="JJ OBJ Toolkit")

    buildUI()
    cmds.showWindow(windowName)

    return windowName


def testCheckboxes():
    deleteCHCheckboxV = cmds.checkBox('deleteCHCheckbox', query=True, value=True)

    return deleteCHCheckboxV
