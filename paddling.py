#! /usr/bin/python3 -u
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
from utilities import cut_numbers,error_trap,show_hex,show_ascii
from pprint import pprint
import Levenshtein
from keying import *
from widgets_tk import StatusBar,SPLASH_SCREEN

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
        
        self.dxs=[]
        self.ntries=1
        self.down=True
        self.last_txt=None
        self.CASUAL_MODE=False
        if not P.gui:
            self.STAND_ALONE=True
        else:
            self.STAND_ALONE=False

        self.suffixes=['/M','/P','/QRP','/MM']
        for i in range(10):
            self.suffixes.append('/'+str(i))

        # Open main or pop-up window depending on if "root" is given
        if root:
            self.win=Toplevel(root)
            self.hide()
        else:
            self.win = Tk()
        self.win.title("Sending Practice by AA2IL")
        self.win.geometry('1700x240+100+10')
        self.root=self.win

        # Create spash screen
        if self.STAND_ALONE:
            self.splash  = SPLASH_SCREEN(self.root,'keyer_splash.png')
            self.status_bar2 = self.splash.status_bar
            self.status_bar2.setText("Howdy Ho!!!!! Creating GUI ...")
        
        # Read list of Panagrams
        self.panagrams = read_text_file('Panagrams.txt',KEEP_BLANKS=False)
        if False:
            for p in self.panagrams:
                P=p.upper()
                N=26*[0]
                for c in P:
                    if c>='A' and c<='Z':
                        N[ord(c)-ord('A')]+=1
                if not all(N):
                    print('\n*** Not a panagram:')
                    print(p)
                    print(N)
            sys.exit(0)
        
        # Read qso template
        self.QSO_Template = read_text_file('QSO_Template.txt',KEEP_BLANKS=False)
        # KEEP_BLANKS=not RANDOM_QSO_MODE)
        #print('QSO_Template=',self.QSO_Template )
        
        # Read words we stumble with
        self.Stumble = read_text_file('Stumble.txt',KEEP_BLANKS=False)

        # Read Book
        self.Book = read_text_file('Book.txt',KEEP_BLANKS=False)

        # Load fonts we want to use
        if sys.version_info[0]==3:
            font1 = tkinter.font.Font(family="monospace",size=12,weight="bold")
            font2 = tkinter.font.Font(family="monospace",size=28,weight="bold")
        else:
            font1 = tkFont.Font(family="monospace",size=12,weight="bold")
            font2 = tkFont.Font(family="monospace",size=28,weight="bold")

        # Put up a box for the practice text - use large font
        # Make this the default object to take the focus & bind keys to effect special mappings
        NCOLS=12
        row=0
        lab = Label(self.win, text="",font=font1)
        lab.grid(row=row,rowspan=1,column=0,columnspan=NCOLS,sticky=E+W)
        self.txt = Text(self.win, height=2, width=60, bg='white', font=font2,wrap=WORD)
        self.txt.grid(row=row+1,rowspan=2,column=0,columnspan=NCOLS,sticky=E+W)
        self.default_object=self.txt
        self.txt.bind("<Key>", self.KeyPress )
        row+=3

        # Create another txt box to put echo from keying device into
        if self.STAND_ALONE:
            self.txt2 = Text(self.win, height=5, width=60, bg='white', font=font1)
            self.txt2.grid(row=row,rowspan=1,column=0,columnspan=NCOLS,sticky=E+W)

            """
            self.S2 = Scrollbar(self.win)
            self.S2.grid(row=row,column=NCOLS,sticky=N+S)
            self.S2.config(command=self.txt2.yview)
            self.txt2.config(yscrollcommand=self.S2.set)
            """
            row+=5
            self.win.geometry('1700x340+100+10')  

        # Radio button group to select type of practice
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
            self.WPM_TXT.set(self.P.PADDLE_WPM)

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

        # ... and to toggle STRICT Mode ...
        col+=1
        self.StrictBtn=Button(self.win, text="Strict",command=self.toggle_strict)
        self.StrictBtn.grid(row=row,column=col,sticky=E+W)
        self.toggle_strict(1)

        # ... and to toggle CASUAL Mode ...
        col+=1
        self.CasualBtn=Button(self.win, text="Casual",command=self.toggle_casual)
        self.CasualBtn.grid(row=row,column=col,sticky=E+W)
        self.toggle_casual(0)

        # ... and to Quit
        col=NCOLS-1
        Button(self.win, text="Quit",command=self.Quit) \
            .grid(row=row,column=col,sticky=E+W)

        # Entry boxes for mock QSO
        if self.STAND_ALONE:
            col=5
            self.Call = Entry(self.root,font=font1,justify='center')
            self.Call.grid(row=row,column=col,sticky=E+W)
            self.Name = Entry(self.root,font=font1,justify='center')
            self.Name.grid(row=row,column=col+1,sticky=E+W)
            self.Rst = Entry(self.root,font=font1,justify='center')
            self.Rst.grid(row=row,column=col+2,sticky=E+W)

        # Entry box to hold levenstien distance
        col=NCOLS-3
        lab = Label(self.win, text="Current",font=font1)
        lab.grid(row=row-1,column=col,sticky=E+W)
        self.LevDx = Entry(self.root,font=font1,\
                           background='lightgreen',justify='center')
        self.LevDx.grid(row=row,column=col,sticky=E+W)

        # Entry box to hold result from previous attempt
        col+=1
        lab = Label(self.win, text="Previous",font=font1)
        lab.grid(row=row-1,column=col,sticky=E+W)
        self.Prior = Entry(self.root,font=font1,\
                           background='lightgreen',justify='center')
        self.Prior.grid(row=row,column=col,sticky=E+W)

        # Make sure all columns are adjusted when we resize the width of the window
        for i in range(NCOLS):
            Grid.columnconfigure(self.win, i, weight=1,uniform='twelve')
        
        # Bind callbacks for whenever a key is pressed or the mouse enters or leaves the window
        self.win.bind("<Key>", self.KeyPress )
        if not self.STAND_ALONE:
            self.win.bind("<Enter>", self.P.gui.Hoover )
            self.win.bind("<Leave>", self.P.gui.Leave )
            self.win.bind('<Button-1>', self.P.gui.Root_Mouse )      

        # If user clicks on 'x' in upper RH corner, hide or quit
        #self.win.protocol("WM_DELETE_WINDOW", self.hide)
        self.win.protocol("WM_DELETE_WINDOW", self.Quit)

        # Status bar along the bottom
        row+=1
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=row,rowspan=1,column=0,columnspan=NCOLS,sticky=E+W)
        self.status_bar.setText("Howdy Ho!")
        
        # Start the ball rolling with this window not visible
        if not self.STAND_ALONE:
            try:
                self.SetWpm(0)
            except:
                error_trap('PADDLING GUI - Problem setting initial WPM',1)
            self.hide()

    ################################################################################

    # Close splash and Show the gui
    def show_gui(self):
        self.root.deiconify()
        self.splash.destroy()
        self.root.update_idletasks()

    # Some last minute inits that need to be done if keyer gui is being used
    def final_inits(self):
        P=self.P
        if P.gui:
            self.Call = P.gui.call
            self.Name = P.gui.name
            self.Rst  = P.gui.rstout

    # Callback to either hide or quit the paddling practice
    def Quit(self):
        P=self.P
        if not P.gui:
            sys.exit(0)
        else:
            self.hide()

    # Callback for monitor level setter
    def SetMonitorLevel(self,level=None):
        if not self.P.sock:
            return

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
        P=self.P
        WPM=int( self.WPM_TXT.get() ) + dWPM
        print('\nSET WPM: WPM=',WPM)
        if WPM>5:
            if P.LOCK_SPEED:
                print('Paddling->SetWpm: LOCKED - Setting speed to WPM=',
                      WPM,'\tresponded=',self.responded,' ...')
                P.keyer.set_wpm(WPM)
                if P.sock:
                    P.sock.set_speed(WPM)
            elif P.keyer_device:
                print('Paddling->SetWpm: NANO - Setting speed to WPM=',
                      WPM,'...')
                P.keyer_device.set_wpm(WPM,idev=2)
            self.WPM_TXT.set(str(WPM))

        # Get a new panagram, call, etc.
        if self.responded:
            print('PADDLING->SetWpm responded=',self.responded)
            Selection=self.Selection.get()
            if Selection!=7 or RANDOM_QSO_MODE:
                self.NewItem()
        
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
        #print("NEW ITEM - Your selection=",Selection)
        self.responded=False

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
                i = random.randint(0, P.Ncalls-1)
                txt += ' '+P.calls[i]

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
            Done=False
            while not Done:
                i = random.randint(0,n-1)
                txt = self.Stumble[i]
                Done = txt!=self.last_txt
            self.last_txt=txt
            #print('Stumble=',txt)

        elif Selection==7:
            
            # Normal QSO
            if RANDOM_QSO_MODE:
                # Pick a call at random
                done = False
                while not done:
                    i = random.randint(0, P.Ncalls-1)
                    call = P.calls[i]
                    name = P.MASTER[call]['name']
                    done = len(call)>2 and len(name)>2

                self.Call.delete(0,END)
                self.Call.insert(0,call)

                self.Name.delete(0,END)
                self.Name.insert(0,name)

            # Pick RST at random
            i = random.randint(2, 10)
            if i==10:
                rst='5NN Plus'
            else:
                #rst='5'+str(i)+'9'
                #print('rst1=',rst)
                rst=cut_numbers('5'+str(i)+'9',3,True)
                #print('rst2=',rst)
            self.Rst.delete(0,END)
            self.Rst.insert(0,rst)

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
            if P.gui:
                txt = P.gui.Patch_Macro(txt)
                txt = P.gui.Patch_Macro2(txt)
            #print('QSO=',txt)
            
        elif Selection==8:

            # Send a book line by line
            txt = self.Book[self.bookmark]
            self.bookmark= (self.bookmark+1) % len(self.Book)
            
        elif Selection==9:

            # Sprint contest - mimicing IambicMaster
            call1,name1,state1 = self.get_sprint_call()
            call1=call1.replace('/SK','/P')
            call2,name2,state2 = self.get_sprint_call()
            call2=call2.replace('/SK','/M')
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

        # Show results for this attempt
        self.Prior.delete(0, END)
        if len(self.dxs)>0:
            self.Prior.insert(0,str(self.dxs[-1])+' - '+str(self.ntries))
        
        # Reset
        self.responded=False
        self.response=''
        self.item=txt.upper()
        self.dxs=[]
        self.ntries=1
        self.down=True
        #print("NEW ITEM - txt=",txt)
        
        if P.NANO_ECHO:
            self.P.keyer.txt2morse(txt)
        if not P.gui:
            self.txt2.insert(END,'\n')

    # Routine to sift through call history and find a good complete sprint entry
    def get_sprint_call(self):

        P=self.P
        call=None
        while not call:
            i = random.randint(0, P.Ncalls-1)
            c = P.calls[i]
            #print('GET SPRINT CALL:',i,c,P.MASTER[c])
            name  = P.MASTER[c]['name'].replace('.','')
            state = P.MASTER[c]['state']
            #print('GET SPRINT CALL:',name,state)
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
    def toggle_strict(self,onoff=None):
        if onoff==None:
            self.STRICT_MODE = not self.STRICT_MODE
        else:
            self.STRICT_MODE = onoff>0
        if self.STRICT_MODE:
            self.StrictBtn.configure(relief='sunken')
            if self.CASUAL_MODE:
                self.toggle_casual()
        else:
            self.StrictBtn.configure(relief='raised')
        
    # Callback to toggle CASUAL_MODE
    def toggle_casual(self,onoff=None):
        if onoff==None:
            self.CASUAL_MODE = not self.CASUAL_MODE
        else:
            self.CASUAL_MODE = onoff>0
        if self.CASUAL_MODE:
            self.CasualBtn.configure(relief='sunken')
            if self.STRICT_MODE:
                self.toggle_strict()
        else:
            self.CasualBtn.configure(relief='raised')
        
    # Routine to check response
    def check_response(self,txt):
        txt0=txt.replace('\n',' ')
        #if txt0==' ' and self.response=='':
        #    return
        
        self.response+=txt0

        # The input text can have all kinds of weird unicode chars,
        # e.g. 8216 and 8217 are left and right single quotes.
        # Strip these out as well as chars we dont usually send in cw.
        txt1=self.item.encode('ascii','ignore').decode("utf-8") \
                        .replace('"','').replace("'","").strip()
        txt2=self.response.replace('=','-').strip()
        if self.CASUAL_MODE:
            txt1=txt1.replace(' ','')
            txt2=txt2.replace(' ','')
            
        n1=len(txt1)
        print('\nitem:    \t',txt1,'\t',n1)
        #print('\t',show_ascii(txt1) )

        n2=len(txt2)
        print('response:\t',txt2,'\t',n2)
        self.responded = n2>0

        if n2>n1:
            txt3=txt2[-n1:]
            #print('txt2:    \t',show_hex(txt2),n2 )
        else:
            txt3=txt2
        dx=Levenshtein.distance(txt1,txt3)
        
        self.LevDx.delete(0, END)
        self.LevDx.insert(0,str(dx))        
        self.dxs.append(dx)

        if len(self.dxs)>3:
            if dx>self.dxs[-2] and self.down:
                self.ntries+=1
                self.down=False
            elif dx<self.dxs[-2] and not self.down:
                self.down=True
        
        if n2>=n1:
            print('txt3:    \t',txt3,'\t',len(txt3))
            if txt3==txt1:
                print('Distances=',self.dxs)
                print('!!! DING DING DING !!!\t# Tries=',self.ntries)
                if self.STRICT_MODE or self.CASUAL_MODE:
                    self.NewItem()
                    return True
                
        return False

