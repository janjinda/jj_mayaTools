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

    def zoomPlus(self, *args):

        self.__init__()
        self.zoom -= 0.1
        mc.setAttr(('%s.zoom' % self.camera), self.zoom)

    def zoomMinus(self, *args):

        self.__init__()
        self.zoom += 0.1
        mc.setAttr(('%s.zoom' % self.camera), self.zoom)

    def panUp(self, *args):

        self.__init__()
        self.vertPan += 0.02
        mc.setAttr(('%s.verticalPan' % self.camera), self.vertPan)

    def panDown(self, *args):

        self.__init__()
        self.vertPan -= 0.02
        mc.setAttr(('%s.verticalPan' % self.camera), self.vertPan)

    def panRight(self, *args):

        self.horizPan += 0.02
        mc.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)

    def panLeft(self, *args):

        self.__init__()
        self.horizPan -= 0.02
        mc.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)

    def zoomPanReset(self, *args):

        self.__init__()
        self.zoom = 1
        self.vertPan = 0
        self.horizPan = 0
        mc.setAttr(('%s.zoom' % self.camera), self.zoom)
        mc.setAttr(('%s.verticalPan' % self.camera), self.vertPan)
        mc.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)
        print ('%s was reset.' % self.camera)


class CameraToolkitUI(object):
    windowName = "CameraToolkitUI"

    def __init__(self):
        self.toolkitA = ZoomPan()

        if mc.window(self.windowName, query=True, exists=True):
            mc.deleteUI(self.windowName)

        mc.window(self.windowName, title="JJ Camera Toolkit")

        self.buildUI()

    def buildUI(self):
        mc.columnLayout()

        mc.frameLayout(label='2D Zoom and Pan', collapsable=True)

        layoutForm = mc.formLayout(numberOfDivisions=100)

        resetBtn = mc.button(label="Reset", w=50, h=25, c=self.toolkitA.zoomPanReset)
        zoomMinusBtn = mc.button(label="-", w=50, h=25, c=self.toolkitA.zoomMinus)
        zoomPlusBtn = mc.button(label="+", w=50, h=25, c=self.toolkitA.zoomPlus)
        panUpBtn = mc.button(label="Up", w=50, h=25, c=self.toolkitA.panUp)
        panLeftBtn = mc.button(label="Left", w=50, h=25, c=self.toolkitA.panLeft)
        panRightBtn = mc.button(label="Right", w=50, h=25, c=self.toolkitA.panRight)
        panDownBtn = mc.button(label="Down", w=50, h=25, c=self.toolkitA.panDown)

        mc.formLayout(layoutForm, e=True, attachForm=[(zoomMinusBtn, 'top', 5), (zoomMinusBtn, 'left', 5),
                                                      (resetBtn, 'top', 5), (resetBtn, 'left', 65),
                                                      (zoomPlusBtn, 'top', 5), (zoomPlusBtn, 'left', 125),
                                                      (zoomPlusBtn, 'right', 5),
                                                      (panUpBtn, 'top', 35), (panUpBtn, 'left', 65),
                                                      (panLeftBtn, 'top', 65), (panLeftBtn, 'left', 5),
                                                      (panRightBtn, 'top', 65), (panRightBtn, 'left', 125),
                                                      (panRightBtn, 'right', 5),
                                                      (panDownBtn, 'top', 95), (panDownBtn, 'left', 65),
                                                      (panDownBtn, 'bottom', 5)])


class CameraToolkitUIQt(QtGui.QDialog):
    def __init__(self):
        super(CameraToolkitUIQt, self).__init__()

        self.setWindowTitle('JJ Camera Toolkit')
        self.toolkit = ZoomPan()

        self.buildUI()

    def buildUI(self):
        print self.toolkit

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


def showUI(type='cmds'):
    if type == "cmds":

        # maya cmds UI
        ui = CameraToolkitUI()
        mc.showWindow(ui.windowName)

    elif type == "qt":

        # Qt UI
        ui = CameraToolkitUIQt()
        ui.show()

    return ui
