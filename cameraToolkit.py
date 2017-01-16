import maya.cmds as mc

class CameraToolkit(object):
	
	def __init__(self):
		
		self.panelFocused = mc.getPanel(withFocus=True)
		self.camera = mc.listRelatives(mc.modelPanel(self.panelFocused, q=True, camera=True), children=True)[0]
		
		mc.setAttr(('%s.panZoomEnabled' % self.camera), 1)
		
		self.zoom = mc.getAttr('%s.zoom' % self.camera)
		self.vertPan = mc.getAttr('%s.verticalPan' % self.camera)
		self.horizPan = mc.getAttr('%s.horizontalPan' % self.camera)
		
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

