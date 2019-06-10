import maya.cmds as cmds


def listSceneMaterials():
    """
    list all materials used by geometry in the scene
    """

    scene_materials = []
    allSG = cmds.ls(type='shadingEngine')
    materialAssignment = {}

    for SG in allSG:
        # if an sg has 'sets' members, it is used in the scene
        connectedGeos = cmds.sets(SG, q=True)
        if connectedGeos:
            material = cmds.listConnections('{}.surfaceShader'.format(SG))[0]
            if material:
                materialAssignment[material] = connectedGeos
    return materialAssignment


def getRoughnessValue(material):
    roughnessAlbedo = cmds.getAttr('%s.specularRoughness' % material)

    return roughnessAlbedo


def linkToTriple():
    # create constant if no map in material
    # probably loop through materials first then geometries
    materialAssignment = listSceneMaterials()

    tripleSwitch = cmds.shadingNode('tripleShadingSwitch', asUtility=True)

    inputIndex = 0
    for key in materialAssignment:
        for geo in materialAssignment[key]:
            shape = cmds.listRelatives(geo, shapes=True)[0]
            cmds.connectAttr('%s.instObjGroups[0]' % shape, '%s.input[%s].inShape' % (tripleSwitch, inputIndex))

            connectedMap = cmds.listConnections('rough_01', d=False, s=True)
            if connectedMap:
                cmds.connectAttr('%s.outColor' % connectedMap, '%s.input[%s].inTriple' % (tripleSwitch, inputIndex))
            else:
                constantColor = cmds.shadingNode('colorConstant', asUtility=True)
                cmds.setAttr('%s.inColor' % constantColor, getRoughnessValue[key])
                cmds.connectAttr('%s.outColor' % constantColor, '%s.input[%s].inTriple' % (tripleSwitch, inputIndex))

            inputIndex += 1

    return tripleSwitch