################################################################################
#
# paddling.py - Rev. 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Gui for sending practice (i.e. fun with paddles)
#
################################################################################
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
################################################################################

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
from nano_io import *
from fileio import read_text_file
from utilities import cut_numbers
from pprint import pprint

################################################################################

TEST_MODE=True
TEST_MODE=False
RANDOM_QSO_MODE=True

################################################################################

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
        self.bookmark=0
        self.last_focus=None
        self.WIN_NAME='PADDLING WINDOW'
        self.OnTop=False
        self.responded=True       # Need to show initial text
        self.item=''
        self.response=''
        self.STRICT_MODE=False
        self.CASUAL_MODE=False

        self.suffixes=['/M','/P','/QRP','/MM']
        for i in range(10):
            self.suffixes.append('/'+str(i))

        # Open main or pop-up window depending on if "root" is given
        if root:
            self.win=Toplevel(root)
        else:
            self.win = Tk()
        self.win.title("Sending Practice by AA2IL")
        self.win.geometry('1700x220+100+10')
        self.root=self.win

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
        self.QSO_Template = read_text_file('QSO_Template.txt',KEEP_BLANKS=False)
        # KEEP_BLANKS=not RANDOM_QSO_MODE)
        #print('QSO_Template=',self.QSO_Template )
        
        # Read words we stumble with
        self.Stumble = read_text_file('Stumble.txt',KEEP_BLANKS=False)

        # Read Book
        self.Book = read_text_file('Book.txt',KEEP_BLANKS=False)

        # Form list of calls - just use what we loaded from the master list
        self.calls = P.calls
        self.Ncalls = len(self.calls)
            
        # Put up a box for the practice text - use large font
        # Make this the default object to take the focus & bind keys to effect special mappings
        row=0
        lab = Label(self.win, text="",font=font1)
        lab.grid(row=row,rowspan=1,column=0,columnspan=12,sticky=E+W)
        self.txt = Text(self.win, height=2, width=60, bg='white', font=font2)
        self.txt.grid(row=row+1,rowspan=2,column=0,columnspan=12,sticky=E+W)
        self.default_object=self.txt
        self.txt.bind("<Key>", self.KeyPress )

        # Radio button group to select type of practice
        row+=3
        self.Selection = IntVar(value=0)
        col=0
        for itype in ['Panagrams','Call Signs','Letters','Letters+Numbers',\
                      'Special Chars', 'All Chars','Stumble','QSO','Book',\
                      'Sprint']:
            button = Radiobutton(self.win, text=itype,
                                 variable=self.Selection,
                                 value=col,command=self.NewItem)
            button.grid(row=row,column=col,sticky=E+W)
            col+=1

        # Spin box to control paddle keying speed (WPM)
        row+=1
        col=0
        self.WPM_TXT = StringVar()
        Label(self.win, text='Paddles:').grid(row=row,column=col,sticky=E+W)
        SB=Spinbox(self.win,              
                   from_=15, to=50,       
                   textvariable=self.WPM_TXT, 
                   bg='white',                
                   command=lambda j=0: self.SetWpm(0))
        SB.grid(row=row,column=col+1,columnspan=1,sticky=E+W)
        SB.bind("<Key>", self.KeyPress )
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

        # Buttons for Previous ...
        row+=1
        col=0
        Button(self.win, text="Previous",command=self.PrevItem) \
            .grid(row=row,column=col,sticky=E+W)

        # ... and Next practice text ...
        col+=1
        Button(self.win, text="Next",command=self.NextItem) \
            .grid(row=row,column=col,sticky=E+W)

        # ... to toggle STRICT Mode ...
        col+=1
        self.StrictBtn=Button(self.win, text="Strict",command=self.toggle_strict)
        self.StrictBtn.grid(row=row,column=col,sticky=E+W)

        # ... to toggle CASUAL Mode ...
        col+=1
        self.CasualBtn=Button(self.win, text="Casual",command=self.toggle_casual)
        self.CasualBtn.grid(row=row,column=col,sticky=E+W)

        # ... and to Quit
        col+=1
        Button(self.win, text="Quit",command=self.hide) \
            .grid(row=row,column=col,sticky=E+W)

        # Make sure all columns are adjusted when we resize the width of the window
        for i in range(12):
            Grid.columnconfigure(self.win, i, weight=1,uniform='twelve')
        
        # Bind callbacks for whenever a key is pressed or the mouse enters or leaves the window
        self.win.bind("<Key>", self.KeyPress )
        self.win.bind("<Enter>", self.P.gui.Hoover )
        self.win.bind("<Leave>", self.P.gui.Leave )
        self.win.bind('<Button-1>', self.P.gui.Root_Mouse )      

        # Not sure what this does?
        self.win.protocol("WM_DELETE_WINDOW", self.hide)

        # Start the ball rolling with this window not visible
        try:
            self.SetWpm(0)
        except:
            pass
        self.hide()

