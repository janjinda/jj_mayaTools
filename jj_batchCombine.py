"""
Combine geometry under parent of first selected geo and inherts it's name. 
You can also choose if you want to take subdivisions and material tags in 
consideration.

Author: Jan Jinda
Email: jj@dneg.com
Version: 1.0.0
"""

# Usual imports
import maya.cmds as cmds
import subdiv_attrs

def subDFilter(inputList):
    """Create dictionary based on RexSubD Attribute.

    Check if the geo has RexSubD applied and creates dictionary with two
    keys subD and noSubD with lists of objects as values.

    Args:
        shapesList: expect a list with geo shapes (list)
        
    Returns:
        A dict filtered geometries. For example:

        {'noSubD': ('panel_001__painted_red_metal_comp_geo'),
         'subD': ('canister_001__heavy_metal_comp_geo'),}
    """
    
    subDDict = {}
    
    for shape in inputList:
        # Query REX Subdiv attributes on the shape node
        if cmds.objExists('%s.rexSubdiv' % shape):
            attr = 'subD'
        else:
            attr = 'noSubD'
        
        geo = cmds.listRelatives(shape, parent=True)[0]
        # Populate a dictionary based on subDiv attributes
        if subDDict.has_key(attr):
            subDDict[attr].append(geo)
        else:
            subDDict[attr] = [geo]
        
    return subDDict

def tagFilter(inputList):
    """Create dictionary based on material tags.

    Sort geometries based on material tags, create a key per material
    tag and a list of corresponding geometries as its values.

    Args:
        inputList: expect a list of geometries to filter
                
    Returns:
        A dict filtered geometries. For example:

        {'painted_red_metal_comp_geo': ('panel_001__painted_red_metal_comp_geo'),
         'heavy_metal_comp_geo': ('canister_001__heavy_metal_comp_geo'),}
    """
    tagsDict = {}
    tagDivider='__'
    
    for geo in inputList:
        # Separate a tag from geometry name
        tag = (geo.split(tagDivider)[1]).replace('_geo','')        
        # Populate a dictionary based on material tags
        if tagsDict.has_key(tag):
            tagsDict[tag].append(geo)
        else:
            tagsDict[tag] = [geo]
            
    return tagsDict
    
def combine(inputList, subds=False):
    """Combine geometries from a list.

    Combine geometries from a list, parent the result geometry to under
    a parent of a first item in the list. It also rename it based on a
    first item in a list.

    Args:
        inputList: expect a list with geometries
        
    Returns:
        A name of a new combined geometry. For example: 'panel_001__painted_red_metal_comp_geo'
    """
    
    if len(inputList) > 1:
        # Find parent groups
        parentGrp = cmds.listRelatives(inputList, parent=True)
        # Combine geometries present in the list and adds suffix to create unique name
        combinedMesh = cmds.polyUnite(inputList, ch=True, mergeUVSets=True, name="%s_X" % inputList[0])[0]        
        # Check if a parent exists and paimport subdiv_attrsrents new geometry to a original parent of first item in a list
        if parentGrp:
            cmds.parent(combinedMesh, parentGrp[0])
        
        cmds.delete(constructionHistory=True)
        # Rename a new geometry based on a name of first item in a list
        newMesh = cmds.rename(combinedMesh, combinedMesh[:-2])
        if subds:
            subdiv_attrs.add_subdiv(cmds.listRelatives(newMesh, shapes=True))
        
        newGeos.append(newMesh)
    else:
        newMesh = None
    
    print newMesh
    return newMesh

def batchCombine(subds, tags):
    """Run a main script.

    Run the main script. Based on a tags attribute it will combine geometries
    with tags or not.

    Args:
        subds: expect boolean if it should take subdivisions in consideration
        tags: expect boolean if it should take tags in consideration
        
    Returns:
        A list of newly created geometries. For example:

        [u'L_head_upp_panel_003__painted_red_metal_comp_geo', 
        u'L_head_upp_panel_002__painted_red_metal_comp_geo']
    """
    
    global sel
    sel = cmds.ls(selection=True)       
    # Remove non-mesh geo from list
    sel = [obj for obj in sel if cmds.listRelatives(obj, children=True, type='mesh')]       
    shapes = cmds.listRelatives(sel, shapes=True)
    
    # Global list of new geos
    global newGeos
    newGeos = []

    # SubD filter enabled
    if subds:
        subDFiltered = subDFilter(shapes)
        for keyA in subDFiltered:
            # Tag filter enabled
            if tags:            
                tagFiltered = tagFilter(subDFiltered[keyA])
                for keyB in tagFiltered:
                    geoList = tagFiltered[keyB]
                    combine(geoList, subds=True)           
            # Tag filter disabled
            else:
                geoList = subDFiltered[keyA]
                combine(geoList, subds=True)
    # SubD filter disabled    
    else:
        # Tag filter enabled     
        if tags:
            tagFiltered = tagFilter(sel)
            for keyB in tagFiltered:
                geoList = tagFiltered[keyB]
                combine(geoList)
        # Tag filter disabled
        else:
            geoList = sel
            combine(geoList)

    cmds.select(newGeos)
    return newGeos
