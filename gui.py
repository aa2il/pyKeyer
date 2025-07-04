############################################################################################
#
# gui.py - Rev 1.1
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# GUI for CW keyer.
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
import os
if sys.version_info[0]==3:
    from tkinter import *
    import tkinter.font
    import tkinter.messagebox
    from tkinter import ttk
else:
    from Tkinter import *
    import tkFont
    import tkMessageBox
import random

import csv
import pytz
from datetime import datetime, date, tzinfo
import time
import cw_keyer
import hint
from dx import Station
from pprint import pprint
import webbrowser
from rig_io import ClarReset,SetTXSplit
from rig_io import DELAY
from rig_control_tk import *
from rotor_control_tk import *
from keyer_control_tk import *
from ToolTip import *
from fileio import *
from threading import enumerate

from cwt import *
from cwopen import *
from foc import *
from sst import *
from sprint import *
from mst import *
from skcc import *
from calls import *
from cqp import *
from wpx import *
from fd import *
from ss import *
from vhf import *
from ten import *
from naqp import *
from iaru import *
from cqww import *
from sats import *
from settings import *
from paddling import *
from ragchew import *
from dx_qso import *
from qrz import *
from utilities import cut_numbers,freq2band,Oh_Canada,error_trap,show_ascii,stack_trace
import pyautogui
from widgets_tk import StatusBar,SPLASH_SCREEN

############################################################################################

UTC = pytz.utc
WPM_STEP = 2                # Key speed step for up/dn buttons - was 4

############################################################################################

def cleanup(x): return x.strip().upper()

# Routine to list threads
def show_threads():
    print('\nList of running threads:')
    threads = enumerate()
    for th in threads:
        print(th,th.getName())
    print(' ')

