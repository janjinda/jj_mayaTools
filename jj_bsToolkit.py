"""
Blend Shapes related little scripts.
"""

import maya.cmds as cmds


def bsSelection(suffix):

    sel = cmds.ls(selection=True)

    for obj in sel:

        newObj= '%s_%s' % (obj,suffix)

        if cmds.objExists(newObj):
           
            blend = cmds.blendShape(newObj, obj)[0]
            cmds.setAttr('%s.%s' % (blend, newObj), 1)


def bsMirror():
    """Mirror hierarchy and rename new objects.
    
    Args:
        None
        
    Returns:
        Nothing
    """

    source = None
    target = None

    # Mirror axis
    axis='X'
    
    # Duplicate selected objects
    sel = cmds.ls(selection=True, o=1)
    
    for i in sel:
        if i.startswith('R_') or i.startswith('L_'):
            source = (cmds.duplicate(i, renameChildren=True))[0]
            cmds.setAttr('%s.scale%s' % (source,axis), -1)
            cmds.makeIdentity(source, apply=True, t=True, r=True, s=True, pn=True)
            
            if source.startswith('R_'):
                target = ('L_%s' % source[2:-1])
            elif source.startswith('L_'):
                target = ('R_%s' % source[2:-1])
            
            bSCreate(source, target)
            
            cmds.delete(target, constructionHistory=True)


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
