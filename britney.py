#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Britney, fractales iterativos
# Copyright (C) 2012 Santiago Laplagne
# Version 0.3.3 2012/08/18

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from io import StringIO
import math
import os
import pickle
import numpy as np
#from numpy import matrix
#from numpy import linalg

import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog
#from tkinter import *
#import tkMessageBox
#import tkColorChooser 
#import tkFileDialog
#from Tkinter import *

from PIL import Image   # You need to install pillow

master = tk.Tk()
master.title("Britney")

# Colors
global noConfig
noConfig = 0;
white = (255, 255, 255)
black = (0,0,0)
red = (255,0,0)
orange = (221, 104, 11)
yellow = (252, 229, 3)
green = (0,255,0)
blue = (0,0,255)
indigo = (180, 0, 255)
violet = (174, 9, 100)
b2 = (0,255, 255)
b3 = (240,190,35)
b4 = (255, 0, 255)
global colors
global bgcolor
global back
global lineWidth
global wi, he
colorSeg = "blue"

# Initial settings
lineDrawn = 0
lineItem = 0
shape = 0   
origin = 1
lvl = 0
maxLev = 7
segs = list()  # All the fractal segments
factors = list()
segs01 = list()   # Only level 0 and 1 segments
segs01.append(list())
segs01.append(list())
i = 0
lineWidth = 3

def displayHelp():
   helpT  = '0-9 \t Cambiar color del nivel \r'
   helpT += ' b  \t Cambiar color de fondo \r'
   helpT += ' o  \t Cambiar forma \r'		
   helpT += ' +  \t Agregar nivel \r'
   helpT += ' -  \t Eliminar nivel \r'
   helpT += '<-- \t Borrar ultimo punto \r'
   helpT += ' l  \t Cargar fractal \r'
   helpT += ' s  \t Guardar fractal \r'
   helpT += ' e  \t Exportar imagen \r'
   helpT += ' c  \t Borrar toda la pantalla \r'
   helpT += ' x  \t Salir \r'
   tkMessageBox.showinfo("Ayuda", helpT)

def htmlColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor
    
# Redraws the fractal in the screen
def redrawFractal(screen, segs, origin, backColor, colors, maxLev, shape):
   global back
   global factors
   screen.delete(tk.ALL)
   screen.configure(background=bgcolor)
   #back = screen.create_rectangle((0, 0, wi, he), fill = bgcolor)
   for l in range(0, maxLev + 1):
      if(len(segs) > l):
         for j in range(0, len(segs[l])):
            if(segs[l][j][2] > 0):
               drawCompo(screen, colors[l], segs[l][j], shape, 0.8**l)
               #drawCompo(screen, colors[l], segs[l][j], shape, factors[l][j][0])
            if l <= 1:
               drawcircle(screen, segs[l][j][0], segs[l][j][1], 1, colors[l])
               if(origin == 1) or (j < (len(segs[l]) - 1)) or (l < len(segs[l])):
                  drawcircle(screen, segs[l][j][2], segs[l][j][3], 1, colors[l])
                  
# Draw one minimal component of the fractal, acording to the selected shape.
def drawCompo(screen, color, segment, shape, widthFactor):
   x1, y1, x2, y2 = segment
   if shape >= 1:
      center = [int((x2+x1)/2), int((y2+y1)/2)]
      radius = int((math.hypot(x2-x1, y2-y1))/2)
      if shape == 1:
         drawcircle(screen, center[0], center[1], radius, color)
      if shape == 2:
         drawcircleempty(screen, center[0], center[1], radius, color)         
   else:
      screen.create_line(x1, y1, x2, y2, fill = color, width = int(lineWidth * widthFactor), capstyle = "round")
    
