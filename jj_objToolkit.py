# JJ Obj Toolkit is a simple set of tools for easier OBJ files manipulation within Maya.

__author__ = "Jan Jinda"
__version__ = "0.9.8"
__documentation__ = "http://janjinda.com/pages/jj-obj-toolkit-help"
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
        dialogOut (list): output selection from a dialog
    """

    # If there are geometries with the same name give warning
    if dupCheck and duplicateCheck():
        dialogOut = None
        cmds.warning("There are multiple geometries with the same name. This should be fixed first."),

    else:
        # Store dialog output to a variable
        dialogOut = cmds.fileDialog2(fileMode=fileMode, caption=diaCaption, okCaption=okCaption,
                                      dialogStyle=2, fileFilter="Waveform OBJ (*.obj *.OBJ)")

    return dialogOut


def importObj(dialogOut):
    """Main import function, removes all unnecessary nodes

    Parameters:
        dialogOut (list): input files from dialog

    Returns:
        newGeo (str): newly imported geometry
    """

    # Import command
    selectedFiles = cmds.file(dialogOut, i=True, type="OBJ", ignoreVersion=True, renameAll=True,
                              mergeNamespacesOnClash=False, options="mo=0, lo=0", pr=True, returnNewNodes=True)
    # Get file name create temp geo name
    fileName = re.sub('[^0-9a-zA-Z]', '_', (dialogOut.split('/')[-1])[0:-4])
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


def exportObj(dialogOut, fileName):
    """Main export function

    Parameters:
        dialogOut (list): directory input from dialog
        fileName (str): file name inherited from geometry name

    Returns:
        fileName (str): file name inherited from geometry name
    """
    
    # Check Force overwrite checkbox
    if testCheckboxes()[1]:
        pmt = False
        force = True
    else:
        pmt = True
        force = False

    # File write command
    cmds.file('%s/%s.%s' % (dialogOut, fileName, 'obj'), force=False,
              options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1',
              type='OBJexport', es=True, pmt=pmt, f=force)

    return fileName


def duplicateCheck():
    """Main export function

     Returns:
         dupExists (bool): result of the check
     """

    # Check if there is duplicate geometry based on mayas long name
    sceneMeshes = cmds.listRelatives(cmds.ls(type='mesh'),parent=True)
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
    
    # Create blend shape between source and target
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

    # Empty variables as they are returned at the end
    bSControlLoc = None
    bsControlAttr = None

    # Check if Delete history option is checked
    if not testCheckboxes()[0]:
        # Create locator and list all keyable attributes
        bSControlLoc = cmds.spaceLocator(n="bShape_ctrl")[0]
        availableAttrs = cmds.listAttr(bSControlLoc, keyable=True)
        
        # Lock all keyable attributes
        for i in availableAttrs:
            cmds.setAttr('%s.%s' % (bSControlLoc, i), lock=True, keyable=False)
        
        # Create custom attritube on the locator
        bsControlAttr = cmds.addAttr(bSControlLoc, shortName='bsAmount', longName='Blend_Shapes_Amount',
                                     defaultValue=1.0,
                                     minValue=0, maxValue=1, keyable=True)
        
        # Connect all blend shapes to the custom attribute
        for i in blendSList:
            if i:
                cmds.connectAttr('%s.bsAmount' % bSControlLoc, '%s.envelope' % i)

    else:
        # Delete history when control not created
        cmds.delete(origGeoList, ch=True)

    return bSControlLoc, bsControlAttr


def importSingle(*args):
    """Available for a user for importing single OBJ

        Returns:
            newGeos (list): list of all new imported geometries
    """

    # Open dialog and store it's output
    newGeos = []
    dialogOut = dialog(dupCheck=False, fileMode=1, diaCaption="Single OBJ Import", okCaption="Import")

    if dialogOut:
        # Run main importObj function
        newGeos = [importObj(dialogOut[0])]

        print "%s OBJs were imported." % len(newGeos),

    return newGeos


def importBatch(*args):
    """Available for a user for importing multiple OBJ

        Returns:
            newGeos (list): list of all new imported geometries
    """

    # Open dialog and store it's output
    newGeos = []
    dialogOut = dialog(dupCheck=False, fileMode=4, diaCaption="Batch OBJ Import", okCaption="Import")

    if dialogOut:
        for i in dialogOut:
            # Run main importObj function
            newGeo = importObj(i)
            newGeos.append(newGeo)

        print "%s OBJs were imported." % len(newGeos),

    return newGeos


def importSingleBS(*args):
    """Available for a user for importing single OBJ as a blend shape to an existing geometry

        Returns:
            newGeos (list): list of all new imported geometries
            blendSList (list): list of all created blend shapes
            bSControlLoc(str): name of a created blend shapes controller
    """

    # Empty variables as they are returned at the end, store selection
    origGeos = cmds.ls(selection=True)
    blendSList = []
    bSControlLoc = None
    nonBlendS = []

    # Find if one geometry is selected
    if len(origGeos) == 1:
        # Run importSingle function
        newGeos = importSingle()

        if newGeos:
            # Define source and target for a blend shape
            source = newGeos[0]
            target = origGeos[0]

            # Check if source and target have same vertex count
            if cmds.polyEvaluate(source, v=True) == cmds.polyEvaluate(target, v=True):
                # Create a blend shape and locator if required
                blendSList = [bSCreate(source=source, target=target)]
                bSControlLoc = bSControlCreate(blendSList=blendSList, origGeoList=origGeos[0])[0]
                cmds.select(bSControlLoc)

            print newGeos, source, nonBlendS
            print "%s OBJs were imported. %s OBJs were blend shaped." % (len(newGeos), len(blendSList)),

    else:
        cmds.warning("Please select one geometry.")

    return newGeos, blendSList, bSControlLoc


def importBatchBS(*args):
    """Available for a user for importing multiple OBJ as a blend shape to an existing corresponding geometries

        Returns:
            newGeos (list): list of all new imported geometries
            blendSList (list): list of all created blend shapes
            bSControlLoc(str): name of a created blend shapes controller
    """

    # Empty variables as they are returned at the end, import OBJs and store all geometries in the scene
    sceneGeos = cmds.listRelatives(cmds.ls(type='mesh'), parent=True)
    validGeos = []
    newGeos = importBatch()
    nonBlendS = []
    blendSList = []
    bSControlLoc = None

    if newGeos:
        for source in newGeos:
            target = source.replace('_obj', '')

            # Check if imported OBJ name matches with any geometry in the scene
            if target in sceneGeos:
                # Check if source and target have same vertex count
                if cmds.polyEvaluate(source, v=True) == cmds.polyEvaluate(target, v=True):
                    validGeos.append(target)

                    # Create a blend shape
                    blendS = bSCreate(source=source, target=target)
                    blendSList.append(blendS)

                else:
                    nonBlendS.append(source)

            else:
                nonBlendS.append(source)

        if not len(nonBlendS)  == 0:
            groupObj = cmds.group(nonBlendS, name='OBJ_import_grp')

        # Create a locator
        if blendSList:
            bSControlLoc = bSControlCreate(blendSList=blendSList, origGeoList=validGeos)[0]

        if bSControlLoc:
            print "%s OBJs imported. %s OBJs blend shaped. bs_ctrl created." % \
                  (len(newGeos), len(blendSList)),
        else:
            print "%s OBJs imported. %s OBJs blend shaped. History deleted." % (len(newGeos), len(blendSList)),

    return newGeos, groupObj, blendSList, bSControlLoc


def exportSingle(*args):
    """Available for a user for exporting selected geometries or all geometries in a hierarchy to a single OBJ

        Returns:
            validGeos (list): list of all geometries which are valid for export
    """

    # Empty variable as they are returned at the end, store selection
    selection = cmds.ls(selection=True)
    validGeos = []

    # Check if at least one geometry is selected
    if len(selection) != 0:
        # Open dialog and store it's output
        dialogOut = dialog(dupCheck=False, fileMode=2, diaCaption="Single OBJ Export", okCaption="Export")

        if dialogOut:
            for i in selection:
                # Store transforms of all selected geometries
                allMeshes = cmds.listRelatives(cmds.listRelatives(i, allDescendents=True, type='mesh', path=True),
                                               parent=True)

                # List valid geometries
                for ii in allMeshes:
                    validGeos.append(ii)

            # Main export, named after first selected geometry
            fileName = validGeos[0]
            exportObj(dialogOut=dialogOut[0], fileName=fileName)
            print ('%s geometries exported to OBJ.' % len(validGeos)),

    else:
        cmds.warning("Nothing selected."),

    return validGeos


def exportBatch(*args):
    """Available for a user for exporting selected geometries or all geometries in a hierarchy to separate OBJs

        Returns:
            validGeos (list): list of all geometries which are valid for export
    """

    # Empty variable as they are returned at the end, store selection
    selection = cmds.ls(selection=True)
    validGeos = []

    # Check if at least one geometry is selected
    if len(selection) != 0:
        # Open dialog and store it's output
        dialogOut = dialog(dupCheck=True, fileMode=2, diaCaption="Batch OBJ Export", okCaption="Export")

        if dialogOut:
            for i in selection:
                # Store transforms of all selected geometries
                allMeshes = cmds.listRelatives(cmds.listRelatives(i, allDescendents=True, type='mesh'), parent=True)

                # List valid geometries
                for ii in allMeshes:
                    validGeos.append(ii)

            # Main export every file named by geometry name
            for i in validGeos:
                cmds.select(i)
                fileName = i
                exportObj(dialogOut=dialogOut[0], fileName=fileName)

            cmds.select(validGeos)

            print ('%s OBJ exported.' % len(validGeos)),

    else:
        cmds.warning("Nothing selected."),

    return validGeos


def buildUI():
    """Build toolkit UI"""

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

    cmds.checkBox('deleteChckB', label='Delete History', width=width)

    # Export section
    cmds.setParent(columnMain)

    cmds.frameLayout(label='Export OBJ', backgroundColor=mainColor, collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.button(label="Export Single", w=width, h=25, c=exportSingle)
    cmds.button(label="Export Batch", w=width, h=25, c=exportBatch)

    cmds.setParent(columnMain)

    cmds.frameLayout(label='Export Options', collapsable=False)
    cmds.columnLayout(rowSpacing=2)

    cmds.checkBox('forceOverwriteChckB', label='Force overwrite', width=width)

    cmds.setParent(columnMain)

    cmds.columnLayout(rowSpacing=2)
    cmds.button(label='Help', width=width, c=help)

    # Footer section
    cmds.setParent(columnMain)

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, (width / 2)), (2, (width / 2))])
    cmds.text(label=__author__, align='left')
    cmds.text(label='')
    cmds.text(label='<a href=%s>janjinda.com</a>' % __website__, hyperlink=True, align='left')
    cmds.text(label=('v%s' % __version__), align='right')


def testCheckboxes():
    """Check state of UI checkboxes

            Returns:
                deleteCHCheckboxV (bool): result of Delete History checkbox
    """

    deleteCHCheckboxV = cmds.checkBox('deleteChckB', query=True, value=True)
    forceOverwriteChckBV = cmds.checkBox('forceOverwriteChckB', query=True, value=True)

    return deleteCHCheckboxV, forceOverwriteChckBV


def help(*args):
    """Open URL with documentation

             Returns:
                 __documentation__ (string): variable value
     """
    cmds.launch(web=__documentation__)

    return __documentation__


def showUI():
    """Show toolkit UI, function called from Maya

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
