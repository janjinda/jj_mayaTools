import maya.cmds as mc


class ViewportToggle(object):

    def __init__(self):

        self.panelFocused = mc.getPanel(withFocus=True)

    def selectionHighlight(self):

        if mc.getPanel(typeOf=self.panelFocused) == 'modelPanel':

            state = mc.modelEditor(self.panelFocused, q=True, selectionHiliteDisplay=False)
            mc.modelEditor(self.panelFocused, e=True, selectionHiliteDisplay=(not state))

    def wireOnShaded(self):

        if mc.getPanel(typeOf=self.panelFocused) == 'modelPanel':

            state = mc.modelEditor(self.panelFocused, q=True, wireframeOnShaded=False)
            mc.modelEditor(self.panelFocused, e=True, wireframeOnShaded=(not state))

    def polygonView(self):

        if mc.getPanel(typeOf=self.panelFocused) == 'modelPanel':
            state = mc.modelEditor(self.panelFocused, query=True, polymeshes=True)
            mc.modelEditor(self.panelFocused, e=True, polymeshes=(not state))
