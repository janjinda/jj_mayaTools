"""
Continue selection pattern based on current user selection. Either ring or loop.

Author: Jan Jinda
Email: jj@dneg.com
Version: 1.0.0
"""
import maya.cmds as cmds
import pymel.core as pm

def selectNEdge():
    """Continue selection pattern based on current user selection. 
    Either ring or loop.

    Args:
        None
        
    Returns:
        Nothing
    """
    
    # Get selection
    sel = cmds.ls(selection = True)
    # Check if two edges are selected
    if len(sel) == 2:
        geo = sel[0].split(".")[0]
        
        # Find edge number
        edgeA = int(sel[0][sel[0].find("[")+1:sel[0].find("]")])
        edgeB = int(sel[1][sel[1].find("[")+1:sel[1].find("]")])

        selType = cmds.polySelect(geo, query = True, edgeRing=edgeA)
        
        # Check if edges are on a loop
        if long('%sL' % edgeB) in selType:
            cmds.polySelect(geo, edgeRingPattern = (edgeA, edgeB))
        else:
            cmds.polySelect(geo, edgeLoopPattern = (edgeA, edgeB))
    # If not exactly two edges selected give warning
    else:
        pm.warning("Select 2 edges!")
