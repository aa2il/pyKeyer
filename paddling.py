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
from fileio import read_text_file
from utilities import cut_numbers

#########################################################################################

TEST_MODE=True
TEST_MODE=False
RANDOM_QSO_MODE=False

#########################################################################################

# GUI for paddle (sending) practice
class PADDLING_GUI():
    def __init__(self,root,P):
        self.P = P

        # Inits
        self.letters=[]
        for i in range(26):
            self.letters.append( chr(i+ord('A')) )
        self.numbers=[]
        for i in range(10):
            self.numbers.append(chr(i+ord('0')))
        self.specials=['/',',','.','?','<AR>','<KN>','<BT>']
        self.stack=[]
        self.stack_ptr=-1
        self.qso_ptr=-1

        # Open main or pop-up window depending on if "root" is given
        if root:
            self.win=Toplevel(root)
        else:
            self.win = Tk()
        self.win.title("Sending Practice by AA2IL")
        self.win.geometry('1500x220+100+10')

        # Load fonts we want to use
        if sys.version_info[0]==3:
            font1 = tkinter.font.Font(family="monospace",size=12,weight="bold")
            font2 = tkinter.font.Font(family="monospace",size=28,weight="bold")
        else:
            font1 = tkFont.Font(family="monospace",size=12,weight="bold")
            font2 = tkFont.Font(family="monospace",size=28,weight="bold")

        # Read list of Panagrams
        self.panagrams = read_text_file('Panagrams.txt')
        
        # Read qso template
        self.QSO_Template = read_text_file('QSO_Template.txt',
                                           KEEP_BLANKS=not RANDOM_QSO_MODE)
        #print('QSO_Template=',self.QSO_Template )
        
        # Read words we stumble with
        self.Stumble = read_text_file('Stumble.txt')
        
        # Form list of calls - just use what we loaded from the master list
        self.calls = P.calls
        self.Ncalls = len(self.calls)
            
        # Put up a box for the practice text - use large font
        row=0
        lab = Label(self.win, text="",font=font1)
        lab.grid(row=row,rowspan=1,column=0,columnspan=12,sticky=E+W)
        #self.txt = Entry(self.win,font=font2)
        self.txt = Text(self.win, height=2, width=60, bg='white', font=font2)
        self.txt.grid(row=row+1,rowspan=2,column=0,columnspan=12,sticky=E+W)

        # Radio button group to select type of practice
        row+=3
        self.Selection = IntVar(value=0)
        col=0
        for itype in ['Panagrams','Call Signs','Letters','Letters+Numbers','Special Chars', \
                      'All Chars','Stumble','QSO']:
            button = Radiobutton(self.win, text=itype,
                                 variable=self.Selection,
                                 value=col,command=self.NewItem)
            button.grid(row=row,column=col,sticky=E+W)
            col+=1

        # Spin box to control keying speed (WPM)
        row+=1
        col=0
        self.WPM_TXT = StringVar()
        Label(self.win, text='Speed:').grid(row=row,column=col,sticky=E+W)
        SB=Spinbox(self.win,              
                   from_=15, to=50,       
                   textvariable=self.WPM_TXT, 
                   bg='white',                
                   command=lambda j=0: self.SetWpm(0))
        SB.grid(row=row,column=col+1,columnspan=1,sticky=E+W)
        if self.P.LOCK_SPEED:
            self.WPM_TXT.set(self.P.WPM)
        else:
            self.WPM_TXT.set('20')

        # Slider to control rig monitor level (i.e. sidetone volume)
        col+=2
        Label(self.win, text='Monitor:').grid(row=row,column=col,sticky=E+W)
        self.Slider2 = Scale(self.win,
                       from_=0, to=100,
                       orient=HORIZONTAL,
                       length=300,       
                       command=self.SetMonitorLevel )
        #label="Monitor Level",       
        self.Slider2.grid(row=row,column=col+1,columnspan=4,sticky=E+W)
        self.SetMonitorLevel()
        
        row+=1
        col=0
        Button(self.win, text="Previous",command=self.PrevItem) \
            .grid(row=row,column=col,sticky=E+W)

        col+=1
        Button(self.win, text="Next",command=self.NextItem) \
            .grid(row=row,column=col,sticky=E+W)
        
        col+=1
        Button(self.win, text="Quit",command=self.hide) \
            .grid(row=row,column=col,sticky=E+W)

        # Make sure all columns are adjusted when we resize the width of the window
        for i in range(12):
            Grid.columnconfigure(self.win, i, weight=1,uniform='twelve')
        
        # Bind a callback to be called whenever a key is pressed
        self.win.bind("<Key>", self.KeyPress )
        #self.win.bind("all", self.KeyPress )
        
        self.win.protocol("WM_DELETE_WINDOW", self.hide)

        # Start the ball rolling
        try:
            self.SetWpm(0)
        except:
            pass
            
        self.hide()

    # Callback for monitor level setter
    def SetMonitorLevel(self,level=None):
        print('\nSet Monitor Level ...',level)
        if level==None:
            level=self.P.sock.get_monitor_gain()
            print(("LEVEL: %d" % level))
            self.Slider2.set(level)
        self.P.sock.set_monitor_gain(level)
        

    # Callback for WPM spinner
    def SetWpm(self,dWPM=0):
        WPM=int( self.WPM_TXT.get() ) + dWPM
        print('Paddling-SetWpm: WPM=',WPM)
        if WPM>5:
            if self.P.LOCK_SPEED:
                self.P.keyer.set_wpm(WPM)
                self.P.sock.set_speed(WPM)
                #self.P.gui.WPM_TXT.set(str(WPM))
                #self.P.gui.set_wpm()
            else:
                nano_set_wpm(self.P.ser,WPM,idev=2)
            self.WPM_TXT.set(str(WPM))

        # Get a new panagram, call, etc.
        Selection=self.Selection.get()
        if Selection!=7 or RANDOM_QSO_MODE:
            self.NewItem()
        
    # Callback when a key is pressed 
    def KeyPress(self,event,id=None):

        key   = event.keysym
        print('Key Press:',key)

        if key in ['Return','KP_Enter','space']:
           self.NewItem()
        elif key in ['plus','KP_Add']:
            self.SetWpm(+1)
        elif key in ['minus','KP_Subtract']:
            self.SetWpm(-1)
           
    # Callback to push a prior item into entry box
    def PrevItem(self):
        if TEST_MODE:
            print('stack=',self.stack)
            print('stack_ptr=',self.stack_ptr)
        if self.stack_ptr>0:
            self.stack_ptr-=1
            txt=self.stack[self.stack_ptr]
            self.txt.delete(1.0, END)
            self.txt.insert(1.0,txt)
        else:
            print('Empty stack')
            
    # Callback to push next or new item into entry box
    def NextItem(self):
        if TEST_MODE:
            print('stack=',self.stack)
            print('stack_ptr=',self.stack_ptr)
        if self.stack_ptr<len(self.stack)-1:
            self.stack_ptr+=1
            txt=self.stack[self.stack_ptr]
            self.txt.delete(1.0, END)
            self.txt.insert(1.0,txt)
        else:
            print('End of stack --> new item')
            self.NewItem()
            
    # Callback to push a new item into entry box
    def NewItem(self):
        P=self.P
        Selection=self.Selection.get()
        print("You selected",Selection)

        if Selection==0:
            # Panagrams
            n=len(self.panagrams)
            #print('There are',n,'panagrams loaded')
            i = random.randint(0,n-1)
            if len(self.stack)==0 and False:
                i=132                        # The quick brown fox ...
            txt = self.panagrams[i]
            if TEST_MODE:
                txt=str(i)+'. '+txt
            #print('Panagram=',txt)

        elif Selection==1:
            # Call signs
            #print('There are',self.Ncalls,'call signs loaded')
            i = random.randint(0, self.Ncalls-1)
            txt = self.calls[i]
            #print('call=',txt)
            
        elif Selection>=2 and Selection<=5:
            # Letter/number/char groups
            if Selection==2:
                items=self.letters
            elif Selection==3:
                items=self.letters+self.numbers
            elif Selection==4:
                items=self.specials
            elif Selection==5:
                items=self.letters+self.numbers+self.specials

            txt=''
            for j in range(5):
                i = random.randint(0, len(items)-1)
                txt += items[i]
            #print('letters=',txt)
            
        elif Selection==6:
            # Words I stumble on
            n=len(self.Stumble)
            #print('There are',n,'stumble-bumblers loaded')
            i = random.randint(0,n-1)
            txt = self.Stumble[i]
            #print('Stumble=',txt)
            
        elif Selection==7:
            # Normal QSO
            if RANDOM_QSO_MODE:
                # Pick a call at random
                done = False
                while not done:
                    i = random.randint(0, self.Ncalls-1)
                    call = self.calls[i]
                    name = P.MASTER[call]['name']
                    done = len(call)>2 and len(name)>2

                P.gui.call.delete(0,END)
                P.gui.call.insert(0,call)

                P.gui.name.delete(0,END)
                P.gui.name.insert(0,name)

            # Pick RST at random
            i = random.randint(2, 10)
            if i==10:
                rst='5NN Plus'
            else:
                #rst='5'+str(i)+'9'
                #print('rst1=',rst)
                rst=cut_numbers('5'+str(i)+'9',3,True)
                #print('rst2=',rst)
            P.gui.rstout.delete(0,END)
            P.gui.rstout.insert(0,rst)

            # Select one of the template lines
            n=len(self.QSO_Template)
            if False:
                i = random.randint(0,n-1)
            else:
                self.qso_ptr+=1
                if self.qso_ptr>n-1:
                    self.qso_ptr=0
                i=self.qso_ptr
            txt = self.QSO_Template[i]
            #print('QSO=',txt)
            txt = self.P.gui.Patch_Macro(txt)
            txt = self.P.gui.Patch_Macro2(txt)
            #print('QSO=',txt)
            
        else:
            print('Unknown selection')
            txt='*** ERROR *** ERROR *** ERROR ***'
            
        self.txt.delete(1.0, END)
        txt=txt.strip()
        self.txt.insert(1.0,txt)
        #self.stack.insert(0,txt)
        self.stack.append(txt)
        if len(self.stack)>100:
            self.stack.pop(0)
        self.stack_ptr=len(self.stack)-1
        
    def show(self):
        print('Show Settings Window ...')
        self.win.update()
        self.win.deiconify()
        self.win.focus_set()      
        self.win.focus_force()      
        self.txt.focus_set()      
        self.txt.focus_force()      
        
    def hide(self):
        print('Hide Settings Window ...')
        self.win.withdraw()
