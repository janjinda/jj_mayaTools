"""
JJ Obj Toolkit is a set of simple scripts tailored to provide clean, easier and more effective
workflow for handling OBJ files in Maya. Thanks to the Import as blend shape options it keeps all your scene
hierarchy, geometry UVs, shader assignments etc.

Installation
============

Copy jj_objToolkit.py from the zip file to your scripts folder. Usually at these locations ():

Windows - \<user's directory>\My Documents/Maya\<version>\scripts
MacOs - /Users/<user's directory>/Library/Preferences/Autodesk/maya/<version>/scripts
Linux - $MAYA_APP_DIR/Maya/<version>/scripts

Run following script or make a shelf button with following script.

import jj_objToolkit
jj_objToolkit.showUI()

"""

__author__ = "Jan Jinda"
__version__ = "1.0.6"
__documentation__ = "https://janjinda.artstation.com/pages/jj-obj-toolkit-doc"
__email__ = "janjinda@janjinda.com"
__website__ = "http://janjinda.com"

import maya.cmds as cmds
import re

from functools import partial


def iMaster(*args):
    """Running import functions based on selected radio button
        Returns:
            importCmd (string): called command
    """
    importCmd = None

    if queryIRadio() == 'iBatch':
        iGeo(4, False)
        importCmd = 'iBatch'

    if queryIRadio() == 'iBSOnSingle':
        iBSOnSingle()
        importCmd = 'iBSOnSingle'

    if queryIRadio() == 'iBSOnMultiple':
        iBSOnMultiple()
        importCmd = 'iBSOnMultiple'

    if queryIRadio() == 'iCombine':
        iGeo(4, False)
        importCmd = 'iCombine'

    return importCmd


def iGeo(fileMode, dupCheck, *args):
    """Main import function, removes all unnecessary nodes
        Parameters:
            dupCheck: (bool): if should check for duplicates
            fileMode (int): passes fileMode to a dialog function
        Returns:
            newGeo (str): newly imported geometry
    """

    # Empty variables as they are returned at the end
    newGeos = []
    objGroup = None

    # Open dialog and store it's output
    dialogOut = dialog(dupCheck=dupCheck, fileMode=fileMode, diaCaption="OBJ Import", okCaption="Import")

    if dialogOut:

        for i in dialogOut:

            # Import command
            selectedFiles = cmds.file(i, i=True, type="OBJ", ignoreVersion=True, renameAll=True,
                                      mergeNamespacesOnClash=False, options="mo=0, lo=0", pr=True, returnNewNodes=True)
            # Get file name create temp geo name
            fileName = re.sub('[^0-9a-zA-Z]', '_', (i.split('/')[-1])[0:-4])
            tempGeoName = fileName + "_polySurface1"

            # Create list of a type of each node created on import
            typeList = []
            for ii in selectedFiles:
                typeList.append(cmds.objectType(ii))

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
            newGeo = ('%s' % fileName)

            if newGeo not in cmds.ls():
                newGeo = cmds.rename(tempGeoName, newGeo)
                newGeos.append(newGeo)
            else:
                newGeo = cmds.rename(tempGeoName, ("%s_obj" % newGeo))
                newGeos.append(newGeo)

        # Check if OBJ_import group already exists
        if not cmds.objExists('OBJ_import_*'):
            num = 1
        else:
            # If group exists increment it's number
            num = (int(cmds.ls('OBJ_import_*')[-1].split('_')[-2])) + 1

        objGroup = cmds.group(name='OBJ_import_%s_grp' % ('%03d' % num), empty=True)
        cmds.parent(newGeos, objGroup)

        # Check if OBJs should be combined
        if queryIRadio() == 'iCombine' and len(newGeos) > 1:
            # Combine new geometries and parent result under OBJ_import_*_grp
            combinedGeo = cmds.polyUnite(newGeos, mergeUVSets=True, name="%s_X" % newGeos[0])[0]
            cmds.parent(combinedGeo, objGroup)
            cmds.delete(constructionHistory=True)
            cmds.rename(combinedGeo, combinedGeo[:-2])

            print "%s OBJs were imported and combined to single geometry." % len(newGeos),

        else:
            print "%s OBJs were imported." % len(newGeos),

    return newGeos, objGroup