# Compute all the segments of the fractal
def updateFractal(segs01, i, origin, maxLev):
   global segs
   global factors
   segs = list()
   factors = list()
   actualLev = maxLev
   while(i**actualLev > 5**7):
     actualLev = actualLev - 1
   if len(segs01[0]) > 0:
      segs.append(np.zeros([1,4], int))
      factors.append(np.zeros([1,1], int))
      segs[0][0][0:4] = segs01[0][0][0:4]
      factors[0][0][0] = 1
      if(len(segs01)>1):
         segs.append(np.zeros([len(segs01[1]), 4], int))
         factors.append(np.zeros([len(segs01[1]), 1], int))
#         for ii in range(0, len(segs01[1])):
#            segs[1][ii][0:4] = segs01[1][ii][0:4]
#            factors[1][ii][0] = 0.9
         segs[1][0:len(segs01[1])][0:4] = segs01[1][0:len(segs01[1])][0:4]
         factors[1][0:len(segs01[1])][0] = 0.9
         if(len(segs01[1])>1) or (origin == 1):         
            A = np.matrix( [[segs01[0][0][0], -segs01[0][0][1], 1, 0], [segs01[0][0][1], segs01[0][0][0], 0, 1], [segs01[0][0][2], -segs01[0][0][3], 1, 0], [segs01[0][0][3], segs01[0][0][2], 0, 1]])
            AI = A.I
            for l in range(2, actualLev):
               segs.append(np.zeros([i**(l), 4], int))
               factors.append(np.zeros([i**(l), 1], int))
               c = 0
               for j in range(0, i**(l-1)):            
                  y = np.matrix( [[segs[l-1][j][0]], [segs[l-1][j][1]], [segs[l-1][j][2]], [segs[l-1][j][3]]] )
                  xx = AI*y
                  B = np.matrix( [[xx[0,0], -xx[1,0]], [xx[1,0], xx[0,0]]] )
                  D1 = B * np.transpose(segs[1][0:len(segs01[1]), 0:2])
                  D2 = B * np.transpose(segs[1][0:len(segs01[1]), 2:4])
                  for z in range(0, i):
                     segs[l][c][0:4] = [int(D1[0,z] + xx[2, 0]), int(D1[1,z] + xx[3, 0]), int(D2[0,z] + xx[2,0]), int(D2[1,z] + xx[3, 0])]
                     factors[l][c][0] = (0.8)
                     c = c + 1
#   return(segs)   

def drawcircle(canv, x, y, rad, color):
    canv.create_oval(x-rad,y-rad,x+rad,y+rad,width=lineWidth, fill=color, outline = color)

def drawcircleempty(canv, x, y, rad, color):
    canv.create_oval(x-rad,y-rad,x+rad,y+rad,width=lineWidth, fill='', outline = color)

def changeStyle(s):
   global shape
   shape = s
   for ii in [0, 1, 2]:
      if (ii == s):
         styleButton[ii].config(relief = SUNKEN)
      else:
         styleButton[ii].config(relief = RAISED)
   redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)

def changeLineWidth(l):
   global lineWidth
   lineWidth = int(l)
   redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)

def changeMaxLev(l):
   global maxLev
   global segs
   global factors
   maxLev = int(l)
   #segs = updateFractal(segs01, i, origin, maxLev)
   updateFractal(segs01, i, origin, maxLev)
   redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)

def changeBackColor():
   global bgcolor
   ctuple,cstr = colorchooser.askcolor(initialcolor=bgcolor, title = 'Color de fondo')
   if ctuple != None:
      bgcolor = cstr
      backColorButton.configure(bg = bgcolor)
      screen.itemconfig(back, fill = bgcolor)
   redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)      

def changeLineColor(cLev):
   global colors
   ctuple,cstr = colorchooser.askcolor(initialcolor=colors[cLev], title = 'Color del nivel ' + str(cLev + 1))
   if(ctuple != None):
      colors[cLev] = cstr
   redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)


def clearScreen():
   global segs
   global factors
   global segs01   
   global origin
   global lvl
   global i
   origin = 1
   lvl = 0
   i = 0
   segs = list()
   factors = list()
   segs01 = list()
   segs01.append(list())
   segs01.append(list())
   screen.delete(tk.ALL)
   back = screen.create_rectangle((0, 0, wi, he), fill = bgcolor)