# The GUI 
class GUI():
    def __init__(self,P):

        # Create root window
        print("\nCreating GUI ...")
        self.root = Tk()
        # width_size x height_size + x_position + y_position
        if P.GEO==None:
            geo='1200x400+250+250'
        else:
            #pyKeyer.py -geo 1500x400+0+240
            geo=P.GEO
        self.root.geometry(geo)

        # Init
        self.MODE = StringVar()
        self.MACRO_TXT = StringVar()
        self.WPM_TXT = StringVar()
        self.FARNS_WPM_TXT = StringVar()
        self.SAT_TXT = StringVar()
        self.qsl_rcvd=tk.IntVar()

        # Over-ride default-font with custom settings
        # Not necesary but I'm leaving this code here fore later reference
        if False:
            print('Default font:',tkinter.font.nametofont('TkTextFont').actual())
            print('Families:',tkinter.font.families())
            self.defaultFont = tkinter.font.nametofont("TkDefaultFont") 
            self.defaultFont.configure(family='DejaVu Sans Mono', 
                                      size=20, 
                                      weight=tkinter.font.NORMAL)
            self.root.option_add("*Font", "ariel")
            print('New Default font:',tkinter.font.nametofont('TkTextFont').actual())
            self.root.option_add("*Label*Font", "Helvetica 20")
            self.root.option_add("*Button*Font", "Arial 15 bold")
            sys.exit(0)
        
        # Init
        self.last_focus=None
        self.WIN_NAME='ROOT WINDOW'
        self.OnTop=False
        self.dx_station = None
        self.CHECK_DIAL = 1
        self.last_qso=None
        self.rig=None
        self.pounced=False
        self.searching=False
        self.MY_CALL = P.SETTINGS['MY_CALL']
        
        # Create spash screen
        self.splash  = SPLASH_SCREEN(self.root,'keyer_splash.png')
        self.status_bar = self.splash.status_bar
        
        # More inits
        self.Done=False
        self.contest = False
        self.P = P
        self.RUNNING=False
        self.P.root = self.root
        self.text_buff=''
        self.macro_label=''
        self.last_text=None

        # Special fonts for various widgets
        FAMILY='monospace'
        #FAMILY='DejaVu Sans Mono'
        if sys.version_info[0]==3:
            self.font1 = tkinter.font.Font(family=FAMILY,size=12,weight="bold")
            self.font2 = tkinter.font.Font(family=FAMILY,size=28,weight="bold")
            self.font3 = tkinter.font.Font(family=FAMILY,size=14) # ,weight="bold")
        else:
            self.font1 = tkFont.Font(family=FAMILY,size=12,weight="bold")
            self.font2 = tkFont.Font(family=FAMILY,size=28,weight="bold")
            self.font3 = tkFont.Font(family=FAMILY,size=14)   # ,weight="bold")

        if False:
            print('\nfamilies=',tkinter.font.families())
            print('\nnames=',tkinter.font.names())
            print('\nfont1=',self.font1.actual())
            print('font2=',self.font2.actual())
            sys.exit(0)

    # Function to actually construct the gui
    def construct_gui(self):
        P=self.P
        self.status_bar.setText("Constructing GUI ...")
        P.MEM.take_snapshot()

        # More inits
        self.keyer=P.keyer;
        self.start_time = None
        self.time_on = None
        self.nqsos_start = 0
        self.sock = self.P.sock

        rig=''
        if P.sock.rig_type2 and P.sock.rig_type2!='None':
            rig=' - '+P.sock.rig_type2
            if P.sock2 and P.sock2.rig_type2 and P.sock2.rig_type2!='None':
                rig+=' + '+P.sock2.rig_type2
                if P.sock3 and P.sock3.rig_type2 and P.sock3.rig_type2!='None':
                    rig+=' + '+P.sock3.rig_type2
        self.root.title("pyKeyer by AA2IL"+rig)
        self.tuning = False
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)

        self.last_call=''
        self.last_shift_key=''
        self.last_hint=''

        self.q = P.q
        self.exch_out=''
        self.ndigits=3
        self.prev_call=''
        self.prev_qso={}
        self.prefill=False
        self.cntr=0

        # Read adif log - why is this stuff in here???? Its not gui, move it elsewhere!!!!
        self.log_book = []
        if P.LOG_FILE==None:
            P.LOG_FILE = P.WORK_DIR+self.MY_CALL.replace('/','_')+".adif"
        print('Opening log file',P.LOG_FILE,'...')
        P.MEM.take_snapshot()
        self.status_bar.setText("Reading log book "+P.LOG_FILE+" ...")
        print('GUI: Reading ADIF log file',P.LOG_FILE)
        qsos = parse_adif(P.LOG_FILE,upper_case=True,verbosity=0)
        for qso in qsos:
            self.log_book.append(qso)

        self.nqsos_start = len(self.log_book)
        print('There are',len(self.log_book),'QSOs in the log book')
        P.MEM.take_snapshot()
        #sys.exit(0)

        # Keep an ADIF copy of the log as well
        if os.path.exists(P.LOG_FILE):
            self.fp_adif = open(P.LOG_FILE,"a+")
        else:
            self.fp_adif = open(P.LOG_FILE,"w")
            #self.fp_adif.write('Simple Log Export<eoh>\n')
            self.fp_adif.write('Created by pyKeyer by AA2IL\n')
            self.fp_adif.write('<USERDEF1:13>RUNNING,{1,0}\n')
            self.fp_adif.write('<eoh>\n')
            self.fp_adif.flush()
        print("GUI: ADIF file name=",P.LOG_FILE) 
        P.MEM.take_snapshot()

        # Also save all sent text to a file
        self.fp_txt = open(P.WORK_DIR+self.MY_CALL.replace('/','_')+".TXT","a+")

        # Add a check file
        if P.PLATFORM=='Linux':
            fname77='snippets.txt'
            if os.path.exists(fname77):
                self.fp_snip = open(fname77,"a+")
            else:
                self.fp_snip = open(fname77,"w")
                self.fp_snip.write('%s\n' % ('#/bin/tcsh -f') )
                self.fp_snip.write('%s\n' % (' ') )
                self.fp_snip.write('%s\n' % ('set fname="capture_*.wav"') )
                self.fp_snip.write('%s\n' % (' ') )
        else:
            self.fp_snip=None

        # Add a tab to manage Rig
        self.rig = RIG_CONTROL(P)
        
        # Add a tab to manage Rotor
        # This is actually rather difficult since there doesn't
        # appear to be a tk equivalent to QLCDnumber
        self.rotor_ctrl = ROTOR_CONTROL(self.rig.tabs,P)

        # Add a tab to manage keyer
        self.keyer_ctrl = KEYER_CONTROL(P)
                    
        # Create s pop-up window for Settings
        self.status_bar.setText("Constructing GUI ...")
        self.SettingsWin = SETTINGS_GUI(self.root,self.P,refreshCB=self.RefreshSettings)
        self.SettingsWin.hide()
            
        # Create pop-up window for Paddle Practice
        self.PaddlingWin = PADDLING_GUI(self.root,self.P)
        if P.SENDING_PRACTICE:
            self.PaddlingWin.show()
        else:
            self.PaddlingWin.hide()
        
        # Add menu bar
        self.ncols=12
        row=0
        self.create_menu_bar()
        
        # Set up basic logging entry boxes
        row+=1
        self.call_lab = Label(self.root, text="Call",font=self.font1)
        self.call_lab.grid(row=row,columnspan=4,column=0,sticky=E+W)
        self.call = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.call.grid(row=row+1,rowspan=2,column=0,columnspan=4,sticky=E+W)
        self.call.bind("<Key>", self.key_press )
        self.call.focus_set()
        self.default_color = self.call.cget("background")
        self.default_object=self.call                    # Make this the default object to take the focus
        
        # For normal operating, these will be visible
        self.name_lab = Label(self.root, text="Name",font=self.font1)
        self.name_lab.grid(row=row,columnspan=4,column=4,sticky=E+W)
        self.name = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.name.grid(row=row+1,rowspan=2,column=4,columnspan=4,sticky=E+W)
        self.name.bind("<Key>", self.key_press )

        self.rstin_lab = Label(self.root, text="RST in",font=self.font1)
        self.rstin_lab.grid(row=row,columnspan=1,column=8,sticky=E+W)
        self.rstin = Entry(self.root,font=self.font2)
        self.rstin.grid(row=row+1,rowspan=2,column=8,columnspan=1,sticky=E+W)
        self.rstin.bind("<Key>", self.key_press )

        self.rstout_lab = Label(self.root, text="RST out",font=self.font1)
        self.rstout_lab.grid(row=row,columnspan=1,column=9,sticky=E+W)
        self.rstout = Entry(self.root,font=self.font2)
        self.rstout.grid(row=row+1,rowspan=2,column=9,columnspan=1,sticky=E+W)
        self.rstout.bind("<Key>", self.key_press )
        if self.P.contest_name=='SATELLITES':
            self.rstin.insert(0,'5')
            self.rstout.insert(0,'5nn')
        else:
            self.rstin.insert(0,'5NN')
            self.rstout.insert(0,'5NN')

        # For contests, some subset of these will be visible instead
        self.exch_lab = Label(self.root, text="Exchange",font=self.font1)
        self.exch_lab.grid(row=row,columnspan=7,column=4,sticky=E+W)
        self.exch = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.exch.grid(row=row+1,rowspan=2,column=4,columnspan=6,sticky=E+W)
        self.exch.bind("<Key>", self.key_press )

        self.qth_lab = Label(self.root, text="QTH",font=self.font1)
        self.qth_lab.grid(row=row,columnspan=3,column=8,sticky=E+W)
        self.qth = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.qth.grid(row=row+1,rowspan=2,column=8,columnspan=2,sticky=E+W)
        self.qth.bind("<Key>", self.key_press )

        self.serial_lab = Label(self.root, text="Serial",font=self.font1)
        self.serial_lab.grid(row=row,columnspan=1,column=4,sticky=E+W)
        self.serial_box = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.serial_box.grid(row=row+1,rowspan=2,column=4,columnspan=1,sticky=E+W)
        self.serial_box.bind("<Key>", self.key_press )

        self.prec_lab = Label(self.root, text="Prec",font=self.font1)
        self.prec_lab.grid(row=row,columnspan=1,column=5,sticky=E+W)
        self.prec = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.prec.grid(row=row+1,rowspan=2,column=5,columnspan=1,sticky=E+W)
        self.prec.bind("<Key>", self.key_press )

        self.cat_lab = Label(self.root, text="Category",font=self.font1)
        self.cat_lab.grid(row=row,columnspan=1,column=5,sticky=E+W)
        self.cat = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.cat.grid(row=row+1,rowspan=2,column=5,columnspan=1,sticky=E+W)
        self.cat.bind("<Key>", self.key_press )

        self.call2_lab = Label(self.root, text="Call",font=self.font1)
        self.call2_lab.grid(row=row,columnspan=1,column=6,sticky=E+W)
        self.call2 = Entry(self.root,font=self.font2)
        self.call2.grid(row=row+1,rowspan=2,column=6,columnspan=1,sticky=E+W)
        self.call2.bind("<Key>", self.key_press )

        self.check_lab = Label(self.root, text="Check",font=self.font1)
        self.check_lab.grid(row=row,columnspan=1,column=7,sticky=E+W)
        self.check = Entry(self.root,font=self.font2,selectbackground='lightgreen')
        self.check.grid(row=row+1,rowspan=2,column=7,columnspan=1,sticky=E+W)
        self.check.bind("<Key>", self.key_press )
        
        self.notes_lab = Label(self.root, text="Notes",font=self.font1)
        self.notes_lab.grid(row=row,columnspan=1,column=8,sticky=E+W)
        self.notes = Entry(self.root,font=self.font2,fg='blue')
        self.notes.grid(row=row+1,rowspan=2,column=8,columnspan=1,sticky=E+W)
        self.notes.bind("<Key>", self.key_press )

        self.hint_lab = Label(self.root, text="Hint",font=self.font1)
        self.hint_lab.grid(row=row,columnspan=1,column=8,sticky=E+W)
        self.hint = Entry(self.root,font=self.font2,fg='blue')
        self.hint.grid(row=row+1,rowspan=2,column=8,columnspan=1,sticky=E+W)
        self.hint.bind("<Key>", self.key_press )

        self.scp_lab = Label(self.root, text="Super Check Partial",font=self.font1)
        self.scp_lab.grid(row=row,columnspan=1,column=9,sticky=E+W)
        self.scp = Entry(self.root,font=self.font2,fg='blue',selectbackground='white')
        self.scp.grid(row=row+1,rowspan=2,column=9,columnspan=1,sticky=E+W)
        self.scp.bind('<Double-Button-1>',self.SCP_Selection)
        self.scp.bind("<Key>", self.key_press )

        # Checkbox to indicate if we've received QSL
        self.qsl_rcvd.set(0)
        self.qsl=tk.Checkbutton(self.root,text='QSL Rcvd', \
                                variable=self.qsl_rcvd)
        self.qsl.grid(row=row+1,column=9,columnspan=1)
        tip = ToolTip(self.qsl, ' QSL has been received ')
        
        # Buttons to access FLDIGI logger
        if False:
            btn = Button(self.root, text='Get',command=self.Set_Log_Fields, \
                         takefocus=0 )
            btn.grid(row=row+1,column=self.ncols-2)
            tip = ToolTip(btn, ' Get FLDIGI Logger Fields ' )

            btn = Button(self.root, text='Put',command=self.Read_Log_Fields,\
                         takefocus=0 ) 
            btn.grid(row=row+1,column=self.ncols-1)
            tip = ToolTip(btn, ' Set FLDIGI Logger Fields ' )

            btn = Button(self.root, text='Wipe',command=self.Clear_Log_Fields,\
                         takefocus=0 ) 
            btn.grid(row=row+2,column=self.ncols-2)
            tip = ToolTip(btn, ' Clear FLDIGI Logger Fields ' )

        # Make sure all columns are adjusted when we resize the width of the window
        for i in range(12):
            Grid.columnconfigure(self.root, i, weight=1,uniform='twelve')

        # Set up two text entry box with a scroll bar
        # The upper box is so we can type in what we receive
        row+=3
        self.txt2_row=row
        self.txt2 = Text(self.root, height=5, width=80, bg='white')
        self.txt2.grid(row=row,column=0,columnspan=self.ncols,stick=N+S+E+W)
        self.S2 = Scrollbar(self.root)
        self.S2.grid(row=row,column=self.ncols,sticky=N+S)
        self.S2.config(command=self.txt2.yview)
        self.txt2.config(yscrollcommand=self.S2.set)
        self.txt2.bind("<Key>", self.key_press )
        self.show_hide_txt2()
            
        # The lower box is so we can type in what we want to send
        row+=1
        Grid.rowconfigure(self.root, row, weight=1)             # Allows resizing
        self.txt = Text(self.root, height=5, width=80, bg='white')
        self.txt.grid(row=row,column=0,columnspan=self.ncols,stick=N+S+E+W)
        self.S = Scrollbar(self.root)
        self.S.grid(row=row,column=self.ncols,sticky=N+S)
        self.S.config(command=self.txt.yview)
        self.txt.config(yscrollcommand=self.S.set)
        if self.P.DIGI:
            c='red'
            self.txt.configure(font=self.font3)
        else:
            c='black'
            c='red'
        self.txt.tag_configure('highlight', foreground=c, relief='raised')

        self.txt.bind("<Key>", self.key_press )
        self.txt.bind('<Button-1>', self.Text_Mouse )      
        self.txt.bind('<Button-2>', self.Text_Mouse )      
        self.txt.bind('<Button-3>', self.Text_Mouse )      

        # Also bind mouse entering or leaving the app
        #self.root.bind("<Key>", self.key_press2 )
        self.root.bind("<Enter>", self.Hoover )
        self.root.bind("<Leave>", self.Leave )
        self.root.bind('<Button-1>', self.Root_Mouse )      

        # Function buttons for pre-defined macros
        row += 10
        self.btns1=[]
        self.btns2=[]
        for i in range(12):
            if i<4:
                c='pale green'
            elif i<8:
                c='indian red'
            else:
                c='slateblue1'
            Grid.columnconfigure(self.root, i, weight=1)
            btn = Button(self.root, text=str(i) , background=c, \
                         command=lambda j=i: self.Send_Macro(j) )
            btn.grid(row=row,column=i,sticky=E+W)
            self.btns1.append(btn)

            btn = Button(self.root, text=str(i) , background=c, \
                         command=lambda j=i+12: self.Send_Macro(j) )
            btn.grid(row=row+1,column=i,sticky=E+W)
            self.btns2.append(btn)

        # Bottom row with various functions
        row += 3
        col=0

        # Set up a spin box to control select contest macro set 
        Label(self.root, text='Macros:').grid(row=row,column=col,sticky=E+W)
        if False:
            SB = ttk.Combobox(self.root,
                             textvariable=self.MACRO_TXT,
                             takefocus=0 )
            SB['values'] = self.P.CONTEST_LIST
            SB.bind('<<ComboboxSelected>>', self.set_macros)
        else:
            # I prefer the way OptionMenu looks
            # Also, there are differences between the tk and ttk versions
            SB = ttk.OptionMenu(self.root, 
                                self.MACRO_TXT, 
                                self.P.CONTEST_LIST[0], 
                                *self.P.CONTEST_LIST, 
                                command=self.set_macros)
        SB.grid(row=row,column=col+1,columnspan=2,sticky=E+W)

        # Set up a spin box to control keying speed (WPM)
        col += 3
        Label(self.root, text='WPM:').grid(row=row,column=col,sticky=E+W)
        SB = Spinbox(self.root,                 \
                     from_=cw_keyer.MIN_WPM,    \
                     to=cw_keyer.MAX_WPM,       \
                     textvariable=self.WPM_TXT, \
                     bg='white',                \
                     justify='center',          \
                     command=lambda j=0: self.set_wpm(0))
        SB.grid(row=row,column=col+1,columnspan=1,sticky=E+W)
        SB.bind("<Key>", self.key_press )
        self.WPM_TXT.set(str(self.keyer.WPM))
        self.set_wpm(0,farnsworth=P.FARNS_WPM)

        # Buttons to change WPM up & down 
        btn = Button(self.root, text='+'+str(WPM_STEP)+' WPM', command=lambda j=WPM_STEP: self.set_wpm(j) )
        btn.grid(row=row+1,column=col,sticky=E+W)
        tip = ToolTip(btn,' Increase Speed ')
        
        btn = Button(self.root, text='-'+str(WPM_STEP)+' WPM', command=lambda j=-WPM_STEP: self.set_wpm(j) )
        btn.grid(row=row+1,column=col+1,sticky=E+W)
        tip = ToolTip(btn,' Decrease Speed ')

        # Set up a spin box to control Farnsworth speed (WPM)
        col += 1
        self.SB3 = Spinbox(self.root,                 \
                           from_=cw_keyer.MIN_WPM,    \
                           to=cw_keyer.MAX_WPM,       \
                           textvariable=self.FARNS_WPM_TXT, \
                           bg='white',                \
                           justify='center',          \
                           command=lambda j=0: self.set_wpm(0))
        self.SB3.grid(row=row,column=col+1,columnspan=1,sticky=E+W)
        self.SB3.bind("<Key>", self.key_press )
        self.FARNS_WPM_TXT.set(str(self.P.FARNS_WPM))
        if not P.FARNSWORTH:
            self.SB3.grid_remove()

        # Entry box to allow changing my counter
        col += 1
        self.counter_lab=Label(self.root, text='Serial:')
        self.counter_lab.grid(row=row,column=col,sticky=E+W)
        self.counter = Entry(self.root,font=self.font2)
        self.counter.bind("<Key>", self.key_press )
        self.counter.grid(row=row,rowspan=1,column=col+1,columnspan=1,sticky=E+W)
        self.counter.delete(0, END)
        self.counter.insert(0,str(self.P.MY_CNTR))
        self.counter_lab.grid_remove()
        self.counter.grid_remove()

        self.dec_btn = Button(self.root, text='Dec', command=lambda j=-1: self.update_counter(j) )
        self.dec_btn.grid(row=row+1,column=col+1,sticky=E+W)
        tip = ToolTip(self.dec_btn,' Decrement Serial')
        
        self.inc_btn = Button(self.root, text='Inc', command=lambda j=+1: self.update_counter(j) )
        self.inc_btn.grid(row=row+1,column=col,sticky=E+W)
        tip = ToolTip(self.inc_btn,' Increment Serial')
                
        # Radio button group to support SO2R
        col += 2              # Need to move this group!
        self.iRadio = IntVar(value=1)
        self.Radio1 = Radiobutton(self.root, text=P.sock1.rig_type2,
                                  variable=self.iRadio,
                                  value=1,command=self.SelectRadio)
        self.Radio1.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(self.Radio1, ' Rig 1 ' )

        col += 1
        if P.sock2:
            self.Radio2 = Radiobutton(self.root,  text=P.sock2.rig_type2,
                                      variable=self.iRadio,
                                      value=2,command=self.SelectRadio)
            self.Radio2.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.Radio2, ' Rig 2 ' )

        if P.sock3:
            col += 1
            self.Radio3 = Radiobutton(self.root,  text=P.sock3.rig_type2,
                                      variable=self.iRadio,
                                      value=3,command=self.SelectRadio)
            self.Radio3.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.Radio3, ' Rig 3 ' )

        # Other buttons - any buttons we need to modify, we need to grab handle to them
        # before we try to pack them.  Otherwise, all we get is the results of the packing

        # Enable/Disable TX button - should be sufficient to just press <CR> in the txt box
        # Put in a pull-down menu if we really need this
        if False:
            self.SendBtn = Button(self.root, text='Send',command=self.Toggle_Immediate_TX,\
                                  takefocus=0 ) 
            self.SendBtn.grid(row=row,column=self.ncols-2)
            tip = ToolTip(self.SendBtn, ' Enable/Disable Immediate Text Sending ' )
        self.Toggle_Immediate_TX(1)

        # PTT button
        self.PTTBtn = Button(self.root, text='  PTT  ',
                             command=self.Toggle_PTT,\
                             takefocus=0 ) 
        self.PTTBtn.grid(row=row,column=self.ncols-3)
        tip = ToolTip(self.PTTBtn, ' Push-To-Talk ' )
        
        # Force rig into a specific mode and set filters
        self.ModeList=['CW','USB','LSB','FM','RTTY','BPSK31']
        self.ModeBox = ttk.OptionMenu(self.root,
                                      self.MODE,
                                      self.ModeList[0],
                                      *self.ModeList,
                                      command=self.Set_Rig_Mode)
        self.ModeBox.grid(row=row,column=self.ncols-2)
        tip = ToolTip(self.ModeBox, ' Set Rig Mode ' )
        if P.INIT_MODE!=None:
            self.MODE.set(P.INIT_MODE)
            self.Set_Rig_Mode(None)
        
        # QRZ button
        btn = Button(self.root, text='QRZ ?',command=self.Call_LookUp,\
                     takefocus=0 ) 
        btn.grid(row=row,column=self.ncols-1)
        tip = ToolTip(btn, ' Query QRZ.com ' )
        
        # Flag it button
        btn = Button(self.root, text='Flag It',command=self.Flag_It,\
                     takefocus=0 ) 
        btn.grid(row=row+1,column=self.ncols-1)
        tip = ToolTip(btn, ' Flag Last QSO ' )
        
        # Set up a spin box to allow satellite logging
        row += 1
        col  = 0
        self.sat_lab = Label(self.root, text='Satellites:')
        self.sat_lab.grid(row=row,column=col,sticky=E+W)
        sat_list=sorted( SATELLITE_LIST )
        if False:
            self.sat_SB = ttk.Combobox(self.root,
                                       textvariable=self.SAT_TXT,
                                       takefocus=0 )
            self.sat_SB['values'] = sat_list
            self.sat_SB.bind('<<ComboboxSelected>>', self.set_satellite)
        else:
            self.sat_SB = ttk.OptionMenu(self.root,
                                        self.SAT_TXT,
                                        sat_list[0],
                                        *sat_list,
                                        command=self.set_satellite)
        self.sat_SB.grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        self.set_satellite('None')
        
        # Reset clarifier
        ClarReset(self,self.P.RX_Clar_On)

        # Some other info
        col=8
        P.RATE_TXT="QSO Rate:"
        self.rate_lab = Label(self.root, text=P.RATE_TXT,font=self.font1)
        self.rate_lab.grid(row=row,columnspan=4,column=col,sticky=W)

        # Buttons to allow quick store & return to spotted freqs
        self.spots=[]
        for j in range(self.P.NUM_ROWS):
            row += 1
            for i in range(12):
                if i<4:
                    c='pale green'
                elif i<8:
                    c='indian red'
                else:
                    c='slateblue1'
                #Grid.columnconfigure(self.root, i, weight=1,uniform='twelve')
                btn = Button(self.root, text='--' , background=c)
                btn.grid(row=row,column=i,sticky=E+W)

                btn.bind('<Button-1>', self.Spots_Mouse )      
                btn.bind('<Button-2>', self.Spots_Mouse )      
                btn.bind('<Button-3>', self.Spots_Mouse )      

                tip = ToolTip(btn, ' Quick Store/Recall ' )
                
                spot = OrderedDict()
                spot['Button'] = btn
                #spot['Call']   = None
                spot['FreqA']   = None
                spot['FreqB']   = None
                spot['Mode']    = None
                spot['Split']   = None
                spot['Ant']     = None
                spot['Fields']  = None
                self.spots.append(spot)

        # Status bar along the bottom
        row+=1
        self.status_bar = StatusBar(self.root)
        self.status_bar.setText("Howdy Ho!")
        self.status_bar.grid(row=row+1,rowspan=1,column=0,columnspan=self.ncols,sticky=E+W)

        # Set macros & restore the state from the last time in
        print('CONSTRUCT GUI - Final inits ...')
        self.PaddlingWin.final_inits()
        self.set_macros()
        self.RestoreState()

        # Kick-off gui updater
        print('CONSTRUCT GUI - Starting Updater ...')
        self.root.after(2000,self.Updater)
        
        # And away we go!
        self.root.deiconify()
        self.splash.destroy()
        self.root.update_idletasks()
        if P.DESKTOP!=None:
            cmd='wmctrl -r "'+self.root.title()+'" -t '+str(P.DESKTOP)
            os.system(cmd)
            cmd='wmctrl -r "'+self.PaddlingWin.win.title()+'" -t '+str(P.DESKTOP)
            os.system(cmd)
        print('CONSTRUCT GUI - And away we go!!!')
        P.MEM.take_snapshot()


    # Callback to show or hide the upper text box
    def show_hide_txt2(self):
        show = self.P.SHOW_TEXT_BOX2        
        if show:
            wght=1
            self.txt2.grid()
            self.S2.grid()
        else:
            wght=0
            self.txt2.grid_remove()
            self.S2.grid_remove()
        Grid.rowconfigure(self.root, self.txt2_row, weight=wght)             # Allows or disables resizing


    # Callback to process mouse events in the root window
    def Root_Mouse(self,event):
        root = self.P.gui.root
        widget = event.widget
        obj = self.Master(widget)
        window=obj.root
        title=window.title()

        print('ROOT MOUSE button=',event.num,'\twidget=',widget,
              '\twindow=',window,'\ttitle=',title)
        if event.num==1:
            # Left click --> grab window selection
            obj.OnTop=True
            if self.P.PLATFORM=='Linux':
                #os.system('wmctrl -a pyKeyer add.above')
                os.system('wmctrl -a "'+title+'"')

            # A bunch of failed attempts - keep this around bx we'll need
            #   something differnet for windoz
            #window.attributes('-topmost', True)
            #window.grab_set()
            #window.grab_set_global()
            #window.lift()
            #root.focus_force()
            #window.after_idle(window.attributes,'-topmost',False)
            #root.update()
            #stk=root.tk.eval('wm stackorder '+str(window))
            #print('stk=',stk)

            # Make this box the default
            if event.widget in self.boxes:
                self.default_object=event.widget

        return
        if evt.num==1:
            # Left click --> select
            try:
                #print(SEL_FIRST,SEL_LAST)
                txt = self.txt.get(SEL_FIRST,SEL_LAST)
                print("Select text:",txt)
                # print("SEL_FIRST:",type(SEL_FIRST),"  SEL_LAST:",SEL_LAST)
            except TclError:
                print("No text selected")
        elif evt.num==2:
            # Middle click --> insert
            try:
                txt = self.txt.get(SEL_FIRST,SEL_LAST)
                print("Select text:",txt)
            except TclError:
                print("No text selected")
                txt = self.last_txt
            print('Insert')
            #self.txt.insert(END, txt+'\n')            
            self.txt.see(END)
            self.last_txt=txt
            if self.P.Immediate_TX:
                self.q.put(txt)
            else:
                self.text_buff+=txt
                self.q.put(txt+' ')
                self.text_buff=''
        elif evt.num==3:
            # Right click --> ???
            pass
        
    # Callback to process mouse events in the big text box
    def Text_Mouse(self,evt):
        print('TEXT MOUSE: button=',evt.num,'\tpos=',evt.x,evt.y)

        shift   = ((evt.state & 0x0001) != 0)
        control = (evt.state & 0x0004) != 0
        mode    = self.MODE.get()
        #print('\tshift=',shift,'\tctrl=',control)
        
        if evt.num==1:

            # Right click --> Make the text box the default widget so we can type things in to xmit
            if mode=='CW' or shift or control:
                self.force_focus(evt.widget)
                return('break')

            # Left click --> select a word
            idx3=self.txt.index("current")
            idx4=self.txt.index("current wordstart")
            idx5=self.txt.index("current wordend")
            print('\tLeft click ... idx=',idx3,idx4,idx5)
            txt = self.txt.get(idx4,idx5).replace(chr(10),'')
            print("\ttxt=",txt,'\tlen=',len(txt),'\t',show_ascii(txt))
            if len(txt)==0:
                print('\tOoops - nothing selected')
                return('break')

            # Insert text into next entry box
            widget=self.default_object
            widget.delete(0, END)
            widget.insert(0,txt)

            # Take care of dupes & hints
            if widget==self.call:
                self.dup_check(txt)
                self.get_hint()
                if self.P.AUTOFILL:
                    self.P.KEYING.insert_hint()
            
            # Move on to the next entry box
            evt.widget=widget
            self.default_object=self.P.KEYING.next_event('Tab',evt)
            self.force_focus(self.default_object)
            return('break')

            # Keeping this around for now
            # Left click --> select
            try:
                idx1=self.txt.index(SEL_FIRST)
                idx2=self.txt.index(SEL_FIRST)
                idx3=self.txt.index(CURRENT)
                print('\tLeft click ... idx=',idx1,idx2,idx3)
                txt = self.txt.get(SEL_FIRST,SEL_LAST)
                print("Select text:",txt)
                # print("SEL_FIRST:",type(SEL_FIRST),"  SEL_LAST:",SEL_LAST)
            except TclError:
                print("No text selected")
        elif evt.num==2:
            # Middle click --> insert
            try:
                txt = self.txt.get(SEL_FIRST,SEL_LAST)
                print("Select text:",txt)
            except TclError:
                print("No text selected")
                txt = self.last_txt
            print('Insert')
            #self.txt.insert(END, txt+'\n')            
            self.txt.see(END)
            self.last_txt=txt
            if self.P.Immediate_TX:
                self.q.put(txt)
            else:
                self.text_buff+=txt
                self.q.put(txt+' ')
                self.text_buff=''
        elif evt.num==3:
            # Right click --> Mske the text box the default widget so we can type things in to xmit
            self.force_focus(evt.widget)
            return('break')

        
    # Callback to process mouse events on the spot buttons
    def Spots_Mouse(self,evt):
        #print 'HELLO!!!!!!!',evt.num

        # Determine which button was clicked
        for i in range(len(self.spots)):
            if self.spots[i]['Button'] == evt.widget:
                idx=i
                break

        # Take action
        if evt.num==1:
            # Left click --> save 
            self.Spots_cb(idx,1)
        elif evt.num==2:
            # Middle click --> clear
            self.Spots_cb(idx,-1)
        elif evt.num==3:
            # Right click --> tune
            self.Spots_cb(idx,2)
        
    # Callback to set logs fields, optionally from fldigi
    def Set_Log_Fields(self,fields=None,CALL_ONLY=False):
        if self.P.WF_ONLY and False:
            print('GUI - SET_LOG_FIELDS skipped - can crash fldigi if in waterfall-only mode')
            return
        
        if not self.P.WF_ONLY and fields==None:
            fields  = self.sock.get_log_fields(CALL_ONLY)
            if CALL_ONLY and len(fields['Call'])==0:
                return
        #print("GUI - SET_LOG_FIELDS ...",fields)

        self.call.delete(0, END)
        self.call.insert(0,fields['Call'])
        self.call.configure(fg='black')
        if CALL_ONLY:
            return fields
        
        self.name.delete(0, END)
        self.name.insert(0,fields['Name'])
        self.qth.delete(0, END)
        self.qth.insert(0,fields['QTH'])

        self.rstin.delete(0, END)
        rst=fields['RST_in']
        if rst=='':
            rst='5nn'
        self.rstin.insert(0,rst)

        self.rstout.delete(0, END)
        rst=fields['RST_out']
        if rst=='':
            rst='5nn'
        self.rstout.insert(0,rst)
        
        self.exch.delete(0, END)
        self.exch.insert(0,fields['Exchange'])
        self.cat.delete(0, END)
        self.cat.insert(0,fields['Category'])

        self.prec.delete(0, END)
        self.prec.insert(0,fields['Prec'])
        self.check.delete(0, END)
        self.check.insert(0,fields['Check'])

        return fields

    # Callback to read log fields and optionally send to fldigi
    def Read_Log_Fields(self,send2fldigi=True):
        print("GUI - READ_LOG_FIELDS ...",send2fldigi,'\tcontest=',self.P.contest_name)
        call    = self.get_call()
        name    = self.get_name()
        qth     = self.get_qth()
        rst_in  = self.get_rst_in()
        rst_out = self.get_rst_out()
        cat     = self.get_cat()

        prec    = self.get_prec()
        check   = self.get_check()

        if self.P.contest_name=='NAQP-CW':
            exchange=qth
        else:
            exchange=self.get_exchange()
        fields = {'Call':call,'Name':name,'RST_in':rst_in,'RST_out':rst_out, \
                  'QTH':qth,'Exchange':exchange, \
                  'Category':cat,'Prec':prec,'Check':check}
        if send2fldigi and not self.P.WF_ONLY:
            print('\tfields=',fields)
            self.sock.set_log_fields(fields)
        return fields

    # Callback to wipe out log fields
    def Clear_Log_Fields(self):
        print('CLEAR_LOG_FILEDS: ...')
        self.call.delete(0, END)
        self.call.configure(bg=self.default_color,fg='black')
        self.name.delete(0, END)
        self.qth.delete(0, END)
        self.rstin.delete(0, END)
        self.rstout.delete(0, END)
        if self.P.contest_name=='SATELLITES':
            self.rstin.insert(0,'5')
            self.rstout.insert(0,'5nn')
        else:
            self.rstin.insert(0,'5NN')
            self.rstout.insert(0,'5NN')
        self.cat.delete(0, END)
        self.scp.delete(0, END)

        self.prec.delete(0, END)
        self.check.delete(0, END)
        self.qsl_rcvd.set(0)
        self.info.delete(0,END)
        
        self.prefill=False
        self.prev_call=''

    # Callback to select a radio for SO2R
    def SelectRadio(self):
        iRadio=self.iRadio.get()
        if iRadio==1:
            self.P.sock=self.P.sock1
            self.P.ser=self.P.ser1
        elif iRadio==2:
            self.P.sock=self.P.sock2
            self.P.ser=self.P.ser2
        else:
            self.P.sock=self.P.sock3
            self.P.ser=self.P.ser3
        self.sock=self.P.sock
        print("You selected radio " + str(iRadio),'\tP.sock=',self.P.sock)
        rig=self.P.sock.rig_type2
        self.root.title("pyKeyer by AA2IL"+rig)

    # Callback to toggle PTT
    def Toggle_PTT(self,iop=None):
        if iop==None:
            self.P.PTT = not self.P.PTT
        print('TOOGLE PTT: ptt=',self.P.PTT,'\tiop=',iop)
        
        # Manage button appearance
        if self.P.PTT:
            self.PTTBtn.configure(background='red',
                                  highlightbackground= 'red',
                                  relief='sunken')
            onoff=True
        else:
            self.PTTBtn.configure(background='green',
                                  highlightbackground= 'green',
                                  relief='raised')
            onoff=False

        # key/unkey
        if self.P.sock_xml!=None:
            self.P.sock_xml.ptt(onoff)
        else:
            self.P.sock.ptt(onoff)
        
    # Callback to toggle sending of text
    def Toggle_Immediate_TX(self,iop=None):
        if iop==None:
            self.P.Immediate_TX = not self.P.Immediate_TX 
        print('\n%%%%%%%%%%%%%%%%%% Toggle_Immediate_TX:',self.P.Immediate_TX,self.text_buff,iop)
        
        """
        # Manage button appearance
        if self.P.Immediate_TX:
            self.SendBtn.configure(background='red',highlightbackground= 'red')
            self.q.put(self.text_buff)
            self.text_buff=''
        else:
            self.SendBtn.configure(background='Green',highlightbackground= 'Green')
        """
        
    # Callback to toggle SO2V mode
    def Toggle_SO2V(self,iop=None):
        print('TOOGLE SO2V:',self.P.SO2V,'\top=',iop)
        if iop==None:
            self.P.SO2V = not self.P.SO2V
        if not self.P.SO2V:
            try:
                self.Select_VFO('A')
            except: 
                error_trap('GUI->TOGGLE SO2V: Unable to set VFO to A',1)
            
        # Manage button appearance
        if self.P.SO2V:
            self.So2vBtn.configure(background='red',
                                   highlightbackground= 'red',
                                   relief='sunken')
            self.P.udp_server.Broadcast('SO2V:ON')

            # Get antenna and tuner settings from VFO A
            time.sleep(DELAY)
            #self.sock.set_vfo('A')
            SetVFO(self,'A')
            time.sleep(DELAY)
            ant=self.sock.get_ant()
            time.sleep(DELAY)
            tuner=self.sock.tuner(-1)
            time.sleep(DELAY)
            #print('TOOGLE SO2V: ant=',ant,'\ttuner=',tuner)

            # Copy settings to VFO B
            #self.sock.set_vfo(op='A->B')
            SetVFO(self,'A->B')
            time.sleep(DELAY)
            #self.sock.set_vfo('B')
            #time.sleep(DELAY)
            
            # Set RX VFO to A and TX VFO to B
            #self.sock.set_vfo(rx='A',tx='B')
            #time.sleep(DELAY)

            self.sock.set_ant(ant)
            time.sleep(DELAY)
            self.sock.tuner(tuner)
            time.sleep(DELAY)

            if self.P.SPLIT_VFOs:
                SetVFO(self,'SPLIT')
            
        else:
            self.So2vBtn.configure(background='Green',
                                   highlightbackground= 'Green',
                                   relief='raised')
            self.P.udp_server.Broadcast('SO2V:OFF')


    # Callback to set VFO to A or B, no splits
    def Select_VFO(self,iop):
        print('SELECT VFO:',iop,self.P.SPLIT_VFOs,' ...................')
        if self.P.SPLIT_VFOs:
            self.Toggle_VFOSplit()
        SetVFO(self,iop)
            
    # Callback to toggle Split VFOs mode
    def Toggle_VFOSplit(self,iop=None):
        if iop==None:
            self.P.SPLIT_VFOs = not self.P.SPLIT_VFOs
        print('TOOGLE VFOSplit:',self.P.SPLIT_VFOs,iop)
        
        # Take appropriate action and manage button appearance
        if self.P.SPLIT_VFOs:
            self.VFOSplitBtn.configure(background='red',
                                       highlightbackground= 'red',
                                       relief='sunken')
            #self.P.udp_server.Broadcast('SPLIT:ON')

            # Set VFO splits
            SetVFO(self,'SPLIT')            
        else:
            self.VFOSplitBtn.configure(background='Green',
                                       highlightbackground= 'Green',
                                       relief='raised')
            #self.P.udp_server.Broadcast('SPLIT:OFF')

            # Turn off VFO splits
            self.Select_VFO('A')            
        
    # Callback to toggle DXSplit mode
    def Toggle_DXSplit(self,iop=None):
        if iop==None:
            self.P.DXSPLIT = not self.P.DXSPLIT
        print('TOOGLE DXSplit:',self.P.DXSPLIT,iop)
        
        # Manage button appearance
        if self.P.DXSPLIT:
            self.DXSplitBtn.configure(background='red',
                                      highlightbackground= 'red',
                                      relief='sunken')                          
            self.P.udp_server.Broadcast('SPLIT:ON')

            # Set TX clarifier (XIT split) to 1 KHz UP by default
            SetTXSplit(self.P,1,True)
        else:
            self.DXSplitBtn.configure(background='Green',
                                      highlightbackground= 'Green',
                                      relief='raised')                   
            self.P.udp_server.Broadcast('SPLIT:OFF')

            # Turn off TX clarifier (XIT split)
            SetTXSplit(self.P,0,False)
        
    # Callback to toggle filter width
    def Toggle_FilterWidth(self,iopt=None):
        if iopt==None:
            self.FilterSelect=1-self.FilterSelect
        else:
            self.FilterSelect=iopt

        mode = self.MODE.get()
        if mode=='CW':
            self.FilterWidths=[50,200]
        elif mode in ['USB','LSB']:
            self.FilterWidths=[1800,2400]
        elif self.P.SPECIAL:
            self.FilterWidths=[2500,3000]
        elif self.P.DIGI:
            self.FilterWidths=[500,2000]
        
        w=self.FilterWidths[self.FilterSelect]
        c=self.FilterColors[self.FilterSelect]
        r=self.FilterReliefs[self.FilterSelect]
        print('TOGGLE FILTER ...',self.FilterSelect,w,c,r)
        
        # Manage button appearance
        self.FilterWidthBtn.configure(text=str(w)+' Hz',
                                      background=c,
                                      highlightbackground=c,
                                      relief=r)
            
        print('TOGGLE FILTER - Setting filter to',w)
        self.sock.set_filter(w)

            
    # Callback to look up a call on qrz.com
    def Call_LookUp(self):
        call = self.get_call()
        if len(call)>=3:
            print('CALL_LOOKUP: Looking up '+call+' on QRZ.com')
            if True:
                link = 'https://www.qrz.com/db/' + call
                webbrowser.open(link, new=2)

            self.qrzWin = CALL_INFO_GUI(self.root,self.P,[call],[self.last_qso])
            #self.qrzWin.hide()

        if self.match1:
            print('\nWorked B4:')
            print(self.last_qso,'\n')
            #for qso in self.log_book:
            #    if qso['CALL']==call:
            #        print(qso)
            #print(' ')
            
        else:
            print('CALL_LOOKUP: Need a valid call first! ',call)
            self.status_bar.setText('QRZ? - Need a valid call first!')
            
    # Callback to flag last QSO
    def Flag_It(self):
        
        # Can use this as a test button also
        if False:
            ClarReset(self,self.P.RX_Clar_On)
            return
        
        note=self.prev_qso['CALL']+'  '+self.prev_qso['TIME_OFF']
        cmd='split_wave $fname -snip ' + self.prev_qso['TIME_OFF'] + \
            ' ; audacity SNIPPIT.wav > & /dev/null'
        print('\n#',note)
        print(cmd,'\n')
        if self.fp_snip:
            self.fp_snip.write('\n# %s\n' % (note) )
            self.fp_snip.write('%s\n' % (cmd) )
            self.fp_snip.flush()

            txt='# FLAG IT!\n'
            self.fp_adif.write(txt+'\n')
            self.fp_adif.flush()
            self.txt.insert(END, txt)            
            self.txt.see(END)
        
    # Callback to bring up rig control menu
    def RigCtrlCB(self):
        print("^^^^^^^^^^^^^^Rig Control...")
        self.rig.show()

    # Callback to bring up keyercontrol menu
    def KeyerCtrlCB(self):
        print("^^^^^^^^^^^^^^Keyer Control...")
        self.keyer_ctrl.show()

    # Callback to key/unkey TX for tuning
    def Tune(self):
        print("Tuning...")
        txt='[TUNE]'
        self.q.put(txt)

    # Callback to clear all spots
    def Clear_All_Spots(self):
        print('CLEAR ALL SPOTS ...')
        for idx in range(len(self.spots)):
            self.Spots_cb(idx,-1)

    # Callback to store & retrieve spotted freqs
    def Spots_cb(self,arg,idir):
        print('\nSPOTS_CB: arg=',arg,'\tidir=',idir,'\tlast_shift=',self.last_shift_key)

        spot = self.spots[arg]
        if idir==0:
            
            # Not sure what this does but probably never get here!
            txt = spot['Button']['text']
            if txt=='--':
                frqA  = 1e-3*self.sock.get_freq(VFO='A') 
                frqB  = 1e-3*self.sock.get_freq(VFO='B') 
                mode  = self.sock.get_mode()
                split = self.sock.split_mode(-1)
                ant = self.sock.get_ant()
                if split:
                    spot['Button']['text'] = "{:,.1f}".format(frqB)
                else:
                    spot['Button']['text'] = "{:,.1f}".format(frq)
                spot['FreqA']=frqA
                spot['FreqB']=frqB
                spot['Mode']=mode
                spot['Split']=split
                spot['Ant']=ant
                spot['Fields'] = self.Read_Log_Fields()
            else:
                frqA  = spot['FreqA']
                frqB  = spot['FreqB']
                mode  = spot['Mode']
                split = spot['Split']
                ant   = spot['Ant']
                self.sock.set_freq(frqA,VFO='A')
                self.sock.set_freq(frqB,VFO='B')
                self.sock.set_mode(mode)
                self.sock.set_ant(ant)
                spot['Button']['text']='--'
                self.Set_Log_Fields(spot['Fields'])

        elif idir==-1:
            
            # Clear
            spot['Button']['text'] = '--'
            spot['FreqA']   = None
            spot['FreqB']   = None
            spot['Mode']    = None
            spot['Split']   = None
            spot['Ant']     = None
            spot['Fields']  = None
            self.P.DIRTY    = True

        elif idir==1:
            
            # Save
            call  = self.get_call().upper()
            frqA  = 1e-3*self.sock.get_freq(VFO='A') 
            frqB  = 1e-3*self.sock.get_freq(VFO='B') 
            mode  = self.sock.get_mode()
            split = self.sock.split_mode(-1)
            ant   = self.sock.get_ant()
            if split:
                spot['Button']['text'] = call+" {:,.1f} ".format(frqB)
            else:
                spot['Button']['text'] = call+" {:,.1f} ".format(frqA)
            spot['FreqA']  = frqA
            spot['FreqB']  = frqB
            spot['Mode']   = mode
            spot['Split']  = split
            spot['Ant']    = ant
            spot['Fields'] = self.Read_Log_Fields()
            self.P.DIRTY   = True

            print('Save SPOT:',frqA,frqB,self.sock.rig_type,self.sock.fldigi_active)
            foffset=self.sock.modem_carrier()
            print('foffset=',foffset)
            spot['Offset']=foffset

            msg  = 'SPOT:'+call+':'+str(frqA)+':'+mode
            print('Save SPOT: Broadcasting spot:',msg)
            self.P.udp_server.Broadcast(msg)

        elif idir==2:
            
            # Restore
            print('\tspot=',spot)
            try:
                frqA  = spot['FreqA']
                frqB  = spot['FreqB']
                mode  = spot['Mode']
                split = spot['Split']
                ant   = spot['Ant']

                print('\tRestore SPOT: frqA/B=',frqA,frqB,'\tmode=',mode,
                      '\n\t\tsplit=',split,'\tant=',ant,
                      '\n\t\tFields=',spot['Fields'])
                
                self.sock.set_freq(frqA,VFO='A')
                self.sock.set_freq(frqB,VFO='B')
                self.sock.set_mode(mode)
                self.sock.set_ant(ant)
                self.Set_Log_Fields(spot['Fields'])
                call=self.get_call().upper()
                self.dup_check(call)
                #self.auto_fill(call,'')

                if 'Offset' in spot:
                    foffset = spot['Offset']
                    print('\tRestore SPOT: frqA=',frqA,'\trig_type=',self.sock.rig_type,
                          '\n\t\tfldigi active=',self.sock.fldigi_active,'\toffset=',foffset)
                    self.sock.modem_carrier(foffset)
                    
            except: 
                error_trap('GUI->SPOTS_CB - Unable to restore spot',1)

        else:
            print('\nSPOTS_CB - NOT SURE HOW WE GOT HERE????!!!')
            

    # Routine to substitute various keyer commands that are stable in macro text
    def Patch_Macro(self,txt):
        txt = txt.replace('[MYCALL]',self.MY_CALL )
        if '[MYSTATE]' in txt:
            self.qth_out = self.P.SETTINGS['MY_STATE']
            txt = txt.replace('[MYSTATE]',self.qth_out)
        if '[MYNAME]' in txt:
            self.name_out = self.P.SETTINGS['MY_NAME']
            txt = txt.replace('[MYNAME]', self.name_out)
        if '[MYQTH]' in txt:
            self.qth_out = self.P.SETTINGS['MY_QTH']
            txt = txt.replace('[MYQTH]',self.qth_out)
        if '[MYCWOPS]' in txt:
            self.cwops = self.P.SETTINGS['MY_CWOPS'] 
            txt = txt.replace('[MYCWOPS]',self.cwops)
        if '[MYSEC]' in txt:
            self.qth_out = self.P.SETTINGS['MY_SEC'] 
            txt = txt.replace('[MYSEC]',self.qth_out)
        if '[MYGRID]' in txt:
            self.qth_out = self.P.SETTINGS['MY_GRID'][0:4]
            txt = txt.replace('[MYGRID]',self.qth_out)
        if '[MYITUZ]' in txt:
            self.qth_out = self.P.SETTINGS['MY_ITU_ZONE'] 
            txt = txt.replace('[MYITUZ]', self.qth_out)
        if '[MYPREC]' in txt:
            self.prec_out = self.P.SETTINGS['MY_PREC']
            txt = txt.replace('[MYPREC]',self.prec_out)
        if '[MYCHECK]' in txt:
            self.check_out = self.P.SETTINGS['MY_CHECK']
            txt = txt.replace('[MYCHECK]', self.check_out)
        if '[MYCQZ]' in txt:
            zone=self.P.SETTINGS['MY_CQ_ZONE']
            if self.P.DIGI and len(zone)==1:
                zone='0'+zone
            txt = txt.replace('[MYCQZ]', zone )
        if '[MYCAT]' in txt:
            self.check_out = self.P.SETTINGS['MY_CAT'] 
            txt = txt.replace('[MYCAT]', self.check_out)
        if '[MYCOUNTY]' in txt:
            self.qth_out = self.P.SETTINGS['MY_COUNTY'] 
            txt = txt.replace('[MYCOUNTY]', self.qth_out)
        if '[MYSKCC]' in txt:
            self.qth_out = self.P.SETTINGS['MY_SKCC']
            txt = txt.replace('[MYSKCC]', self.qth_out )
        if '[MYRIG]' in txt:
            rig = self.P.SETTINGS['MY_RIG']
            txt = txt.replace('[MYRIG]', rig )
        if '[MYANT]' in txt:
            ant = self.P.SETTINGS['MY_ANT']
            txt = txt.replace('[MYANT]', ant )
        if '[MYAGE]' in txt:
            age = self.P.SETTINGS['MY_AGE']
            txt = txt.replace('[MYAGE]', age )
        if '[HAMAGE]' in txt:
            age = self.P.SETTINGS['MY_HAM_AGE']
            txt = txt.replace('[HAMAGE]', age )
        if '[MYOCCUPATION]' in txt:
            occ = self.P.SETTINGS['MY_OCCUPATION']
            txt = txt.replace('[MYOCCUPATION]', occ )

        """
        if '[CALL]' in txt:
            call=self.get_call()
            txt = txt.replace('[CALL]', call )
        if '[NAME]' in txt:
            name=self.get_name()
            txt = txt.replace('[NAME]', name )
        """

        return txt
    
    # Routine to substitute various keyer commands that change quickly in macro text 
    def Patch_Macro2(self,txt,state=0):

        P=self.P

        # Check if any shift keys were pressed
        if state:
            shift   = (state & 0x0001) != 0
            control = (state & 0x0004) != 0
            if P.PLATFORM=='Linux':
                alt = (state & 0x0008) != 0 
            elif P.PLATFORM=='Windows':
                alt = (state & 0x20000) != 0
            else:
                print('PATCH_MACRO:  **** ERROR **** Unknown platform',P.PLATFORM)
                alt = (state & 0x0008) != 0 

            # Yes - shorten response by eliminating my call
            if alt or control or shift:
                if self.MY_CALL in txt:
                    txt = txt.replace(self.MY_CALL,'')

        # Greeting might depend on local time of day
        if '[GDAY]' in txt:
            try:
                # Use his local time
                call=self.get_call()
                stn = Station(call)
                utc = datetime.now(timezone.utc)
                #print('GUI->GDAY: utc=',utc)
                if time.daylight:
                    # My station is under daylight savings time - ugh!
                    offset = -stn.offset+1
                else:
                    offset = -stn.offset
                local = utc.astimezone(timezone(timedelta(hours=offset)))
                hour = local.hour
                #print('GUI->GDAY: offset=',offset,'\tlocal=',local,'\thour=',hour)
            except:
                # Well that didnt work - use my local time instead
                hour = datetime.now().hour
                #print('GUI->GDAY: Ooops hour=',hour)
            
            if hour<12:
                txt = txt.replace('[GDAY]','GM' )
            elif hour<18:
                txt = txt.replace('[GDAY]','GA' )
            else:
                txt = txt.replace('[GDAY]','GE' )
            #print('GUI->GDAY: txt=',txt)

        # Vary the greeting for friends
        if '[HOWDY]' in txt:
            GREETINGS=['FB','FB','TNX','GL']
            i = random.randint(0, len(GREETINGS)-1)
            txt = txt.replace('[HOWDY]',GREETINGS[i])

        # Check if call has changed - if so, repeat it
        call = self.get_call().upper()
        if '[CALL_CHANGED]' in txt:
            call2 = self.last_call
            #print '---- CALL:',call,call2,call==call2
            if call==call2:
                txt = txt.replace('[CALL_CHANGED]','')
            else:
                stn1 = Station(call)
                try:
                    prefix1=stn1.call_prefix+stn1.call_number
                    print('STN1:',stn1.call_prefix,stn1.call_number,stn1.call_suffix)
                except:
                    error_trap('PATCH MACRO2 - Problem getting prefix for STN1')
                    print('\tcall  =',call)
                    print('\tcall2 =',call2)
                    prefix1=''
                    
                stn2 = Station(call2)
                try:
                    prefix2=stn2.call_prefix+stn2.call_number
                    print('STN2:',stn2.call_prefix,stn2.call_number,stn2.call_suffix)
                except:
                    error_trap('PATCH MACRO2 - Problem getting prefix for STN2 - call2='+call2)
                    prefix2=''

                # Only send back part that has changed, provided it is long enough
                call3=call
                if prefix1==prefix2 and len(stn1.call_suffix)>1:
                    call3=stn1.call_suffix
                elif stn1.call_suffix==stn2.call_suffix and len(prefix1)>1:
                    call3=prefix1
                txt = txt.replace('[CALL_CHANGED]',call3)

        # Fill in his call ...
        if '[CALL]' in txt:
            txt = txt.replace('[CALL]',call)
            self.last_call=call

        # Fill in his serial ...
        if '[SERIAL_IN]' in txt:
            serial=self.get_serial().upper()
            txt = txt.replace('[SERIAL_IN]',str(serial))
            self.last_call=call

        # ... and his name ...
        his_name=self.get_name().replace('?','')
        my_name = self.P.SETTINGS['MY_NAME']
        if ('?' in his_name) or (his_name==my_name and '[NAME] '+my_name in txt and False):
            txt = txt.replace('[NAME] ','')
        else:
            txt = txt.replace('[NAME]',his_name )

        # ... and his RST
        txt = txt.replace('[RST]', self.get_rst_out() )

        # Take care of exchange
        if '[EXCH]' in txt:
            txt = txt.replace('[EXCH]', '' )
            self.exch_out = txt

        # Collapse whitespace
        txt = txt.replace('  ',' ')
        #txt=" ".join(txt.split())
        return txt

    # Function to send cw text 
    def Send_CW_Text(self,txt):
        print('SEND CW TEXT: txt=',txt,'\tpounced=',self.pounced,
              '\trunning=',self.RUNNING,'\tsearching=',self.searching)

        # Send text to keyer ...
        self.q.put(txt)

        # ... and to big text box ...
        if self.pounced:
            call = self.get_call().upper()
            print('\tcall=',call)
            if self.RUNNING or self.searching:
                txt2='************* Whoooops! Unlogged pounced??? **********'
                txt2+='   call= '+call+'\n'
                print(txt2)
                txt = txt2+txt
                self.pounced=False
                self.searching=False
            else:
                txt  = '['+call+'] '+txt
        if '[LOG]' not in txt or True:
            if self.P.DIGI:
                txt='\n'+txt
            else:
                txt+='\n'
        if not self.P.DIGI or '[LOG]' in txt or True:
            print('\ttxt=',txt)

            if self.P.DIGI:
                self.txt.insert(END, txt, ('highlight'))
            else:
                self.txt.insert(END, txt)
            self.txt.see(END)
            self.root.update_idletasks()

        # ... and to disk
        self.fp_txt.write('%s\n' % (txt) )
        self.fp_txt.flush()
    
    # Callback to send a pre-defined macro
    def Send_Macro(self,arg,state=0):
        print('SEND_MACRO: arg=',arg,'\t',arg in self.macros)
        #print(self.macros)
        if arg not in self.macros:
            return

        P=self.P
        label = self.macros[arg]["Label"]
        if arg<=2 or (arg>=0+12 and arg<=2+12):
            self.RUNNING = True
            #elif arg in [5,5+12]:
        elif 'S&P' in label:
            self.RUNNING = False
            self.pounced=True
        elif self.MY_CALL in label:
           self.searching==True
 
        if arg in [1,4,5]:
            self.time_on = datetime.utcnow().replace(tzinfo=UTC)
            print('TIME_ON A set to',self.time_on.strftime('%H%M%S'))

        # Keep track of what we last sent
        txt = self.macros[arg]["Text"]
        P.LAST_MACRO=arg

        # Set register to tell practice exec what op has done
        P.OP_STATE=0
        if 'CQ' in label or 'QRZ' in label:
            P.OP_STATE |= 1
        if 'Reply' in label:
            P.OP_STATE |= 2+32
        if 'TU' in label:
            P.OP_STATE |= 4
        if '?' in label and 'QRZ?' not in label:
            P.OP_STATE |= 8
        if '[MYCALL]' in label:
            P.OP_STATE |= 16
        if 'Log QSO' in label:
            P.OP_STATE |= 64
        self.macro_label=label
        print('SEND_MACRO: arg=',arg,'\tlabel=',label,'\tOP_STATE=',P.OP_STATE)

        # Highlight appropriate buttons for running or s&p
        self.P.KEYING.highlight(self,arg)
        print("\nSend_Macro:",arg,':\ttxt=',txt,'\tstate=',state)
        if '[SERIAL]' in txt or '[SERIAL_CUT]' in txt:
            if False:
                # Old - reading from rig or fldigi or somewhere else?!
                cntr = self.sock.get_serial_out()
                print('SEND MACRO: cntr1=',cntr,'\tndigits=',self.ndigits)
                if not cntr or cntr=='':
                    cntr=self.P.MY_CNTR
            else:
                # Use local counter!!!
                cntr=self.P.MY_CNTR
            print('SEND MACRO: cntr2=',cntr,'\tndigits=',self.ndigits)
            if '[SERIAL]' in txt:
                self.cntr = cut_numbers(cntr,ndigits=self.ndigits)
                txt = txt.replace('[SERIAL]',self.cntr)
                print('SEND MACRO: cntr=',self.cntr,'\ttxt=',txt,'\tndigits=',self.ndigits,'\tALL=False')
            else:
                self.cntr = cut_numbers(cntr,ALL=True,ndigits=3)
                txt = txt.replace('[SERIAL_CUT]',self.cntr)
                print('SEND MACRO: cntr=',self.cntr,'\ttxt=',txt,
                      '\tndigits=',3,'\tALL=',True)
            #self.serial_out = self.cntr

        # Fill in name
        name=self.get_name().upper()
        if name=='' and '[NAME]' in txt:
            try:
                call=self.get_call().upper()
                name2=self.P.MASTER[call]['name']
                my_name = self.P.SETTINGS['MY_NAME']
                if name2==my_name and '[NAME] '+my_name in txt:
                    name2=' '
                txt = txt.replace('[NAME]',name2).replace('  ',' ')
            except:
                error_trap('GUI->SEND MACRO - Unable to retrieve NAME')

        # Send macro text
        txt = self.Patch_Macro2(txt,state)
        print('\nSEND_MACRO: txt=',txt)
        self.Send_CW_Text(txt)
        

    # Routine to hide all of the input boxes
    def hide_all(self):
        print('HIDE ALL ...',self.serial_box)
        self.cat_lab.grid_remove()
        self.cat.grid_remove()
        self.rstin_lab.grid_remove()
        self.rstin.grid_remove()
        self.rstout_lab.grid_remove()
        self.rstout.grid_remove()
        self.exch_lab.grid_remove()
        self.exch.grid_remove()
        self.name_lab.grid_remove()
        self.name.grid_remove()
        self.qth_lab.grid_remove()
        self.qth.grid_remove()
        
        self.serial_lab.grid_remove()
        self.serial_box.grid_remove()
        self.counter.grid_remove()
        self.inc_btn.grid_remove()
        self.dec_btn.grid_remove()
        
        self.prec_lab.grid_remove()
        self.prec.grid_remove()
        self.call2_lab.grid_remove()
        self.call2.grid_remove()
        self.check_lab.grid_remove()
        self.check.grid_remove()
        self.notes_lab.grid_remove()
        self.notes.grid_remove()
        self.hint_lab.grid_remove()
        self.hint.grid_remove()
        self.scp_lab.grid_remove()
        self.scp.grid_remove()
        self.qsl.grid_remove()

        self.sat_lab.grid_remove()
        self.sat_SB.grid_remove()

    # Callback to set Satellite list spinner
    def set_satellite(self,val):
        print('SET_SATELLITE: val=',val)
        #print SATELLITE_LIST
        #self.SAT_TXT.set(str(SATELLITE_LIST[val]))
        self.SAT_TXT.set(val)

    # Callback to read Satellite list spinner
    def get_satellite(self):
        val=self.SAT_TXT.get()

        # If necessary, Change name to be compatible with lotw
        if val=='UVSQ-SAT':
            val='UVSQ'
            
        return val
        
    # Callback for Macro list spinner
    def set_macros(self,val=None):

        #print('SET_MACROS: val=',val)
        if not val:
            val=self.P.contest_name
            self.MACRO_TXT.set(val)
        print('SET_MACROS: val=',val)

        #idx = self.P.CONTEST_LIST.index(val)
        #print('SET_MACROS: val=',val,'\tidx=',idx,'\t)

        # Initiate keying module for this contest
        if val=='CWT':
            self.P.KEYING=CWOPS_KEYING(self.P)
        elif val=='FOC-BW':
            self.P.KEYING=FOCBW_KEYING(self.P)
        elif val=='SST':
            self.P.KEYING=SST_KEYING(self.P)
        elif val=='MST':
            self.P.KEYING=MST_KEYING(self.P)
        elif val=='WRT':
            self.P.KEYING=WRT_KEYING(self.P)
        elif val=='NS':
            self.P.KEYING=SPRINT_KEYING(self.P)
        elif val=='SKCC':
            self.P.KEYING=SKCC_KEYING(self.P)
        elif val=='CALLS':
            self.P.KEYING=CALLS_KEYING(self.P)
        elif val=='CW Open':
            self.P.KEYING=CWOPEN_KEYING(self.P)
        elif val=='SATELLITES':
            self.P.KEYING=SAT_KEYING(self.P)
        elif val in ['ARRL-VHF','CQ-VHF','STEW PERRY','MAKROTHEN']:
            self.P.KEYING=VHF_KEYING(self.P,val)
        elif val=='CQP':
            self.P.KEYING=CQP_KEYING(self.P)
        elif val in self.P.STATE_QPs+['TEN-TEN','WAG','ARRL-160M','RAC','BERU',
                                      'FOC-BW99','JIDX','CQMM','HOLYLAND','AADX',
                                      'IOTA','MARAC','SAC','OCDX','SOLAR',
                                      'SPDX','POTA','YURI','MMC','AWT']:
            self.P.KEYING=DEFAULT_KEYING(self.P,val)
        elif val.find('NAQP')>=0:
            self.P.KEYING=NAQP_KEYING(self.P,val)
        elif val=='IARU-HF':
            self.P.KEYING=IARU_KEYING(self.P)
        elif val=='CQWW':
            self.P.KEYING=CQWW_KEYING(self.P)
        elif val=='ARRL-SS-CW':
            self.P.KEYING=SS_KEYING(self.P)
        elif val=='ARRL-FD' or val=='WINTER-FD':
            self.P.KEYING=FD_KEYING(self.P)
        elif val.find('CQ-WPX')>=0:
            self.P.KEYING=WPX_KEYING(self.P,val)
        elif val=='ARRL-10M' or val=='ARRL-DX' or val=='CQ-160M':
            self.P.KEYING=TEN_METER_KEYING(self.P,val)
        elif val=='Ragchew':
            self.P.KEYING=RAGCHEW_KEYING(self.P,val)
        elif val=='DX-QSO':
            self.P.KEYING=DX_KEYING(self.P,val)
        elif val=='Default':
            self.P.KEYING=DEFAULT_KEYING(self.P)
        elif val=='RANDOM CALLS':
            self.P.KEYING=RANDOM_CALLS_KEYING(self.P)
        else:
            print('SET_MACROS: *** ERROR *** Cant figure which contest !')
            print('val=',val)
            #return
            sys.exit(0)
            
        self.P.contest_name  = self.P.KEYING.contest_name
        self.macros = self.P.KEYING.macros()
        
        for i in range(12):
            if i in self.macros:
                lab = self.macros[i]["Label"].replace('[MYCALL]',self.MY_CALL )
                self.btns1[i].configure( text=lab )

                txt = self.Patch_Macro( self.macros[i]["Text"] )
                self.macros[i]["Text"] = txt
                tip = ToolTip(self.btns1[i], ' '+txt+' ' )

            if i+12 in self.macros:
                lab = self.macros[i+12]["Label"].replace('[MYCALL]',self.MY_CALL )
                self.btns2[i].configure( text=lab )
                txt = self.Patch_Macro( self.macros[i+12]["Text"] )
                self.macros[i+12]["Text"] = txt
                tip = ToolTip(self.btns2[i], ' '+txt+' ' )
                self.btns2[i].grid()
            else:
                self.btns2[i].grid_remove()

        #print( self.P.CONTEST)
        #for key in self.P.CONTEST.keys():
        #    self.P.CONTEST[key]=False
        #self.P.CONTEST[val] = True
        #print( self.P.CONTEST)
                
        # Enable the specific input boxes
        self.P.KEYING.enable_boxes(self)

        """
        elif self.P.CONTEST[val]:
            # Generic contest exchange 
            self.contest=True
            self.hide_all()

            self.exch_lab.grid()
            self.exch.grid()
            
        else:
            # Generic QSO
            self.contest=False
            self.hide_all()

            self.name_lab.grid()
            self.name.grid()
            self.rstin_lab.grid()
            self.rstin.grid()
            self.rstout_lab.grid()
            self.rstout.grid()
        """

    # Callback for WPM spinner
    def set_wpm(self,dWPM=0,farnsworth=None):
        WPM=int( self.WPM_TXT.get() ) + dWPM
        if farnsworth!=None:
            WPM2=farnsworth
        elif self.P.FARNSWORTH:
            WPM2=int( self.FARNS_WPM_TXT.get() )
        else:
            WPM2=None
            
        if WPM>=5:
            print('GUI->SET WPM: Setting speed to',WPM,WPM2,'wpm ...')
            self.keyer.set_wpm(WPM,farnsworth=WPM2)
            self.sock.set_speed(WPM)
            self.WPM_TXT.set(str(WPM))
            self.P.WPM = WPM

    # Callback to return everything to defaults
    def Reset_Defaults(self):
        print("Reset...")
        txt="[RESET]"
        self.q.put(txt)
        WPM=self.keyer.get_wpm()
        self.WPM_TXT.set(str(WPM))

    # Read counter from the entry box
    def update_counter(self,adj=0):
        cntr = self.counter.get()
        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ UPDATE COUNTER ^^^^^^^^^^^^^^^^^^^^',cntr,adj)
        try:
            if cntr=='':
                self.P.MY_CNTR = 1
            else:
                self.P.MY_CNTR = max(1,int(cntr)+adj)
            self.counter.delete(0, END)
            self.counter.insert(0,str(self.P.MY_CNTR))
        except: 
            print('\ncntr=',cntr)
            error_trap('GUI->UPDATE COUNTER - Unable to convert counter')
            
        return True

    # Read his call from the entry box
    def get_call(self):
        call = self.call.get()
        call2 = call.replace(' ','').upper()

        # Insert large caps call into entry box - this causes the insertion
        # point to change which is a problem if we're correcting the call on
        # the fly so it is disabled for now.  Can probably try to remember
        # the insertion point and make adjustment but this is more than I
        # really care to do right now.
        if call!=call2 and False:
            self.call.delete(0, END)
            self.call.insert(0,call2)
            self.call.configure(fg='black')
            
        return call2

    # Read his name from the entry box
    def get_name(self):
        txt=self.name.get().strip()
        if txt=='' and not self.contest:
            txt='OM'
        return txt.upper()

    # Read incoming RST from the entry box
    def get_rst_in(self):
        txt=self.rstin.get().strip()
        if txt=='':
            txt='5NN'
        return txt.upper()

    # Read outgoing RST from the entry box
    def get_rst_out(self):
        txt=self.rstout.get().strip()
        if txt=='':
            txt='5NN'
        elif len(txt)==2:
            txt=txt+'N'
        elif len(txt)==1:
            txt=txt+'NN'
        return txt.upper()

    # Read exchange data from the entry box
    def get_exchange(self):
        return self.exch.get().upper()

    # Read qth from entry box
    def get_qth(self):
        return self.qth.get().upper()

    # Read notes from entry box
    def get_notes(self):
        return self.notes.get()

    # Read category from entry box
    def get_cat(self):
        return self.cat.get().upper()

    # Read serial in from entry box
    def get_serial(self):
        return self.serial_box.get().upper()

    # Read serial out from entry box
    def get_counter(self):
        return self.counter.get().upper()

    # Read prec from entry box
    def get_prec(self):
        return self.prec.get().upper()

    # Read call2 from entry box
    def get_call2(self):
        return self.call2.get().upper()

    # Read check from entry box
    def get_check(self):
        return self.check.get().upper()

    # Get a clue
    def get_hint(self,call=None):
        print('GUI - GET_HINT: call=',call)
        if call==None:
            call = self.call.get()

        #if len(call)>=3 and not self.P.NO_HINTS:
        if len(call)>=3:
            self.dx_station = Station(call)
            #pprint(vars(self.dx_station))
            h = hint.master(self.P,call,self.dx_station,VERBOSITY=1)
            if not h:
                h,junk = Oh_Canada(self.dx_station)
        else:
            h=None
            self.dx_station = None
            
        self.hint.delete(0, END)
        #print('\tGET_HINT: h=',h)
        if h:
            self.hint.insert(0,h)
        self.P.KEYING.set_info_box()
        self.last_hint=h
        
        return h


    # Show scoring summary in big text box
    def ScoringSummary(self):
        if self.P.SCORING:
            self.P.SCORING.otf_summary()
        else:
            self.txt.insert(END, 'Ooops - no scoring summary!', ('highlight'))
            self.txt.see(END)
    
    # Save program state
    def SaveState(self):
        spots  = []
        frqsA  = []
        frqsB  = []
        modes  = []
        splits = []
        ants   = []
        flds   = []
        for spot in self.spots:
            spots.append( spot['Button']['text'] )
            frqsA.append( spot['FreqA'] )
            frqsB.append( spot['FreqB'] )
            modes.append( spot['Mode'] )
            ants.append( spot['Ant'] )
            splits.append( spot['Split'] )
            flds.append( spot['Fields'] )
        now = datetime.utcnow().replace(tzinfo=UTC)

        STATE={'now'        : now.strftime('%Y-%m-%d %H:%M:%S'), 
               'bookmark'   : self.PaddlingWin.bookmark,
               'serial'     : self.P.MY_CNTR,
               'contest_id' : self.P.CONTEST_ID,
               'spots'      : spots,
               'freqsA'     : frqsA,
               'freqsB'     : frqsB,
               'modes'      : modes,
               'splits'     : splits,
               'ants'       : ants,
               'fields'     : flds }
        print('STATE=',STATE)
        with open(self.P.WORK_DIR+'state.json', "w") as outfile:
            json.dump(STATE, outfile)
        if False:
            with open('keyer.log', "a") as outfile2:
                outfile2.write('Save State:    \t'+now.strftime('%Y-%m-%d %H:%M:%S')+'\t')
                json.dump(STATE, outfile2)
                outfile2.write('\n')

        self.P.DIRTY=False
        print('SaveState: cntr=',self.P.MY_CNTR)

    # Clear store/recall butons
    def ClearState(self):

        for i in range(len(self.spots)):
            self.spots[i]['Button']['text'] = '--'
            self.spots[i]['FreqA']  = None
            self.spots[i]['FreqB']  = None
            self.spots[i]['Mode']   = None
            self.spots[i]['Split']  = None
            self.spots[i]['Ant']    = None
            self.spots[i]['Fields'] = None
            self.P.DIRTY = True
                
    
    # Restore program state
    def RestoreState(self):
        try:
            fname=self.P.WORK_DIR+'state.json'
            print('\nRESTORE STATE: fname=',fname)
            with open(fname) as json_data_file:
                STATE = json.load(json_data_file)
            print('\tSTATE=',STATE)
            now = datetime.utcnow().replace(tzinfo=UTC)
            if False:
                with open('keyer.log', "a") as outfile3:
                    outfile3.write('Restore State: \t'+now.strftime('%Y-%m-%d %H:%M:%S')+'\t')
                    json.dump(STATE, outfile3)
                    outfile3.write('\n')
        except: 
            error_trap('GUI->RESTORE STATE: Problem restoring state')
            return
            
        now        = datetime.utcnow().replace(tzinfo=UTC)

        time_stamp = datetime.strptime( STATE['now'] , '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC)
        
        age = (now - time_stamp).total_seconds()/60  
        print('RESTORE STATE: now=',now,'\ntime_stamp=',time_stamp,
              '\nAge=',age,' mins.')

        # Restore the book mark
        self.PaddlingWin.bookmark = max( STATE['bookmark'] ,0 )
        print('RESTORE STATE: Bookmark=',self.PaddlingWin.bookmark)

        # If we're in a contest, restore the serial counter
        if self.P.CONTEST_ID==STATE['contest_id'] and age<self.P.MAX_AGE:
            self.P.MY_CNTR = STATE['serial']
        else:
            self.P.MY_CNTR = 1
        print('RESTORE STATE: Counter=',self.P.MY_CNTR)
        self.counter.delete(0, END)
        self.counter.insert(0,str(self.P.MY_CNTR))

        # If not too much time has elapsed, restore the spots 
        if age<30:
            spots = STATE['spots']
            if len(spots)>12*self.P.NUM_ROWS:
                spots=spots[:12*self.P.NUM_ROWS]
            print('RestoreState: Spots=',spots)
            frqsA  = STATE['freqsA']
            frqsB  = STATE['freqsB']
            modes  = STATE['modes']
            splits = STATE['splits']
            ants   = STATE['ants']
            flds   = STATE['fields']
            for i in range(len(spots)):
                print(i,len(spots),len(self.spots))
                self.spots[i]['Button']['text'] = spots[i]
                self.spots[i]['FreqA']  = frqsA[i]
                self.spots[i]['FreqB']  = frqsB[i]
                self.spots[i]['Mode']   = modes[i]
                self.spots[i]['Split']  = splits[i]
                self.spots[i]['Ant']    = ants[i]
                self.spots[i]['Fields'] = flds[i]
                
        self.P.DIRTY=False
        #sys.exit(0)

    # Exit
    def Quit(self):
        
        # Make sure we really want to do this and didn't just fat-finger something
        msg='Really Quit?'
        lab="pyKeyer"
        if sys.version_info[0]==3:
            result=tkinter.messagebox.askyesno(lab,msg)
        else:
            result=tkMessageBox.askyesno(lab,msg)
        if not result:
            print('Quit Cancelled.')
            return
        
        self.SaveState()
        self.fp_adif.close()
        self.fp_txt.close()
        if self.fp_snip:
            self.fp_snip.close()
        self.P.SHUTDOWN=True

        # Immediately stop sending
        try:
            self.keyer.abort()     
            if not self.q.empty():
                self.q.get(False)
                self.q.task_done()
        except:
            error_trap('QUIT - Problem stopping keyer')

        # Loop through all the threads and close (join) them
        #print "Waiting for WatchDog to quit..."
        #while self.P.WATCHDOG:
        #    time.sleep(.1)
        print("Waiting for threads to quit...")
        show_threads()
        if self.P.Timer:
            print('\tWaiting for Timer thread to quit ...')
            self.P.Timer.cancel()
        #threads = enumerate()
        #for th in threads:
        for th in self.P.threads:
            name = th.getName()
            if name=='Sidetone Osc' and not self.P.SideTone.started:
                continue
            print('\tWaiting for thread to quit -',name,' ...')
            self.P.Stopper.set()
            th.join()
            print('\t... Thread quit -',th.getName())

        # Make sure root window is clobbered
        try:
            print('Destroying root window ...')
            self.root.destroy()
        except:
            error_trap('QUIT - Failed to destroying root window ... Giving up!')
            sys.exit(0)
            
        show_threads()
        print("\nThat's all folks!\n")
        self.Done=True
        sys.exit(0)

    # Log the qso
    def log_qso(self):

        # Check for minimal fields
        call=self.get_call().upper()
        valid = len(call)>=3
        name=self.get_name().upper()
        qth =self.get_qth().upper()
        notes =self.get_notes()
        print('LOG_QSO:',call,name,qth,flush=True)
        qso2 = {}
        srx=0

        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        
        if self.contest:
            rst='5NN'
            #exch,valid,self.exch_out,qso2 = self.P.KEYING.logging()
            x = self.P.KEYING.logging()
            exch = x[0]
            valid = x[1]
            self.exch_out = x[2]
            if len(x)>=4:
                qso2 = x[3]
            if len(x)>=5:
                srx = x[4]
        else:
            rstin =self.get_rst_in().upper()
            exch=str(rstin)+','+ name
            print('name=',name)
            print('rst=',rstin)
            print('exch=',exch)
            qso2={}

        # Make sure a satellite is selected if needed - MOVE THIS TO LOGGING() IN SATS.PY
        satellite = self.get_satellite()
        if self.P.contest_name=='SATELLITES' and satellite=='None':
            errmsg='Need to Select a Satellite!'
            valid=False
        else:
            errmsg='Missing one or more fields!'
            
        if valid:
            print('LOG IT! contest=',self.contest,self.P.contest_name,\
                  '\nP.sock=',self.P.sock,self.P.sock.rig_type2)
            #print(self.sock.run_macro(-1))
        
            # Get time stamp, freq, mode, etc.
            now       = datetime.utcnow().replace(tzinfo=UTC)
            if not self.start_time:
                self.start_time = now
            date_off  = now.strftime('%Y%m%d')
            time_off  = now.strftime('%H%M%S')

            if self.P.contest_name=='Ragchew' or True:
                print('LOG IT! TIME_ON B=',self.time_on.strftime('%H%M%S'))
                if self.time_on:
                    date_on = self.time_on.strftime('%Y%m%d')
                    time_on = self.time_on.strftime('%H%M%S')
                else:
                    print('\nFile &&&&&&&&&&&&&&&&&&&&&&&&&&&& EXPECTED TIME ON &&&&&&&&&&&&&&&&&&')
                    date_on = date_off
                    time_on = time_off
            else:
                date_on = date_off
                time_on = time_off
                
            # Read the radio 
            freq_kHz = 1e-3*self.sock.get_freq()
            freq     = int( freq_kHz )
            if self.P.DIGI:
                mode     = self.P.sock_xml.get_mode()
            else:
                mode     = self.P.sock.get_mode()
            if mode in ['CW-U']:
                mode='CW'
            elif mode=='FMN':
                mode='FM'
            elif mode=='AMN':
                mode='AM'
            elif mode in ['PKTUSB','PSK-U','DATA-U']:
                mode='RTTY'
            band = freq2band(1e-3*freq_kHz)
            if band in ['None','MW']:
                print("*** WARNING - Can't determine band - no rig connection?")
                band='160m'

            # For satellites, read vfo B also  - MOVE THIS TO LOGGING() IN SATS.PY
            if self.P.contest_name=='SATELLITES':
                freq_kHz_rx = freq_kHz
                band_rx     = band

                freq_kHz    = 1e-3*self.sock.get_freq(VFO='B')
                freq        = int( freq_kHz )
                band        = freq2band(1e-3*freq_kHz)

            else:
                freq_kHz_rx = freq_kHz
                band_rx     = band

            # Do some error checking                    
            if mode!=self.sock.mode and self.sock.connection!='NONE' and False:
                txt='##### WARNING ##### Mode mismatch in gui - radio:'+mode+'\tWoof:'+self.sock.mode
                print(txt)                          # Print error msg to terminal ...
                self.txt.insert(END, txt+'\n')      # ... and put it in the console text window
                self.txt.see(END)

            if band!=self.sock.band and self.sock.connection!='NONE' and False:
                txt='##### WARNING ##### Band mismatch in gui - radio:'+band+'\tWoof:'+self.sock.band
                print(txt)
                self.txt.insert(END, txt+'\n')
                self.txt.see(END)
            
            # Construct QSO record
            qso = dict( list(zip(['QSO_DATE_ON','TIME_ON',
                                  'QSO_DATE_OFF','TIME_OFF',
                                  'CALL','FREQ','BAND','MODE', 
                                  'SRX_STRING','STX_STRING',
                                  'NAME','QTH','SRX','STX',
                                  'SAT_NAME','FREQ_RX','BAND_RX','NOTES',
                                  'RUNNING','MY_RIG','CONTEST_ID'],
                                 [date_on,time_on,date_off,time_off,
                                  call,
                                  str( round(1e-3*freq_kHz,4) ),band,mode, 
                                  exch,self.exch_out,name,qth,
                                  str(srx),str(self.cntr),
                                  satellite,
                                  str( round(1e-3*freq_kHz_rx,4)),
                                  band_rx,notes,str(int(self.RUNNING)),
                                  self.P.sock.rig_type2,
                                  self.P.CONTEST_ID] )))
            if self.MY_CALL != self.P.SETTINGS['MY_OPERATOR']:
                qso['OPERATOR'] = self.P.SETTINGS['MY_OPERATOR']
            qso.update(qso2)

            # Send spot to bandmap - only do if S&P
            if self.P.udp_server:
                # LOG:CALL:BAND:FREQ:MODE:DATE_OFF:TIME_OFF:QTH
                msg  = 'LOG:'+call+':'+band+':'+str(freq_kHz)+':'+mode+':'+date_off+':'+time_off+':'+qth
                print('LOG QSO: Broadcasting spot:',msg)
                self.P.udp_server.Broadcast(msg)
                
                if not self.RUNNING:
                    msg  = 'SPOT:'+call+':'+str(freq_kHz)+':'+mode
                    print('LOG QSO: Broadcasting spot:',msg)
                    self.P.udp_server.Broadcast(msg)

            # Log contact using FLLOG
            if self.P.sock_log.connection=='FLLOG':
                print('GUI->LOG_QSO: via FLLOG ...')
                self.P.sock_log.Add_QSO(qso)

            # Log contact using FLDIGI - dont use if in RTTY mode - This path needs work!!!
            elif self.sock.connection=='FLDIGI' and self.sock.fldigi_active and not self.P.PRACTICE_MODE and False:
                print('GUI->LOG_QSO: FLDIGI ...')
                fields = {'Call':call,'Name':name,'RST_out':rstout,'QTH':qth,'Exchange':exch}
                if not self.P.WF_ONLY:
                    self.sock.set_log_fields(fields)
                self.sock.set_mode('CW')
                self.sock.run_macro(47)

            # Reset clarifier
            ClarReset(self,self.P.RX_Clar_On)

            # Make sure practice exec gets what it needs
            if self.P.PRACTICE_MODE:
                print('GUI->LOG_QSO - PRACTICE MODE: Waiting for handshake ... EVT2=',\
                      self.keyer.evt2.isSet(),\
                      '\nIf you want to log an actual contact, exit PRACTICE_MODE and try again',flush=True)
                while self.keyer.evt2.isSet():
                    print('\tEVT2:',self.keyer.evt2.isSet(), '\tSTOP:',self.keyer.stop,flush=True )
                    time.sleep(1)
                print('LOG_QSO: Got handshake ...',\
                      '\tevt2 set=',self.keyer.evt2.isSet(),'\tstop=',self.keyer.stop,flush=True )

            # Clear fields
            self.prefill=False
            self.call.delete(0,END)
            self.prev_call=''
            self.time_on=None
            self.call.focus_set()
            self.call.configure(bg=self.default_color,fg='black')
            self.name.delete(0,END)
            self.qth.delete(0,END)
            self.notes.delete(0,END)
            self.hint.delete(0,END)
            self.scp.delete(0,END)
            self.serial_box.delete(0,END)
            self.prec.delete(0,END)
            self.call2.delete(0,END)
            self.check.delete(0,END)
            self.exch.delete(0,END)
            self.cat.delete(0,END)
            self.info.delete(0,END)
            self.qsl_rcvd.set(0)
            
            self.rstin.delete(0,END)
            self.rstout.delete(0,END)
            if self.P.contest_name=='SATELLITES':
                self.rstin.insert(0,'5')
                self.rstout.insert(0,'5nn')
                self.exch.configure(background=self.default_color)
                self.qth.configure(background=self.default_color)
            else:
                self.rstin.insert(0,'5Nn')
                self.rstout.insert(0,'5NN')

            # Save out to simple log file also
            freq_MHz=1e-3*freq
            self.fp_txt.write('%s,%s,%s,%s,%s,%s,"%s","%s","%s"\n' % \
                              (date_off,time_off,call,str(freq_MHz),
                               band,mode,exch,self.exch_out,satellite) )
            self.fp_txt.write('----------\n')
            self.fp_txt.flush()

            self.log_book.append(qso)
            #print self.log_book

            # Update ADIF file
            if not self.P.PRACTICE_MODE:
                qso2 =  {key.upper(): val for key, val in list(qso.items())}
                print("GUI: ADIF writing QSO=",qso2)
                write_adif_record(self.fp_adif,qso2,self.P)
                print(' ')
                self.prev_qso=qso2

                try:
                    #txt=qso2['CALL']+' '+qso2['FREQ']+' '+qso2['SRX_STRING']
                    txt=' '+call+' '+str(freq)+' '+exch+'\n'
                    self.txt.insert(END, txt, ('highlight'))
                    self.txt.see(END)
                except: 
                    error_trap('GUI->LOG QSO: ERROR writing logged info to big text box')
                    
            self.P.gui.status_bar.setText('Contact with '+call+' Logged!!!')
                    
            # On the fly scoring
            try:
                if self.P.SCORING:
                    self.P.SCORING.otf_scoring(qso)
                else:
                    stack_trace('OOOOPs - no scoring routine')
            except: 
                error_trap('GUI->LOG QSO: Failed to update score :-(',1)

            # Clobber any presets that have this call
            idx=0
            for spot in self.spots:
                #print idx,spot
                try:
                    if spot['Fields']:
                        call2 = spot['Fields']['Call'].upper()
                    else:
                        idx+=1
                        continue
                except:
                    error_trap('LOG QSO - ????????????')
                    continue
                if call==call2:
                    print('\n@@@ Clobbering spot @@@@ idx=',idx,'\nspot=',spot)
                    self.Spots_cb(idx,-1)
                idx+=1

        else:
            # There was a problem
            self.status_bar.setText('*** Missing one or more fields ***')
            print('*** Missing one or more fields ***',self.contest)
            print('Call=',call)
            if self.contest:
                print('Exch=',exch)
            if False:
                tkinter.messagebox.showerror("pyKeyer - Logging",errmsg)

        # Save these for error checking in practice mode
        #print '%%% Saving exchange ***'
        self.keyer.call = call
        self.keyer.name = name
        self.keyer.qth  = qth
        #keyer.exch = exch
        #print '%%% Exchange saved ***'

        # Increment QSO counter
        self.P.MY_CNTR += 1
        self.counter.delete(0, END)
        self.counter.insert(0,str(self.P.MY_CNTR))
        self.P.DIRTY = True

        # Make sure we're on VFO A
        if self.P.SO2V:
            try:
                self.Select_VFO('A')
            except: 
                error_trap('GUI->LOG QSO: Unable to set VFO to A',1)

        # Save the current state
        self.SaveState()        

        # Get ready for next QSO
        self.pounced=False
        self.searching=False
        next_widget=self.call
        self.default_object=self.call  
        self.call.focus_set()
        
    # Routine to force the focus
    def force_focus(self,next_widget):
        print('FORCE FOCUS: Focus young man!',next_widget)
        next_widget.focus_set()      
        next_widget.focus_force()
        self.root.update_idletasks()

    # Callback when an entry box takes focus - clears selection so we don't overwrite
    def take_focus(self,W):
        
        widget = self.root.nametowidget(W)             # Convert widget name to instance 
        #print('TAKE FOCUS: Focus young man!',widget)
        widget.focus_set()
        if widget==self.call and False:
            widget.selection_clear()                   # ... and clear the selection
        return True

    # Sets selection of most of the boxes
    def Set_Selection(self,widget):
        
        print('Set Selection ...',widget)
        if widget!=self.call:
            widget.select_range(0,"end")
            widget.event_generate("<<Copy>>")
        self.default_object=widget

    # Watchdog-like routine to update gui
    # Things changing the gui MUST be called from the gui thread to avoid memory leaks!!!!
    def Updater(self):
        P=self.P
        if P.WPM2!=P.WPM:
            self.WPM_TXT.set(str(P.WPM2))
            P.WPM=P.WPM2
        self.rate_lab.config(text=P.RATE_TXT)
        self.rig.UpdateRigGui()
        self.root.after(1000,self.Updater)
        
    # Routine to compute QSO Rate
    # We should NOT have long calcs like this in the gui thread!
    # Perhaps this is why it is sometimes sluggish.
    def qso_rate(self):
        if self.start_time:
            now = datetime.utcnow().replace(tzinfo=UTC)
            dt0 = (now - self.start_time).total_seconds()+1 # In seconds

            nqsos = 0
            dt = min(10*60.,dt0)         # Ten minutes
            for qso in self.log_book:
                #print(qso["QSO_DATE_OFF"]+" "+qso["TIME_OFF"])
                #print('QSO_RATE:',qso)
                try:
                    if "QSO_DATE_OFF" in qso:
                        doff = qso["QSO_DATE_OFF"]
                    else:
                        doff = qso["QSO_DATE"]
                    if "TIME_OFF" in qso:
                        toff = qso["TIME_OFF"]
                    else:
                        toff = qso["TIME_ON"]
                    date_off = datetime.strptime( doff+" "+toff, \
                                "%Y%m%d %H%M%S") \
                                .replace(tzinfo=UTC)
                except: 
                    error_trap('GUI->QSO RATE: Problem with qso=')
                    print('qso',qso)
                    continue
                
                age = (now - date_off).total_seconds() # In seconds
                if age<=dt:
                    nqsos+=1
                    
            rate = float(nqsos) / dt * 3600.
            nqsos2 = len(self.log_book)-self.nqsos_start
            rate2 = float(nqsos2) / dt0 * 3600.
            self.P.RATE_TXT='QSOs: {:3d} /hr : {:3d} /hr : {:d}'.format( int(rate+0.5),int(rate2+0.5),nqsos2 )

            
    # Routine to check & flag dupes
    def dup_check(self,call):
        VERBOSITY=1
        
        #print('DUP_CHECK: call=',call,'\tmax age=',self.P.MAX_AGE)
        self.time_on = datetime.utcnow().replace(tzinfo=UTC)
        print('DUP_CHECK: call=',call,'\tTIME_ON set to',self.time_on.strftime('%H%M%S'))

        # Look for dupes
        self.match1=False                # True if there is matching call
        self.match2=False                # True if the match is within the last 48 hours on current band and mode
        last_exch=''
        self.last_qso=None
        now = datetime.utcnow().replace(tzinfo=UTC)
        freq = self.sock.get_freq()
        if self.P.DIGI:
            mode = self.P.sock_xml.get_mode()
        else:
            mode = self.sock.get_mode()
        band = freq2band(1e-6*freq)
            
        if self.P.sock_log.connection=='FLLOG' and True:
            self.match1 = self.P.sock_log.Dupe_Check(call)
            print('DUP_CHECK: match1=',self.match1)
            if self.match1:
                self.match2 = self.P.sock_log.Dupe_Check(call,mode,self.P.MAX_AGE,freq)
                print('DUP_CHECK: match2=',self.match2)
                qso = self.P.sock_log.Get_Last_QSO(call)
                print('DUP_CHECK: last qso=',qso)
                if 'SRX_STRING' in qso :
                    last_exch = qso['SRX_STRING']
                if False:    # Shouldnt need to do this but there was a bug in how fllog handled local & utc times
                    date_off = datetime.strptime( qso["QSO_DATE_OFF"] +" "+ qso["TIME_OFF"] , "%Y%m%d %H%M%S") \
                                       .replace(tzinfo=UTC)
                    age = (now - date_off).total_seconds() # In seconds
                    self.match2 = self.match2 or (age<self.P.MAX_AGE*60 and qso['BAND']==band and qso['MODE']==mode)
                    #print('DUP_CHECK: match 1 & 2:',self.match1,self.match2)

        else:
            
            for qso in self.log_book:
                if 'CALL' not in qso:
                    print('DUP_CHECK: - File - CALL not in QSO!!!\nqso=',qso,'\tcall=',call)
                elif qso['CALL']==call:
                    self.match1 = True
                    self.last_qso=qso
                    date_off = datetime.strptime( qso["QSO_DATE_OFF"]+" "+qso["TIME_OFF"] , "%Y%m%d %H%M%S") \
                                       .replace(tzinfo=UTC)
                    age = (now - date_off).total_seconds() # In seconds

                    # There are some contests that are "special"
                    if self.P.contest_name=='SATELLITES':
                        
                        # Need to add more logic to this going forward
                        print('DUP_CHECK: Worked before on sats ',call)
                        self.match2 = True
                        
                    elif self.P.contest_name in ['ARRL-VHF','CQ-VHF']:
                        
                        # Group phone mode together
                        #PHONE_MODES=['FM','SSB','USB','LSB']
                        #match3 = qso['MODE']==mode or (qso['MODE'] in PHONE_MODES and mode in PHONE_MODES)

                        # Actually, can only work each station once per band, regardless of mode
                        match3 = qso['BAND']==band 

                        # Rovers can be reworked if they are in a different grid square
                        if '/R' in call:
                            qth = self.P.gui.get_qth().upper()
                            if 'QTH' in qso:
                                qth2=qso['QTH']
                            else:
                                qth2=''
                            match4 = qth==qth2
                        else:
                            match4 = True

                        # Combine it all together
                        self.match2 = self.match2 or (age<self.P.MAX_AGE*60 and match3 and match4)
                        
                    elif self.P.contest_name=='ARRL-SS-CW':
                        
                        # Can only work each station once regardless of band
                        self.match2 = self.match2 or (age<self.P.MAX_AGE*60 and qso['MODE']==mode)
                        
                    else:
                        
                        # Most of the time, we can work each station on each band and mode
                        self.match2 = self.match2 or (age<self.P.MAX_AGE*60 and qso['BAND']==band and qso['MODE']==mode)
                        if VERBOSITY>0:
                            print('DUP_CHECK: match2=',self.match2,
                                  '\tage=',age,self.P.MAX_AGE,'\tband=',band,
                                  '\tmode=',mode)
                        
                    if self.P.contest_name=='SATELLITES':
                        try:
                            qth=qso['QTH']
                        except:
                            qth=''
                        try:
                            name=qso['NAME']
                        except:
                            name=''
                        try:
                            b4=qso['QSL_RCVD']
                        except:
                            b4='N'
                        last_exch = qth+','+name+','+b4
                    else:
                        last_exch = qso['SRX_STRING']

        # If there was a dupe, change color of call entry box & show last exchange
        if self.match1:
            print('DUP_CHECK: Call match:',call)
            if self.match2:
                self.call.configure(bg="coral")
            else:
                self.call.configure(bg="lemon chiffon")
                
            if self.match2 and len( self.exch.get() )==0:
                self.prefill=True
                a=last_exch.split(',')
                print('DUPE_CHECK: last_exch - a=',a)
                self.P.KEYING.dupe(a)

                """
                elif self.P.SPRINT:
                    #self.serial_box.delete(0,END)
                    if len(a)>=2:
                        self.name.delete(0,END)
                        self.name.insert(0,a[1])
                        if len(a)>=3:
                            self.qth.delete(0,END)
                            self.qth.insert(0,a[2])
                else:
                    self.exch.delete(0,END)
                    self.exch.insert(0,last_exch)
                """
                
        else:

            # Clear pre-filled fields - this is still problematic so it is disabled for now
            # It wipes out valid exchange if we change call - ugh!
            # The flag self.prefill seems to be a problem - need to work on this?
            if (self.prev_call != call and False) or (self.prefill and False):
                self.name.delete(0,END)
                self.qth.delete(0,END)
                self.cat.delete(0,END)
                self.serial_box.delete(0,END)
                self.hint.delete(0, END)
                self.exch.delete(0,END)

            # Check fldigi logger
            if self.sock.connection=='FLDIGI' and not self.P.PRACTICE_MODE and False:
                fields  = self.sock.get_log_fields()
                print("DUP_CHECK: Log Fields =",fields)
                if len( self.name.get() )==0 and len(fields['Name'])>0:
                    self.name.delete(0, END)
                    self.name.insert(0,fields['Name'])
                if len( self.qth.get() )==0 and len(fields['QTH'])>0:
                    self.qth.delete(0, END)
                    self.qth.insert(0,fields['QTH'])

            # Use default color
            self.call.configure(background=self.default_color)

############################################################################################
    
    # Handlers for double-click in the SCP box
    # This first one responds immediately to the double click.
    # However, the selection is not made until after this callback
    # returns so we just schedule to actual handler here.    
    def SCP_Selection(self,evt):
        print('SCP SELECTION: evt num=',evt.num)
        self.scp.after(20,lambda: self.SCP_Selection2(evt) )

    # This is the actual handler that copies the selected callsign into
    # the call sign box
    def SCP_Selection2(self,evt):
        print('SCP SELECTION2: Select Present=',evt.widget.select_present(),'\tAuto Fill=',self.P.AUTOFILL)
        if evt.widget.select_present():
            if True:
                # Copy selected call into call entry box
                call = evt.widget.selection_get()
                print('Call:',call)
                if ' ' in call:
                    print('SCP_SELECTION - Whoops!',call)
                    call=''
                self.call.delete(0, END)
                self.call.insert(0,call)
            else:
                # Another way to do this
                evt.widget.event_generate("<<Copy>>")
                self.call.delete(0, END)
                self.call.event_generate("<<Paste>>")
            
            next_widget=self.call
            self.default_object=self.call  
            self.call.focus_set()

            if self.P.AUTOFILL:
                print('SCP SELECTION2: Autofilling...')
                self.get_hint(call)
                self.P.KEYING.insert_hint()
            
        else:
            print('Nothing to do')

############################################################################################
    
    # Test routine
    def event_trap(self,event):
        print('EVENT_TRAP: evt=',event,event.type)

        
    # Callback when mouse enters a widget
    def Hoover(self,event):

        DEBUG=0
                
        # Which window are we in?
        widget = event.widget
        obj = self.Master(widget)
        window=obj.root

        # Check if some widget has the focus
        try:
            focus=window.focus_get()
            #parent_name = focus.winfo_parent()
            #parent = focus._nametowidget(parent_name)
            obj2 = self.Master(focus)
            if obj2:
                parent=obj2.root
            else:
                parent=None
        except:
            error_trap('HOVER: Probably outside keyer app?')
            parent=None

        if DEBUG:
            print('HOVER: Mouse entering ',obj.WIN_NAME,'- widget',widget,
                  '\twindow=',window,'\tFocus=',obj.last_focus)

        # Make sure root window has the focus
        # If not, raise it to the top and make it our focus
        #if parent!=window:
        if not obj.OnTop:
            obj.OnTop=True
            if DEBUG:
                print('HOVER: Raising ',obj.WIN_NAME,
                      '===============================================')
            #self.P.gui.root.call('wm', 'attributes', '.', '-topmost', True)
            #window.attributes('-topmost', True)
            ##self.P.gui.root.grab_set()
            ##self.P.gui.root.grab_set_global()

            if self.P.AGGRESSIVE:
                # This seems to be the only reliable way to do this!
                title=window.title()
                if self.P.PLATFORM=='Linux':
                    #os.system('wmctrl -a pyKeyer')
                    os.system('wmctrl -a "'+title+'"')
            elif False:
                # This sort of worked but not quite
                # Keep all of this around bx we'll need
                #   something differnet for windoz
                window.grab_set()
                window.grab_set_global()
                window.lift()
                window.focus_force()
                window.focus()
                window.focus_set()

            # A bunch of failed attempts - KEEP!!
            #window.transient()
            #window.attributes('-topmost', False)
            #window.grab_release()
            #window.after_idle(self.P.gui.root.grab_release)
            #    window.after_idle(window.attributes,'-topmost',False)
            #window.after_idle(self.P.gui.root.call, 'wm', 'attributes', '.', '-topmost', False)
            focus=None

        if not focus:

            # No focus - return focus to last widget that had it
            # If none, set focus to call entry box
            if obj.last_focus:
                widget=obj.last_focus
            else:
                try:
                    widget=obj.default_object
                except:
                    return
            print('HOVER: No Focus -',obj.WIN_NAME,'- Setting focus to',widget)
            try:
                widget.focus_force()
            except:
                error_trap('GUI->HOVER ERROR')

    def Master(self,widget):

        #print('MASTER: widget=',widget)
        #print('MASTER: roots=',self.P.gui.root,self.P.gui.PaddlingWin.win)

        master=widget
        while master!=None:
            #print('MASTER: master=',master,master==self.root,master==self.PaddlingWin.win)
            if master==self.P.gui.root:
                #print('MASTER: In Main Root Window ...')
                return self.P.gui
            elif master==self.P.gui.PaddlingWin.win:
                #print('MASTER: In Paddling Window ...')
                return self.P.gui.PaddlingWin
            else:
                master=master.master
            
    # Callback when mouse leaves a widget
    def Leave(self,event):

        DEBUG=0

        # Which window are we in?
        widget = event.widget
        obj = self.Master(widget)
        window=obj.root
        
        # Keep track of widget that last had the focus
        obj.last_focus = window.focus_get()
        if DEBUG:
            print('LEAVE: Mouse leaving ',obj.WIN_NAME,'- widget',widget,
                  '\twindow=',window,'\tFocus=',obj.last_focus)

        if widget==window:
            if DEBUG:
                print('LEAVE: Letting go ...--------------------------------------------------------------')
            #window.attributes('-topmost', False)
            #window.after_idle(self.P.gui.root.call, 'wm', 'attributes', '.', '-topmost', False)
            window.grab_release()
            obj.OnTop=False
            
        
############################################################################################

    # Callback when a key is pressed
    def key_press(self,event,id=None):

        P = self.P
        DF=100
        key   = event.keysym
        num   = event.keysym_num
        ch    = event.char
        state = event.state

        # Modfiers
        shift     = ((state & 0x0001) != 0)
        #caps_lock = state & 0x0002
        control   = (state & 0x0004) != 0

        # Well this is screwy - there seems to be a difference between
        # linux and windoz
        if P.PLATFORM=='Linux':
            #alt       = (state & 0x0088) != 0     # Both left and right ALTs
            alt       = (state & 0x0008) != 0 
            #num_lock  = state & 0x0010
        elif P.PLATFORM=='Windows':
            alt       = (state & 0x20000) != 0 
            #num_lock  = state & 0x008
            
        #mouse1 = state & 0x0100
        #mouse2 = state & 0x0200
        #mouse3 = state & 0x0400

        #obj = self.Master(event.widget)
        #window=obj.root

        print("Key Press:",key,'\tState:',hex(state),shift,control,alt)
        #print('\tself=',self,'\tobj=',obj,'\twindow=',window)

        # This should never happen
        if len(key)==0:
            print('Key Press: I dont know what I am doing here!')
            return

        # Check for special keys
        ret_val = "break"              # Assume its one of the special keys
        if key=='Shift_L':
            
            # Left Shift 
            self.last_shift_key='L'
                
        elif key=='Shift_R':
            
            # Right Shift 
            self.last_shift_key='R'

        elif key=='Up':
            
            # Up arrow
            print('RIT Up',DF)
            self.sock.rit(1,DF)
                
        elif key=='Down':
            
            # Down arrow
            print('RIT Down',-DF)
            self.sock.rit(1,-DF)

        elif key=='KP_Decimal':
            
            # "." on keypad
            print('Reset clarifier')
            ClarReset(self,self.P.RX_Clar_On)

        elif key in ['Prior','KP_Add','plus']:
            
            # Page up or big +
            print('WPM Up')
            if P.SENDING_PRACTICE:
                self.PaddlingWin.SetWpm(+1)
            else:
                self.set_wpm(dWPM=+WPM_STEP)
            #return('break')
                
        elif key in ['Next','KP_Subtract','minus']:
            
            # Page down or big -
            print('WPM Down')
            if P.SENDING_PRACTICE:
                self.PaddlingWin.SetWpm(-1)
            else:
                self.set_wpm(dWPM=-WPM_STEP)
            #return('break')

        elif key in ['slash','question'] and (alt or control):
            
            # Quick way to send '?'
            self.q.put('?')
            self.P.OP_STATE |= 8
            print('KEY PRESS - op_state=',self.P.OP_STATE)

        elif key in ['r','R'] and (alt or control):
            
            # Send 'RR'
            self.Send_CW_Text('RR')

        elif key in ['p','P'] and (alt or control):

            # Screen capture
            self.PrtScrn()
    
        elif key in ['t','T'] and (alt or control):

            # Query rig
            self.QueryRig()
    
        elif key in ['b','B'] and (alt or control):

            # Update bandmap spots
            self.UpdateBandmap()
    
        elif key=='Left':
            
            # Left arrow - move down the bandmap
            if alt or control:
                # Get a suggested run freq from the bandmap
                self.SuggestRunFreq('DOWN')
            elif shift:
                # Tune to next spot
                self.NextSpotFreq('DOWN')
            else:
                return
                
        elif key=='Right':
            
            # Right arrow - move up the bandmap
            if alt or control:
                # Get a suggested run freq from the bandmap
                self.SuggestRunFreq('UP')
            elif shift:
                # Tune to next spot
                self.NextSpotFreq('UP')
            else:
                return
                
        elif key=='Home' and False:
            
            # DON'T REMAP THE HOME KEY - ITS USEFUL FOR EDITing
            # Insert Does this now if we are in the Exch Window
            # Reverse call sign lookup
            #if key=='Home' or (key=='r' and (alt or control)):
            self.P.KEYING.reverse_call_lookup()

        elif key=='space' and (shift or alt or control):

            # Toggle PTT
            self.Toggle_PTT()
    
        elif (key=='Delete' and False) or (key in ['w','W'] and (alt or control)):

            # Erase entire entry box
            print('DELETE - CLEAR BOX ...')
            if event.widget==self.txt or event.widget==self.txt2:
                #print('Text Box ...')
                event.widget.delete(1.0,END)     # Clear the entry box
            else:
                print('Not in Text Box ...')
                event.widget.delete(0,END)     # Clear the entry box
                if event.widget==self.call:
                    self.call.configure(background=self.default_color)

            # Wipe all fields Alt-w
            if key in ['w','W'] and (alt or control):
                #print('ALT-W')
                self.call.delete(0, END)
                self.call.configure(background=self.default_color)
                self.call2.delete(0, END)
                self.cat.delete(0, END)
                self.rstin.delete(0, END)
                self.rstout.delete(0, END)
                if self.P.contest_name=='SATELLITES':
                    self.rstin.insert(0,'5')
                    self.rstout.insert(0,'5nn')
                else:
                    self.rstin.insert(0,'5nn')
                    self.rstout.insert(0,'5NN')
                self.exch.delete(0, END)
                self.exch.configure(background=self.default_color)
                self.name.delete(0, END)
                self.qth.delete(0, END)
                self.qth.configure(background=self.default_color)
                self.serial_box.delete(0, END)
                self.prec.delete(0, END)
                self.hint.delete(0, END)
                self.check.delete(0, END)
                self.qsl_rcvd.set(0)
                self.scp.delete(0, END)

                next_widget=self.call
                self.default_object=self.call  
                self.call.focus_set()
                self.default_object=self.call

        elif key=='Insert' or (key in ['i','I'] and (alt or control)):

            if event.widget==self.call:
                self.auto_fill(self.call.get(),'@@@')
                #self.auto_fill(None,'@@@')
            elif event.widget==self.exch:
                # Copy hints to fields or reverse call look-up
                val=self.P.KEYING.reverse_call_lookup()
                if val==None or len(val)==0:
                    self.P.KEYING.insert_hint()
            else:
                self.P.KEYING.insert_hint()

        elif key=='Escape':
            
            # Immediately stop sending
            print('Escape!')
            self.fp_txt.write('ESCAPE!!!!!\n')
            self.fp_txt.flush()
            
            self.keyer.abort()     
            if not self.q.empty():
                self.q.get(False)
                self.q.task_done()

        elif key=='Tab' and not shift:
            
            # Move to next entry box
            print('Tab: shift=',shift)
            if event.widget==self.txt and self.P.SHOW_TEXT_BOX2:
                self.txt2.focus_set()
            elif event.widget==self.txt2 and self.P.SHOW_TEXT_BOX2:
                self.txt.focus_set()
            elif event.widget==self.txt or event.widget==self.txt2:
                print('Text box',key,len(key),key=='Tab')
                self.call.focus_set()
                self.default_object=self.call
            else:
                event.widget.selection_clear() 
                widget=self.P.KEYING.next_event(key,event)
                self.Set_Selection(widget)

        # Windows is screwy the way it handles the left-tab
        elif key=='ISO_Left_Tab' or (key=='Tab' and shift):
            
            # Move to prior entry box
            key='ISO_Left_Tab'
            print('Left Tab: shift=',shift)
            if event.widget==self.txt:
                self.txt2.focus_set()
            elif event.widget==self.txt2:
                self.txt.focus_set()
            elif event.widget==self.txt or event.widget==self.txt2:
                self.call.focus_set()
                self.default_object=self.call
            else:
                event.widget.selection_clear() 
                widget=self.P.KEYING.next_event(key,event)
                self.Set_Selection(widget)

        elif (key=='Return' or key=='KP_Enter') and \
             event.widget!=self.txt and event.widget!=self.txt2:

            # Send appropriate macro and move on to next box
            event.widget.selection_clear() 
            widget=self.P.KEYING.next_event(key,event)
            self.Set_Selection(widget)
        
        elif key[0]=='F':
            
            # Function keys
            idx=int( key[1:] ) - 1
            
            #print('Last shift=',self.last_shift_key)
            if not alt and not control:
                # Send a macro
                if not shift:
                    self.Send_Macro(idx)
                else:
                    self.Send_Macro(idx+12)
            elif control:
                # Quick Store 
                self.Spots_cb(idx,1)
            elif alt:
                # Quick Recall
                self.Spots_cb(idx,2)
            else:
                print('Modified Function Key not supported',shift,control,alt)
                
        else:
            if (len(key)>1 or alt or control) and True:
                print('Key Press: Un-used key combo',key,alt,control)
                
            # The entry change hasn't happened yet so just schedule updater
            self.root.after(20,lambda: self.process_entry_boxes(event))
            #window.after(20,lambda: self.process_entry_boxes(event))
            return
        
        return "break"


    # Function to take care of SCPs and Auto Fills
    def auto_fill(self,call,key):
        print('GUI-AUTO_FILL: call=',call,'\tkey=',key,
              '\tUSE SCP=',self.P.USE_SCP,'\tAUTOFILL=',self.P.AUTOFILL)

        # Check against SCP database
        if self.P.USE_SCP:
            scps,scps2 = self.P.KEYING.SCP.match(call,VERBOSITY=0)
            self.scp.delete(0, END)
            self.scp.insert(0, scps)

            # Auto-complete
            if key=='@@@' or (len(key)==1 and self.P.AUTO_COMPLETE):
                KEY=key.upper()
                if KEY=='@@@' or (KEY>='A' and KEY<='Z' and len(scps2)==1):
                    call2=scps[0]
                    print('AUTO FILL: call=',call,'\tcall2=',call2,'\tkey=',key)
                    self.call.delete(0, END)
                    self.call.insert(0,call2)
                    self.call.select_range( len(call), END )
                    call=call2

            # Highlight callsign if we have an exact match
            if len(scps)>0 and call==scps[0]:
                self.call.configure(fg='red')
            else:
                self.call.configure(fg='black')

        # Take care of hints
        self.get_hint(call)
        if key=='@@@' or self.P.AUTOFILL:
            self.P.KEYING.insert_hint()
            if self.sock.rig_type=='FLDIGI' and self.sock.fldigi_active and not self.P.DIGI:
                print('AUTOFILL: Setting FLDIGI log fields ...')
                self.Read_Log_Fields()
    
    # Callback when something changes in an entry box
    def process_entry_boxes(self,event):

        key   = event.keysym
        ch    = event.char
                            
        # Next widget is by default the current widget
        next_widget=event.widget
    
        # Are we in a text window?
        if event.widget==self.txt:
            
            # Lower text window - Don't send control chars
            if len(ch)>0:
                if ord(ch)==13:
                    if self.P.Immediate_TX:
                        self.q.put(' ')
                    else:
                        self.q.put(self.text_buff+' ')
                        self.text_buff=''
                elif ord(ch)>=32 and ord(ch)<127:
                    if self.P.Immediate_TX:
                        self.q.put(ch)
                    else:
                        self.text_buff+=ch

        elif event.widget==self.txt2:
            # Upper text window which is just used for typing in rx text
            #print('UPPER TEXT WINDOW')
            pass

        # Update callsign info 
        elif event.widget==self.call:

            # Call has changed ...
            call=self.get_call().upper()
            self.time_on = datetime.utcnow().replace(tzinfo=UTC)
            print('Updated Call=',call,'\tTIME_ON D=',self.time_on.strftime('%H%M%S'))

            # Update fldigi and check for dupes
            #if not self.P.WF_ONLY:
            #self.sock.set_log_fields({'Call':call}) 
            self.dup_check(call)
            self.info.delete(0,END)
            self.auto_fill(call,key)

            # Save call so we can keep track of changes
            self.prev_call = call
            
        elif event.widget==self.name:

            name=self.get_name().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'Name':name})

        elif event.widget==self.qth:
            
            qth=self.get_qth().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'QTH':qth})

            if len(qth)>0 and self.P.contest_name=='CQP':
                self.P.KEYING.qth_hints()
            elif self.P.contest_name=='SATELLITES':
                if len(qth)==4 and not qth in self.P.grids:
                    self.qth.configure(background="lime")
                else:
                    self.qth.configure(background=self.default_color)
                    
        elif event.widget==self.cat:

            print('PROCESS ENTRY BOXES - CAT ...')
            cat=self.get_cat().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'Cat':cat})

        elif event.widget==self.rstin:

            rst=self.get_rst_in().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'RST_in':rst})

        elif event.widget==self.rstout:

            rst=self.get_rst_out().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'RST_out':rst})

        elif event.widget==self.exch:

            exch=self.get_exchange().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'Exchange':exch})

            if self.P.contest_name=='SATELLITES':
                if len(exch)==4 and not exch in self.P.grids:
                    self.exch.configure(background="lime")
                else:
                    self.exch.configure(background=self.default_color)
                    
        elif event.widget==self.counter:

            print('^^^^^^^^^^^ Counter window',self.P.MY_CNTR)
            self.update_counter()
            
        elif event.widget==self.serial_box:

            serial=self.get_serial().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'Serial_out':serial})
                
        elif event.widget==self.prec:

            prec=self.get_prec().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'Prec':prec})

        elif event.widget==self.call2:

            call2=self.get_call2().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'Call2':call2})

        elif event.widget==self.check:

            check=self.get_check().upper()
            if not self.P.WF_ONLY:
                self.sock.set_log_fields({'Check':check})
            
    