def eGeo(*args):
    """Main export function
        Returns:
            validGeos (list): list of all exported geometries
    """

    # Empty variable as they are returned at the end, store selection
    selection = cmds.ls(selection=True)
    validGeos = []

    # Check if at least one geometry is selected
    if len(selection) != 0:
        # Check export mode
        if queryERadio() == 'eCombine':
            diaCaption = 'Combined'
        else:
            diaCaption = 'Batch'

        # Check Force overwrite checkbox
        if queryEChckB()[0]:
            pmt = False
            force = True
        else:
            pmt = True
            force = False

        # Check Ignore duplicate geo checkbox
        if queryEChckB()[1]:
            dupCheck = False
        else:
            dupCheck = True

        # Open dialog and store it's output
        dialogOut = dialog(dupCheck=dupCheck, fileMode=2, diaCaption="%s OBJ Export" % diaCaption, okCaption="Export")

        if dialogOut:
            dialogOut = dialogOut[0]

            # Run duplicateCheck and store into variables        
            duplicateExists, duplicateMeshes = duplicateCheck()

            for i in selection:
                # Store transforms of all selected geometries
                allMeshes = cmds.listRelatives(cmds.listRelatives(i, allDescendents=True, type='mesh', path=True),
                                               parent=True)

                # List valid geometries
                for ii in allMeshes:
                    # Storing long name in case there are duplicates
                    validGeos.append(cmds.ls(i, long=True)[0])

            # Check if just single file should be exported
            if queryERadio() == 'eCombine':
                # Single export
                i = validGeos[0].replace('|', '_')[1:]

                cmds.file('%s/%s.%s' % (dialogOut, i, 'obj'), force=False,
                          options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1',
                          type='OBJexport', es=True, pmt=pmt, f=force)

                print ('%s geometries exported to single OBJ.' % len(validGeos)),

            else:

                # Batch export
                for i in validGeos:
                    cmds.select(i, replace=True)

                    if duplicateExists and i.split('|')[-1] in duplicateMeshes:
                        i = i.replace('|', '_')[1:]

                    else:
                        i = i.split('|')[-1]

                    cmds.file('%s/%s.%s' % (dialogOut, i, 'obj'), force=False,
                              options='groups=1;ptgroups=1;materials=0;smoothing=1;normals=1',
                              type='OBJexport', es=True, pmt=pmt, f=force)

                print ('%s geometries exported to OBJs.' % len(validGeos)),

            cmds.select(validGeos, replace=True)

    else:
        cmds.warning("Nothing selected."),

    return validGeos


def iBSOnSingle(*args):
    """Importing OBJs as blend shape targets on one selected geometry
        Returns:
            newGeos (list): list of all new imported geometries
            bSList (list): list of all created blend shapes
            bSCtrlLoc(str): name of a created blend shapes controller
    """

    # Empty variables as they are returned at the end, store selection
    origGeos = cmds.ls(selection=True)
    bSList = []
    bSCtrlLoc = None
    newGeos = []
    validGeos = []

    # Find if one geometry is selected
    if len(origGeos) == 1:
        # Run iGeo function
        newGeos, objGroup = iGeo(4, True)
        target = origGeos[0]
        if newGeos:
            # Define source and target for a blend shape
            for i in newGeos:
                if cmds.polyEvaluate(i, v=True) == cmds.polyEvaluate(target, v=True):
                    validGeos.append(i)

            # Check if source and target have same vertex count
            if validGeos:
                validGeos.append(target)
                bS = cmds.blendShape(validGeos)
                bSList.append(bS)

                cmds.delete(validGeos[:-1])
                cmds.select(bS)

                print "%s OBJs imported. %s OBJs blend shaped." % (len(newGeos), len(validGeos) - 1),
            else:
                print "%s OBJs imported. %s OBJs blend shaped." % (len(newGeos), len(validGeos)),

    else:
        cmds.warning("Please select one geometry.")

    return newGeos, bSList


