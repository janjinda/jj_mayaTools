from maya import cmds
from PySide import QtCore, QtGui


class ZoomPan(object):
    """A set of methods for setting current camera Zoom and Pan"""

    def __init__(self):

        self.panelFocused = cmds.getPanel(withFocus=True)

        try:

            self.panelTest()

        except RuntimeError:

            print "Not in model panel!"

        else:

            self.getCamera()

            cmds.setAttr(('%s.panZoomEnabled' % self.camera), 1)

            self.zoom = cmds.getAttr('%s.zoom' % self.camera)
            self.vertPan = cmds.getAttr('%s.verticalPan' % self.camera)
            self.horizPan = cmds.getAttr('%s.horizontalPan' % self.camera)

    def panelTest(self):
        """Tests if the model panel is active and prevents script from crashing."""

        panelType = cmds.getPanel(typeOf=self.panelFocused)

        if panelType != 'modelPanel':
            raise RuntimeError

    def getCamera(self):
        """Finds a current active camera."""

        self.camera = cmds.modelPanel(self.panelFocused, q=True, camera=True)

        # Checks if the self.camera is really camera, transform is sometimes selected instead
        if cmds.objectType(self.camera) == 'camera':

            pass

        else:
            self.camera = cmds.listRelatives(self.camera, children=True)[0]

    def zoomPlus(self, *args):
        """Simple method iterating on Zoom Plus."""

        self.__init__()
        self.zoom -= 0.1
        cmds.setAttr(('%s.zoom' % self.camera), self.zoom)

    def zoomMinus(self, *args):
        """Simple method iterating on Zoom Minus."""

        self.__init__()
        self.zoom += 0.1
        cmds.setAttr(('%s.zoom' % self.camera), self.zoom)

    def panUp(self, *args):
        """Simple method iterating on Pan Up."""

        self.__init__()
        self.vertPan += 0.02
        cmds.setAttr(('%s.verticalPan' % self.camera), self.vertPan)

    def panDown(self, *args):
        """Simple method iterating on Pan Down."""

        self.__init__()
        self.vertPan -= 0.02
        cmds.setAttr(('%s.verticalPan' % self.camera), self.vertPan)

    def panRight(self, *args):
        """Simple method iterating on Pan Right."""

        self.horizPan += 0.02
        cmds.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)

    def panLeft(self, *args):
        """Simple method iterating on Pan Left."""

        self.__init__()
        self.horizPan -= 0.02
        cmds.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)

    def zoomPanReset(self, *args):
        """Resets Zoom and Pan and disables Zoom and Pan on the camera."""
        self.__init__()
        self.zoom = 1
        self.vertPan = 0
        self.horizPan = 0
        cmds.setAttr(('%s.zoom' % self.camera), self.zoom)
        cmds.setAttr(('%s.verticalPan' % self.camera), self.vertPan)
        cmds.setAttr(('%s.horizontalPan' % self.camera), self.horizPan)
        cmds.setAttr(('%s.panZoomEnabled' % self.camera), 1)
        print ('%s was reset.' % self.camera)


class CameraToolkitUI(object):
    """Creates toolkit dialog using Maya UI."""

    windowName = "CameraToolkitUI"

    def __init__(self):
        self.toolkitA = ZoomPan()

        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName, title="JJ Camera Toolkit")

        self.buildUI()

    def buildUI(self):
        cmds.columnLayout()

        cmds.frameLayout(label='2D Zoom and Pan', collapsable=True)

        layoutForm = cmds.formLayout(numberOfDivisions=100)

        resetBtn = cmds.button(label="Reset", w=50, h=25, c=self.toolkitA.zoomPanReset)
        zoomMinusBtn = cmds.button(label="-", w=50, h=25, c=self.toolkitA.zoomMinus)
        zoomPlusBtn = cmds.button(label="+", w=50, h=25, c=self.toolkitA.zoomPlus)
        panUpBtn = cmds.button(label="Up", w=50, h=25, c=self.toolkitA.panUp)
        panLeftBtn = cmds.button(label="Left", w=50, h=25, c=self.toolkitA.panLeft)
        panRightBtn = cmds.button(label="Right", w=50, h=25, c=self.toolkitA.panRight)
        panDownBtn = cmds.button(label="Down", w=50, h=25, c=self.toolkitA.panDown)

        cmds.formLayout(layoutForm, e=True, attachForm=[(zoomMinusBtn, 'top', 5), (zoomMinusBtn, 'left', 5),
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
    """Creates toolkit dialog using PyQt."""

    def __init__(self):
        super(CameraToolkitUIQt, self).__init__()

        self.setWindowTitle('JJ Camera Toolkit')
        self.toolkit = ZoomPan()

        self.settings = QtCore.QSettings('JJ', 'jjCameraToolkit')
        geometry = self.settings.value('geometry', '')
        self.restoreGeometry(geometry)

        self.buildUI()

    def closeEvent(self, event):
        geometry = self.saveGeometry()
        self.settings.setValue('geometry', geometry)
        super(CameraToolkitUIQt, self).closeEvent(event)

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
    """Function to open toolkit window. Maya UI or Qt can be chosen using parameter."""

    if type == "cmds":

        # maya cmds UI
        ui = CameraToolkitUI()
        cmds.showWindow(ui.windowName)

    elif type == "qt":

        # Qt UI
        ui = CameraToolkitUIQt()
        ui.show()

    return ui