############################################################################################

    # Callback to force rig into CW mode
    def Set_Rig_Mode(self,evt):
        mode = self.MODE.get()
        print('SET RIG MODE: mode=',mode)
        self.sock.set_mode(mode)
        if self.P.udp_server:
            self.P.udp_server.Broadcast('MODE:'+mode)
        if mode=='CW':
            self.sock.set_filter(['Narrow','200 Hz'],mode)
            self.sock.set_breakin(1)
            self.sock.set_monitor_gain(10)
            self.FilterWidths=[50,200]
        elif mode in ['FM','RTTY','BPSK31']:
            self.sock.set_filter(['Wide','2400 Hz'],mode)
            if mode=='RTTY':
                self.P.sock_xml.squelch_mode(0)
                self.sock.set_monitor_gain(35)
            self.FilterWidths=[500,2000]
        elif mode in ['USB','LSB']:
            self.FilterWidths=[1800,2400]
                
        """
        else:
            self.sock.set_filter(['Narrow','1800 Hz'],'CW')
        """

        

    # Callback for practice with computer text
    def PracticeCB(self):
        self.P.PRACTICE_MODE = not self.P.PRACTICE_MODE
        P.practice.enable = P.practice.enable and self.P.PRACTICE_MODE

    # Callback to toggle echoing of nano IO text
    def Toggle_Nano_Echo(self):
        print('TOGGLE NANO ECHO:',self.P.NANO_ECHO)
        self.P.NANO_ECHO = not self.P.NANO_ECHO 
        
    # Callback to toggle auto filling of hints info
    def AutoFillCB(self):
        self.P.AUTOFILL = not self.P.AUTOFILL

    # Callback to toggle paddling window
    def Toggle_Paddling_Win(self):
        self.P.SENDING_PRACTICE = not self.P.SENDING_PRACTICE
        if self.P.SENDING_PRACTICE:
            self.PaddlingWin.show()
        else:
            self.PaddlingWin.hide()

    # Callback to toggle speed adjustment
    def AdjustSpeedCB(self):
        self.P.ADJUST_SPEED = not self.P.ADJUST_SPEED

    # Callback to toggle lock speed adjustment
    def LockSpeedCB(self):
        self.P.LOCK_SPEED = not self.P.LOCK_SPEED

    # Callback to turn sidetone on and off
    def SideToneCB(self):
        print("Toggling Sidetone ...")
        self.P.SIDETONE = not self.P.SIDETONE
        if self.P.SIDETONE:
            if self.P.SideTone.started:
                self.P.SideTone.resume()
            else:
                self.P.SideTone.start()
        else:
            if self.P.SideTone.started and self.P.SideTone.enabled:
                self.P.SideTone.pause()

    # Callback to turn capture on and off
    def CaptureCB(self):
        print("Toggling Audio Capture ...")
        self.P.CAPTURE = not self.P.CAPTURE
        if self.P.CAPTURE:
            if self.P.capture.started:
                self.P.capture.resume()
            else:
                self.P.capture.start()
        else:
            if self.P.capture.started and self.P.capture.enabled:
                self.P.capture.pause()

    # Callback to turn Farnsworth Spacing on and off
    def FarnsworthCB(self):
        print("Toggling Farnsworth Spacing ...")
        self.P.FARNSWORTH = not self.P.FARNSWORTH
        if self.P.FARNSWORTH:
            self.SB3.grid()
        else:
            self.SB3.grid_remove()

    # Callback to turn split text window on & off
    def SplitTextCB(self):
        print("Toggling Split Text ...")
        self.P.SHOW_TEXT_BOX2 = not self.P.SHOW_TEXT_BOX2
        self.show_hide_txt2()
               
    # Callback to show/hide hints entry box
    def ShowHintsCB(self):
        self.P.NO_HINTS = not self.ShowHints.get()
        print("Toggling Show/Hide Hints ...",self.P.NO_HINTS)
        if not self.P.NO_HINTS:
            self.hint_lab.grid()
            self.hint.grid()
        else:
            self.hint_lab.grid_remove()
            self.hint.grid_remove()
               
    # Callback to show/hide Super Check Partialentry box
    def ShowScpCB(self):
        self.P.USE_SCP = self.ShowSCP.get()
        print("Toggling Show/Hide SCP ...",self.P.USE_SCP)
        if self.P.USE_SCP:
            self.scp_lab.grid()
            self.scp.grid()
            self.hint_lab.grid_remove()
            self.hint.grid_remove()
            self.notes_lab.grid_remove()
            self.notes.grid_remove()
        else:
            self.scp_lab.grid_remove()
            self.scp.grid_remove()

    # Callback to enable/disable auto-complete
    def AutoCompleteCB(self):
        self.P.AUTO_COMPLETE = not self.P.AUTO_COMPLETE

    # Callback to put rig into CW mode
    def SetCWModeCB(self):
        self.sock.set_mode('CW')

    # Callback to activate callsign that is in the on deck circle
    def BatterUp(self):

        print('Swing batter swing ...')
        call  = self.OnDeckCircle.get()
        call2 = self.get_call()
        if call!=call2:
            self.Clear_Log_Fields()
            self.call.insert(0,call)
            self.dup_check(call)
            if self.contest:
                self.get_hint(call)
                if self.P.AUTOFILL:
                    self.P.KEYING.insert_hint()
        if self.P.SO2V:
            self.sock.set_vfo(rx='A',tx='B')
                    
    # Callback to request updated list of spots on the bandmap
    def UpdateBandmap(self):
        print('UPDATE BANDMAP - Requesting updated spot list ...')
        if True:
            self.P.udp_server.Broadcast('SpotList:Refresh')
        else:
            spot_list_query(self.P,None)

    # Callback to request a suggested run freq from the bandmap
    def SuggestRunFreq(self,opt):
        frq = round( 1e-3*self.sock.get_freq() , 2)
        print('SUGGEST RUN FREQ - Requesting suggested run freq ...',opt,frq)
        msg='RunFreq:'+opt+':'+str(frq)
        self.P.udp_server.Broadcast(msg)
        print('msg=',msg)

    # Callback to request freq of next spot from the bandmap
    def NextSpotFreq(self,opt):
        frq = round( 1e-3*self.sock.get_freq() , 2)
        print('NEXT SPOT FREQ - Requesting spot freq ...',opt,frq)
        msg='SpotFreq:'+opt+':'+str(frq)
        self.P.udp_server.Broadcast(msg)
        print('msg=',msg)

    # Callback to capture the screen 
    def PrtScrn(self):

        s=time.strftime("_%Y%m%d_%H%M%S", time.gmtime())      # UTC
        fname='/tmp/ScreenShot_'+s+'.png'
        print('Taking screen snapshot ...',fname)
        screenshot = pyautogui.screenshot()
        screenshot.save(fname)
        print('Done.')
            
    # Callback to query rig
    def QueryRig(self):

        rig=self.sock.rig_type2
        print('Rig query...',rig)
        frqA  = 1e-3*self.sock.get_freq(VFO='A') 
        mode  = self.sock.get_mode()
        txt = '{:s} \t {:d} \t {:s}\n'.format(rig,int(frqA),mode)
        self.P.gui.txt.insert(END, txt, ('highlight'))
        self.P.gui.txt.see(END)
        print('Done.')
            
    # Callback to update settings changes
    def RefreshSettings(self):

        print('Refreshing Settings ...')
        self.MY_CALL = self.P.SETTINGS['MY_CALL']
        self.set_macros()
        print('... Done.')
            