################################################################################

# If this file is called as main, run as independent exe
# Not quite there yet ...
if __name__ == '__main__':

    import cw_keyer
    from settings import read_settings
    from load_history import load_history

    print('Howdy Ho!')
    
    # Structure to contain processing params
    class PADDLING_PARAMS:
        def __init__(self):

            # Init
            self.sock=None
            self.gui=None
            self.LOCK_SPEED=True
            self.WPM=22
            self.PADDLE_WPM=22
            self.USE_KEYER=True
            self.FIND_KEYER=True
            self.NANO_ECHO=True
            self.last_char_time=time.time()
            self.need_eol=False
            
            # Read config file
            self.SETTINGS,RCFILE = read_settings('.keyerrc')

            
    # Function to ckeck keyer to see if the op has responded
    def check_keyer(P):

        txt=P.keyer_device.nano_read()
        #print('CHECK KEYER - txt=',txt,len(txt))

        """
        # Check if its been a while since the last char was received
        # This won't work properly bx linux is not real-time - need to put this in the keyer
        if P.WINKEYER or P.K3NG_IO:
            t=time.time()
            dt=t-P.last_char_time
            if P.need_eol and dt>1.5:
                txt='\n'+txt
                P.need_eol=False
            else:
                P.need_eol=True
                P.last_char_time=t
        """
        
        if len(txt)>0:
            P.PaddlingWin.txt2.insert(END,txt)
            ding=P.PaddlingWin.check_response(txt)
            if ding:
                P.PaddlingWin.txt2.insert(END,'\n')
            P.PaddlingWin.txt2.see(END)
            #print('CHECK KEYER: txt=',txt,len(txt),
            #      '\tding=',ding,P.PaddlingWin.responded)

        # Do it again in 100ms
        timer = P.PaddlingWin.win.after(100, check_keyer, P)


    # Set basic run-time params
    P=PADDLING_PARAMS()

    # Create GUI
    P.PaddlingWin = PADDLING_GUI(None,P)

    # Load master call list
    print('Reading master history file ...')
    P.PaddlingWin.status_bar2.setText('Reading master history file ...')
    MY_CALL2 = P.SETTINGS['MY_CALL'].split('/')[0]
    P.HIST_DIR=os.path.expanduser('~/'+MY_CALL2+'/')
    P.MASTER,fname9 = load_history(P.HIST_DIR+'master.csv')
    P.calls = list(P.MASTER.keys())
    P.Ncalls = len(P.calls)
    
    # We need the keyer
    P.PaddlingWin.status_bar2.setText('Opening keyer ...')
    P.keyer=cw_keyer.Keyer(P,P.WPM)
    P.ser=open_keying_port(P,True,1)
    P.PaddlingWin.SetWpm(0)

    # And away we go!
    P.PaddlingWin.status_bar2.setText('Ready to rock ...')
    P.PaddlingWin.show_gui()
    P.PaddlingWin.status_bar.setText("Let's Rock!")
    P.PaddlingWin.NewItem()
    timer = P.PaddlingWin.win.after(1000, check_keyer, P)
    mainloop()

    print("Y'all come on back now ya hear!")

    
