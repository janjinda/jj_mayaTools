"""
Automatically generated 3 point light rig based on your scene scale.

Author: Jan Jinda
Email: janjinda@janjinda.com
Version: 1.0.0
"""

# Usual imports
import maya.cmds as cmds

def createLightRig():
    """Create 3 point light righ

    Create and move lights based on the scene bounding box and switch
    Viewport 2.0
    
    Args:
        None
        
    Returns:
        Nothing
    """
    # Object names
    lightGroupName = 'jj_lightRig_grp'
    lightKeyName = 'key_light'
    lightRimName = 'rim_light'
    lightFillName = 'fill_light'
    lightRimTargetName = 'rim_light_target_null'

    # Check if light rig already exists
    if not cmds.objExists(lightGroupName):
        # Create all objects
        lightKey = cmds.directionalLight(n=lightKeyName)
        lightRim = cmds.spotLight(n=lightRimName)
        lightFill = cmds.ambientLight(n=lightFillName)
        lightRimTarget = cmds.spaceLocator(n=lightRimTargetName)
        
        # Get the scene bounding box if scene is not empty
        scene = cmds.ls(type='mesh')
        if len(scene) == 0:
            bBox = ((-5, 5), (0, 15), (-5, 5))
        else:
            bBox = cmds.polyEvaluate(scene, boundingBox=1)
            
        bBoxList = [element for tupl in bBox for element in tupl]
        
        # Set scale factor based on bounding box size
        if max(bBoxList) > 200 or min(bBoxList) < -200:
            scaleFactor = 20
        else:
            scaleFactor = 3    
        
        # Save bounding box coordinates
        lightKeyX = (bBox[0])[1]
        lightKeyY = (bBox[1])[1]
        lightKeyZ = (bBox[2])[1]
        
        lightRimX = (bBox[0])[0]
        lightRimY = (bBox[1])[1]
        lightRimZ = (bBox[2])[0]

        # Transform lights based on coordinates and scale factor
        cmds.move(round((lightKeyX+lightKeyX/3)),
                  round((lightKeyY+lightKeyY/3)),
                  round((lightKeyZ+lightKeyZ/2)),
                  lightKey)
                  
        cmds.rotate(-35,20,0, lightKey)
        cmds.scale(scaleFactor,scaleFactor,scaleFactor, lightKey)

        cmds.move(round((lightRimX+lightRimX/3)),
                  round((lightRimY+lightRimY/3)),
                  round((lightRimZ+lightRimZ/2)),
                  lightRim)
                  
        cmds.scale(scaleFactor,scaleFactor,scaleFactor, lightRim)
        
        # Aim rim right to the middle of the bounding box
        cmds.aimConstraint(lightRimTarget, cmds.listRelatives(lightRim, parent=1), aimVector=(0,0,-1))
        cmds.move(0,(round(((bBox[1])[1])/2)),0, lightRimTarget)
        
        # Set all lights attributes
        cmds.setAttr('%s.color' % lightRim,0.6,0.8,1)
        cmds.setAttr('%s.intensity' % lightRim,1.25)
        cmds.setAttr('%s.penumbraAngle' % lightRim,50)
        cmds.setAttr('%s.useDepthMapShadows' % lightRim,1)
        cmds.setAttr('%s.dmapResolution' % lightRim,4096)
        cmds.setAttr('%s.dmapFilterSize' % lightRim,4)
        
        cmds.setAttr('%s.useDepthMapShadows' % lightKey,1)
        cmds.setAttr('%s.dmapResolution' % lightKey,4096)
        cmds.setAttr('%s.dmapFilterSize' % lightKey,4)
        
        cmds.setAttr('%s.intensity' % lightFill,0.35)
        
        # Group lights and reset pivot to origin
        lights = [lightKey, lightRim, lightFill, lightRimTarget[0]]
        lightsGroup = cmds.group(lights, name=lightGroupName)
        cmds.xform(lightsGroup, ws=True, sp=(0,0,0), rp=(0,0,0))
        
        # Reorder outliner to have ligth rig right after default cameras
        cmds.reorder(lightsGroup, front=True)
        cmds.reorder(lightsGroup, relative=4)
        
        # Switch Viewport 2.0 function
        switchViewport2()


def switchViewport2():
    """Turns on Viewport 2.0 and turns on lights and shadows

    Args:
        None
        
    Returns:
        Nothing
    """
    # Get current panel
    panelFocused = cmds.getPanel(withFocus=True)
    
    # Check if current panel is a viewport
    if cmds.getPanel(typeOf=panelFocused) == 'modelPanel':
        # Switch to Viewport 2.0
        cmds.modelEditor(panelFocused, e=True, rendererName='vp2Renderer')
        # Turn on all necessary features (shadows, lights, AAA, AO)
        cmds.modelEditor(panelFocused, e=True, shadows=True)
        cmds.modelEditor(panelFocused, e=True, displayLights='all')
        cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable', 1)
        cmds.setAttr('hardwareRenderingGlobals.ssaoEnable', 1)
        