############################################################################################
    
    # Function to create menu bar
    def create_menu_bar(self):
        print('Creating Menubar ...')

        toolbar = Frame(self.root, bd=1, relief=RAISED)
        toolbar.grid(row=0,columnspan=self.ncols,column=0,sticky=E+W)
        
        menubar = Menubutton(toolbar,text='File',relief='flat')
        menubar.pack(side=LEFT, padx=2, pady=2)
            
        Menu1 = Menu(menubar, tearoff=0)
        Menu1.add_command(label="Settings ...", command=self.SettingsWin.show)
        Menu1.add_command(label="Rig Control ...", command=self.RigCtrlCB)
        Menu1.add_command(label="Keyer Control ...", command=self.KeyerCtrlCB)
        Menu1.add_command(label="Paddling ...", command=self.Toggle_Paddling_Win)
        Menu1.add_command(label="Clear Stores ...", command=self.ClearState)
        Menu1.add_command(label="Scoring Summary ...", command=self.ScoringSummary)
        Menu1.add_separator()
        
        Menu1.add_checkbutton(
            label="Set Rig CW",
            underline=0,
            command=self.SetCWModeCB
        )
        
        self.Capturing = BooleanVar(value=self.P.CAPTURE)
        Menu1.add_checkbutton(
            label="Capture Audio",
            underline=0,
            variable=self.Capturing,
            command=self.CaptureCB
        )
        
        self.Farnsworth = BooleanVar(value=self.P.FARNSWORTH)
        Menu1.add_checkbutton(
            label="Farnsworth",
            underline=0,
            variable=self.Farnsworth,
            command=self.FarnsworthCB
        )
        
        self.Tuning = BooleanVar(value=False)
        Menu1.add_checkbutton(
            label="Tune",
            underline=0,
            variable=self.Tuning,
            command=self.Tune
        )
        
        self.Practice = BooleanVar(value=self.P.PRACTICE_MODE)
        Menu1.add_checkbutton(
            label="Practice Mode",
            underline=0,
            variable=self.Practice,
            command=self.PracticeCB
        )

        self.AutoFill = BooleanVar(value=self.P.AUTOFILL)
        Menu1.add_checkbutton(
            label="Auto Fill",
            underline=0,
            variable=self.AutoFill,
            command=self.AutoFillCB
        )
        
        self.ShowHints = BooleanVar(value=not self.P.NO_HINTS)
        Menu1.add_checkbutton(
            label="Show Hints",
            underline=0,
            variable=self.ShowHints,
            command=self.ShowHintsCB
        )
        
        self.ShowSCP = BooleanVar(value=self.P.USE_SCP)
        Menu1.add_checkbutton(
            label="Show SCP",
            underline=0,
            variable=self.ShowSCP,
            command=self.ShowScpCB
        )
        
        self.AutoComplete = BooleanVar(value=self.P.AUTO_COMPLETE)
        Menu1.add_checkbutton(
            label="Auto Complete",
            underline=0,
            variable=self.AutoComplete,
            command=self.AutoCompleteCB
        )
        
        self.SideTone = BooleanVar(value=self.P.SIDETONE)
        Menu1.add_checkbutton(
            label="SideTone",
            underline=0,
            variable=self.SideTone,
            command=self.SideToneCB
        )
        
        self.AdjustSpeed = BooleanVar(value=self.P.ADJUST_SPEED)
        Menu1.add_checkbutton(
            label="Adjust Speed",
            underline=0,
            variable=self.AdjustSpeed,
            command=self.AdjustSpeedCB
        )
        
        self.LockSpeed = BooleanVar(value=self.P.LOCK_SPEED)
        Menu1.add_checkbutton(
            label="Lock Speed",
            underline=0,
            variable=self.LockSpeed,
            command=self.LockSpeedCB
        )
        
        self.NanoEcho = BooleanVar(value=self.P.NANO_ECHO)
        Menu1.add_checkbutton(
            label="Nano Echo",
            underline=0,
            variable=self.NanoEcho,
            command=self.Toggle_Nano_Echo
        )
        
        self.SplitTxt = BooleanVar(value=self.P.SHOW_TEXT_BOX2)
        Menu1.add_checkbutton(
            label="Split Text Win",
            underline=0,
            variable=self.SplitTxt,
            command=self.SplitTextCB
        )
        
        self.ImmediateTX = BooleanVar(value=self.P.Immediate_TX)
        Menu1.add_checkbutton(
            label="Immediate TX",
            underline=0,
            variable=self.ImmediateTX,
            command=self.Toggle_Immediate_TX
        )
        
        Menu1.add_checkbutton(
            label="Clear All Spots ...",
            underline=0,
            command=self.Clear_All_Spots
        )
        
        Menu1.add_separator()
        Menu1.add_command(label="Exit", command=self.Quit)

        menubar.menu =  Menu1
        menubar["menu"]= menubar.menu  

        self.OnDeckCircle=Entry(toolbar,text='On Deck Circle')
        self.OnDeckCircle.pack(side=LEFT, padx=2, pady=2)
        self.OnDeckCircle.bind("<Key>", self.key_press )
        Button(toolbar,text="Batter Up",command=self.BatterUp) \
            .pack(side=LEFT, padx=2, pady=2)
        
        Button(toolbar,text="VFO A",command=lambda: self.Select_VFO('A')) \
            .pack(side=LEFT, padx=2, pady=2)
        Button(toolbar,text="VFO B",command=lambda: self.Select_VFO('B')) \
            .pack(side=LEFT, padx=2, pady=2)
        
        self.VFOSplitBtn = Button(toolbar,
                                 text="Split",
                                 command=self.Toggle_VFOSplit)
        self.VFOSplitBtn.pack(side=LEFT, padx=2, pady=2)
        
        Button(toolbar,text="A->B",command=lambda: SetVFO(self,'A->B')) \
            .pack(side=LEFT, padx=2, pady=2)
        Button(toolbar,text="Swap",command=lambda: SetVFO(self,'A<->B')) \
            .pack(side=LEFT, padx=2, pady=2)
        #Button(toolbar,text="TXW",command=lambda: SetVFO(self,'TXW')) \
            #    .pack(side=LEFT, padx=2, pady=2)
            
        self.So2vBtn = Button(toolbar,text="SO2V", command=self.Toggle_SO2V)
        self.So2vBtn.pack(side=LEFT, padx=2, pady=2)
        
        self.DXSplitBtn = Button(toolbar,
                                 text="DX Split",
                                 command=self.Toggle_DXSplit)
        self.DXSplitBtn.pack(side=LEFT, padx=2, pady=2)
        
        if self.P.SPECIAL:
            self.FilterWidths=[2500,3000]
        elif self.P.DIGI:
            self.FilterWidths=[500,2000]
        else:
            self.FilterWidths=[50,200]
        self.FilterColors=['red','green']
        self.FilterReliefs=['sunken','raised']
        self.FilterWidthBtn = Button(toolbar,
                                     command=self.Toggle_FilterWidth)
        self.FilterWidthBtn.pack(side=LEFT, padx=2, pady=2)
        self.Toggle_FilterWidth(1)

        # Spin box to control paddle keying speed (WPM)
        SB2=Spinbox(toolbar,
                    from_=cw_keyer.MIN_WPM, 
                    to=50,       
                    textvariable=self.PaddlingWin.WPM_TXT, 
                    bg='white', justify='center',            
                    command=lambda j=0: self.PaddlingWin.SetWpm(0))
        SB2.pack(side=RIGHT, padx=2, pady=2)
        SB2.bind("<Key>", self.key_press )
        Label(toolbar, text='Paddles:').pack(side=RIGHT, padx=2, pady=2)
        
        # Screen capture
        #Button(toolbar,text="PrtScrn",command=self.PrtScrn) \
            #    .pack(side=RIGHT, padx=2, pady=2)

        # A place to put some info
        self.info = Entry(toolbar,font=self.font1,selectbackground='lightgreen')
        self.info.pack(side=RIGHT, padx=2, pady=2)
        self.info.bind("<Key>", self.key_press )

