import maya.cmds as mc
from PySide import QtCore, QtGui


class CameraToolkit(object):
    def __init__(self):

        self.panelFocused = mc.getPanel(withFocus=True)

        self.panelType = (True if mc.getPanel(typeOf=self.panelFocused)=='modelPanel' else False)

        if self.panelType == True:

            self.camera = mc.listRelatives(mc.modelPanel(self.panelFocused, q=True, camera=True), children=True)[0]

            mc.setAttr(('%s.panZoomEnabled' % self.camera), 1)

            self.zoom = mc.getAttr('%s.zoom' % self.camera)
            self.vertPan = mc.getAttr('%s.verticalPan' % self.camera)
            self.horizPan = mc.getAttr('%s.horizontalPan' % self.camera)

        else:
            raise RuntimeError('Not in model panel!')

    def zoomPlus(self):

        newZoom = self.zoom - 0.1
        mc.setAttr(('%s.zoom' % self.camera), newZoom)

    def zoomMinus(self):

        newZoom = self.zoom + 0.1
        mc.setAttr(('%s.zoom' % self.camera), newZoom)

    def panUp(self):

        newVertPan = self.vertPan + 0.02
        mc.setAttr(('%s.verticalPan' % self.camera), newVertPan)

    def panDown(self):

        newVertPan = self.vertPan - 0.02
        mc.setAttr(('%s.verticalPan' % self.camera), newVertPan)

    def panRight(self):

        newHorizPan = self.horizPan + 0.02
        mc.setAttr(('%s.horizontalPan' % self.camera), newHorizPan)

    def panLeft(self):

        newHorizPan = self.horizPan - 0.02
        mc.setAttr(('%s.horizontalPan' % self.camera), newHorizPan)

    def zoomPanReset(self):

        newZoom = 1
        newVertPan = 0
        newHorizPan = 0
        mc.setAttr(('%s.zoom' % self.camera), newZoom)
        mc.setAttr(('%s.verticalPan' % self.camera), newVertPan)
        mc.setAttr(('%s.horizontalPan' % self.camera), newHorizPan)
        print ('%s was reset.' % self.camera)

class CameraToolkitUI(QtGui.QDialog):

    def __init__(self):
        super(CameraToolkitUI, self).__init__()

        self.setWindowTitle('Camera Toolkit')
        self.toolkit = CameraToolkit()

        self.buildUI()

    def buildUI(self):
        layout = QtGui.QGridLayout(self)

        zoomPlusBtn = QtGui.QPushButton('+')
        zoomPlusBtn.clicked.connect(self.toolkit.zoomPlus)
        layout.addWidget(zoomPlusBtn, 0, 0)

        resetBtn = QtGui.QPushButton('Reset')
        resetBtn.clicked.connect(self.toolkit.zoomPanReset)
        layout.addWidget(resetBtn, 0, 1)

        zoomMinusBtn = QtGui.QPushButton('-')
        zoomMinusBtn.clicked.connect(self.toolkit.zoomMinus)
        layout.addWidget(zoomMinusBtn, 0, 2)

        panUpBtn = QtGui.QPushButton('Up')
        panUpBtn.clicked.connect(self.toolkit.panUp)
        layout.addWidget(panUpBtn, 1, 1)

        panLeftBtn = QtGui.QPushButton('Left')
        panLeftBtn.clicked.connect(self.toolkit.panLeft)
        layout.addWidget(panLeftBtn, 2, 0)

        panRightBtn = QtGui.QPushButton('Left')
        panRightBtn.clicked.connect(self.toolkit.panRight)
        layout.addWidget(panRightBtn, 2, 2)

        panDownBtn = QtGui.QPushButton('Down')
        panDownBtn.clicked.connect(self.toolkit.panDown)
        layout.addWidget(panDownBtn, 3, 1)


def showUI():

    ui = CameraToolkitUI()
    ui.show()
    return ui