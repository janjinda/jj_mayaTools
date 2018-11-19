# JJ Obj Toolkit is a simple set of tools for easier manipulation with Obj files in Maya.

__author__ = "Jan Jinda"
__version__ = "0.9.6"
__email__ = "janjinda@janjinda.com"
__website__ = "http://janjinda.com"

import maya.cmds as cmds
import re


def dialog(dupCheck, diaCaption, fileMode, okCaption):
    """Opens an file dialog set up based on given parameters

    Parameters:
        dupCheck (boll):
        diaCaption (str): dialog window caption
        fileMode (int): defines dialog behaviour
                        0 Any file, whether it exists or not
                        1 A single existing file
                        2 The name of a directory. Both directories and files are displayed in the dialog
                        3 The name of a directory. Only directories are displayed in the dialog
                        4 Then names of one or more existing files
        okCaption (str): caption of the OK button

    Returns:
        dialogPath (list): output selection from a dialog
    """

    # If there are meshes with the same name give warning
    if dupCheck and duplicateCheck():
        dialogPath = None
        cmds.warning("There are multiple geometries with the same name. This should be fixed first."),

    else:
        # Store dialog output to a variable
        dialogPath = cmds.fileDialog2(fileMode=fileMode, caption=diaCaption, okCaption=okCaption,
                                  dialogStyle=2, fileFilter="Waveform OBJ (*.obj *.OBJ)")

    return dialogPath


def importObj(dialogPath):
    """Main import function, removes all unnecessary nodes

    Parameters:
        dialogPath (list): input files from dialog

    Returns:
        newGeo (str): newly imported geometry
    """

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
    """Main export function

    Parameters:
        dialogPath (list): directory input from dialog
        fileName (str): file name inherited from geometry name

    Returns:
        fileName (str): file name inherited from geometry name
    """

    # File write command
    cmds.file('%s/%s.%s' % (dialogPath, fileName, 'obj'), force=False,
              options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1', type='OBJexport', es=True)

    return fileName


def duplicateCheck():
    """Main export function

     Returns:
         dupExists (bool): result of the check
     """

    # Check if there is duplicate mesh based on mayas long name
    sceneMeshes = cmds.ls(type='mesh')
    dupExists = any('|' in i for i in sceneMeshes)

    return dupExists


def bSCreate(source, target):
    """Creates blend shape deformer

        Parameters:
            source (list): blend shape source geometry
            target (str): blend shape target geometry

        Returns:
            blendS (str): name of a created blend shape deformer
    """

    blendS = cmds.blendShape(source, target)[0]
    cmds.setAttr('%s.%s' % (blendS, source), 1)
    cmds.delete(source)

    return blendS


def bSControlCreate(blendSList, origGeoList, *args):
    """Creates locator with an attribute for controlling all created blend shapes

        Parameters:
            blendSList (list): list of all created blend shapes
            origGeoList (list): list of all geometries which were blend shaped

        Returns:
            bSControlLoc (str): name of a created locator
            bsControlAttr (str): name of a created custom attribute
    """

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
    """Available for a user for importing single OBJ

        Returns:
            newGeos (list): list of all new imported geometries
    """

    newGeos = []
    dialogPath = dialog(dupCheck=False, fileMode=1, diaCaption="Single OBJ Import", okCaption="Import")

    if dialogPath:
        newGeos = [importObj(dialogPath[0])]
        cmds.select(clear=True)

        print "%s OBJs were imported." % len(newGeos),

    return newGeos


def importBatch(*args):
    """Available for a user for importing multiple OBJ

        Returns:
            newGeos (list): list of all new imported geometries
    """

    newGeos = []
    dialogPath = dialog(dupCheck=False, fileMode=4, diaCaption="Batch OBJ Import", okCaption="Import")

    if dialogPath:
        for i in dialogPath:
            newGeo = importObj(i)
            newGeos.append(newGeo)
        cmds.select(clear=True)

        print "%s OBJs were imported." % len(newGeos),

    return newGeos


def importSingleBS(*args):
    """Available for a user for importing single OBJ as a blend shape to an existing geometry

        Returns:
            newGeos (list): list of all new imported geometries
            blendSList (list): list of all created blend shapes
            bSControlLoc(str): name of a created blend shapes controller
    """

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
    """Available for a user for importing multiple OBJ as a blend shape to an existing corresponding geometries

        Returns:
            newGeos (list): list of all new imported geometries
            blendSList (list): list of all created blend shapes
            bSControlLoc(str): name of a created blend shapes controller
    """

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
    """Available for a user for exporting selected geometries or all geometries in a hierarchy to a single OBJ

        Returns:
            validGeos (list): list of all geometries which are valid for export
    """
    selection = cmds.ls(selection=True)
    validGeos = []

    if len(selection) != 0:
        dialogPath = dialog(dupCheck=False, fileMode=2, diaCaption="Single OBJ Export", okCaption="Export")

        if dialogPath:
            for i in selection:
                allMeshes = cmds.listRelatives(cmds.listRelatives(i, allDescendents=True, type='mesh', path=True), parent=True)

                for ii in allMeshes:
                    validGeos.append(ii)

            fileName = validGeos[0]
            exportObj(dialogPath=dialogPath[0], fileName=fileName)
            print ('%s geometries exported to OBJ.' % len(validGeos)),

    else:
        cmds.warning("Nothing selected!"),

    return validGeos


def exportBatch(*args):
    """Available for a user for exporting selected geometries or all geometries in a hierarchy to separate OBJs

        Returns:
            validGeos (list): list of all geometries which are valid for export
    """
    selection = cmds.ls(selection=True)
    validGeos = []

    if len(selection) != 0:
        dialogPath = dialog(dupCheck=True, fileMode=2, diaCaption="Batch OBJ Export", okCaption="Export")

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

    else:
        cmds.warning("Nothing selected!"),

    return validGeos


def buildUI():
    """Building toolkit UI"""

    # UI variables
    mainColor = [0.0438, 0.4032, 0.553]
    width = 150

    columnMain = cmds.columnLayout(rowSpacing=10)

    # Import section
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

    # Export section
    cmds.setParent(columnMain)

    cmds.frameLayout(label='Export OBJ', backgroundColor=mainColor, collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.button(label="Export Single", w=width, h=25, c=exportSingle)
    cmds.button(label="Export Batch", w=width, h=25, c=exportBatch)

    # Footer section
    cmds.setParent(columnMain)

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, (width / 2)), (2, (width / 2))])
    cmds.text(label=__author__, align='left')
    cmds.text(label='')
    cmds.text(label='<a href=%s>janjinda.com</a>' % __website__, hyperlink=True, align='left')
    cmds.text(label=('v%s' % __version__), align='right')


def testCheckboxes():
    """Checking state of UI checkboxes

            Returns:
                deleteCHCheckboxV (bool): result of Delete History checkbox
     """
    deleteCHCheckboxV = cmds.checkBox('deleteCHCheckbox', query=True, value=True)

    return deleteCHCheckboxV


def showUI():
    """Showing toolkit UI, function called from Maya

        Returns:
            windowName (str): name of a toolkit window passed to Maya
    """
    windowName = "ObjToolkitUI"

    if cmds.window(windowName, query=True, exists=True):
        cmds.deleteUI(windowName)

    cmds.window(windowName, title="JJ OBJ Toolkit")

    buildUI()
    cmds.showWindow(windowName)

    return windowName
