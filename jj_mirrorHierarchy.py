from maya import cmds

def mirrorHierarchyX():
    
    selection = cmds.ls(selection=True, o=1)
    
    duplicates = cmds.duplicate(selection, renameChildren=True)

    for obj in duplicates:
        cmds.delete(constructionHistory=True)

    newObjects = [item+("1") for item in selection]
        
    for obj in newObjects:

        cmds.setAttr("%s.scaleX" % (obj), -1)
             

    selection = cmds.ls(selection=True, dag=True, long=True)
    selection.sort(key=len, reverse=True)

    for obj in selection:
        
        shortName = obj.split("|")[-1]

        if shortName.startswith("R_"):
            newName = shortName.replace("R_", "L_")
            
        elif shortName.startswith("L_"):
            newName = shortName.replace("L_", "R_")
            
        else:
            newName = shortName
        
        if newName.endswith("1"):
            newName = newName[:-1]

        cmds.rename(shortName, newName)

    cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=False, preserveNormals=True)
