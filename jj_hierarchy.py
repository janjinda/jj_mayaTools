"""
Tool for storing and restoring heierarchy or just reselecting same
objects somewhere else.

Author: Jan Jinda
Email: jj@dneg.com
Version: 1.0.0
"""

# Usual imports
import maya.cmds as cmds
import json
import pymel.core as pm

def storeHierarchy(presetFile):
    """Store hierarchy into a json file.

    Hierarchy is stored as a dictionary, where parent obj is a key
    and group is a value.
    
    Args:
        presetFile: String path to the json file. For example:'/user_data/temp/temp'
        
    Returns:
        A stored dictionary. For example:

        {"L_gun_ext_chasis_001__heavyDuty_metal_comp_geo": "L_gun_ext_chasis_001_grp", 
         "L_arm_upperArm_panel_004_001__painted_metal_brown_comp_geo": "L_arm_upperArm_panel_004_grp", 
         "C_head_panel_0008__painted_metal_brown_comp_geo": "C_head_grp"
        }
    """
    
    sel = cmds.ls(selection=True)
    data = {}

    for obj in sel:
        hasParent = bool(cmds.listRelatives(obj, parent=True))
        if hasParent:    
            parent = cmds.listRelatives(obj, parent=True)[0]
        else:
            parent = 'world'    
               
        data[obj] = parent

    with open('%s.json' % presetFile, 'w') as f:
        json.dump(data, f, indent=4)
        
    return data
        

def restoreHierarchy(presetFile):
    """Restore hierarchy of selected objects from the json file.

    Hierarchy restored from a dictonary in the json file.
    
    Args:
        presetFile: String path to the json file. For example:'/user_data/temp/temp'
        
    Returns:
        A restored dictionary. For example:

        {"L_gun_ext_chasis_001__heavyDuty_metal_comp_geo": "L_gun_ext_chasis_001_grp", 
         "L_arm_upperArm_panel_004_001__painted_metal_brown_comp_geo": "L_arm_upperArm_panel_004_grp", 
         "C_head_panel_0008__painted_metal_brown_comp_geo": "C_head_grp"
        }
    """
    
    sel = cmds.ls(selection=True)

    with open('%s.json' % presetFile, 'r') as f:
        data = json.load(f)

    for obj in sel:
        if not data[obj] == 'world':
            cmds.parent(obj, data[obj])
    
    return data
        
def selectGeos(presetFile):
    """Select objects stored in the json file.

    Select objects from a dictonary in the json file (keys).
    
    Args:
        presetFile: String path to the json file. For example:'/user_data/temp/temp'
        
    Returns:
        A list of restored objects. For example:

        [u'C_head_panel_0008__painted_metal_brown_comp_geo', 
         u'L_arm_upperArm_panel_004_001__painted_metal_brown_comp_geo',
         u'L_gun_ext_chasis_001__heavyDuty_metal_comp_geo']
    """

    with open('%s.json' % presetFile, 'r') as f:
        data = (json.load(f)).keys()
	
	selectable = []
	scene = cmds.ls()

    for obj in data:
	    if obj in scene:
		    selectable.append(obj)
    
    cmds.select(selectable)

    if data != selectable:
        pm.warning("Not all geometries are present in the scene.")
    
    return data
    
def mirrorHierarchy():
    """Mirror hierarchy and rename new objects.
    
    Args:
        None
        
    Returns:
        Nothing
    """
    
    # Mirror axis
    axis='X'
    
    # Duplicate selected objects
    sel = cmds.ls(selection=True, o=1)
    newObjects = cmds.duplicate(sel, renameChildren=True)
    
    # Delete history just in case
    for obj in newObjects:
        cmds.delete(constructionHistory=True)
    
    # Scale selected group    
    cmds.setAttr('%s.scale%s' % (newObjects[0],axis), -1)
               
    for obj in newObjects:
        # Rename R_ and L_ prefixes
        if obj.startswith('R_'):
            newName = obj.replace('R_', 'L_')
        elif obj.startswith('L_'):
            newName = obj.replace('L_', 'R_')
        else:
            newName = obj
        
        if newName.endswith('1'):
            newName = newName[:-1]
            
        cmds.rename(obj, newName)
    
    # Freeze transforms
    cmds.makeIdentity(apply=True, t=True, r=True, s=True, pn=True)
    
def sortSelection():
    """Alphabetically sort selected items in the outliner."""
    
    sortSel = sorted(cmds.ls(selection=True))
    sortSel.reverse()

    for obj in sortSel:
        cmds.reorder(obj, front=True)
