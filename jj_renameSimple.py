import maya.cmds as mc

# defining dictionary of possible suffixes
SUFFIXES = {
    'mesh': 'geo',
    'joint': 'jnt',
    'locator': 'loc',
    'nurbsCurve': 'crv',
    'camera': None
}

DEFAULT_SUFFIX = 'grp'


def renameSimple(selection=False):
    """
    This function will rename any objects to have the correct suffix
    Args:
        selection: Whether or not we use the current selection

    Returns:
        A list of objects we operated on

    """

    # stores an selected object to the selection variable
    objects = mc.ls(selection=selection, dag=True, long=True)

    if selection and not objects:
        raise RuntimeError("You don't have anything selected!")

    # sorts selection based on lengh of object's name
    objects.sort(key=len, reverse=True)

    # for each obj in selection creates shortname based on objects name
    for obj in objects:
        shortName = obj.split("|")[-1]

        # diggs into the hierarchy and finds type of the object or child, if there's a hierarchy
        children = mc.listRelatives(obj, children=True, fullPath=True) or []

        if len(children) == 1:
            child = children[0]
            objType = mc.objectType(child)
        else:
            objType = mc.objectType(obj)

        # assigning suffix from the dictionary to suffix variable
        suffix = SUFFIXES.get(objType, DEFAULT_SUFFIX)

        # skipping objects which should be without suffix (in the dictionary marked as none)
        if not suffix:
            continue

        # skipping objects which already has an suffix
        if obj.endswith('_' + suffix):
            continue

        # creating new name for the object and renaming it
        newName = '%s_%s' % (shortName, suffix)
        mc.rename(obj, newName)

        index = objects.index(obj)
        objects[index] = obj.replace(shortName, newName)

    return
