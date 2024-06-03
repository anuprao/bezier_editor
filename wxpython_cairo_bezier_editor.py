#!/usr/bin/env python

import sys
import math
import os

#

import wx

try:
	import wx.lib.wxcairo as wxcairo
	import cairo
	haveCairo = True
except ImportError:
	haveCairo = False
	
#----------------------------------------------------------------------
 
class curvePoint:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.r = 5
		self.h = None
		self.bSelected = False

	def contains(self, px, py):
		dist = math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)
		return dist <= self.r

	def move(self, dx, dy):
		#print('move')
		self.x = self.x + dx
		self.y = self.y + dy

	def move_to(self,x, y):

		dx = x - self.x
		dy = y - self.y

		self.x = x
		self.y = y

		if None != self.h:
			self.h.move(dx, dy)

	def setAnchorCorner(self):
		if None != self.h:
			self.h.setAnchorCorner()

	def setAnchorSmooth_sym(self):
		if None != self.h:
			self.h.setAnchorSmooth_sym()

	def setAnchorSmooth_asym(self):
		if None != self.h:
			self.h.setAnchorSmooth_asym()

class curveAnchor:

	def __init__(self, x, y, sx, sy):
		self.x = x
		self.y = y
		self.sx = sx
		self.sy = sy

		self.h = None

	def move(self, dx, dy):
		#print('move')
		self.x = self.x + dx
		self.y = self.y + dy

	def move_to(self,x, y):

		#dx = x - self.x
		#dy = y - self.y

		self.x = x
		self.y = y

		if None != self.h:
			self.h.update_other_anchor(self)

	def contains(self, px, py):
		#print("curveAnchor.contains : ", px, py)
		dx = math.fabs(self.x - px)
		dy = math.fabs(self.y - py)
		return (dx <= (self.sx/2)) and (dy <= (self.sy/2)) 

class curveSeg:
	def __init__(self, a, d, infx=0.0, infy=0.0):
		self.a = a
		self.d = d
		self.infx = infx
		self.infy = infy
		self.b = None
		self.c = None
		self.computeDefaultHandle()

	def computeDefaultHandle(self):

		dx = self.d.x - self.a.x
		dy = self.d.y - self.a.y
		incrx = dx / 3
		incry = dy / 3
		
		#print(dx)
		#print(dy)
		#print(incrx)
		#print(incry)

		self.b = curveAnchor(self.a.x + incrx + (self.infx*incry), self.a.y + incry + (self.infy*incrx), 10, 10)
		self.c = curveAnchor(self.d.x - incrx + (self.infx*incry), self.d.y - incry + (self.infy*incrx), 10, 10)

class curveHandle:

	HANDLE_CORNER = 0
	HANDLE_SMOOTH_SYM = 1
	HANDLE_SMOOTH_ASYM = 2

	def __init__(self, p):
		self.p = p
		self.p.h = self

		self.a1 = None
		self.a2 = None

		self.eMode = curveHandle.HANDLE_CORNER		

	def set_a1(self, a):
		if None != a :
			self.a1 = a
			self.a1.h = self.p.h

	def set_a2(self, a):
		if None != a :
			self.a2 = a
			self.a2.h = self.p.h

	##########

	def update_a1_smooth_sym(self):
		#print('update_a1_smooth_sym')

		if None != self.a2:
			dx = self.a2.x - self.p.x
			dy = self.a2.y - self.p.y

			if None != self.a1:
				self.a1.x = self.p.x - dx
				self.a1.y = self.p.y - dy

	def update_a2_smooth_sym(self):
		#print('update_a2_smooth_sym')

		if None != self.a1:
			dx = self.p.x - self.a1.x
			dy = self.p.y - self.a1.y

			if None != self.a2:
				self.a2.x = self.p.x + dx
				self.a2.y = self.p.y + dy

	##########

	def update_a1_smooth_asym(self):
		#print('update_a1_smooth_asym')

		if None != self.a2:
			ix = self.a2.x - self.p.x
			iy = self.a2.y - self.p.y
			i = math.sqrt((ix ** 2) + (iy ** 2))

			#print("i", i)
			
			if 0.1 < i:

				if None != self.a1:

					jx = self.p.x - self.a1.x
					jy = self.p.y - self.a1.y
					j = math.sqrt((jx ** 2) + (jy ** 2))

					#print("j", j)

					if 0.1 < j:

						#jx/j = ix/i
						jx = (j*ix)/i
						jy = (j*iy)/i

						self.a1.x = self.p.x - jx
						self.a1.y = self.p.y - jy

						#s = self.p.x - dx
						#self.a1.y = self.p.y - dy

	def update_a2_smooth_asym(self):
		#print('update_a2_smooth_asym')

		if None != self.a1:
			ix = self.p.x - self.a1.x
			iy = self.p.y - self.a1.y
			i = math.sqrt((ix ** 2) + (iy ** 2))

			#print("i", i)
			
			if 0.1 < i:

				if None != self.a2:

					jx = self.a2.x - self.p.x
					jy = self.a2.y - self.p.y
					j = math.sqrt((jx ** 2) + (jy ** 2))

					#print("j", j)

					if 0.1 < j:

						#jx/j = ix/i
						jx = (j*ix)/i
						jy = (j*iy)/i

						self.a2.x = self.p.x + jx
						self.a2.y = self.p.y + jy

						#s = self.p.x - dx
						#self.a1.y = self.p.y - dy

	##########			

	def update_other_anchor(self, sampleAnchor):
		
		if curveHandle.HANDLE_SMOOTH_SYM == self.eMode :
					
			if sampleAnchor == self.a1:
				self.update_a2_smooth_sym()

			if sampleAnchor == self.a2:
				self.update_a1_smooth_sym()

		if curveHandle.HANDLE_SMOOTH_ASYM == self.eMode :
					
			if sampleAnchor == self.a1:
				self.update_a2_smooth_asym()

			if sampleAnchor == self.a2:
				self.update_a1_smooth_asym()

	def move(self, dx, dy):
		#print('move')
	
		if None != self.a1:
			self.a1.move(dx, dy)
		
		if None != self.a2:
			self.a2.move(dx, dy)

	def setAnchorCorner(self):
		self.eMode = curveHandle.HANDLE_CORNER	

	def setAnchorSmooth_sym(self):
		self.eMode = curveHandle.HANDLE_SMOOTH_SYM

		self.update_a2_smooth_sym()

	def setAnchorSmooth_asym(self):
		self.eMode = curveHandle.HANDLE_SMOOTH_ASYM

		self.update_a2_smooth_asym()		

