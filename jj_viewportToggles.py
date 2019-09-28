import maya.cmds as cmds


class ViewportToggle(object):
    """

    Viewport Toggles is a simple set of methods for controlling viewport features visibility in Maya.

    """

    def __init__(self):

        # Finds current viewport (panel).
        self.panelFocused = cmds.getPanel(withFocus=True)

    def selectionHighlight(self):

        """Toggles selection highlighting in the current viewport"""

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':

            state = cmds.modelEditor(self.panelFocused, q=True, selectionHiliteDisplay=False)
            cmds.modelEditor(self.panelFocused, e=True, selectionHiliteDisplay=(not state))

    def wireOnShaded(self):

        """Toggles wireframe on shaded polygonal objects in the current viewport"""

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':

            state = cmds.modelEditor(self.panelFocused, q=True, wireframeOnShaded=False)
            cmds.modelEditor(self.panelFocused, e=True, wireframeOnShaded=(not state))

    def hidePolygonView(self):

        """Toggles visibility of all polygonal objects in the current viewport"""

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':
            state = cmds.modelEditor(self.panelFocused, query=True, polymeshes=True)
            cmds.modelEditor(self.panelFocused, e=True, polymeshes=(not state))

    def isolatePolygonView(self):

        """Toggles visibility of control objects to show just polygons in the current viewport"""

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':
            stateNurbs = cmds.modelEditor(self.panelFocused, query=True, nurbsCurves=True)
            stateLocators = cmds.modelEditor(self.panelFocused, query=True, locators=True)
            stateHandles = cmds.modelEditor(self.panelFocused, query=True, handles=True)
            stateJoints = cmds.modelEditor(self.panelFocused, query=True, joints=True)
            stateDeformers = cmds.modelEditor(self.panelFocused, query=True, deformers=True)
            stateLights = cmds.modelEditor(self.panelFocused, query=True, lights=True)
            statePlugins = cmds.modelEditor(self.panelFocused, query=True, pluginShapes=True)
            stateCameras = cmds.modelEditor(self.panelFocused, query=True, cameras=True)

            cmds.modelEditor(self.panelFocused, e=True, nurbsCurves=(not stateNurbs))
            cmds.modelEditor(self.panelFocused, e=True, locators=(not stateLocators))
            cmds.modelEditor(self.panelFocused, e=True, handles=(not stateHandles))
            cmds.modelEditor(self.panelFocused, e=True, joints=(not stateJoints))
            cmds.modelEditor(self.panelFocused, e=True, deformers=(not stateDeformers))
            cmds.modelEditor(self.panelFocused, e=True, lights=(not stateLights))
            cmds.modelEditor(self.panelFocused, e=True, pluginShapes=(not statePlugins))
            cmds.modelEditor(self.panelFocused, e=True, cameras=(not stateCameras))
