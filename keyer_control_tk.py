############################################################################################
#
# Rig Control GUI - Tk version - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Portion of GUI related to keyer controls - Tk version
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
    import tkinter.messagebox
else:
    from Tkinter import *
    import ttk
from functools import partial
from os import system
from utilities import list_all_serial_devices,error_trap
from pprint import pprint

################################################################################

class KEYER_CONTROL():
    def __init__(self,P):
        self.P = P
        parent = P.root
        self.sock = P.sock

        # If there is not a keyer connected/detected, just issue a warning
        if P.keyer_device:
            self.winkey_mode = P.keyer_device.winkey_mode
            print('KEYER CONTROL INIT: Winkey mode=',hex(self.winkey_mode))
        else:
            self.winkey_mode = 0
            self.P.gui.splash.hide()
            list_all_serial_devices(True)
            msg="No keyer found!\n\nAll sending will be via keyboard"
            result=tkinter.messagebox.showwarning('Keyer Control',msg)
            self.P.gui.splash.show()
        
        self.win=Toplevel(parent)
        self.win.title("Keyer Control")
        self.tabs = ttk.Notebook(self.win)          # Create Tab Control
        self.win.withdraw()
        self.win.protocol("WM_DELETE_WINDOW", self.hide)

        # Add a tab for keyer control
        tab1 = ttk.Frame(self.tabs)              # Create a tab 
        self.tabs.add(tab1, text='Keyer Ctrl')   # Add the tab
        self.tabs.pack(expand=1, fill="both")    # Pack to make visible

        ######################################################################

        # Create a frame with buttons to select Iambic mode
        IambicFrame = Frame(tab1)
        IambicFrame.pack(side=TOP)
        
        self.status = StringVar(parent)
        Label(IambicFrame, textvariable=self.status ).pack(side=TOP)
        self.status.set( 'WinKeyer Mode='+hex(self.winkey_mode) )

        self.iambic = IntVar(parent)
        self.keyer_modes = {'Iambic A':1 , 'Iambic B':0 , 'Ultimatic':2,'Bug':3}
        for (txt,val) in self.keyer_modes.items():
            Radiobutton(IambicFrame, 
                        text=txt,
                        indicatoron = 0,
                        variable=self.iambic, 
                        command=lambda: self.SelectIambic(self),
                        value=val).pack(side=LEFT,anchor=W)
        self.SelectIambic(1)

        ######################################################################

        # Create a frame with buttons to support other misc functions
        MiscFrame = Frame(tab1)
        MiscFrame.pack(side=TOP)

        self.Buttons=[]
        self.Flags=[]
        self.keyer_flags={"Paddle Watchdog":0x80 , "Paddle Echo":0x40, "Paddle Swap":0x08, \
                          "Serial Echo":0x04, "Autospace":0x02, "Contest Spacing":0x01}
        i=0
        for (txt,mask) in self.keyer_flags.items():
            b = Button(MiscFrame, text=txt,
                       command=lambda j=i, m=mask: self.ToggleButton(0,j,m) )
            b.pack(side=LEFT,anchor=W)
            self.Buttons.append(b)
            self.Flags.append(None)
            self.ToggleButton(1,i,mask)
            i+=1

        # Ready to rock & roll
        self.hide()

        
    def show(self):
        print('Show Keyer Control Window ...')
        if self.P.keyer_device:
            self.win.update()
            self.win.deiconify()
        else:
            ports = list_all_serial_devices(True)
            ndev=0
            for port in ports:
                if 'USB' in str(port):
                    ndev+=1
                    print('\nport=',port,':')
                    pprint(vars(port))
                    txt=str(port)+' : '+port.description+'\n'
                    self.P.gui.txt.insert(END, txt)

            msg='No keyer found!\n\nThere were '+str(ndev)+' USB devices found\n'
            result=tkinter.messagebox.showwarning('Keyer Control',msg)
            self.P.gui.txt.insert(END, msg)
        
    def hide(self):
        print('Hide Keyer Control Window ...')
        self.win.withdraw()
        
    ############################################################################################

    def CloseWindow(self):
        print('Close window')
        self.P.gui.KeyerCtrlCB()

    def SelectIambic(self,iopt=None):
        print('\nSELECT IAMBIC: opt=',iopt,'\twk mode=',hex(self.winkey_mode))
        if iopt==1:
            if self.P.keyer_device.protocol=='WINKEYER':
                m = (self.winkey_mode & 0x30) >> 4
                print('\tm=',hex(m))
            elif self.P.keyer_device.protocol=='NANO_IO':
                m = ord('A')
            self.iambic.set( m )
        else:
            m = self.iambic.get()
            print('\tm=',m)
            if self.P.keyer_device.protocol=='WINKEYER':
                self.winkey_mode = (self.winkey_mode & ~0x30) | (m<<4)
            
        print('\twinkey mode=',hex(self.winkey_mode))
        if self.P.keyer_device:
            if self.P.keyer_device.protocol=='WINKEYER':
                self.P.keyer_device.send_command(chr(0x0E)+chr(self.winkey_mode))       
                self.status.set( 'WinKeyer Mode='+hex(self.winkey_mode) )
            elif self.P.keyer_device.protocol=='NANO_IO':
                self.P.keyer_device.send_command('~'+chr(m))
                self.status.set( 'Nano IO Mode='+chr(m) )

    def ToggleButton(self,iopt,i,mask):
        #print('\nTOGGLE BUTTON: opt=',iopt,'\ti=',i,'\tmask=',mask)
        if iopt==1:
            if self.P.keyer_device.protocol=='WINKEYER':
                m = self.winkey_mode & mask
                #print('\tm=',hex(m))
                self.Flags[i] = m>0
        else:
            if self.P.keyer_device.protocol=='WINKEYER':
                self.Flags[i]  = not self.Flags[i]
                if self.Flags[i]:
                    self.winkey_mode = self.winkey_mode | mask
                else:
                    self.winkey_mode = self.winkey_mode & ~mask
                
        #print('\t',self.Flags[i],'\twk mode=',hex(self.winkey_mode))
        if self.P.keyer_device:
            if self.P.keyer_device.protocol=='WINKEYER':
                self.P.keyer_device.send_command(chr(0x0E)+chr(self.winkey_mode))       
                self.status.set( 'WinKeyer Mode='+hex(self.winkey_mode) )

        if not self.Flags[i]:
            self.Buttons[i].configure(relief='raised')
        else:
            self.Buttons[i].configure(relief='sunken')
                
