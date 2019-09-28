"""
Tool for removing color sets from either entire scene or just a selection.

Author: Jan Jinda
Email: jj@dneg.com
Version: 1.0.1
"""

# Usual imports
import maya.cmds as cmds

def colorSetsRemove(scene=True):
    """Remove all color sets
    
    Args:
        Boolean - if True function runs on entire scene, if False just on selection
        
    Returns:
        Nothing
    """
   
    # Variable used to find if function ran
    colorSetsFound = False
    
    # List meshes based on keyword
    if scene:
        geoList = cmds.ls(type='mesh')    
    else:
        geoList = cmds.ls(selection=True)
        geoList = [obj for obj in geoList if cmds.listRelatives(obj, children=True, type='mesh')]
    
    for geo in geoList:
        # Find all color sets on geo
        colorSetsList = cmds.polyColorSet(geo, query=True, allColorSets=True)
        # Delete color sets if exists
        if colorSetsList:
            for colorSet in colorSetsList:
                cmds.polyColorSet(geo, allColorSets=True, delete=True)
                colorSetsFound = True
    
    # Let user know if clean up was performed
    if colorSetsFound:   
        cmds.warning("All color sets were deleted.")
    else:
        cmds.warning("Everything OK!")
