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


def getValue(material, slot):
    albedoValue = cmds.getAttr('%s.%s' % (material, slot))

    return albedoValue


def linkToTriple(slot):
    materialAssignment = listSceneMaterials()

    tripleSwitch = cmds.shadingNode('tripleShadingSwitch', asUtility=True, name=('%sAlbedo_tripleSwitch' % slot))
    cmds.setAttr('%s.default' % tripleSwitch, 0,0,0)

    inputIndex = 0
    for key in materialAssignment:

        albedoInput = cmds.listConnections('%s.%s' % (key, slot), d=False, s=True)

        if not albedoInput:
            constantColor = cmds.shadingNode('colorConstant', asUtility=True, name='constant_%s_util' % str(round(getValue(key, slot),2)).replace('.', ''))
            cmds.setAttr('%s.inColor' % constantColor, getValue(key, slot), getValue(key, slot), getValue(key, slot))

        for shape in materialAssignment[key]:
            cmds.connectAttr('%s.instObjGroups[0]' % shape, '%s.input[%s].inShape' % (tripleSwitch, inputIndex))

            if albedoInput:
                cmds.connectAttr('%s.outColor' % albedoInput[0], '%s.input[%s].inTriple' % (tripleSwitch, inputIndex))
            else:
                cmds.connectAttr('%s.outColor' % constantColor, '%s.input[%s].inTriple' % (tripleSwitch, inputIndex))

            inputIndex += 1

    return tripleSwitch


def aovOverrideShader(slot):
    aiUtilityS = cmds.shadingNode('aiUtility', asShader=True, name='%s_albedo_aiUtil' % slot)
    cmds.setAttr('%s.shadeMode' % aiUtilityS, 2)

    tripleSwitch = linkToTriple(slot)
    cmds.connectAttr('%s.output' % tripleSwitch, '%s.color' % aiUtilityS)