def iBSOnMultiple(*args):
    """Importing multiple OBJs as a blend shape to an existing corresponding geometries
        Returns:
            newGeos (list): list of all new imported geometries
            bSList (list): list of all created blend shapes
            bSCtrlLoc(str): name of a created blend shapes controller
    """

    # Empty variables as they are returned at the end, import OBJs and store all geometries in the scene
    sceneGeos = [x.encode('UTF8') for x in cmds.listRelatives(cmds.ls(type='mesh'), parent=True)]
    validGeos = []
    newGeos, objGroup = iGeo(4, True)
    nonBS = []
    bSList = []
    bSCtrlLoc = None

    # Convert lists to dictionary with matching lowercase names
    sceneGeos = {i: i.lower() for i in sceneGeos}

    if newGeos:
        for source in newGeos:
            sourceLwr = source.lower()
            sourceLwr = sourceLwr.encode('UTF8')
            targetLwr = sourceLwr.replace('_obj', '')

            # Check if imported OBJ name matches with any geometry in the scene
            if targetLwr in sceneGeos.values():
                target = sceneGeos.keys()[sceneGeos.values().index(targetLwr)]

                # Check if source and target have same vertex count
                if cmds.polyEvaluate(source, v=True) == cmds.polyEvaluate(target, v=True):
                    validGeos.append(target)

                    # Create a blend shape
                    bS = bSCreate(source=source, target=target)
                    bSList.append(bS)

                else:
                    nonBS.append(source)

            else:
                nonBS.append(source)

        # Create a locator
        if bSList:
            bSCtrlLoc = bSCtrlCreate(bSList=bSList, origGeoList=validGeos)[0]

        if not cmds.listRelatives(objGroup):
            cmds.delete(objGroup)

        if not queryIChckB():
            print "%s OBJs imported. %s OBJs blend shaped. bs_ctrl created." % \
                  (len(newGeos), len(bSList)),
        else:
            print "%s OBJs imported. %s OBJs blend shaped. History deleted." % (len(newGeos), len(bSList)),

    return newGeos, objGroup, bSList, bSCtrlLoc


def bSCreate(source, target):
    """Creates blend shape deformer
        Parameters:
            source (list): blend shape source geometry
            target (str): blend shape target geometry
        Returns:
            bS (str): name of a created blend shape deformer
    """

    # Create blend shape between source and target
    bS = cmds.blendShape(source, target)[0]
    cmds.setAttr('%s.%s' % (bS, source), 1)
    cmds.delete(source)

    return bS


def bSCtrlCreate(bSList, origGeoList, *args):
    """Creates locator with an attribute for controlling all created blend shapes
        Parameters:
            bSList (list): list of all created blend shapes
            origGeoList (list): list of all geometries which were blend shaped
        Returns:
            bSCtrlLoc (str): name of a created locator
            bSCtrlAttr (str): name of a created custom attribute
    """

    # Empty variables as they are returned at the end
    bSCtrlLoc = None
    bSCtrlAttr = None

    # Check if Delete history option is checked
    if not queryIChckB():
        # Create locator and list all keyable attributes
        bSCtrlLoc = cmds.spaceLocator(n="bShape_ctrl")[0]
        availableAttrs = cmds.listAttr(bSCtrlLoc, keyable=True)

        # Lock all keyable attributes
        for i in availableAttrs:
            cmds.setAttr('%s.%s' % (bSCtrlLoc, i), lock=True, keyable=False)

        # Create custom attribute on the locator
        bSCtrlAttr = cmds.addAttr(bSCtrlLoc, shortName='bsAmount', longName='Blend_Shapes_Amount',
                                  defaultValue=1.0,
                                  minValue=0, maxValue=1, keyable=True)

        # Connect all blend shapes to the custom attribute
        for i in bSList:
            if i:
                cmds.connectAttr('%s.bsAmount' % bSCtrlLoc, '%s.envelope' % i)

    else:
        # Delete history when control not created
        cmds.delete(origGeoList, ch=True)

    return bSCtrlLoc, bSCtrlAttr


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
    dupExists, duplicateMeshes = duplicateCheck()
    # If there are geometries with the same name give warning
    if dupCheck and dupExists:
        dialogOut = None
        cmds.warning(
            "There are multiple geometries with the same name. This should be fixed first. %s" % duplicateMeshes),

    else:
        # Store dialog output to a variable
        dialogOut = cmds.fileDialog2(fileMode=fileMode, caption=diaCaption, okCaption=okCaption,
                                     dialogStyle=2, fileFilter="Waveform OBJ (*.obj *.OBJ)")

    return dialogOut


def duplicateCheck(*args):
    """Checks for name duplicates in a scene
        Returns:
            dupExists (bool): result of the check
            duplicateMeshes (list): list of duplicate meshes

     """

    # Check if there is duplicate geometry based on mayas long name
    sceneMeshes = cmds.listRelatives(cmds.ls(type='mesh'), parent=True)
    duplicateMeshes = []
    dupExists = None

    if sceneMeshes:
        for i in sceneMeshes:
            if '|' in i or sceneMeshes.count(i) > 1:
                dupExists = True
                duplicateMeshes.append(i)
            else:
                dupExists = False

    return dupExists, duplicateMeshes


def queryIRadio(*args):
    """Check which Import radio button is selected
        Returns:
            selectedIRadio (string): name of selected radio button
    """
    selectedIRadio = cmds.radioCollection('iRadio', query=True, select=True)

    return selectedIRadio


