#########################################################################################
#
# paddling.py - Rev. 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Gui for sending practice (i.e. fun with paddles)
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
#########################################################################################

import sys
import os
if sys.version_info[0]==3:
    from tkinter import *
    import tkinter.font
else:
    from Tkinter import *
    import tkFont
import time
import random
from nano_io import nano_set_wpm

#########################################################################################

class PADDLING_GUI():
    def __init__(self,root,P):
        self.P = P

        if root:
            self.win=Toplevel(root)
        else:
            self.win = Tk()
        self.win.title("Sending Practice")

        if sys.version_info[0]==3:
            font1 = tkinter.font.Font(family="monospace",size=12,weight="bold")
            font2 = tkinter.font.Font(family="monospace",size=28,weight="bold")
        else:
            font1 = tkFont.Font(family="monospace",size=12,weight="bold")
            font2 = tkFont.Font(family="monospace",size=28,weight="bold")
        
        row=0
        self.txt = Entry(self.win,font=font2)
        self.txt.grid(row=row,rowspan=2,column=0,columnspan=12,sticky=E+W)

        # Radio button group to select type of practice
        row+=2
        self.Selection = IntVar(value=1)
        col=0
        for itype in ['Panagrams','Call Signs']:
            button = Radiobutton(self.win, text=itype,
                                 variable=self.Selection,
                                 value=col,command=self.NewItem)
            col+=1
            button.grid(row=row,column=col+1,sticky=E+W)
            #tip = ToolTip(self.Radio1, ' Rig 1 ' )


        # Set up a spin box to control keying speed (WPM)
        row+=1
        self.WPM_TXT = StringVar()
        Label(self.win, text='Speed:').grid(row=row,column=col,sticky=E+W)
        SB=Spinbox(self.win,
                   from_=15, to=50,\
                   textvariable=self.WPM_TXT,\
                   command=lambda j=0: self.SetWpm(0))
        SB.grid(row=row,column=col+1,columnspan=1,sticky=E+W)
        self.WPM_TXT.set('20')
        self.SetWpm(0)

        row+=1
        self.NextButton = Button(self.win, text="Next",command=self.NewItem)
        self.NextButton.grid(row=row,column=0,sticky=E+W)
        #self.NextButton.focus_set()            # Grab focus
        
        button = Button(self.win, text="Quit",command=self.hide)
        button.grid(row=row,column=1,sticky=E+W)

        # Make sure all columns are adjusted when we resize the width of the window
        for i in range(12):
            Grid.columnconfigure(self.win, i, weight=1,uniform='twelve')
        
        # Bind a callback to be called whenever a key is pressed
        self.win.bind("<Key>", self.KeyPress )
        #self.win.bind("all", self.KeyPress )
        
        self.win.protocol("WM_DELETE_WINDOW", self.hide)

        # Read list of Panagrams
        with open('Panagrams.txt') as f:
            self.panagrams = f.readlines()
        self.Ngrams=len( self.panagrams )
        
        # Form list of calls - just use what we loaded from the master list
        self.calls = P.calls
        self.Ncalls = len(self.calls)

        # Start the ball rolling 
        self.NewItem()
        
        self.show()
        

    # Callback for WPM spinner
    def SetWpm(self,dWPM=0):
        WPM=int( self.WPM_TXT.get() ) + dWPM
        print('SetWpm: WPM=',WPM)
        if WPM>=15:
            nano_set_wpm(self.P.ser,WPM,idev=2)

        
        
    # Callback when a key is pressed 
    def KeyPress(self,event,id=None):

        key   = event.keysym
        #num   = event.keysym_num
        #ch    = event.char
        #state = event.state

        print('Key Press:',key)

        if key=='Return' or key=='KP_Enter' or key=='space':
           self.NewItem()
           
    # Callback to push a new item into entry box
    def NewItem(self):
        Selection=self.Selection.get()
        print("You selected",Selection)

        if Selection==0:
            print('There are',self.Ngrams,'panagrams loaded')
            i = random.randint(0, self.Ngrams-1)
            txt = self.panagrams[i]
            print('Panagram=',txt)

        else:
            print('There are',self.Ncalls,'call signs loaded')
            i = random.randint(0, self.Ncalls-1)
            txt = self.calls[i]
            print('call=',txt)

        self.txt.delete(0, END)
        self.txt.insert(0,txt.strip())
        
    def show(self):
        print('Show Settings Window ...')
        self.win.update()
        self.win.deiconify()
        
    def hide(self):
        print('Hide Settings Window ...')
        self.win.withdraw()
