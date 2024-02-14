############################################################################################
#
# Rotor Control GUI - Tk version - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Portion of GUI related to rig controls - Tk version
#
# To Do:  This should be part of a library
#
############################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################################

import sys
if sys.version_info[0]==3:
    from tkinter import *
    import tkinter.ttk as ttk
else:
    from Tkinter import *
    import ttk
from rig_io.socket_io import *
from widgets_tk import *
try:
    from pyhamtools.locator import calculate_heading
    bearing_ok=True
except:
    bearing_ok=False

################################################################################

class ROTOR_CONTROL():
    def __init__(self,tabs,P):
        self.sock = P.sock_rotor
        self.MY_GRID = P.SETTINGS['MY_GRID']
        if self.sock.connection == 'NONE' and True:
            return None

        # Create a new tab 
        self.tab = ttk.Frame(tabs)                  # Create a tab 
        tabs.add(self.tab, text='Rotor')            # Add the tab
        tabs.pack(expand=1, fill="both")           # Pack to make visible
        self.visible = True

        # Add Az controls - top is desired, bottom is actual
        row=0
        col=0
        lb = Label(self.tab,text="Azimuth:")        #,font=font1)
        lb.grid(row=row,column=col) 
        self.direction = Entry(self.tab)
        self.direction.grid(row=row,column=col+1)  #,rowspan=1,columnspan=3)

        row+=1
        ndigits=3           # -180 to +180
        ndec=0
        self.azlcd1 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=None)
        self.azlcd1.label.grid(row=row,column=col)    # ,2,4)
  
        row+=2
        self.azlcd2 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=self.setRotorAz)
        self.azlcd2.label.grid(row=row,column=col)    #,2,4)

        # Add El controls - top is desired, bottom is actual
        row=0
        col=5
        lb2=Label(self.tab,text="Elevation:")
        lb2.grid(row=row,column=col)
        self.direction2 = Entry(self.tab)
        self.direction2.grid(row=row,column=col+1)    # ,1,3)

        row+=1
        self.ellcd1 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=None)
        self.ellcd1.label.grid(row=row,column=col)            #,2,4)

        row+=2
        self.ellcd2 = MyLCDNumber(self.tab,ndigits,ndec,True,True,wheelCB=self.setRotorEl)
        self.ellcd2.label.grid(row=row,column=col)         # ,2,4)
        
        # Initial positions
        pos=self.sock.get_position()
        print('pos=',pos)
        if pos[0] and pos[0]>180:
            pos[0]-=360
        if pos[0] and pos[0]<-180:
            pos[0]+=360
        self.azlcd1.set(pos[0])
        self.ellcd1.set(pos[1])
        self.azlcd2.set(pos[0])
        self.ellcd2.set(pos[1])

        # Add entry box for input of a grid square
        row+=2
        col=0
        lb3=Label(self.tab,text="Grid:")
        lb3.grid(row=row,column=col)
        self.grid_sq = Entry(self.tab)
        self.grid_sq.bind("<Return>",self.newGridSquare)
        #self.grid_sq.setToolTip('Point to a Grid')
        self.grid_sq.grid(row=row,column=col+1)            # ,1,3)
        
        # Add button to zero the rotor
        col=5
        self.btn = Button(self.tab,text='Rotor Home',command=self.rotorHome)
        #self.btn.setToolTip('Rotor to 0 az/el')
        self.btn.grid(row=row,column=col)                # ,1,4)
        
        
    # Function to update rotor az
    def setRotorAz(self,az):
        print('setRotorAz:',az)
        if False:
            if az>179.9:
                az=179.9
                self.azlcd2.set(az)
            elif az<-179.9:
                az=-179.9
                self.azlcd2.set(az)
        else:
            if az>180:
                az-=360
            elif az<-179.9:
                az+=360
            self.azlcd2.set(az)
            
        pos=self.sock.get_position()
        pos[0]=az
        self.sock.set_position(pos)

    # Function to update rotor el
    def setRotorEl(self,el):
        print('setRotorEl:',el)
        if el>179.9:
            el=179.9
            self.ellcd2.set(el)
        elif el<0:
            el=0
            self.ellcd2.set(el)
        pos=self.sock.get_position()
        pos[1]=el
        self.sock.set_position(pos)

    # Function to send rotor to 0 az and 0 el
    def rotorHome(self):
        pos=[0,0]
        self.sock.set_position(pos)
        self.azlcd2.set(pos[0])
        self.ellcd2.set(pos[1])

    # Function to point rotor toward a user specified grid square
    def newGridSquare(self,evt):
        txt=self.grid_sq.get()
        print('newGridSquare:',txt)
        if len(txt)==4 and bearing_ok:
            try:
                print('Computing bearing ...')
                bearing = calculate_heading(self.MY_GRID,txt)
                print('bearing=',bearing)
                self.azlcd2.set(bearing)
                self.setRotorAz(bearing)
            except Exception as e: 
                print('Problem computing bearing for',self.MY_GRID,txt)
                print( str(e) )

    # Function to give nominal direction info
    def nominalBearing(self):
        az=self.azlcd1.val
        if az<0:
            az+=360
        if az<15 or az>=345:
            txt='North - Idaho'
        elif az>=15 and az<30:
            txt='N-NE - Chicago'
        elif az>=30 and az<60:
            txt='NE - Minnesota'
        elif az>=60 and az<75:
            txt='E-NE - New York'
        elif az>=75 and az<105:
            txt='E - Georgia/Carribean'
        elif az>=105 and az<120:
            txt='E-SE - Central/South America'
        elif az>=120 and az<150:
            txt='SE - Central/South America'
        elif az>=150 and az<165:
            txt='S-SE - South America'
        elif az>=165 and az<195:
            txt='South - Antartica'
        elif az>=195 and az<210:
            txt='South - SouthWest'
        elif az>=210 and az<240:
            txt='SW - New Zealand'
        elif az>=240 and az<255:
            txt='W-SW - Australia'
        elif az>=255 and az<285:
            txt='West - Hawaii'
        elif az>=285 and az<300:
            txt='West - NorthWest'
        elif az>=300 and az<330:
            txt='NW - San Fransisco/Japan'
        elif az>=330 and az<345:
            txt='N-NW - Alaska/Washington'
        else:
            txt='???????????????????'
            
        #print('@@@@@@@@@@@@@222 Nominal Bearing:',az,txt)
        self.direction.delete(0,END)
        self.direction.insert(0,txt)
        
        el=self.ellcd1.val
        if el<30 or el>150:
            txt='Horizon'
        elif (el>=30 and el<60) or (el>=120 and el<150):
            txt='Well Above'
        elif el>=60 and el<120:
            txt='Up'

        self.direction2.delete(0,END)
        self.direction2.insert(0,txt)