def saveFile():
   global lvl
   global segs01
#   print(segs01)
   files = [ ('Fractal Britney', '.art'), ("Todos los archivos",".*")]
   f = filedialog.asksaveasfile(mode = "wb", filetypes = files, defaultextension = files)
   
#   print("save file");
#   print("segs01 = ", segs01);
#   print("i = ", i);
#   print("origin = ", origin);
#   print("lvl = ", lvl);
        
   if(f):
      pickle.dump(segs01, f)
      pickle.dump(colors, f)
      pickle.dump(bgcolor, f)
      pickle.dump(i, f)
      pickle.dump(origin, f)
      pickle.dump(lvl, f)
      pickle.dump(maxLev, f)
      f.close

def exportImage():
   redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
   infile = filedialog.asksaveasfilename(filetypes = [ ('EPS files', '.eps'), ('JPG files', '.jpg'), ('PNG files', '.png'), ("All files",".*")])
   filename, ext = os.path.splitext(infile)
   if (ext == '.eps'):
      screen.postscript(file=filename)      
   if (ext == '.jpg'):  
      postFile = screen.postscript()
      im = Image.open(StringIO.StringIO(postFile))
      im.save(infile)            
   if (ext == '.jpg'):  
      postFile = screen.postscript()
      im = Image.open(StringIO.StringIO(postFile))
      im.save(infile, 'JPEG', quality = 100, optimize = True)            
   if (ext == '.png'):  
      postFile = screen.postscript()
      im = Image.open(StringIO.StringIO(postFile))
      im.save(infile, 'PNG')            
   
def loadFile():
   global segs01
   global colors
   global bgcolor
   global i
   global origin
   global lvl
   global maxLev
   
   f = filedialog.askopenfile(mode = "rb", filetypes = [ ('Fractal Britney', '.art'), ("Todos los archivos",".*")])
   if(f):
      segs01 = pickle.load(f)
      colors = pickle.load(f)
      bgcolor = pickle.load(f)
      i = pickle.load(f)
      origin = pickle.load(f)
      lvl = pickle.load(f)
#      print("load file");
#      print("segs01 = ", segs01);
#      print("i = ", i);
#      print("origin = ", origin);
#      print("lvl = ", lvl);
      maxLev = pickle.load(f)
      updateFractal(segs01, i, origin, maxLev)
      redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)

# Shows a preview of the line you are creating
def mouseMove(event):
   global lineDrawn
   global lineItem
   
#   print("move");
#   print("lvl = ", lvl);
#   print("i = ", i);
#   print("segs01 = ", segs01);
   
   if origin == 0:
      x1, y1, x2, y2 = segs01[lvl][i][0], segs01[lvl][i][1], event.x, event.y 
      if shape >= 1:
         xCenter, yCenter = [int((x2+x1)/2), int((y2+y1)/2)]
         rad = int((math.hypot(x2-x1, y2-y1))/2)
         x1, y1, x2, y2 = xCenter-rad,yCenter-rad,xCenter+rad,yCenter+rad
      if lineDrawn == 0:
         if shape >= 1:
            lineItem = screen.create_oval(x1, y1, x2, y2, width=1, fill='', outline = colors[lvl])
         else: 
            lineItem = screen.create_line(x1, y1, x2, y2, fill = colors[lvl])
         lineDrawn = 1
      else:
         screen.coords(lineItem, x1, y1, x2, y2)
              
def callback(event):   # Mouse button pressed
   global segs
   global factors
   global segs01   
   global origin
   global lvl
   global i
   global lineDrawn