################################################################################

    # Callback for monitor level setter
    def SetMonitorLevel(self,level=None):
        print('\nSet Monitor Level ...',level)
        if level==None:
            level=self.P.sock.get_monitor_gain()
            print(("LEVEL: %d" % level))
            self.Slider2.set(level)
        self.P.sock.set_monitor_gain(level)
        if True:
            level=self.P.sock.get_monitor_gain()
            print(("LEVEL: %d" % level))
        

    # Callback for WPM spinner
    def SetWpm(self,dWPM=0):
        WPM=int( self.WPM_TXT.get() ) + dWPM
        if WPM>5:
            if self.P.LOCK_SPEED:
                print('Paddling->SetWpm: LOCKED - Setting speed to WPM=',
                      WPM,'...')
                self.P.keyer.set_wpm(WPM)
                self.P.sock.set_speed(WPM)
                #self.P.gui.WPM_TXT.set(str(WPM))
                #self.P.gui.set_wpm()
            else:
                print('Paddling->SetWpm: NANO - Setting speed to WPM=',
                      WPM,'...')
                self.P.keyer_device.set_wpm(WPM,idev=2)
            self.WPM_TXT.set(str(WPM))

        # Get a new panagram, call, etc.
        #print('HEY 1', self.responded)
        if self.responded:
            Selection=self.Selection.get()
            if Selection!=7 or RANDOM_QSO_MODE:
                self.NewItem()
        #print('HEY 2', self.responded)
        
    # Callback when a key is pressed 
    def KeyPress(self,event,id=None):

        key   = event.keysym
        print('Paddling->Key Press:',key)

        if key in ['Return','KP_Enter','space']:
            
            self.NewItem()
            return "break"
        
        elif key in ['Prior','KP_Add']:
            
            # Page up or big +
            self.SetWpm(+1)
            return "break"
        
        elif key in ['Next','KP_Subtract']:
            
            # Page down or big -
            self.SetWpm(-1)
            return "break"
           
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
        #print("You selected",Selection)
        self.responded=False
        #print('HEY 3', self.responded)

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
            txt=''
            for j in range(5):
                i = random.randint(0, self.Ncalls-1)
                txt += ' '+self.calls[i]

                # Add a "/" once in a while more practice
                if '/' not in txt:
                    i = random.randint(0,10)
                    if i>6:
                        i = random.randint(0,len(self.suffixes)-1)
                        txt+=self.suffixes[i]                        
                
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
            for k in range(5):
                for j in range(5):
                    i = random.randint(0, len(items)-1)
                    txt += items[i]
                txt += ' '
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
            
        elif Selection==8:
            
            txt = self.Book[self.bookmark]
            self.bookmark= (self.bookmark+1) % len(self.Book)
            
        elif Selection==9:
            
            call1,name1,state1 = self.get_sprint_call()
            call2,name2,state2 = self.get_sprint_call()
            serial = str( random.randint(0,999) )
            i = random.randint(0,1)
            if i==0:
                txt=call1+' '+call2+' '+name2+' '+state2+' '+serial
            else:
                txt=call1+' '+name2+' '+state2+' '+serial+' '+call2
            
        else:
            print('Unknown selection')
            txt='*** ERROR *** ERROR *** ERROR ***'
            
        self.txt.delete(1.0, END)
        txt=txt.strip()
        self.txt.insert(1.0,txt)
        self.stack.append(txt)
        if len(self.stack)>100:
            self.stack.pop(0)
        self.stack_ptr=len(self.stack)-1

        self.response=''
        self.item=txt.upper()
        
        if self.P.NANO_ECHO:
            self.P.keyer.txt2morse(txt)

    # Routine to sift through call history and find a good complete sprint entry
    def get_sprint_call(self):
        
        call=None
        while not call:
            i = random.randint(0, self.Ncalls-1)
            c = self.calls[i]
            print(i,c)
            print(self.P.MASTER[c])
            name  = self.P.MASTER[c]['name'].replace('.','')
            state = self.P.MASTER[c]['state']
            print(name,state)
            if len(name)>1 and len(state)>=2:
                call=c

        return call,name,state
            
            
    # Routine to show the main window
    def show(self):
        
        print('Show Paddling Window ...')
        self.P.NANO_ECHO = True
        self.win.update()
        self.win.deiconify()
        self.win.focus_set()      
        self.win.focus_force()      
        self.txt.focus_set()      
        self.txt.focus_force()      
        
    # Routine to hide the main window
    def hide(self):
        print('Hide Settings Window ...')
        self.win.withdraw()

################################################################################

    # Callback to toggle STRICT_MODE
    def toggle_strict(self):
        self.STRICT_MODE = not self.STRICT_MODE
        if self.STRICT_MODE:
            self.StrictBtn.configure(relief='sunken')
            if self.CASUAL_MODE:
                self.toggle_casual()
        else:
            self.StrictBtn.configure(relief='raised')
        
    # Callback to toggle CASUAL_MODE
    def toggle_casual(self):
        self.CASUAL_MODE = not self.CASUAL_MODE
        if self.CASUAL_MODE:
            self.CasualBtn.configure(relief='sunken')
            if self.STRICT_MODE:
                self.toggle_strict()
        else:
            self.CasualBtn.configure(relief='raised')
        
    # Routine to check response
    def check_response(self,txt):
        self.response+=txt.replace('\n',' ')
        if self.CASUAL_MODE:
            txt1=self.item.replace(' ','')
            txt2=self.response.replace(' ','')
        else:
            txt1=self.item
            txt2=self.response
            
        n1=len(txt1)
        print('\nitem:    ',txt1,n1)

        n2=len(txt2)
        print('response:',txt2,n2)

        if n2>=n1:
            txt3=txt2[-n1:]
            print('txt3    :',txt3,len(txt3))
            if txt3==txt1:
                print('!!! DING DING DING !!!')
                if self.STRICT_MODE or self.CASUAL_MODE:
                    self.NewItem()
