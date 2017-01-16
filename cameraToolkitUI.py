from cameraToolkit import CameraToolkit
from PySide import QtCore, QtGui


class CameraToolkitUI(QtGui.QDialog):

    def __init__(self):
        super(CameraToolkitUI, self).__init__()

        self.setWindowTitle('OBJ Toolkit')
        self.toolkit = CameraToolkit()

        self.buildUI()

    def buildUI(self):
        layout = QtGui.QVBoxLayout(self)

        iSingleBtn = QtGui.QPushButton('Import Single OBJ')
        iSingleBtn.clicked.connect(self.toolkit.importSingle)
        layout.addWidget(iSingleBtn)

        iBatchBtn = QtGui.QPushButton('Import Batch OBJ')
        iBatchBtn.clicked.connect(self.toolkit.importBatch)
        layout.addWidget(iBatchBtn)

        iSingleBSBtn = QtGui.QPushButton('Import Single OBJ as bShape')
        iSingleBSBtn.clicked.connect(self.toolkit.importSingleBShape)
        layout.addWidget(iSingleBSBtn)

        iBatchBSBtn = QtGui.QPushButton('Import Batch OBJ as bShape')
        iBatchBSBtn.clicked.connect(self.toolkit.importBatchBShape)
        layout.addWidget(iBatchBSBtn)

        eBatchBtn = QtGui.QPushButton('Export Batch OBJ')
        eBatchBtn.clicked.connect(self.toolkit.exportBatch)
        layout.addWidget(eBatchBtn)


def showUI():
    ui = CameraToolkitUI()
    ui.show()
    return ui
