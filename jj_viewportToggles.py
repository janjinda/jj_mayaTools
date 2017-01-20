from maya import cmds


class ViewportToggle(object):

    def __init__(self):

        self.panelFocused = cmds.getPanel(withFocus=True)

    def selectionHighlight(self):

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':

            state = cmds.modelEditor(self.panelFocused, q=True, selectionHiliteDisplay=False)
            cmds.modelEditor(self.panelFocused, e=True, selectionHiliteDisplay=(not state))

    def wireOnShaded(self):

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':

            state = cmds.modelEditor(self.panelFocused, q=True, wireframeOnShaded=False)
            cmds.modelEditor(self.panelFocused, e=True, wireframeOnShaded=(not state))

    def polygonView(self):

        if cmds.getPanel(typeOf=self.panelFocused) == 'modelPanel':
            state = cmds.modelEditor(self.panelFocused, query=True, polymeshes=True)
            cmds.modelEditor(self.panelFocused, e=True, polymeshes=(not state))
