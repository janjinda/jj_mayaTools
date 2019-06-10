import maya.cmds as cmds


def listSceneMaterials():
    """
    list all materials used by geometry in the scene
    """

    scene_materials = []
    allSG = cmds.ls(type='shadingEngine')
    materialAssignment = {}

    for SG in allSG:
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
    materialAssignment = listSceneMaterials()

    tripleSwitch = cmds.shadingNode('tripleShadingSwitch', asUtility=True, name='roughnessAlbedo_tripleSwitch')
    cmds.setAttr('%s.default' % tripleSwitch, 0,0,0)

    inputIndex = 0
    for key in materialAssignment:

        albedoInput = cmds.listConnections('%s.specularRoughness' % key, d=False, s=True)

        if not albedoInput:
            constantColor = cmds.shadingNode('colorConstant', asUtility=True, name='constant_%s' % str(getRoughnessValue(key)).replace('.', ''))
            cmds.setAttr('%s.inColor' % constantColor, getRoughnessValue(key), getRoughnessValue(key), getRoughnessValue(key))

        for shape in materialAssignment[key]:
            cmds.connectAttr('%s.instObjGroups[0]' % shape, '%s.input[%s].inShape' % (tripleSwitch, inputIndex))

            if albedoInput:
                cmds.connectAttr('%s.outColor' % albedoInput[0], '%s.input[%s].inTriple' % (tripleSwitch, inputIndex))
            else:
                cmds.connectAttr('%s.outColor' % constantColor, '%s.input[%s].inTriple' % (tripleSwitch, inputIndex))

            inputIndex += 1

    return tripleSwitch


def overrideShader():
    aiUtilityS = cmds.shadingNode('aiUtility', asShader=True, name='roughnessAlbedo_util')
    cmds.setAttr('%s.shadeMode' % aiUtilityS, 2)

    tripleSwitch = linkToTriple()
    cmds.connectAttr('%s.output' % tripleSwitch, '%s.color' % aiUtilityS)


overrideShader()