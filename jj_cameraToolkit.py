import maya.cmds as mc
from PySide import QtCore, QtGui


class ZoomPan(object):

    def __init__(self):

        self.panelFocused = mc.getPanel(withFocus=True)

        try:

            self.panelTest()

        except RuntimeError:

            print "Not in model panel!"

        else:
            
            self.getCamera()

            mc.setAttr(('%s.panZoomEnabled' % self.camera), 1)

            self.zoom = mc.getAttr('%s.zoom' % self.camera)
            self.vertPan = mc.getAttr('%s.verticalPan' % self.camera)
            self.horizPan = mc.getAttr('%s.horizontalPan' % self.camera)

    def panelTest(self):

        panelType = mc.getPanel(typeOf=self.panelFocused)

        if panelType != 'modelPanel':
            raise RuntimeError
            
    def getCamera(self):
        
        self.camera = mc.modelPanel(self.panelFocused, q=True, camera=True)
        
        if mc.objectType(self.camera) == 'camera':

            pass

        else:
            self.camera = mc.listRelatives(self.camera, children=True)[0]

    def zoomPlus(self):

        self.zoom -= 0.1
        mc.setAttr(('%s.zoom' % self.camera), self.zoom)

    def zoomMinus(self):

        self.zoom += 0.1
        mc.setAttr(('%s.zoom' % self.camera), self.zoom)

    def panUp(self):

        self.vertPan += 0.02
        mc.setAttr(('%s.verticalPan' % self.camera), self.vertPan)

    def panDown(self):

        self.vertPan -= 0.02
        mc.setAttr(('%s.verticalPan' % self.camera), self.vertPan)

    def panRight(self):

        self.horizPan += 0.02
        mc.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)

    def panLeft(self):

        self.horizPan -= 0.02
        mc.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)

    def zoomPanReset(self):

        self.zoom = 1
        self.vertPan = 0
        self.horizPan = 0
        mc.setAttr(('%s.zoom' % self.camera), self.zoom)
        mc.setAttr(('%s.verticalPan' % self.camera), self.vertPan)
        mc.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)
        print ('%s was reset.' % self.camera)


class CameraToolkitUI(QtGui.QDialog):

    def __init__(self):
        super(CameraToolkitUI, self).__init__()

        self.setWindowTitle('Camera Toolkit')
        self.toolkit = ZoomPan()

        self.buildUI()

    def buildUI(self):

        layoutBox = QtGui.QVBoxLayout(self)

        gBox = QtGui.QGroupBox(self)
        gBox.setTitle('2D Zoom and Pan')

        layoutGrid = QtGui.QGridLayout(self)
        gBox.setLayout(layoutGrid)

        layoutBox.addWidget(gBox)

        zoomPlusBtn = QtGui.QPushButton('+')
        zoomPlusBtn.clicked.connect(self.toolkit.zoomPlus)
        layoutGrid.addWidget(zoomPlusBtn, 0, 0)

        resetBtn = QtGui.QPushButton('Reset')
        resetBtn.clicked.connect(self.toolkit.zoomPanReset)
        layoutGrid.addWidget(resetBtn, 0, 1)

        zoomMinusBtn = QtGui.QPushButton('-')
        zoomMinusBtn.clicked.connect(self.toolkit.zoomMinus)
        layoutGrid.addWidget(zoomMinusBtn, 0, 2)

        panUpBtn = QtGui.QPushButton('Up')
        panUpBtn.clicked.connect(self.toolkit.panUp)
        layoutGrid.addWidget(panUpBtn, 1, 1)

        panLeftBtn = QtGui.QPushButton('Left')
        panLeftBtn.clicked.connect(self.toolkit.panLeft)
        layoutGrid.addWidget(panLeftBtn, 2, 0)

        panRightBtn = QtGui.QPushButton('Left')
        panRightBtn.clicked.connect(self.toolkit.panRight)
        layoutGrid.addWidget(panRightBtn, 2, 2)

        panDownBtn = QtGui.QPushButton('Down')
        panDownBtn.clicked.connect(self.toolkit.panDown)
        layoutGrid.addWidget(panDownBtn, 3, 1)


def showUI():

    ui = CameraToolkitUI()
    ui.show()
    return ui

