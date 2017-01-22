from maya import cmds


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

    def polygonView(self):

        """Toggles visibility of all polygonal objects in the current viewport"""

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':
            state = cmds.modelEditor(self.panelFocused, query=True, polymeshes=True)
            cmds.modelEditor(self.panelFocused, e=True, polymeshes=(not state))