#   print("press");
#   print("lvl = ", lvl);
#   print("i = ", i);
#   print("segs01 = ", segs01);
   
   if (i<=4):
     if (origin == 1):
        origin = 0
        lineDrawn = 0
        segs01[lvl].append([0, 0, 0, 0])            
        segs01[lvl][i][0] = event.x
        segs01[lvl][i][1] = event.y
        drawcircle(screen, segs01[lvl][i][0], segs01[lvl][i][1], 1, colors[lvl])
     else:
        origin = 1
        segs01[lvl][i][2] = event.x
        segs01[lvl][i][3] = event.y
        drawcircle(screen, segs01[lvl][i][2], segs01[lvl][i][3], 1, colors[lvl])
        drawCompo(screen, colors[lvl], segs01[lvl][i], shape, lvl) 
        if lvl == 1:
           #print("i = i + 1")
           i = i + 1
           updateFractal(segs01, i, origin, maxLev)
           redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
        else:
           segs.append(np.zeros([1,4], int))
           factors.append(np.zeros([1,1], int))
           segs[0][0][0:4] = segs01[0][0][0:4]
           factors[0][0][0] = 1
           lvl = 1

def resize(event):
   wi, he = master.winfo_width(), master.winfo_height()
   screen.config(width=wi - 165, height=he-20)

def backKeyI():
   global colors, bgcolor
   global shape, maxLev, lvl 
   global segs, segs01
   global origin, i
   global lineWidth
   global lineDrawn
   
   
   if (len(segs01[0]) > 0):
      origin = 1 - origin
      if(origin == 0):
         if i > 0:
            i = i - 1
         elif lvl == 1:
            lvl = 0
         segs01[lvl][i][2:4] = [0, 0]
         updateFractal(segs01, i, origin, maxLev)
         redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
         lineDrawn = 0
      else:
         segs01[lvl].pop()
         updateFractal(segs01, i, origin, maxLev)
         redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)

def backKey(event):
   backKeyI()
   mouseMove(event)
      
def key(event):
   global colors, bgcolor
   global shape, maxLev, lvl 
   global segs, segs01
   global origin, i
   global lineWidth
   global lineDrawn

   if event.char == '>':
      if lineWidth < 20:
         lineWidth = lineWidth + 1
         widthScale.set(lineWidth)
         redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
   if event.char == '<':
      if lineWidth > 1:
         lineWidth = lineWidth - 1
         widthScale.set(lineWidth)
         redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
   if event.char == '+' and maxLev <= 9:
      maxLev = maxLev + 1
      maxLevScale.set(maxLev)
      updateFractal(segs01, i, origin, maxLev)
      redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
   if event.char == '-' and maxLev >= 3:
      maxLev = maxLev - 1
      maxLevScale.set(maxLev)
      updateFractal(segs01, i, origin, maxLev)
      redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
   if event.char == 'h':
      displayHelp()
   if event.char == 'e':
      exportImage()
   if event.char == 'x':
      master.destroy()
   if event.char == 'o':
      shape = (shape + 1) % 3
      redrawFractal(screen, segs, origin, bgcolor, colors, maxLev, shape)
   if event.char == 'b':
      changeBackColor()
   if event.char != '':
      if ord(event.char) >= 48 and ord(event.char) <= 57:
         cLev = (ord(event.char) - 48) % 10
         changeLineColor(cLev)
   if event.char == 'c':
      clearScreen()
   if event.char == 'l':
      loadFile()
   if event.char == 's':
      saveFile()
  
colors = [htmlColor(red), htmlColor(blue), htmlColor(yellow), htmlColor(green), htmlColor(orange), htmlColor(indigo), htmlColor(b2), htmlColor(violet), htmlColor(b3), htmlColor(b4)]
bgcolor = htmlColor(black)
      	  
wi = 640
he = 480
#master.configure(bg='white', width = wi, height = he)
master.configure(bg='white')
      	  
#wi, he = master.winfo_width(), master.winfo_height()

#screen = Canvas(master, width=wi - 165, height=he-20, background = "black")
screen = tk.Canvas(master, width=wi - 165, height=he-20, background = "black")
back = screen.create_rectangle((0, 0, wi-165, he-20), fill = bgcolor)

screen.grid(rowspan = 18)

filledCircle = tk.PhotoImage(file="img/filledCircle.gif")
emptyCircle = tk.PhotoImage(file="img/emptyCircle.gif")
line = tk.PhotoImage(file="img/line.gif")