class curve:
	def __init__(self):
		self.infy = -0.5

		self.arrPoints = []
		self.arrHandles = []
		self.arrSegments = []

	def addPoint(self, sampleCurvePoint):

		prevIdxPt = len(self.arrPoints) - 1
		#print("#", prevIdxPt)

		self.arrPoints.append(sampleCurvePoint)

		newCurveHandle = curveHandle(sampleCurvePoint)
		self.arrHandles.append(newCurveHandle)

		if 0 <= prevIdxPt :

			newIdxPt = prevIdxPt + 1
			#print("##", newIdxPt)

			a = self.arrPoints[prevIdxPt]
			d = self.arrPoints[newIdxPt]
			newCurveSeg = curveSeg(a, d, infy= self.infy)
			self.arrSegments.append(newCurveSeg)

			#newCurveHandle.a1 = newCurveSeg.c
			newCurveHandle.set_a1(newCurveSeg.c)

			prevCurveHandle = self.arrHandles[prevIdxPt]
			#prevCurveHandle.a2 = newCurveSeg.b
			prevCurveHandle.set_a2(newCurveSeg.b)

			# Toggle 
			self.infy = -self.infy

class panelEditor(wx.Panel):
	def __init__(self, parent, txtStatus, pos, size):
		wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
		self.txtStatus = txtStatus

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		
		self.Bind(wx.EVT_LEFT_DOWN, self.OnDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnUp)
		self.Bind(wx.EVT_MOTION, self.OnDrag)

		self.oCurve = curve()

		a = curvePoint(50,200)
		self.oCurve.addPoint(a)
		d = curvePoint(350, 200)
		self.oCurve.addPoint(d)
		g = curvePoint(650, 200)
		self.oCurve.addPoint(g)

		self.currDragNode = None
		self.currSelNode = None
		
		#print("-+-")
		#print(self.oCurve.arrHandles[1].a2.y)

		#self.oCurve.arrHandles[1].a1.y = 0
		#self.oCurve.arrHandles[1].update_a2_smooth_sym()

		#self.oCurve.arrHandles[1].a2.y = 400
		#self.oCurve.arrHandles[1].update_a1_smooth_sym()

		'''
		for sh in self.oCurve.arrHandles:
			print("---")

			print('p', sh.p.x, sh.p.y)

			if None == sh.a1:
				print('None')
			else:
				#print('a1', type(sh.a1))
				print('a1', sh.a1.x, sh.a1.y)

			if None == sh.a2:
				print('None')
			else:
				#print('a2', type(sh.a2))
				print('a2', sh.a2.x, sh.a2.y)

		print("-=-")
		'''

	def findNodeAtLoc(self, x, y):
		tmpSelNode = None
		for pt in self.oCurve.arrPoints:
			if True == pt.contains(x,y):
				tmpSelNode = pt
				break

		return tmpSelNode

	def findAnchorAtLoc(self, x, y):
		tmpSelAnchor = None
		#print("findAnchorAtLoc", x, y)
		for handle in self.oCurve.arrHandles:
			if None != handle.a1:
				if True == handle.a1.contains(x,y):
					tmpSelAnchor = handle.a1
					#print('a1')
					break
			if None != handle.a2:
				if True == handle.a2.contains(x,y):
					tmpSelAnchor = handle.a2
					#print('a2')
					break

		return tmpSelAnchor

	def setCurrSelNode(self, sampleNode):
		prevNode = self.currSelNode
		self.currSelNode = sampleNode
		#print("currSelNode", self.currSelNode)

		if None != sampleNode:
			self.currSelNode.bSelected = True
		else:
			if None != prevNode:
				prevNode.bSelected = False

	def setAnchorCorner(self):
		if None != self.currSelNode:
			self.currSelNode.setAnchorCorner()

	def setAnchorSmooth_sym(self):
		if None != self.currSelNode:
			self.currSelNode.setAnchorSmooth_sym()

	def setAnchorSmooth_asym(self):
		if None != self.currSelNode:
			self.currSelNode.setAnchorSmooth_asym()

	def OnDown(self, event):
		x, y = event.GetPosition()
		tmpLabel = "Click coordinates: X={} Y={}".format(x,y)
		self.txtStatus.SetLabel(tmpLabel)

		self.setCurrSelNode(None)

		if None == self.currDragNode:
			self.currDragNode = self.findNodeAtLoc(x,y)
			if None == self.currDragNode:
				self.currDragAnchor = self.findAnchorAtLoc(x,y)
		'''
				if None == self.currDragAnchor:
					print('None')
				else:
					print("Anchor", self.currDragAnchor)
			else:
				print("Node", self.currDragNode)
		'''
		
		self.setCurrSelNode(self.currDragNode)

	def OnUp(self, event):
		x, y = event.GetPosition()

		tmpLabel = "Release coordinates: X={} Y={}".format(x,y)
		self.txtStatus.SetLabel(tmpLabel)

		self.currDragNode = None

	def OnDrag(self, event):
		x, y = event.GetPosition()
		if not event.Dragging():
			event.Skip()
			return

		event.Skip()     

		#obj = event.GetEventObject()
		#sx, sy = obj.GetScreenPosition()
		#self.Move(sx+x,sy+y)

		tmpLabel = "Dragging positions: X={} Y={}".format(x,y)
		self.txtStatus.SetLabel(tmpLabel)

		if None != self.currDragNode:

			#print("Node", self.currDragNode)

			self.currDragNode.move_to(x,y)

		else:

			if None != self.currDragAnchor:

				#print("Anchor", self.currDragAnchor)
				self.currDragAnchor.move_to(x,y)

		self.Refresh()

	def OnPaint(self, evt):
		if self.IsDoubleBuffered():
			dc = wx.PaintDC(self)
		else:
			dc = wx.BufferedPaintDC(self)
		dc.SetBackground(wx.WHITE_BRUSH)
		dc.Clear()

		self.Render(dc)

	def renderCurveNode(self, ctx, a):

		# Draw circle at 'a'
		ctx.move_to(a.x, a.y)
		ctx.arc(a.x, a.y, a.r, 0, 2*math.pi)
		ctx.close_path()

		if True == a.bSelected:
			ctx.set_source_rgb(0.2, 1, 0.2)
		else:
			ctx.set_source_rgb(1, 0.5, 0.5)

		ctx.fill()

	def renderHandle(self, ctx, a, b):

		# Draw line from 'a' to 'b'
		ctx.move_to(a.x, a.y)
		ctx.line_to(b.x, b.y)
		ctx.set_source_rgb(0.5, 0.5, 0.5)
		ctx.set_line_width(0.5)
		ctx.stroke()

	def renderAnchor(self, ctx, b, eMode, bSelected):

		if curveHandle.HANDLE_SMOOTH_SYM == eMode :
			ctx.rectangle(b.x-5 -3, b.y-5 -3 , b.sx + 6, b.sy + 6)

			ctx.set_source_rgb(0.5, 0.5, 1)
			ctx.set_line_join(cairo.LINE_JOIN_ROUND)
			ctx.stroke()

		elif curveHandle.HANDLE_SMOOTH_ASYM == eMode :
			ctx.rectangle(b.x-5 -3, b.y-5 -3 , b.sx + 6, b.sy + 6)

			ctx.set_source_rgb(1, 0.1, 1)
			ctx.set_line_join(cairo.LINE_JOIN_ROUND)
			ctx.stroke()

		# Draw square at 'b'
		ctx.rectangle(b.x-5, b.y-5, b.sx, b.sy)
		ctx.set_source_rgb(0.5, 0.5, 1)
		ctx.fill()

	def renderCurveSegment(self, ctx, a, b, c, d, bNodes=False, bHandles=False, bAnchors=False):

		# Draw the image
		ctx.move_to(a.x, a.y)
		ctx.curve_to(b.x, b.y, c.x, c.y, d.x, d.y)
		ctx.set_source_rgb(1, 0, 0)
		ctx.set_line_width(2)
		ctx.stroke()

		'''
		if True == bHandles :
			self.renderHandle(ctx, a, b)
			self.renderHandle(ctx, c, d)
		'''

		'''
		if True == bAnchors :
			self.renderAnchor(ctx, b)
			self.renderAnchor(ctx, c)
		'''

		'''
		if True == bNodes :
			self.renderCurveNode(ctx, a)
			self.renderCurveNode(ctx, d)
		'''

	def renderCurve(self, ctx, sampleCurve, bNodes=False, bHandles=False, bAnchors=False):

		for sampleCurveSeg in sampleCurve.arrSegments:
			
			#print(sampleCurveSeg)
			self.renderCurveSegment(ctx, sampleCurveSeg.a, sampleCurveSeg.b, sampleCurveSeg.c, sampleCurveSeg.d, bNodes, bHandles, bAnchors)

		if True == bNodes :
			for pt in sampleCurve.arrPoints:
				self.renderCurveNode(ctx, pt)

		for handle in sampleCurve.arrHandles:
			if True == bAnchors :
				if None != handle.a1:
					self.renderAnchor(ctx, handle.a1, handle.eMode, handle.p.bSelected)
				if None != handle.a2:
					self.renderAnchor(ctx, handle.a2, handle.eMode, handle.p.bSelected)
			if True == bHandles :
				if None != handle.a1:
					self.renderHandle(ctx, handle.p, handle.a1)
				if None != handle.a2:
					self.renderHandle(ctx, handle.p, handle.a2)


	def Render(self, dc):
		# Draw some stuff on the plain dc
		#sz = self.GetSize()
		#print(sz)
		
		# now draw something with cairo
		ctx = wxcairo.ContextFromDC(dc)
		#ctx = cairo.Context(surface)

		#

		#dc.SetPen(wx.Pen("black", 1))

		# Paint the background
		ctx.set_source_rgb(1, 1, 1)
		ctx.paint()

		self.renderCurve(ctx, self.oCurve, True, True, True)

