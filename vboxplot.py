# -*- coding: utf-8 -*-
"""
2019/01/07
李长圣 @ 南京大学
功能：
绘制颗粒及墙体
"""

import os
import shutil

def get_color_map(filename):
	"""
	2018/05/28
	LI ChangSheng @ nanyang technological university
	use：
	get the color map of colorfile

	input：
	[1]ColorFileName
	a str

	output：
	[1]ColorMap
	a dict

	example：
	ColorFileName  = r'./ColorRicebal.txt'

	"""
	xfile = open(filename, "r")#, encoding = 'utf-8')
	colorlist = []
	for line in xfile:
		ltmp = line.split()
		#print (ltmp, '\n')
		for i in range(len(ltmp)):
			ltmp[i] = float(ltmp[i])
		colorlist.append(ltmp)
	xfile.close()
	
	colormap={}
	colormap['light gray']  = (colorlist[0],0)
	colormap['green']       = (colorlist[1],1)
	colormap['yellow']      = (colorlist[2],2)
	colormap['red']         = (colorlist[3],3)
	colormap['white']       = (colorlist[4],4)
	colormap['black']       = (colorlist[5],5)
	colormap['medium gray'] = (colorlist[6],6)
	colormap['blue']        = (colorlist[7],7)
	colormap['green blue']  = (colorlist[8],8)
	colormap['violet']      = (colorlist[9],9)
	return colorlist,colormap

#DispGrad = np.mat(entries)
#print (DispGrad )

from pylab import *
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
def plot_ball(fig, ax, BALL, ColorList):
	"""
	输入参数：
	[1] fig  
	[2] Ball  颗粒信息[ index id x y r color]
	[3] ColorList
		[0.85 0.85 0.85 
		 0.00 1.00 0.00
		 1.00 1.00 0.00
		 1.00 0.00 0.00 
		 0.90 0.90 0.90 
		 0.15 0.15 0.15 
		 0.50 0.50 0.50 
		 0.00 0.00 1.00 
		 0.00 1.00 1.00 
		 1.00 0.00 1.00]
	"""

	VBOXid   = [int(oneInfo[1])   for oneInfo in BALL]
	VBOXx    = [float(oneInfo[2]) for oneInfo in BALL]
	VBOXy    = [float(oneInfo[3]) for oneInfo in BALL]
	VBOXr    = [float(oneInfo[4]) for oneInfo in BALL]
	VBOXcolor= [int(oneInfo[5])   for oneInfo in BALL]
	#plt.plot(VBOXx,VBOXy,'.')
	left   = 0.0
	right  = 0.0
	bottom = 0.0
	top    = 0.0
	radiusMax=0.0
	
	for i in range(len(VBOXx)):
#		if VBOXy[i] < 0.0:
#			continue
		center   = (VBOXx[i],VBOXy[i])
		radius   = VBOXr[i]
		vboxc    = VBOXcolor[i]
		colorRGB = ColorList[vboxc]
		cir = Circle(xy = center, radius = radius, facecolor=colorRGB)
		ax.add_patch(cir)
		
		#search_boundary
		if VBOXx[i] < left:
			left = VBOXx[i]
		if VBOXx[i] > right:
			right = VBOXx[i]
		if VBOXy[i] < bottom:
			bottom = VBOXy[i]
		if VBOXy[i] > top:
			top = VBOXy[i]
		radiusMax=max(radiusMax,radius)

	return left,right+2.0*radiusMax,bottom,top+2.0*radiusMax

