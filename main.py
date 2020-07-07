#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2020/07/07 增加 --showsurface
2020/06/24 增加 --colormap
2020/05/24 增加 --wallshow
2019/08/26
李长圣 @ 东华理工大学
实现并行绘图，增加 --xmove= --ymove=

2019/01/07
李长圣 @ 南京大学

功能：
读取VBOX计算结果，生成jpg图片
plot ball to jpg

输入参数：
[1] DataDir  VBOX计算结果所在目录

输出：
[1] jpg格式文件

例如：
./main.py --dir=./example 
./main.py --dir=./example --xmax=40000 --ymax=10000 --xmove=-1000.0 --ymove=-1000.0 --xmin=0.0 --ymin=0.0 --major_locator=10000.0 --minor_locator=1000.0 --fontsize=12 --pagesize=14 --topshow=false --wallshow=true --colormap=./mycolormap.txt
"""

import concurrent.futures

import os, sys, getopt
import matplotlib.ticker as ticker
import vboxio
import vboxplot
import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
from pylab import *

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

def usage():
	#print("------do not give the dir of data , usage:----------")
	print("用法: vbox2jpg --dir=./data --dpi=300")
	print("	-------参数说明----------")
	print("	--dir   VBOX数据所在目录")
	print("	--xmax 绘图X最大值")
	print("	--ymax 绘图Y最大值")
	print("	--xmin 绘图X最小值，默认0.0")
	print("	--ymin 绘图Y最小值，默认0.0")
	print("	--xmove 坐标沿x轴偏移量，默认0.0")
	print("	--ymove 坐标沿y轴偏移量，默认0.0")
	print("	--major_locator 主坐标刻度间隔，默认10000")
	print("	--minor_locator 次坐标刻度间隔，默认1000")
	print("	--fontsize 坐标刻度字体大小，默认9")
	print("	--max_workers 并行进程数，默认24")
	print("	--dpi 图片分辨率，默认600")
	print("	--linewidth 线粗细，默认0.5")
	print("	--pagesize 图片大小，单位cm，默认14")	
	print("	--leftshow 显示坐标轴左线框，取值true/false，默认true")
	print("	--rightshow 显示坐标轴右边框，取值true/false，默认true")	
	print("	--bottomshow 显示坐标轴下线框，取值true/false，默认true")
	print("	--topshow 显示坐标轴上边框，取值true/false，默认true")
	print("	--wallshow 显示wall墙，取值true/false，默认true")
	print("	--showsurface 显示变形边界true/false，默认true")
	print("	--colormap 指定颜色配置文件，格式为10x3的矩阵，对应十个RGB值，默认取值见https://doc.geovbox.com/latest/color/．建议直接制定该文件的绝对路径或者相对路径，如--colormap=/home/zhangsan/MyColorMap.txt或--colormap=./ＭyColorMap.txt．如果仅指定文件名，如--colormap=ＭyColorMap.txt，搜索顺序为 当前目录 > --dir指定的目录 > Home．")

#print ('参数个数为:', len(sys.argv))
#print ('参数列表:', str(sys.argv))
if (len(sys.argv) < 2):
	usage()
	sys.exit()

opts, args = getopt.getopt(sys.argv[1:], "hi:o:",longopts=['dir=','xmax=','ymax=','xmove=','ymove=','xmin=','ymin=','major_locator=','minor_locator=','fontsize=','max_workers=','dpi=','linewidth=','pagesize=','leftshow=','rightshow=','bottomshow=','topshow=','wallshow=','colormap=','--showsurface='])
input_file=""
output_file=""
DataDir=""
xmax=1000000000.0
ymax=1000000000.0
xmove=0.0
ymove=0.0
xmin=0.0
ymin=0.0
major_locator=10000.0
minor_locator=1000.0
fontsize=9
max_workers=24
dpi=600
linewidth=0.5
pagesize=14
topshow='true'
rightshow='true'
bottomshow='true'
leftshow='true'
wallshow='true'
showsurface= 'true'
colormap='default'

for op, value in opts:
	if op == "-h":
		usage()
		sys.exit()
	elif op == "--dir":
		DataDir = value
		print ("DataDir", DataDir)
	elif op == "--xmax":
		xmax = float(value)
	elif op == "--ymax":
		ymax = float(value)
	elif op == "--xmove":
		xmove = float(value)
	elif op == "--ymove":
		ymove = float(value)
	elif op == "--xmin":
		xmin = float(value)
	elif op == "--ymin":
		ymin = float(value)
	elif op == "--major_locator":
		major_locator = float(value)
	elif op == "--minor_locator":
		minor_locator = float(value)
	elif op == "--fontsize":
		fontsize = float(value)
	elif op == "--max_workers":
		max_workers = int(value)
	elif op == "--dpi":
		dpi = int(value)
	elif op == "--linewidth":
		linewidth = float(value)
	elif op == "--pagesize":
		pagesize = float(value)
	elif op == "--topshow":
		topshow=value
	elif op == "--rightshow":
		rightshow=value
	elif op == "--bottomshow":
		bottomshow=value
	elif op == "--leftshow":
		leftshow=value
	elif op == "--wallshow":
		wallshow=value
	elif op == "--showsurface":
		showsurface=value
	elif op == "--colormap":
		colormap=value

VBOXscriptDir=sys.path[0]
sys.path.append(VBOXscriptDir)
#print "vboxscript",vboxscript
#print ("参数个数：",len(sys.argv))
if len(sys.argv) < 2:
	usage()
	os._exit(0)

import os.path #判断文件是否存在
colormapfile=''
if (colormap == 'default') :
	colormapfile=VBOXscriptDir+'/ColorRicebal.txt'
else:
	colormapfile=colormap
	#print("1:", colormapfile)
	if ( os.path.isfile(colormapfile) == False ):
		colormapfile=DataDir+colormap
		if ( os.path.isfile(colormapfile) == False ):
			colormapfile=os.path.join(os.environ['HOME'],colormap)
			if ( os.path.isfile(colormapfile) == False ):
				print("找不到", colormap)
print("colormap:", colormapfile)

flist = []
plt.close('all')
ColorList, ColorMap = vboxplot.get_color_map(colormapfile)
VBOXfile= vboxio.get_file_list(DataDir, FileNamePrefix='all_', FileNameSuffix='.dat')
for file in VBOXfile:
	print(xmove,ymove)
def gen_fig(file):
	print("read file:%s"%(file) )
	Wall,Ball=vboxio.read_data(file)
	vboxio.xy_move(Wall, Ball, xmove, ymove)

	fig=plt.figure(1)
#	ax = subplot(111,aspect='equal')
	ax=plt.gca()
	bleft,bright,bbottom,btop = vboxplot.plot_ball(fig,ax,Ball,ColorList)
	#print('wallshow',wallshow)
	wleft,wright,wbottom,wtop=bleft,bright,bbottom,btop
	if (wallshow == 'true'): 
		wleft,wright,wbottom,wtop = vboxplot.plot_wall(fig,ax,Wall,ColorList,linewidth=linewidth)
	if (showsurface == 'true'): 
		vboxplot.plot_surface(fig,ax,Ball,linewidth=linewidth)
	#print('222')
	left   = min(bleft  ,wleft)
	right  = max(bright ,wright)
	bottom = min(bbottom,wbottom)
	top    = max(btop   ,wtop)
	#figName='test'
	
	right=min(right,xmax)
	top  =min(top,ymax)
	
	left=max(left,xmin);
	bottom=max(bottom,ymin);	
	#print(left,right,bottom,top)

	realticks=range(0, 400000, int(major_locator) )
	showticks= [str(x) for x in range(0, 400, int(int(major_locator)/1000) )]
	plt.xticks(realticks,showticks)
	plt.yticks(realticks,showticks)
	ax.xaxis.set_minor_locator(ticker.MultipleLocator(minor_locator))
	ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_locator))
	# 设置刻度字体大小
	plt.xticks(fontsize=fontsize)
	plt.yticks(fontsize=fontsize)
	plt.tick_params(labelsize=fontsize)
	###设置坐标轴的粗细
	ax.spines['bottom'].set_linewidth(linewidth);###设置底部坐标轴的粗细
	ax.spines['left'].set_linewidth(linewidth);####设置左边坐标轴的粗细
	ax.spines['right'].set_linewidth(linewidth);###设置右边坐标轴的粗细
	ax.spines['top'].set_linewidth(linewidth);####设置上部坐标轴的粗细
	#set 刻度线粗细 刻度线与标签的间隔
	ax.tick_params(which='both',width=linewidth, pad=1);

	VBOXfileJPG = file.replace('.dat','.jpg')

	#wi,hi=fig.get_size_inches()
	wi=right-left
	hi=top-bottom
#	print("wi", wi, "hi",hi)
#	hi=3.0
	wcm=pagesize #cm
	#hcm=
	winch=wcm/2.54
	hinch=winch/wi*hi
#	hinch=1
	#print("winch", winch, "hinch",hinch)
	fig.set_size_inches(w=winch,h=hinch)

	#plt.axis('equal')   #changes limits of x or y axis so that equal increments of x and y have the same length
#	plt.plot(VBOXx,VBOXy,'.')
	#print(left,right,bottom,top)
	plt.xlim(left=left)#, xmax = 0.16)
	plt.xlim(right=right)
	plt.ylim(bottom=bottom)
	plt.ylim(top=top)
	#去掉边框
	#print("topshow:",topshow)
	if (topshow=='false'): ax.spines['top'].set_visible(False)
	if (rightshow=='false'): ax.spines['right'].set_visible(False)
	if (bottomshow=='false'): ax.spines['bottom'].set_visible(False)
	if (leftshow=='false'): ax.spines['left'].set_visible(False)

	fig.savefig(VBOXfileJPG,dpi=dpi, bbox_inches="tight")#, pad_inches=0.0)
	plt.close(fig)
#	fig.savefig(figName+'.pdf',dpi=300, bbox_inches="tight")

#开辟的进程数应小于文件数
max_workers=min(max_workers,len(VBOXfile))
print("parallel num:",max_workers)
print("file num:",len(VBOXfile))
#2019-08-26 实现并行绘图 max_workers=5
with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
	VBOXfileList= VBOXfile
	executor.map(gen_fig, VBOXfileList)
#for file in VBOXfile:

#	gen_fig(file)