#----------------------------------------------------------------------

class frameWindow(wx.Frame):
	def __init__(self, title):
		wx.Frame.__init__(self, None, title=title, size=(540,960))

		self.txtStatus = wx.StaticText(self, -1, label="Left click mouse, move and release", size=(512,20))

		########

		vbox_m = wx.BoxSizer(wx.VERTICAL)

		####
		
		hbox_top = wx.BoxSizer(wx.HORIZONTAL)

		self.btnAnchorCorner = wx.Button(self, label='Corner', size=(70, 30))
		hbox_top.Add(self.btnAnchorCorner, proportion=1)

		self.btnAnchorSmooth_sym = wx.Button(self, label='Smooth Sym', size=(70, 30))
		hbox_top.Add(self.btnAnchorSmooth_sym, proportion=1)

		self.btnAnchorSmooth_asym = wx.Button(self, label='Smooth Asym', size=(70, 30))
		hbox_top.Add(self.btnAnchorSmooth_asym, proportion=1)

		vbox_m.Add(hbox_top, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=4)

		####

		hbox_mid = wx.BoxSizer(wx.HORIZONTAL)

		self.panel = panelEditor(self, self.txtStatus, (0,20), (720,480))
		hbox_mid.Add(self.panel, proportion=1, flag=wx.EXPAND)

		vbox_m.Add(hbox_mid, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=4)

		####
		
		hbox_bottom = wx.BoxSizer(wx.HORIZONTAL)

		
		hbox_bottom.Add(self.txtStatus, proportion=1, flag=wx.EXPAND)

		vbox_m.Add(hbox_bottom, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=4)

		########

		self.SetSizer(vbox_m)

		################################

		self.btnAnchorCorner.Bind(wx.EVT_BUTTON, self.OnAnchorCorner)
		self.btnAnchorSmooth_sym.Bind(wx.EVT_BUTTON, self.OnAnchorSmooth_sym)
		self.btnAnchorSmooth_asym.Bind(wx.EVT_BUTTON, self.OnAnchorSmooth_asym)
		

	def OnAnchorCorner(self, e):
		#print('OnAnchorCorner')
		self.panel.setAnchorCorner()

	def OnAnchorSmooth_sym(self, e):
		#print('OnAnchorSmooth_sym')
		self.panel.setAnchorSmooth_sym()

	def OnAnchorSmooth_asym(self, e):
		#print('OnAnchorSmooth_asym')
		self.panel.setAnchorSmooth_asym()


#----------------------------------------------------------------------

if __name__ == '__main__':
	 
	appEditor = wx.App()#redirect=True)
	top = frameWindow("Path Editor")
	top.Show()
	appEditor.MainLoop()