styleButton = []
styleButton.append(tk.Button(master, image = line, command = lambda: changeStyle(0), relief = tk.SUNKEN))
styleButton.append(tk.Button(master, image = filledCircle, command = lambda: changeStyle(1)))
styleButton.append(tk.Button(master, image = emptyCircle, command = lambda: changeStyle(2)))
for ii in [0, 1, 2]:
   styleButton[ii].grid(row = 0, column = ii + 1, padx = 5, pady = 5)

widthScale = tk.Scale(master, from_=1, to=20, command = changeLineWidth, orient=tk.HORIZONTAL, length = 120, label = "Ancho de línea")
widthScale.set(lineWidth)
widthScale.grid(row = 1, column = 1, columnspan = 3, padx = 5, pady = 5, sticky = tk.W+tk.E)

maxLevScale = tk.Scale(master, from_=2, to=10, command = changeMaxLev, orient=tk.HORIZONTAL, label = "Niveles")
maxLevScale.set(maxLev)
maxLevScale.grid(row = 2, column = 1, columnspan = 3, padx = 5, pady = 5, sticky = tk.W+tk.E)

backColorButton = tk.Button(master, text = "Fondo", fg = htmlColor(white), bg = bgcolor, command = changeBackColor)
backColorButton.grid(row = 3, column = 1, columnspan = 3, padx = 5, pady = 5, sticky = tk.W+tk.E)

lineColorButton = []
for ii in range(0, 10):
   lineColorButton.append(tk.Button(master, bg = colors[ii], text = str(ii + 1), command = lambda ii = ii: changeLineColor(ii)))
   lineColorButton[ii].grid(row = 4 + (ii)//3, column = (ii % 3) + 1, columnspan = 1, padx = 5, pady = 1, sticky = tk.W+tk.E)   

clearPointButton = tk.Button(master, text = 'Borrar último punto', command = backKeyI)
clearPointButton.grid(row = 15, column = 1, columnspan = 3, padx = 5, pady = 5, sticky = tk.W+tk.E+tk.S)
   
clearButton = tk.Button(master, text = 'Borrar todo', command = clearScreen)
clearButton.grid(row = 16, column = 1, columnspan = 3, padx = 5, pady = 5, sticky = tk.W+tk.E)

exitButton = tk.Button(master, text = 'Salir', command = master.destroy)
exitButton.grid(row = 17, column = 1, columnspan = 3, padx = 5, pady = 5, sticky = tk.W+tk.E)
master.rowconfigure(15, weight = 5)

# create a toplevel menu
menubar = tk.Menu(master)

# create a pulldown menu, and add it to the menu bar
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Abrir", command=loadFile)
filemenu.add_command(label="Guardar", command=saveFile)
filemenu.add_command(label="Exportar", command=exportImage)
filemenu.add_separator()
filemenu.add_command(label="Salir", command=master.quit)
menubar.add_cascade(label="Archivos", menu=filemenu)

# create more pulldown menus
#editmenu = Menu(menubar, tearoff=0)
#editmenu.add_command(label="Cut", command=master.quit)
#editmenu.add_command(label="Copy", command=master.quit)
#editmenu.add_command(label="Paste", command=master.quit)
#menubar.add_cascade(label="Edit", menu=editmenu)

menubar.add_command(label="Ayuda", command=displayHelp)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Ayuda", command=displayHelp)
#menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
master.config(menu=menubar)

RWidth=master.winfo_screenwidth()*2/3
RHeight=master.winfo_screenheight()*2/3
master.geometry(("%dx%d")%(RWidth, RHeight))
#master.attributes('-zoomed', True)


screen.bind("<Button-1>", callback)
screen.bind("<Motion>", mouseMove)
master.bind("<BackSpace>", backKey)
master.bind("<Configure>", resize)
master.bind("<Tab>", backKey)
master.bind("<Delete>", backKey)
master.bind("<Key>", key)

#screen.pack()

tk.mainloop()