from matplotlib.lines import Line2D
def plot_wall(fig, ax, WALL, ColorList,linewidth=1):
	"""
	输入参数：
	[1] fig  
	[2] Wall  墙体信息[ index id p1x p1y p2x p2y color ]
	[3] ColorList
		[0.85 0.85 0.85 
		 0.00 1.00 0.00
		 1.00 1.00 0.00
		 1.00 0.00 0.00 
		 0.90 0.90 0.90 
		 0.15 0.15 0.15 
		 0.50 0.50 0.50 
		 0.00 0.00 1.00 
		 0.00 1.00 1.00 
		 1.00 0.00 1.00]
	"""
	wid     = [int(oneInfo[1])   for oneInfo in WALL]
	wp1x    = [float(oneInfo[2]) for oneInfo in WALL]
	wp1y    = [float(oneInfo[3]) for oneInfo in WALL]
	wp2x    = [float(oneInfo[4]) for oneInfo in WALL]
	wp2y    = [float(oneInfo[5]) for oneInfo in WALL]
	#wcolor= [int(oneInfo[5])   for oneInfo in WALL]
	
	left   = 0.0
	right  = 0.0
	bottom = 0.0
	top    = 0.0
	
	#plt.plot(VBOXx,VBOXy,'.')
	for i in range(len(wid)):
		# 两条line的数据 
		line1 = [(wp1x[i], wp1y[i]), (wp2x[i], wp2y[i])] 
		(line1_xs, line1_ys) = zip(*line1) 
		# 创建两条线，并添加 
		ax.add_line(Line2D(line1_xs, line1_ys, linewidth=linewidth, color='black')) 

		#search_boundary
		left   = min(left, wp1x[i], wp2x[i])
		right  = max(right, wp1x[i], wp2x[i])
		bottom = min(bottom, wp1y[i], wp2y[i])
		top    = max(top, wp1y[i], wp2y[i])
		#print(left,right,bottom,top)
	return left,right,bottom,top
from matplotlib.lines import Line2D
import numpy as np
def plot_surface(fig, ax,  BALL,linewidth=1):
	"""
	输入参数：
	[1] fig  
	[2] Ball  颗粒信息[ index id x y r color]
	[3] ColorList
		[0.85 0.85 0.85 
		 0.00 1.00 0.00
		 1.00 1.00 0.00
		 1.00 0.00 0.00 
		 0.90 0.90 0.90 
		 0.15 0.15 0.15 
		 0.50 0.50 0.50 
		 0.00 0.00 1.00 
		 0.00 1.00 1.00 
		 1.00 0.00 1.00]
	[4] wallleft,wallright 边界墙信息
	"""
	VBOXid   = [int(oneInfo[1])   for oneInfo in BALL]
	VBOXx    = [float(oneInfo[2]) for oneInfo in BALL]
	VBOXy    = [float(oneInfo[3]) for oneInfo in BALL]
	VBOXr    = [float(oneInfo[4]) for oneInfo in BALL]
	dx=200
	dy=5000
	left =min(VBOXx)
	right =max(VBOXx)
	nx= int(ceil((right - left)/dx))
	ycol=np.zeros((2,nx))
	for i in range(len(VBOXx)):
		index = int(ceil((VBOXx[i]-left)/dx))
		if(index>0):
			index=index-1
		if(VBOXy[i] > ycol[0,index]):
			ycol[0,index] = VBOXy[i]+VBOXr[i]
			ycol[1,index] = i
	wp1x=np.zeros(nx)
	wp1y=np.zeros(nx)
	for i in range(nx):
		wp1x[i]=dx*i+left
		if i>0 and i<(nx-1):
			if abs(ycol[0,i] - ycol[0,i-1]) <dy and abs(ycol[0,i+1] - ycol[0,i])<dy:
				wp1y[i]=ycol[0,i]*0.5+ycol[0,i-1]*0.25+ycol[0,i+1]*0.25
			else:
				wp1y[i]=ycol[0,i]
		else:
			wp1y[i]=ycol[0,i]
	ax.add_line(Line2D(wp1x, wp1y , linewidth=linewidth, color='black')) 


def fig_set(fig):
	"""
	输入参数：
	[1] fig  
	"""

	#plt.plot(VBOXx,VBOXy,'.')
	plt.xlim(left=0.0)#, xmax = 0.16)
	#plt.xlim(right = 120)
	plt.ylim(bottom=0.0)
	plt.axis('equal')   #changes limits of x or y axis so that equal increments of x and y have the same length

	#plt.ylim(top =20)
	#plt.show()
	wi,hi=fig.get_size_inches()
	#print("wi", wi, "hi",hi)
	wcm=8 #cm
	#hcm=
	winch=wcm/2.54
	hinch=winch/wi*hi
	#print("winch", winch, "hinch",hinch)
	fig.set_size_inches(w=winch,h=hinch)




