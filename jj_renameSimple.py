"""
Combinine geometry under parent of first selected geo and inherts it's name. 
You can also choose if you want to take subdivisions and material tags in 
consideration.

Author: Jan Jinda
Email: jj@dneg.com
Version: 1.0.0
"""
# Usual imports
import maya.cmds as cmds

# Defining dictionary of possible suffixes
suffixes = {
    'mesh': 'geo',
    'joint': 'jnt',
    'locator': 'ctr',
    'nurbsCurve': 'crv',
    'camera': None
}

suffixDefault = 'grp'


def renameSimple(selection=True):
    """
    This function will rename any objects to have the correct suffix
    Args:
        selection: Whether or not we use the current selection

    Returns:
        A list of objects we operated on

    """

    # Stores an selected object to the selection variable
    objects = cmds.ls(selection=selection, dag=True, long=True)

    if selection and not objects:
        raise RuntimeError("You don't have anything selected!")

    # Sorts selection based on length of object's name
    objects.sort(key=len, reverse=True)

    # For each obj in selection creates shortname based on objects name
    for obj in objects:
        shortName = obj.split("|")[-1]

        # Digs into the hierarchy and finds type of the object or child, if there's a hierarchy
        children = cmds.listRelatives(obj, children=True, fullPath=True) or []

        if len(children) == 1:
            child = children[0]
            objType = cmds.objectType(child)
        else:
            objType = cmds.objectType(obj)

        # Assigning suffix from the dictionary to suffix variable
        suffix = suffixes.get(objType, suffixDefault)

        # Skipping objects which should be without suffix (in the dictionary marked as none)
        if not suffix:
            continue

        # Skipping objects which already has an suffix
        if obj.endswith('_' + suffix):
            continue

        # Creating new name for the object and renaming it
        newName = '%s_%s' % (shortName, suffix)
        cmds.rename(obj, newName)

        index = objects.index(obj)
        objects[index] = obj.replace(shortName, newName)

    return
