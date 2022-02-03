############################################################################################
#
# gui.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
if sys.version_info[0]==3:
    from tkinter import *
    import tkinter.font
    import tkinter.messagebox
else:
    from Tkinter import *
    import tkFont
    import tkMessageBox
import csv
import pytz
from datetime import datetime, date, tzinfo
import time
import cw_keyer
import hint
from dx.spot_processing import Station
from pprint import pprint
import webbrowser
from rig_io.socket_io import ClarReset
from rig_control_tk import *
from rotor_control_tk import *
from ToolTip import *
import pickle
from fileio import *
from threading import enumerate
from audio_io import WaveRecorder

from cwt import *
from cwopen import *
from sst import *
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
from ragchew import *
from dx_qso import *
from qrz import *

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

        print("\nCreating GUI ...")
        self.root = Tk()
        # width_size x height_size + x_position + y_position
        self.root.geometry('1200x400+250+250')
        
        self.Done=False
        self.contest = False
        self.P = P
        self.P.LAST_MSG = -1
        self.P.root = self.root
        self.keyer=P.keyer;
        self.start_time = datetime.utcnow().replace(tzinfo=UTC)
        self.nqsos_start = 0
        self.sock = self.P.sock

        print(P.sock.rig_type2)
        if P.sock.rig_type2 and P.sock.rig_type2!='None':
            rig=' - '+P.sock.rig_type2
            if P.sock2 and P.sock2.rig_type2 and P.sock2.rig_type2!='None':
                rig+=' + '+P.sock2.rig_type2
        else:
            rig=''
        self.root.title("pyKeyer by AA2IL"+rig)
        self.tuning = False
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)

        self.MACRO_TXT = StringVar()
        self.macro_label = ''

        self.last_call=''
        self.last_shift_key=''
        self.last_hint=''

        self.q = P.q
        self.exch_out=''
        self.ndigits=3
        self.prev_call=''
        self.prefill=False
        self.cntr=0

        # Open simple log file & read its contents
        MY_CALL = P.SETTINGS['MY_CALL']
        fname = MY_CALL.replace('/','_')+".LOG"
        print('Opening log file',fname,'...')
        try:
            self.fp_log = open(fname,"r+")
        except:
            self.fp_log = open(fname,"w")

        if False:
            with self.fp_log as csvfile:
                csvReader = csv.reader(csvfile, dialect='excel')
                #hdrs = next(csvReader)
                #print('hdrs=',hdrs)
                for row in csvReader:
                    print(row)
                    # do stuff with rows...
            sys.exit(0)
        
        csvReader = csv.reader(self.fp_log, dialect='excel')
        try:
            hdrs = list(map(cleanup, next(csvReader)))
            print('hdrs=',hdrs)
        except:
            self.fp_log.write('QSO_DATE_OFF,TIME_OFF,CALL,FREQ,BAND,MODE,SRX_STRING,STX_STRING,SAT_NAME\n')
            self.fp_log.flush()

        self.log_book = []

        try:
            for line in csvReader:
                #print 'line=',line
                qso = dict(list(zip(hdrs, line)))
                #print 'qso=',qso
                if P.USE_LOG_HISTORY:
                    self.log_book.append(qso)
                elif P.USE_MASTER:
                    call=qso['CALL']
                    if not call in P.calls:
                        #print('Call not in Master list:',call,'\t- Adding it')
                        self.log_book.append(qso)
                        P.calls.append(call)
        except:
            pass

        # Read adif log also
        if P.LOG_FILE==None:
            P.LOG_FILE = MY_CALL.replace('/','_')+".adif"
        if P.USE_ADIF_HISTORY:
            print('fname_adif=',P.LOG_FILE)
            qsos = parse_adif(P.LOG_FILE,upper_case=True,verbosity=0)
            for qso in qsos:
                self.log_book.append(qso)

        self.nqsos_start = len(self.log_book)
        print('There are',len(self.log_book),'QSOS in the log book')
        #sys.exit(0)

        # Keep an ADIF copy of the log as well
        self.fp_adif = open(P.LOG_FILE,"a+")
        print("GUI: ADIF file name=", self.fp_adif) 

        # Also save all sent text to a file
        self.fp_txt = open(MY_CALL.replace('/','_')+".TXT","a+")

        # Add menu bar
        ncols=12
        row=0
        self.create_menu_bar()
        
        # Set up basic logging entry boxes
        #row+=1
        if sys.version_info[0]==3:
            font1 = tkinter.font.Font(family="monospace",size=12,weight="bold")
            font2 = tkinter.font.Font(family="monospace",size=28,weight="bold")
        else:
            font1 = tkFont.Font(family="monospace",size=12,weight="bold")
            font2 = tkFont.Font(family="monospace",size=28,weight="bold")
        self.call_lab = Label(self.root, text="Call",font=font1)
        self.call_lab.grid(row=row,columnspan=4,column=0,sticky=E+W)
        if False:
            self.call_sv = StringVar()
            self.call = Entry(self.root,font=font2, textvariable=self.call_sv,
                              validate="all", validatecommand=self.check_call)
        elif False:
            # valid percent substitutions (from the Tk entry man page)
            # note: you only have to register the ones you need;
            #
            # %d = Type of action (1=insert, 0=delete, -1 for others)
            # %i = index of char string to be inserted/deleted, or -1
            # %P = value of the entry if the edit is allowed
            # %s = value of entry prior to editing
            # %S = the text string being inserted or deleted, if any
            # %v = the type of validation that is currently set
            # %V = the type of validation that triggered the callback
            #      (key, focusin, focusout, forced)
            # %W = the tk name of the widget
            vcmd = (self.root.register(self.check_call),'%P','%V','%W')
            self.call = Entry(self.root,font=font2,validate="key", validatecommand=vcmd )
        else:
            self.call = Entry(self.root,font=font2 )
            
        self.call.grid(row=row+1,rowspan=2,column=0,columnspan=4,sticky=E+W)
        self.call.focus_set()            # Grab focus
        self.default_color = self.call.cget("background")

        # For normal operating, these will be visible
        vcmd = (self.root.register(self.take_focus),'%W')
        self.name_lab = Label(self.root, text="Name",font=font1)
        self.name_lab.grid(row=row,columnspan=4,column=4,sticky=E+W)
        self.name = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.name.grid(row=row+1,rowspan=2,column=4,columnspan=4,sticky=E+W)

        self.rstin_lab = Label(self.root, text="RST in",font=font1)
        self.rstin_lab.grid(row=row,columnspan=1,column=8,sticky=E+W)
        self.rstin = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.rstin.grid(row=row+1,rowspan=2,column=8,columnspan=1)

        self.rstout_lab = Label(self.root, text="RST out",font=font1)
        self.rstout_lab.grid(row=row,columnspan=1,column=9,sticky=E+W)
        self.rstout = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.rstout.grid(row=row+1,rowspan=2,column=9,columnspan=1)
        if self.P.contest_name=='SATELLITES':
            self.rstin.insert(0,'5')
            self.rstout.insert(0,'5nn')
        else:
            self.rstin.insert(0,'5NN')
            self.rstout.insert(0,'5NN')

        # For contests, some subset of these will be visible instead
        self.exch_lab = Label(self.root, text="Exchange",font=font1)
        self.exch_lab.grid(row=row,columnspan=7,column=4,sticky=E+W)
        self.exch = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.exch.grid(row=row+1,rowspan=2,column=4,columnspan=6,sticky=E+W)

        self.qth_lab = Label(self.root, text="QTH",font=font1)
        self.qth_lab.grid(row=row,columnspan=3,column=8,sticky=E+W)
        self.qth = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.qth.grid(row=row+1,rowspan=2,column=8,columnspan=2)

        self.serial_lab = Label(self.root, text="Serial",font=font1)
        self.serial_lab.grid(row=row,columnspan=1,column=4,sticky=E+W)
        self.serial = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.serial.grid(row=row+1,rowspan=2,column=4,columnspan=1)

        self.prec_lab = Label(self.root, text="Prec",font=font1)
        self.prec_lab.grid(row=row,columnspan=1,column=5,sticky=E+W)
        self.prec = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.prec.grid(row=row+1,rowspan=2,column=5,columnspan=1)

        self.cat_lab = Label(self.root, text="Category",font=font1)
        self.cat_lab.grid(row=row,columnspan=1,column=5,sticky=E+W)
        self.cat = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.cat.grid(row=row+1,rowspan=2,column=5,columnspan=1)

        self.call2_lab = Label(self.root, text="Call",font=font1)
        self.call2_lab.grid(row=row,columnspan=1,column=6,sticky=E+W)
        self.call2 = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.call2.grid(row=row+1,rowspan=2,column=6,columnspan=1)

        self.check_lab = Label(self.root, text="Check",font=font1)
        self.check_lab.grid(row=row,columnspan=1,column=7,sticky=E+W)
        self.check = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.check.grid(row=row+1,rowspan=2,column=7,columnspan=1)
        
        self.hint_lab = Label(self.root, text="Hint",font=font1)
        self.hint_lab.grid(row=row,columnspan=1,column=8,sticky=E+W)
        self.hint = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd,fg='blue')
        self.hint.grid(row=row+1,rowspan=2,column=8,columnspan=1)

        # Checkbox to indicate if we've received QSL
        self.qsl_rcvd=tk.IntVar()
        self.qsl_rcvd.set(0)
        self.qsl=tk.Checkbutton(self.root,text='QSL Rcvd', \
                                variable=self.qsl_rcvd)
        self.qsl.grid(row=row+1,column=9,columnspan=1)
        tip = ToolTip(self.qsl, ' QSL has been received ')
        
        # Buttons to access FLDIGI logger
        if False:
            btn = Button(self.root, text='Get',command=self.Set_Log_Fields, \
                         takefocus=0 )
            btn.grid(row=row+1,column=ncols-2)
            tip = ToolTip(btn, ' Get FLDIGI Logger Fields ' )

            btn = Button(self.root, text='Put',command=self.Read_Log_Fields,\
                         takefocus=0 ) 
            btn.grid(row=row+1,column=ncols-1)
            tip = ToolTip(btn, ' Set FLDIGI Logger Fields ' )

            btn = Button(self.root, text='Wipe',command=self.Clear_Log_Fields,\
                         takefocus=0 ) 
            btn.grid(row=row+2,column=ncols-2)
            tip = ToolTip(btn, ' Clear FLDIGI Logger Fields ' )
        
        # Set up text entry box with a scroll bar
        row+=3
        Grid.rowconfigure(self.root, row, weight=1)             # Allows resizing
        for i in range(12):
            Grid.columnconfigure(self.root, i, weight=1,uniform='twelve')
        
        self.txt = Text(self.root, height=10, width=80, bg='white')
        self.S = Scrollbar(self.root)
        self.txt.grid(row=row,column=0,columnspan=ncols,stick=N+S+E+W)
        self.S.grid(row=row,column=ncols,sticky=N+S)
        self.S.config(command=self.txt.yview)
        self.txt.config(yscrollcommand=self.S.set)

        # Bind a callback to be called whenever a key is pressed
        self.root.bind("<Key>", self.key_press )
        #self.root.bind("all", self.key_press )
        self.txt.bind("<Tab>", self.key_press )

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

        # Set up a spin box to control select macro set
        Label(self.root, text='Macros:').grid(row=row,column=col,sticky=E+W)
        SB = OptionMenu(self.root,self.MACRO_TXT,*self.P.CONTEST_LIST, \
             command=self.set_macros).grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        col += 3

        # Set up a spin box to control keying speed (WPM)
        self.WPM_TXT = StringVar()
        Label(self.root, text='Speed:').grid(row=row,column=col,sticky=E+W)
        SB = Spinbox(self.root, from_=cw_keyer.MIN_WPM, to=cw_keyer.MAX_WPM,\
                     textvariable=self.WPM_TXT,\
                     command=lambda j=0: self.set_wpm(0))\
                     .grid(row=row,column=col+1,columnspan=1,sticky=E+W)
        self.WPM_TXT.set(str(self.keyer.WPM))
        self.set_wpm(0)

        btn = Button(self.root, text='+'+str(WPM_STEP)+' WPM', command=lambda j=WPM_STEP: self.set_wpm(j) )
        btn.grid(row=row+1,column=col,sticky=E+W)
        tip = ToolTip(btn,' Increase Speed ')
        
        btn = Button(self.root, text='-'+str(WPM_STEP)+' WPM', command=lambda j=-WPM_STEP: self.set_wpm(j) )
        btn.grid(row=row+1,column=col+1,sticky=E+W)
        tip = ToolTip(btn,' Decrease Speed ')

        # Entry box to allow changing my counter
        col += 2
        self.counter_lab=Label(self.root, text='Serial:')
        self.counter_lab.grid(row=row,column=col,sticky=E+W)
        self.counter = Entry(self.root,font=font2,validate='focusin',validatecommand=self.update_counter)
        self.counter.grid(row=row,rowspan=1,column=col+1,columnspan=1,sticky=E+W)
        self.counter.delete(0, END)
        self.counter.insert(0,str(self.P.MY_CNTR))
        self.counter_lab.grid_remove()
        self.counter.grid_remove()

        # Radio button group to support SO2R
        col += 2
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

        # Other buttons - any buttons we need to modify, we need to grab handle to them
        # before we try to pack them.  Otherwise, all we get is the results of the packing

        # Capture
        if False:
            col += 2
            self.CaptureBtn = Button(self.root, text='Capture',command=self.CaptureAudioCB ) 
            self.CaptureBtn.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.CaptureBtn, ' Capture Rig Audio ' )
            self.CaptureAudioCB(-1)
        
        # Practice button
        if False:
            col += 1
            self.PracticeBtn = Button(self.root, text='Practice', command=self.PracticeCB )
            self.PracticeBtn.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.PracticeBtn,' Toggle Practice Mode ')
            P.PRACTICE_MODE = not P.PRACTICE_MODE
            self.PracticeCB()

        # Button to turn SIDETONE on and off
        if False:
            col += 1
            self.SideToneBtn = Button(self.root, text='SideTone', command=self.SideToneCB )
            self.SideToneBtn.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.SideToneBtn,' Toggle Sidetone Osc ')
            P.SIDETONE = not P.SIDETONE
            self.SideToneCB()

        # TUNE button
        if False:
            col += 1
            self.TuneBtn = Button(self.root, text='Tune',bg='yellow',\
                                  highlightbackground= 'yellow', \
                                  command=self.Tune )
            self.TuneBtn.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.TuneBtn,' Key Radio to Ant Tuning ')

        # QRZ button
        col += 1
        btn = Button(self.root, text='QRZ ?',command=self.Call_LookUp,\
                     takefocus=0 ) 
        btn.grid(row=row,column=ncols-1)
        tip = ToolTip(btn, ' Query QRZ.com ' )
        
        # Set up a spin box to allow satellite logging
        row += 1
        col  = 0
        self.SAT_TXT = StringVar()
        Label(self.root, text='Satellites:').grid(row=row,column=col,sticky=E+W)
        sat_list=sorted( SATELLITE_LIST )
        SB = OptionMenu(self.root,self.SAT_TXT,*sat_list, \
                        command=self.set_satellite).grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        self.set_satellite('None')

        """
        # Don't need these anymore

        # Reset button
        col = 8
        btn = Button(self.root, text='Reset',command=self.Reset_Defaults ) 
        btn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(btn, ' Reset to Default Params ' )

        # Save state button
        col += 1
        btn = Button(self.root, text='Save State',command=self.SaveState ) 
        btn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(btn, ' Save State ' )

        # Restore state button
        col += 1
        btn = Button(self.root, text='Restore State',command=self.RestoreState ) 
        btn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(btn, ' Restore State ' )

        # Quit button
        col += 1
        btn = Button(self.root, text='Quit',command=self.Quit ) 
        btn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(btn, ' Exit Program ' )

        """
            
        # Reset clarifier
        ClarReset(self)

        # Some other info
        #row += 1
        #col=0
        col=8
        self.rate_lab = Label(self.root, text="QSO Rate:",font=font1)
        self.rate_lab.grid(row=row,columnspan=4,column=col,sticky=W)
        #Label(self.root, text="--- Spots ---",font=font1) \
        #    .grid(row=row,column=int(ncols/2),columnspan=2,sticky=E+W)

        # Other capabilities accessed via menu
        if False:
            col += 4
            self.RigCtrlBtn = Button(self.root, text='Rig Ctrl', command=self.RigCtrlCB )
            self.RigCtrlBtn.grid(row=row,column=col,sticky=E+W)
            tip = ToolTip(self.RigCtrlBtn,' Show/Hide Rig Control Frame ')
        self.rig = RIG_CONTROL(P)
        
        # Add a tab to manage Rotor
        # This is actually rather difficult since there doesn't
        # appear to be a tk equivalent to QLCDnumber
        self.rotor_ctrl = ROTOR_CONTROL(self.rig.tabs,P)

        # Settings
        self.SettingsWin = SETTINGS_GUI(self.root,self.P)
        self.SettingsWin.hide()
        
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
                spot['Freq']   = None
                spot['Fields'] = None
                self.spots.append(spot)

        # Restore the state from the last time in
        self.RestoreState()
        
        # And away we go!
        self.set_macros()
        

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
        
    # callback to set logs fields, optionally from fldigi
    def Set_Log_Fields(self,fields=None):
        if fields==None:
            fields  = self.sock.get_log_fields()
        print("Set Log Fields =",fields)
        self.call.delete(0, END)
        self.call.insert(0,fields['Call'])
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

    # callback to read log fields and optionally send to fldigi
    def Read_Log_Fields(self,send2fldigi=True):
        print("Read_Log_Fields ...")
        call=self.get_call()
        name=self.get_name()
        qth=self.get_qth()
        rst_in  = self.get_rst_in()
        rst_out = self.get_rst_out()
        cat     = self.get_cat()

        prec    = self.get_prec()
        check   = self.get_check()
        
        exchange=self.get_exchange()
        fields = {'Call':call,'Name':name,'RST_in':rst_in,'RST_out':rst_out, \
                  'QTH':qth,'Exchange':exchange, \
                  'Category':cat,'Prec':prec,'Check':check}
        if send2fldigi:
            self.sock.set_log_fields(fields)
        return fields

    # callback to wipe out log fields
    def Clear_Log_Fields(self):
        self.call.delete(0, END)
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

        self.prec.delete(0, END)
        self.check.delete(0, END)
        self.qsl_rcvd.set(0)
        
        self.prefill=False
        self.prev_call=''

    # Callback to select a radio for SO2R
    def SelectRadio(self):
        iRadio=self.iRadio.get()
        if iRadio==1:
            self.P.sock=self.P.sock1
            self.P.ser=self.P.ser1
        else:
            self.P.sock=self.P.sock2
            self.P.ser=self.P.ser2
        self.sock=self.P.sock
        print("You selected radio " + str(iRadio),'\tP.sock=',P.sock)
        rig=P.sock.rig_type2
        self.root.title("pyKeyer by AA2IL"+rig)
        
    # callback to look up a call on qrz.com
    def Call_LookUp(self):
        call = self.get_call()
        if len(call)>=3:
            print('CALL_LOOKUP: Looking up '+call+' on QRZ.com')
            if True:
                link = 'https://www.qrz.com/db/' + call
                webbrowser.open(link, new=2)

            self.qrzWin = CALL_INFO_GUI(self.root,self.P,call)
            #self.qrzWin.hide()
            
        else:
            print('CALL_LOOKUP: Need a valid call first! ',call)
            
    # callback for practice with computer text
    def PracticeCB(self):
        self.P.PRACTICE_MODE = not self.P.PRACTICE_MODE
        print("Practice ...",self.P.PRACTICE_MODE)

    # callback to turn sidetone on and off
    def SideToneCB(self):
        print("Toggling Sidetone ...")
        self.P.SIDETONE = not self.P.SIDETONE

    # Callback to bring up rig control menu
    def RigCtrlCB(self):
        print("^^^^^^^^^^^^^^Rig Control...")
        self.rig.show()

    # Callback to key/unkey TX for tuning
    def Tune(self):
        print("Tuning...")
        if False:
            self.tuning = not self.tuning
            if self.tuning:
                self.TuneBtn.configure(background='red',highlightbackground= 'red')
            else:
                self.TuneBtn.configure(background='yellow',highlightbackground= 'yellow')
        txt='[TUNE]'
        self.q.put(txt)

    # Callback to store & retrieve spotted freqs
    def Spots_cb(self,arg,idir):
        print('\nSPOT_CB:',arg,idir,self.last_shift_key)

        spot = self.spots[arg]
        if idir==0:
            # Not sure what this does but probably never get here!
            txt = spot['Button']['text']
            if txt=='--':
                frq = self.sock.get_freq() / 1e3
                spot['Button']['text'] = "{:,.1f}".format(frq)
                spot['Freq']=frq
                spot['Fields'] = self.Read_Log_Fields()
            else:
                #frq = float( txt.replace(',','') )
                frq = spot['Freq']
                self.sock.set_freq(frq)
                spot['Button']['text']='--'
                self.Set_Log_Fields(spot['Fields'])

        elif idir==-1:
            # Clear
            spot['Button']['text'] = '--'
            spot['Freq'] = None
            spot['Fields'] = None
            self.P.DIRTY = True

        elif idir==1:
            # Save
            call=self.get_call().upper()
            frq = self.sock.get_freq() / 1e3
            spot['Button']['text'] = call+" {:,.1f} ".format(frq)
            spot['Freq']=frq
            spot['Fields'] = self.Read_Log_Fields()
            self.P.DIRTY = True

        elif idir==2:
            # Restore
            try:
                frq = spot['Freq']
                self.sock.set_freq(frq)
                self.Set_Log_Fields(spot['Fields'])
                call=self.get_call().upper()
                self.dup_check(call)
                if self.contest:
                    self.get_hint(call)
            except:
                pass

    # Routine to substitute various keyer commands that are stable in macro text
    def Patch_Macro(self,txt):
        txt = txt.replace('[MYCALL]',self.P.SETTINGS['MY_CALL'] )
        if '[MYSTATE]' in txt:
            self.qth_out = self.P.SETTINGS['MY_STATE']
            txt = txt.replace('[MYSTATE]',self.qth_out)
        if '[MYNAME]' in txt:
            self.name_out = self.P.SETTINGS['MY_NAME']
            txt = txt.replace('[MYNAME]', self.name_out)
        if '[MYQTH]' in txt:
            self.qth_out = self.P.SETTINGS['MY_QTH']
            txt = txt.replace('[MYQTH]',self.qth_out)
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
            self.qth_out = self.P.SETTINGS['MY_CQ_ZONE']
            txt = txt.replace('[MYCQZ]', self.qth_out )
        if '[MYCAT]' in txt:
            self.check_out = self.P.SETTINGS['MY_CAT'] 
            txt = txt.replace('[MYCAT]', self.check_out)
        if '[MYCOUNTY]' in txt:
            self.qth_out = self.P.SETTINGS['MY_COUNTY'] 
            txt = txt.replace('[MYCOUNTY]', self.qth_out)

        return txt
    
    # Routine to substitute various keyer commands that change quickly in macro text 
    def Patch_Macro2(self,txt):
    
        if '[GDAY]' in txt:
            hour = datetime.now().hour
            if hour<12:
                txt = txt.replace('[GDAY]','GM' )
            elif hour<16:
                txt = txt.replace('[GDAY]','GA' )
            else:
                txt = txt.replace('[GDAY]','GE' )

        call = self.get_call().upper()
        call2 = self.last_call
        #print '---- CALL:',call,call2,call==call2
        if call==call2:
            txt = txt.replace('[CALL_CHANGED]','')
        else:
            txt = txt.replace('[CALL_CHANGED]',call)

        if '[CALL]' in txt:
            txt = txt.replace('[CALL]',call)
            self.last_call=call
        
        txt = txt.replace('[NAME]',self.get_name() )
        txt = txt.replace('[RST]', self.get_rst_out() )

        if '[EXCH]' in txt:
            txt = txt.replace('[EXCH]', '' )
            self.exch_out = txt

                
        return txt

    # Callback to send a pre-defined macro
    def Send_Macro(self,arg):
        #print 'arg=',arg,self.macros.has_key(arg)
        #print self.macros
        if arg not in self.macros:
            return
        
        txt = self.macros[arg]["Text"]
        if arg in [0,5]:
            self.P.LAST_MSG = arg                # Last was a reply - make sure he got it ok
        elif arg in [2,4]:
            self.P.LAST_MSG = -1                 # Last was TU or my call
        #print 'LAST_MSG=',txt,arg,self.P.LAST_MSG

        # Highlight appropriate buttons for running or s&p
        self.P.KEYING.highlight(self,arg)
        self.macro_label = self.macros[arg]["Label"]
        print("\nSend_Marco:",arg,':',self.macro_label,txt)
        if '[SERIAL]' in txt:
            cntr = self.sock.get_serial_out()
            if not cntr or cntr=='':
                cntr=self.P.MY_CNTR
            print('GUI: cntr=',cntr,'\tndigits=',self.ndigits)
            self.cntr = cw_keyer.cut_numbers(cntr,ndigits=self.ndigits)
            txt = txt.replace('[SERIAL]',self.cntr)
            self.serial_out = self.cntr
            print('GUI: cntr=',self.cntr,'\ttxt=',txt,'\tndigits=',self.ndigits)

        # This should have already been handled when we loaded the macros
        #txt = self.Patch_Macro(txt)
        txt = self.Patch_Macro2(txt)

        # Send text to keyer ...
        self.q.put(txt)

        # ... and to big text box ...
        self.txt.insert(END, txt+'\n')
        self.txt.see(END)
        self.root.update_idletasks()

        # ... and to disk
        self.fp_txt.write('%s\n' % (txt) )
        self.fp_txt.flush()
        

    # Routine to hide all of the input boxes
    def hide_all(self):
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
        self.serial.grid_remove()
        self.prec_lab.grid_remove()
        self.prec.grid_remove()
        self.call2_lab.grid_remove()
        self.call2.grid_remove()
        self.check_lab.grid_remove()
        self.check.grid_remove()
        self.hint_lab.grid_remove()
        self.hint.grid_remove()
        self.qsl.grid_remove()

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

        if not val:
            val=self.P.contest_name
            self.MACRO_TXT.set(val)
        print('SET_MACROS: val=',val)

        # Initiate keying module for this contest
        if val.find('CW Ops')>=0:
            self.P.KEYING=CWOPS_KEYING(self.P)
        elif val=='SST':
            self.P.KEYING=SST_KEYING(self.P)
        elif val=='CW Open':
            self.P.KEYING=CWOPEN_KEYING(self.P)
        elif val=='SATELLITES':
            self.P.KEYING=SAT_KEYING(self.P)
        elif val=='ARRL VHF' or val=='STEW PERRY':
            self.P.KEYING=VHF_KEYING(self.P,val)
        elif val=='CQP':
            self.P.KEYING=CQP_KEYING(self.P)
        elif val.find('NAQP')>=0:
            self.P.KEYING=NAQP_KEYING(self.P)
        elif val=='IARU-HF':
            self.P.KEYING=IARU_KEYING(self.P)
        elif val=='CQWW':
            self.P.KEYING=CQWW_KEYING(self.P)
        elif val=='ARRL-SS-CW':
            self.P.KEYING=SS_KEYING(self.P)
        elif val=='ARRL-FD':
            self.P.KEYING=FD_KEYING(self.P)
        elif val.find('CQ-WPX')>=0:
            self.P.KEYING=WPX_KEYING(self.P)
        elif val=='ARRL-10M' or val=='ARRL-DX':
            self.P.KEYING=TEN_METER_KEYING(self.P,val)
        elif val=='Ragchew':
            self.P.KEYING=RAGCHEW_KEYING(self.P,val)
        elif val=='DX-QSO':
            self.P.KEYING=DX_KEYING(self.P,val)
        elif val=='Default':
            self.P.KEYING=DEFAULT_KEYING(self.P)
        else:
            print('GUI: *** ERROR *** Cant figure which contest !')
            print(val)
            sys.exit(0)
            
        self.P.SPRINT   = val.find('Sprint')         >= 0
        
        self.P.contest_name  = self.P.KEYING.contest_name
        self.macros = self.P.KEYING.macros()
        
        MY_CALL = self.P.SETTINGS['MY_CALL']
        for i in range(12):
            lab = self.macros[i]["Label"].replace('[MYCALL]',MY_CALL )
            self.btns1[i].configure( text=lab )

            txt = self.Patch_Macro( self.macros[i]["Text"] )
            self.macros[i]["Text"] = txt
            tip = ToolTip(self.btns1[i], ' '+txt+' ' )

            if i+12 in self.macros:
                lab = self.macros[i+12]["Label"].replace('[MYCALL]',MY_CALL )
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
    def set_wpm(self,dWPM=0):
        WPM=int( self.WPM_TXT.get() ) + dWPM
        #print('SET_WPM: WPM,dWPM=',WPM,dWPM)
        if WPM>=5:
            self.keyer.set_wpm(WPM)
            #set_speed(self.P.sock,WPM)
            self.sock.set_speed(WPM)
            self.WPM_TXT.set(str(WPM))

    # Callback to return everything to defaults
    def Reset_Defaults(self):
        print("Reset...")
        txt="[RESET]"
        self.q.put(txt)
        WPM=self.keyer.get_wpm()
        self.WPM_TXT.set(str(WPM))

    # Callback to toggle audio recording on & off
    def CaptureAudioCB(self,iopt=None):
        P=self.P
        print("============================================== Capture Audio ...",iopt,P.CAPTURE)
        if iopt==-1:
            iopt=None
            P.CAPTURE = not P.CAPTURE
        if (iopt==None and not P.CAPTURE) or iopt==1:
            if not P.CAPTURE:
                #self.CaptureBtn['text']='Stop Capture'
                #self.CaptureBtn.configure(background='red',highlightbackground= 'red')
                P.CAPTURE = True
                print('Capture rig audio started ...')

                s=time.strftime("_%Y%m%d_%H%M%S", time.gmtime())      # UTC
                dirname=''
                P.wave_file = dirname+'capture'+s+'.wav'
                print('\nOpening',P.wave_file,'...')

                if P.sock.rig_type2=='FT991a':
                    gain=[4,1]
                else:
                    gain=[1,1]
                P.rec = WaveRecorder(P.wave_file, 'wb',channels=1,wav_rate=8000,rb2=P.osc.rb2,GAIN=gain)
                
                if not P.RIG_AUDIO_IDX:
                    P.RIG_AUDIO_IDX = P.rec.list_input_devices('USB Audio CODEC')
                P.rec.start_recording(P.RIG_AUDIO_IDX)
                
        else:
            if P.CAPTURE:
                #self.CaptureBtn['text']='Capture'
                #self.CaptureBtn.configure(background='green',highlightbackground= 'green')
                if P.RIG_AUDIO_IDX:
                    P.rec.stop_recording()
                    P.rec.close()
                P.CAPTURE = False
                print('Capture rig audio stopped ...')

    # Read counter from the entry box
    def update_counter(self):
        cntr = self.counter.get()
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ UPDATE COUNTER ^^^^^^^^^^^^^^^^^^^^',cntr)
        try:
            self.P.MY_CNTR = int( cntr )
        except:
            print('*** GUI  - ERROR *** Unable to convert counter entry to int:',cntr)
        return True

    # Read his call from the entry box
    def get_call(self):
        return self.call.get().upper()

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

    # Read category from entry box
    def get_cat(self):
        return self.cat.get().upper()

    # Read serial from entry box
    def get_serial(self):
        return self.serial.get().upper()

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
    def get_hint(self,call):
        #print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! call=',call)

        #if len(call)>=3 and not self.P.NO_HINTS:
        if len(call)>=3:
            self.dx_station = Station(call)
            #pprint(vars(self.dx_station))
            h = hint.master(self.P,call,self.dx_station)
            if not h:
                h = hint.oh_canada(self.dx_station)
        else:
            h=None
            
        self.hint.delete(0, END)
        if h:
            self.hint.insert(0,h)
        self.last_hint=h
        #print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! h=',h)


    # Save program state
    def SaveState(self):
        spots = []
        frqs  = []
        flds  = []
        for spot in self.spots:
            #print spot
            spots.append( spot['Button']['text'] )
            frqs.append( spot['Freq'] )
            flds.append( spot['Fields'] )
        fp = open('state.pcl', 'wb')

        now = datetime.utcnow().replace(tzinfo=UTC)
        pickle.dump(now, fp)

        pickle.dump(self.P.MY_CNTR, fp)
        pickle.dump(spots, fp)
        pickle.dump(frqs, fp)
        pickle.dump(flds, fp)
        fp.close()
        self.P.DIRTY=False
        #print('SaveState:',self.P.MY_CNTR)
        #print('SaveState:',spots)
        #print('SaveState:',frqs)
        #print('SaveState:',flds)

    # Restore program state
    def RestoreState(self):
        try:
            fp = open('state.pcl', 'rb')
        except:
            print('RestoreState: state.pcl not found')
            return
            
        now        = datetime.utcnow().replace(tzinfo=UTC)
        time_stamp = pickle.load(fp)
        age = (now - time_stamp).total_seconds()/60  
        #print('RestoreState: Age=',age,' Mins')

        # If we're in a long contest, restore the serail counter
        if age<self.P.MAX_AGE:
            self.P.MY_CNTR = pickle.load(fp)
            print('RestoreState: Counter=',self.P.MY_CNTR)
            self.counter.delete(0, END)
            self.counter.insert(0,str(self.P.MY_CNTR))

        # If not too much time has elapsed, restore the spots 
        if age<30:
            spots = pickle.load(fp)
            if len(spots)>12*self.P.NUM_ROWS:
                spots=spots[:12*self.P.NUM_ROWS]
            print('RestoreState: Spots=',spots)
            frqs = pickle.load(fp)
            flds = pickle.load(fp)
            for i in range(len(spots)):
                print(i,len(spots),len(self.spots))
                self.spots[i]['Button']['text'] = spots[i]
                self.spots[i]['Freq']=frqs[i]
                self.spots[i]['Fields']=flds[i]
                
        fp.close()
        self.P.DIRTY=False

    # Exit
    def Quit(self):
        # Make sure we really want to do this and didn't just fat-fingure something
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
        self.fp_log.close()
        self.fp_adif.close()
        self.fp_txt.close()
        self.P.SHUTDOWN=True

        # Immediately stop sending
        self.keyer.abort()     
        if not self.q.empty():
            self.q.get(False)
            self.q.task_done()

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
            print('\tWaiting for thread to quit -',name,' ...')
            self.P.Stopper.set()
            th.join()
            print('\t... Thread quit -',th.getName())

        # Make sure root window is clobbered
        try:
            print('Destroying root window ...')
            self.root.destroy()
        except:
            print('Failed to destroying root window ... Giving up!')
            sys.exit(0)
            
        show_threads()
        print("\nThat's all folks!\n")
        self.Done=True
        sys.exit(0)

    # Callback when call sign box has changed - apparently not called?
    def check_call(self,P,V,W):
        #call=self.get_call()
        #call=self.call_sv.get()
        #print 'HEY!!!!!!! ',P,V,W
        self.sock.set_log_fields({'Call':P})

        delay_ms=5
        time.sleep(.001*delay_ms)
        self.root.attributes('-topmost', True)              # Raising root above all other windows
        self.call.focus_force()
        time.sleep(.001*delay_ms)
        self.root.attributes('-topmost', False)              # Raising root above all other windows
        #self.root.after(delay_ms,self.root.attributes,'-topmost',False)

        return True

    # Log the qso
    def log_qso(self):

        # Check for minimal fields
        call=self.get_call().upper()
        valid = len(call)>=3
        name=self.get_name().upper()
        qth =self.get_qth().upper()
        print('LOG_QSO:',call,name,qth)
        serial=0

        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        
        if self.contest:
            rst='5NN'
            exch,valid,self.exch_out = self.P.KEYING.logging()
        else:
            rstin =self.get_rst_in().upper()
            exch=str(rstin)+','+ name
            print('name=',name)
            print('rst=',rstin)
            print('exch=',exch)

        # Make sure a satellite is selected if needed
        satellite = self.get_satellite()
        if self.P.contest_name=='SATELLITES' and satellite=='None':
            errmsg='Need to Select a Satellite!'
            valid=False
        else:
            errmsg='Missing one or more fields!'
            
        if valid:
            print('LOG IT! contest=',self.contest,self.P.contest_name,\
                  'P.sock=',self.P.sock,self.P.sock.rig_type2)
            #print(self.sock.run_macro(-1))

            # Get time stamp, freq, mode, etc.
            UTC       = pytz.utc
            now       = datetime.utcnow().replace(tzinfo=UTC)
            date_off  = now.strftime('%Y%m%d')
            time_off  = now.strftime('%H%M%S')
            
            # Read the radio 
            freq_kHz = 1e-3*self.sock.get_freq()
            freq     = int( freq_kHz )
            mode     = self.sock.get_mode()
            if mode=='FMN':
                mode='FM'
            elif mode=='AMN':
                mode='AM'
            band     = str( self.sock.get_band() )
            if band[-1]!='m':
                band += 'm'

            # For satellites, read vfo B also
            if self.P.contest_name=='SATELLITES':
                freq_kHz_rx = freq_kHz
                band_rx     = band

                freq_kHz    = 1e-3*self.sock.get_freq(VFO='B')
                freq        = int( freq_kHz )
                band        = str( self.sock.get_band(VFO='B') )
                if band[-1]!='m':
                    band += 'm'

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
            
            # Construct exchange out
            if self.contest and self.P.SPRINT:
                self.exch_out = str(self.cntr)+','+MY_NAME+','+MY_STATE
                
            qso = dict( list(zip(['QSO_DATE_OFF','TIME_OFF','CALL','FREQ','BAND','MODE', \
                                  'SRX_STRING','STX_STRING','NAME','QTH','SRX',
                                  'STX','SAT_NAME','FREQ_RX','BAND_RX'],  \
                           [date_off,time_off,call,str(1e-3*freq_kHz),band,mode, \
                            exch,self.exch_out,name,qth,str(serial),
                            str(self.cntr),satellite,str(1e-3*freq_kHz_rx),band_rx] )))

            if self.P.sock3.connection=='FLLOG':
                print('GUI: =============== via FLLOG ...')
                self.P.sock3.Add_QSO(qso)

            elif self.sock.connection=='FLDIGI' and self.sock.fldigi_active and not self.P.PRACTICE_MODE:
                print('GUI: =============== via FLDIGI ...')
                fields = {'Call':call,'Name':name,'RST_out':rstout,'QTH':qth,'Exchange':exch}
                self.sock.set_log_fields(fields)
                self.sock.set_mode('CW')
                self.sock.run_macro(47)

            # Reset clarifier
            #self.sock.send('RC;RT0;XT0;')
            ClarReset(self)
            #self.sock.rit(0,0)

            # Make sure practice exec gets what it needs
            if self.P.PRACTICE_MODE:
                print('LOG_QSO: Waiting for handshake ...',self.keyer.evt.isSet() )
                while self.keyer.evt.isSet():
                    time.sleep(0.1)
                print('LOG_QSO: Got handshake ...')

            # Clear fields
            self.prefill=False
            self.call.delete(0,END)
            self.prev_call=''
            self.call.focus_set()
            self.call.configure(background=self.default_color)
            self.name.delete(0,END)
            self.qth.delete(0,END)
            self.hint.delete(0,END)
            self.serial.delete(0,END)
            self.prec.delete(0,END)
            self.call2.delete(0,END)
            self.check.delete(0,END)
            self.exch.delete(0,END)
            self.cat.delete(0,END)
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
            self.fp_log.write('%s,%s,%s,%s,%s,%s,"%s","%s","%s"\n' % \
                              (date_off,time_off,call,str(freq),band,mode,exch,self.exch_out,satellite) )
            self.fp_log.flush()
            self.fp_txt.write('%s,%s,%s,%s,%s,%s,"%s","%s","%s"\n' % \
                              (date_off,time_off,call,str(freq),band,mode,exch,self.exch_out,satellite) )
            self.fp_txt.write('----------\n')
            self.fp_txt.flush()

            self.log_book.append(qso)
            #print self.log_book

            # Update ADIF file
            if not self.P.PRACTICE_MODE:
                qso2 =  {key.upper(): val for key, val in list(qso.items())}
                print("GUI: ADIF writing QSO=",qso2)
                write_adif_record(self.fp_adif,qso2,self.P)

            # Clobber any presets that have this call
            idx=0
            for spot in self.spots:
                #print idx,spot
                try:
                    call2 = spot['Fields']['Call'].upper()
                except:
                    call2 = None
                if call==call2:
                    print('@@@@@@@@@@@@@ Clobbering spot @@@@@@@@@@@@@@@@@@@@@',idx,spot)
                    self.Spots_cb(idx,-1)
                idx+=1

        else:
            print('*** Missing one or more fields ***',self.contest)
            print('Call=',call)
            if self.contest:
                print('Exch=',exch)
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

        # Save the current state
        self.SaveState()        

    # Routine to force the focus
    def force_focus(self,next_widget):
        #print 'Take focus'
        next_widget.focus_set()      
        next_widget.focus_force()
        self.root.update_idletasks()

    # Callback when an entry box takes focus - clears selection so we don't overwrite
    def take_focus(self,W):
        #print '\nFocus young man! W=',W
        widget = self.root.nametowidget(W)         # Convert widget name to instance
        #widget.icursor(END)                        # Move cursor to end ... - prevents editing - ugh!
        widget.selection_clear()                   # ... and clear the selection
        return True

    # Routine to compute QSO Rate
    def qso_rate(self):
        now = datetime.utcnow().replace(tzinfo=UTC)
        dt0 = (now - self.start_time).total_seconds()+1 # In seconds
        #print 'QSO Rate:',now
        if self.P.sock3.connection=='FLLOG' and False:
            print('Need to add code for FLLOG???')
        else:
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
                except Exception as e: 
                    print('Problem with qso=',qso)
                    print( str(e) )
                    continue
                
                age = (now - date_off).total_seconds() # In seconds
                if age<=dt:
                    nqsos+=1
                    
            rate = float(nqsos) / dt * 3600.
            nqsos2 = len(self.log_book)-self.nqsos_start
            rate2 = float(nqsos2) / dt0 * 3600.
            #print nqsos,' in',dt,' secs --->',rate,' QSOs/Hour'
            #txt = 'QSO Rate: {:d} per Hour'.format(int(rate+0.5))
            #self.rate_lab.config(text=txt)
            self.rate_lab.config(text='QSOs: {:3d} /hr : {:3d} /hr : {:d}'.format( int(rate+0.5),int(rate2+0.5),nqsos2 ))

    # Routine to check & flag dupes
    def dup_check(self,call):
        print('DUP_CHECK: call=',call,self.P.MAX_AGE)

        # Look for dupes
        match1=False                # True if there is matching call
        match2=False                # True if the match is within the last 48 hours on current band and mode
        last_exch=''
        now = datetime.utcnow().replace(tzinfo=UTC)
        if self.P.sock3.connection=='FLLOG' and True:
            freq   = self.sock.get_freq()
            mode   = self.sock.get_mode()
            match1 = self.P.sock3.Dupe_Check(call)
            print('match1=',match1)
            if match1:
                match2 = self.P.sock3.Dupe_Check(call,mode,self.P.MAX_AGE,freq)
                print('match2=',match2)
                qso = self.P.sock3.Get_Last_QSO(call)
                print('last qso=',qso)
                if 'SRX_STRING' in qso :
                    last_exch = qso['SRX_STRING']
                if False:    # Shouldnt need to do this but there was a bug in how fllog handled local & utc times
                    date_off = datetime.strptime( qso["QSO_DATE_OFF"] +" "+ qso["TIME_OFF"] , "%Y%m%d %H%M%S") \
                                       .replace(tzinfo=UTC)
                    age = (now - date_off).total_seconds() # In seconds
                    band = str( self.sock.get_band() )
                    if band[-1]!='m':
                        band += 'm'
                    match2 = match2 or (age<self.P.MAX_AGE*60 and qso['BAND']==band and qso['MODE']==mode)
                    print('match 1&22:',match1,match2)

        else:
            for qso in self.log_book:
                if qso['CALL']==call:
                    match1 = True
                    date_off = datetime.strptime( qso["QSO_DATE_OFF"]+" "+qso["TIME_OFF"] , "%Y%m%d %H%M%S") \
                                       .replace(tzinfo=UTC)
                    age = (now - date_off).total_seconds() # In seconds
                    mode = self.sock.get_mode()
                    band = str( self.sock.get_band() )
                    if band[-1]!='m':
                        band += 'm'

                    # There are some contests that are "special"
                    if self.P.contest_name=='SATELLITES':
                        # Need to add more logic to this going forward
                        print(call,'- Worked before on sats')
                        match2 = True
                        
                    elif self.P.contest_name=='ARRL VHF' and True:
                        # Group phone mode together
                        #PHONE_MODES=['FM','SSB','USB','LSB']
                        #match3 = qso['MODE']==mode or (qso['MODE'] in PHONE_MODES and mode in PHONE_MODES)

                        # Actually, can only work each station once per band, regardless of mode
                        match3 = qso['BAND']==band 

                        # Rovers can be reworked if they are in a different grid square
                        if '/R' in call:
                            qth = self.P.gui.get_qth().upper()
                            match4 = qth==qso['QTH']
                        else:
                            match4 = True

                        # Combine it all together
                        match2 = match2 or (age<self.P.MAX_AGE*60 and match3 and match4)
                        
                    elif self.P.contest_name=='ARRL-SS-CW':
                        # Can only work each station once regardless of band
                        match2 = match2 or (age<self.P.MAX_AGE*60 and qso['MODE']==mode)
                    else:
                        # Most of the time, we can work each station on each band and mode
                        match2 = match2 or (age<self.P.MAX_AGE*60 and qso['BAND']==band and qso['MODE']==mode)
                        
                    if self.P.contest_name=='SATELLITES':
                        #print('HEEEEEEEEYYYYYYYYYYYYYY')
                        #print(qso)
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
        if match1:
            print('Call match:',call)
            if match2:
                self.call.configure(background="coral")
            if len( self.exch.get() )==0:
                self.prefill=True
                a=last_exch.split(',')
                print('last_exch - a=',a)
                self.P.KEYING.dupe(a)

                """
                elif self.P.SPRINT:
                    #self.serial.delete(0,END)
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
            #if (self.prev_call != call and True) or self.prefill:
                self.name.delete(0,END)
                self.qth.delete(0,END)
                self.cat.delete(0,END)
                self.serial.delete(0,END)
                self.hint.delete(0, END)
                self.exch.delete(0,END)

            # Kludge - should be taken care of above?
            #if (self.prev_call != call and True) or self.prefill:
            #    self.hint.delete(0, END)
                    
            # Check fldigi logger
            if self.sock.connection=='FLDIGI' and not self.P.PRACTICE_MODE and False:
                fields  = self.sock.get_log_fields()
                print("Log Fields =",fields)
                if len( self.name.get() )==0 and len(fields['Name'])>0:
                    self.name.delete(0, END)
                    self.name.insert(0,fields['Name'])
                if len( self.qth.get() )==0 and len(fields['QTH'])>0:
                    self.qth.delete(0, END)
                    self.qth.insert(0,fields['QTH'])

            # Use default color
            self.call.configure(background=self.default_color)


############################################################################################
    
    # Callback when a key is pressed in an entry box
    def key_press(self,event,id=None):

        key   = event.keysym
        num   = event.keysym_num
        ch    = event.char
        state = event.state

        # Modfiers
        shift     = ((state & 0x0001) != 0)
        #caps_lock = state & 0x0002
        control   = (state & 0x0004) != 0
        alt       = (state & 0x0088) != 0                 # Both left and right ALTs
        #num_lock  = state & 0x0010
        #mouse1 = state & 0x0100
        #mouse2 = state & 0x0200
        #mouse3 = state & 0x0400

        if False:
            print("Key Press:",key) #,ch,len(key),num
            print('State:',state,shift,control,alt)
            #print event

        # This should never happen
        if len(key)==0:
            return

        # Check for special keys
        if len(key)>=2 or alt or control:
            if len(key)==1:
                key=key.lower()
            
            #print('Special:',key,'\t',state)
            #if key=='Shift_L' or key=='Shift_R':
            #    return("break")
                
            if key=='Shift_L':
                self.last_shift_key='L'
                
            if key=='Shift_R':
                self.last_shift_key='R'

            DF=100
            if key=='Up':
                print('RIT Up',DF)
                #self.sock.send('RT1;RU0050;')
                self.sock.rit(1,DF)
                return("break")
                
            if key=='Down':
                print('RIT Down',-DF)
                #self.sock.send('RT1;RD0050;')
                self.sock.rit(1,-DF)
                return("break")

            if key=='KP_Decimal':
                print('Reset clarifier')
                #self.sock.send('RC;RT0;XT0;')
                ClarReset(self)
                #self.sock.rit(0,0)
                return("break")

            # Quick way to send '?'
            if (key=='slash' or key=='question') and (alt or control):
                self.q.put('?')
                return("break")

            # This works but seemed problematic in normal operating??
            if (key=='Delete' and False) or (key=='w' and alt):
                print('Delete - clear box')
                if event.widget!=self.txt:
                    event.widget.delete(0,END)     # Clear the entry box
                    if event.widget==self.call:
                        self.call.configure(background=self.default_color)

                # Wipe all fields Alt-w
                if (key=='w' or key=='e') and alt:
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
                    self.serial.delete(0, END)
                    self.prec.delete(0, END)
                    self.hint.delete(0, END)
                    self.check.delete(0, END)
                    self.qsl_rcvd.set(0)

                    next_widget=self.call
                    self.call.focus_set()
                    return("break")

            # Copy hints to fields
            if key=='Insert' or (key=='i' and alt):
                h = self.hint.get()
                print('h=',h,len(h))
                if len(h)==0:
                    return "break"
                h = h.split(' ')
                print('h=',h)
                
                self.P.KEYING.insert_hint(h)
                """
                elif self.P.SPRINT:
                    self.name.delete(0, END)
                    self.name.insert(0,h[0])
                    self.qth.delete(0, END)
                    self.qth.insert(0,h[1])
                """

                return "break"

            # Immediately stop sending
            if key=='Escape':
                print('Escape!')
                self.keyer.abort()     
                if not self.q.empty():
                    self.q.get(False)
                    self.q.task_done()

            # Move to next entry box
            if key=='Tab':
                if event.widget==self.txt:
                    print('Text box',key,len(key),key=='Tab')
                    self.call.focus_set()
                    return("break")
                elif self.contest:
                    self.P.KEYING.next_event(key,event)
                    return("break")
                    """
                    elif self.P.SPRINT  and event.widget==self.qth:
                        #print 'QTH box',key,len(key),key=='Tab'
                        self.call.focus_set()
                        return("break")
                    """

            elif key=='ISO_Left_Tab':
                self.P.KEYING.next_event(key,event)
                return("break")
                    
            # Return key in the text box - nothing to do
            if (key=='Return' or key=='KP_Enter') and event.widget!=self.txt and True:
                pass

            # Check for function keys
            elif key[0]=='F':
                idx=int( key[1:] ) - 1

                print(self.last_shift_key)
                if not alt and not control:
                    if not shift:
                        self.Send_Macro(idx)
                    else:
                        self.Send_Macro(idx+12)
                elif control:
                    self.Spots_cb(idx,1)
                elif alt:
                    self.Spots_cb(idx,2)
                else:
                    print('Modified Function Key not supported',shift,control,alt)
                return("break")

        # Are we in the text window?
        next_widget=event.widget             # Next widget is by default the current widget
        if event.widget==self.txt:
            # Don't send control chars
            if len(ch)>0:
                if ord(ch)>=32 and ord(ch)<127:
                    #print('KEY_PRESS: Q-Put',ch)
                    self.q.put(ch)

        # Update info in fldigi
        elif event.widget==self.call:
            call=self.get_call().upper()
            self.sock.set_log_fields({'Call':call})
            self.dup_check(call)

            # If we're in a contest and the return key was pressed, send response and get ready for the exchange
            if (key=='Return' or key=='KP_Enter') and len(call)>0:
                next_widget = self.P.KEYING.next_event(key,event)

                """
                elif self.contest and self.P.SPRINT:
                    next_widget=self.serial
                    if self.P.LAST_MSG==0:
                        self.Send_Macro(1)                 # Send reply
                    else:
                        self.Send_Macro(4)                 # Send my call
                """

            # Take care of hints
            if self.contest:
                self.get_hint(call)
                                        
            if self.P.SPRINT:
                if key=='Tab':
                    self.force_focus(self.serial)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.qth)
                    return("break")

            # Save call so we can keep track of changes
            self.prev_call = call

        elif event.widget==self.name:
            name=self.get_name().upper()
            #self.name.delete(0, END)             # Causes arrow keys not to work - ugh!
            #self.name.insert(0, name)
            self.sock.set_log_fields({'Name':name})

            # If we're in a contest and the return key was pressed, get ready for rest of the exchange
            if key=='Return' or key=='KP_Enter':
                next_widget = self.P.KEYING.next_event(key,event)
                """
                elif self.contest and (self.P.SPRINT):
                    next_widget=self.qth
                """

            if self.P.SPRINT:
                if key=='Tab':
                    self.force_focus(self.qth)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.serial)
                    return("break")
                    
        elif event.widget==self.qth:
            qth=self.get_qth().upper()
            #self.qth.delete(0, END)           # Causes arrow keys not to work - ugh!
            #self.qth.insert(0, qth)
            self.sock.set_log_fields({'QTH':qth})

            if len(qth)>0 and self.P.contest_name=='CQP':
                self.P.KEYING.qth_hints()
            elif self.P.contest_name=='SATELLITES':
                if len(qth)==4 and not qth in self.P.grids:
                    self.qth.configure(background="lime")
                else:
                    self.qth.configure(background=self.default_color)
                    
            # If we're in a contest and the return key was pressed, send reply
            if key=='Return' or key=='KP_Enter':
                if self.contest:
                    #next_widget=self.qth
                    next_widget = self.P.KEYING.next_event(key,event)
                    """
                    elif self.P.SPRINT:

                        if self.P.LAST_MSG==0:
                            self.Send_Macro(2)                     # Send TU
                        elif self.P.LAST_MSG==5:
                            self.Send_Macro(7)                     # Log the QSO
                            #self.Send_Macro(0)                    # Send CQ
                        else:
                            self.Send_Macro(5)                     # Send my excahnge

                    else:
                        print('!!!!!!!!!!!!! GUI - should never get here !!!!!!!!!!')
                    """
                    
            """
            elif self.P.SPRINT:
                if key=='Tab':
                    self.force_focus(self.call)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.name)
                    return("break")
            """
            
        elif event.widget==self.cat:
            cat=self.get_cat().upper()

        elif event.widget==self.rstin:
            rst=self.get_rst_in().upper()
            self.sock.set_log_fields({'RST_in':rst})
            next_widget = self.P.KEYING.next_event(key,event)
            return("break")

        elif event.widget==self.rstout:
            rst=self.get_rst_out().upper()
            self.sock.set_log_fields({'RST_out':rst})
            if key=='Return' or key=='KP_Enter':
                next_widget = self.P.KEYING.next_event(key,event)       # 1
                return("break")

        elif event.widget==self.exch:
            exch=self.get_exchange().upper()
            self.sock.set_log_fields({'Exchange':exch})

            if self.P.contest_name=='SATELLITES':
                if len(exch)==4 and not exch in self.P.grids:
                    self.exch.configure(background="lime")
                else:
                    self.exch.configure(background=self.default_color)
                    
            # If we're in a contest and the return key was pressed, send reply
            if key=='Return' or key=='KP_Enter':
                if self.contest:
                    next_widget = self.P.KEYING.next_event(key,event)        #2

        elif event.widget==self.counter:
            print('^^^^^^^^^^^ Counter window',self.P.MY_CNTR)
            
        elif event.widget==self.serial:
            serial=self.get_serial().upper()
            self.sock.set_log_fields({'Serial_out':serial})
            if key=='Return' or key=='KP_Enter':
                next_widget = self.P.KEYING.next_event(key,event)
            """
            elif self.P.SPRINT:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.name)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")
            """
                
        elif event.widget==self.prec:
            prec=self.get_prec().upper()
            self.sock.set_log_fields({'Prec':prec})

        elif event.widget==self.call2:
            call2=self.get_call2().upper()
            self.sock.set_log_fields({'Call2':call2})

        elif event.widget==self.check:
            print('!!!Check!!!')
            check=self.get_check().upper()
            self.sock.set_log_fields({'Check':check})
            
        # Make sure we keep the focus
        self.root.focus_set()
        next_widget.focus_set()      
            
        delay_ms=5
        time.sleep(.001*delay_ms)
        self.root.attributes('-topmost', True)              # Raising root above all other windows
        next_widget.focus_force()
        time.sleep(.001*delay_ms)
        self.root.attributes('-topmost', False)              # Raising root above all other windows

        next_widget.focus_set()      
        next_widget.focus_force()
        self.root.update_idletasks()


############################################################################################

     # Open dialog window for basic settings
    def Settings(self):
        #self.SettingsWin = SETTINGS_GUI(self.root,self.P)
        self.SettingsWin.show()

    
    # Function to create menu bar
    def create_menu_bar(self):
        print('Creating Menubar ...')
                   
        menubar = Menu(self.root)
        Menu1 = Menu(menubar, tearoff=0)

        Menu1.add_command(label="Settings ...", command=self.Settings)
        Menu1.add_command(label="Rig Control ...", command=self.RigCtrlCB)
        Menu1.add_separator()
        
        self.Capturing = BooleanVar(value=self.P.CAPTURE)
        Menu1.add_checkbutton(
            label="Capture Audio",
            underline=0,
            variable=self.Capturing,
            command=self.CaptureAudioCB
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
        
        self.SideTone = BooleanVar(value=self.P.SIDETONE)
        Menu1.add_checkbutton(
            label="SideTone",
            underline=0,
            variable=self.SideTone,
            command=self.SideToneCB
        )
        
        Menu1.add_separator()
        Menu1.add_command(label="Exit", command=self.Quit)
        menubar.add_cascade(label="File", menu=Menu1)

        self.root.config(menu=menubar)

        
