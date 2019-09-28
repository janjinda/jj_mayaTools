"""
Tool for reloading component selection on objects with the same topology.

Author: Jan Jinda
Email: jj@dneg.com
Version: 1.0.0
"""

# Usual imports
import maya.cmds as cmds

def storeCompSel():
    """Stores component selection.

    Args:
        None
        
    Returns:
        Nothing
    """
    
    # Get selection
    sel = cmds.ls(selection=True)
    # Find out component type and store to global variable
    global componentType
    componentType = sel[0][sel[0].find(".")+1:sel[0].find("[")]
    # Find component number and save it to global variable
    global componentNums
    componentNums = []
    for component in sel:
        componentNum = component[component.find("[")+1:component.find("]")]
        componentNums.append(componentNum)


def restoreCompSel():
    """Restores component selection.

    Args:
        None
        
    Returns:
        Nothing
    """
    # Get selection
    sel = cmds.ls(selection=True)
    # Selects components based on stored variables
    toSel = []
    for geo in sel:
        for number in componentNums:
            toSel.append('%s.%s[%s]' % (geo, componentType, number))
    
    cmds.select(toSel,add=True)
    cmds.hilite(replace=True)

def delEdge():
    """Restores component selection.

    Args:
        None
        
    Returns:
        Nothing
    """
    # Get selection
    sel = cmds.ls(selection=True)
    # Selects components based on stored variables
    toSel = []
    for geo in sel:
        for number in componentNums:
            toSel.append('%s.%s[%s]' % (geo, componentType, number))
    
    cmds.polyDelEdge(toSel, cv=True, ch=False)