def queryERadio(*args):
    """Check which Export radio button is selected
            Returns:
                selectedERadio (string): name of selected radio button
    """
    selectedERadio = cmds.radioCollection('eRadio', query=True, select=True)

    return selectedERadio


def queryIChckB():
    """Check state of UI Import checkboxes
            Returns:
                deleteCHChckV (bool): value of Delete History checkbox
    """

    deleteChckB = cmds.checkBox('deleteChckB', query=True, value=True)

    return deleteChckB


def queryEChckB():
    """Check state of UI Export checkboxes
            Returns:
                forceOverwriteChckV (bool): value of Force overwrite checkbox
    """

    forceOverwriteChckB = cmds.checkBox('forceOverwriteChckB', query=True, value=True)
    ignoreDuplicatesChckB = cmds.checkBox('ignoreDuplicatesChckB', query=True, value=True)

    return forceOverwriteChckB, ignoreDuplicatesChckB


def deleteChckBEnable(state, *args):
    """Check state of UI Export checkboxes
            Returns:
                forceOverwriteChckV (bool): value of Force overwrite checkbox
    """
    if state == 'True':
        cmds.checkBox('deleteChckB', edit=True, enable=True)
    elif state == 'False':
        cmds.checkBox('deleteChckB', edit=True, enable=False, value=False)


def buildUI():
    """Build toolkit UI
            Returns:
                winWidth (int): width of toolkit window in pixels
                winHeight (int): heigth of toolkit window in pixels
    """

    # UI variables
    mainColor = [0.33, 0.58, 0.63]
    buttonColor = [0.45, 0.45, 0.45]
    winWidth = 160
    winHeight = 360

    columnMain = cmds.columnLayout()

    # Import section
    cmds.frameLayout(label='Import OBJ', backgroundColor=mainColor, marginHeight=3)
    cmds.button(label="Import", backgroundColor=buttonColor, h=25, c=iMaster)

    cmds.frameLayout(label='Import Options')
    cmds.columnLayout(rowSpacing=2)

    cmds.radioCollection('iRadio')
    cmds.radioButton('iBatch', label='Batch', select=True)
    cmds.radioButton('iBSOnSingle', label='Batch blendS on Single', onc=partial(deleteChckBEnable, 'False'),
                     ofc=partial(deleteChckBEnable, 'True'))
    cmds.radioButton('iBSOnMultiple', label='Batch blendS on Multiple')
    cmds.radioButton('iCombine', label='Combined', onc=partial(deleteChckBEnable, 'False'),
                     ofc=partial(deleteChckBEnable, 'True'))

    cmds.columnLayout(rowSpacing=2)
    cmds.checkBox('deleteChckB', label='Delete history', width=winWidth)

    # Export section
    cmds.setParent(columnMain)

    cmds.frameLayout(label='Export OBJ', backgroundColor=mainColor, marginHeight=3)
    cmds.button(label="Export", backgroundColor=buttonColor, h=25, c=eGeo)

    cmds.frameLayout(label='Export Options')
    cmds.columnLayout(rowSpacing=2)

    cmds.radioCollection('eRadio')
    cmds.radioButton('eBatch', label='Batch', select=True)
    cmds.radioButton('eCombine', label='Combined')

    cmds.columnLayout(rowSpacing=2)
    cmds.checkBox('forceOverwriteChckB', label='Force overwrite', width=winWidth)
    cmds.checkBox('ignoreDuplicatesChckB', label='Ignore duplicate geos', width=winWidth, )

    # Footer section
    cmds.setParent(columnMain)

    cmds.columnLayout(rowSpacing=2)
    cmds.button(label='Help', width=winWidth, c=help)

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, (winWidth / 2)), (2, (winWidth / 2))])
    cmds.text(label=__author__, align='left')
    cmds.text(label='')
    cmds.text(label='<a href=%s>janjinda.com</a>' % __website__, hyperlink=True, align='left')
    cmds.text(label=('v%s' % __version__), align='right')

    return winWidth, winHeight


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

    # Delete window if it already exists
    if cmds.window(windowName, query=True, exists=True):
        cmds.deleteUI(windowName)

    # Create window
    cmds.window(windowName, title="JJ OBJ Toolkit", sizeable=False, tlb=True)

    # Build UI
    winWidth, winHeight = buildUI()

    # Edit window size after building UI
    cmds.window(windowName, e=True, width=winWidth, height=winHeight)

    # Show UI to user
    cmds.showWindow(windowName)

    return windowName
