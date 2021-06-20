############################################################################################
#
# keyer_hui.py - Rev 1.0
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
from rig_io.ft_tables import *
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

############################################################################################

UTC = pytz.utc
MAX_AGE_HOURS=48
WPM_STEP = 2

############################################################################################

def cleanup(x): return x.strip().upper()

# Routine to list threads
def show_threads():
    print('\nList of running threads:')
    threads = enumerate()
    for th in threads:
        print(th,th.getName())
    print(' ')

# Routine to determine contest name
def get_contest_name(P):
    if P.CW_SS:
        return 'ARRL-SS-CW'
    elif P.NAQP:
        return 'NAQP-CW'
    elif P.SST:
        return 'SST'
    elif P.CWops:
        return 'CW Ops Mini-Test'
    elif P.WPX:
        return 'CQ-WPX-CW'
    elif P.ARRL_DX:
        return 'ARRL-DX'
    elif P.ARRL_10m:
        return 'ARRL-10M'
    elif P.ARRL_FD:
        return 'ARRL-FD'
    elif P.ARRL_VHF:
        return 'ARRL-VHF'
    elif P.CAL_QP:
        return 'CQP'
    elif P.SPRINT:
        return 'NCCC-Sprint'
    elif P.CQ_WW:
        return 'CQWW'
    elif P.IARU:
        return 'IARU-HF'
    else:
        return 'None'
    

# The GUI 
class GUI():
    def __init__(self,P,MACROS):

        print("\nCreating GUI ...")
        self.root = Tk()
        # width_size x height_size + x_position + y_position
        self.root.geometry('1200x400+250+250')
        
        self.Done=False
        self.contest = False
        self.P = P
        self.P.LAST_MSG = -1
        self.keyer=P.keyer;
        self.start_time = datetime.utcnow().replace(tzinfo=UTC)
        self.nqsos_start = 0

        print(P.sock.rig_type2)
        if P.sock.rig_type2:
            rig=' - '+P.sock.rig_type2
        else:
            rig=''
        self.root.title("pyKeyer by AA2IL"+rig)
        self.tuning = False
        self.rig_ctrl = False
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)

        self.MACROS = MACROS
        self.MACRO_TXT = StringVar()
        self.macro_label = ''

        self.last_call=''
        self.last_shift_key=''

        self.sock = P.sock
        self.q = P.q
        self.exch_out=''
        self.ndigits=3
        self.prev_call=''
        self.prefill=False
        self.cntr=0

        MY_CALL = P.SETTINGS['MY_CALL']

        # Open simple log file & read its contents
        fname = MY_CALL.replace('/','_')+".LOG"
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
                        print('Call not in Master list:',call,'\t- Adding it')
                        self.log_book.append(qso)
        except:
            pass

        self.nqsos_start = len(self.log_book)
        #print self.log_book
        #sys.exit(0)

        # Keep an ADIF copy of the log as well
        self.fp_adif = open(MY_CALL.replace('/','_')+".adif","a+")
        print("KEYER_GUI: ADIF file name=", self.fp_adif) 

        # Also save all sent text to a file
        self.fp_txt = open(MY_CALL.replace('/','_')+".TXT","a+")

        # Set up basic logging entry boxes
        ncols=12
        row=0

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

        self.rst_lab = Label(self.root, text="RST in",font=font1)
        self.rst_lab.grid(row=row,columnspan=3,column=8,sticky=E+W)
        self.rst = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.rst.grid(row=row+1,rowspan=2,column=8,columnspan=3)

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

        # Buttons to access FLDIGI logger
        btn = Button(self.root, text='Get',command=self.Set_Log_Fields,takefocus=0 )
        btn.grid(row=row+1,column=ncols-2)
        tip = ToolTip(btn, ' Get FLDIGI Logger Fields ' )

        btn = Button(self.root, text='Put',command=self.Read_Log_Fields,takefocus=0 ) 
        btn.grid(row=row+1,column=ncols-1)
        tip = ToolTip(btn, ' Set FLDIGI Logger Fields ' )

        btn = Button(self.root, text='Wipe',command=self.Clear_Log_Fields,takefocus=0 ) 
        btn.grid(row=row+2,column=ncols-2)
        tip = ToolTip(btn, ' Clear FLDIGI Logger Fields ' )
        
        btn = Button(self.root, text='QRZ.com',command=self.Web_LookUp,takefocus=0 ) 
        btn.grid(row=row+2,column=ncols-1)
        tip = ToolTip(btn, ' Query QRZ.com ' )

        # Set up text entry box with a scroll bar
        row+=3
        Grid.rowconfigure(self.root, row, weight=1)             # Allows resizing
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
        MACRO_LIST=list(self.MACROS.keys())
        print('MACROS:',MACRO_LIST)
        if self.P.CW_SS:
            idx=MACRO_LIST.index('ARRL CW SS')
        elif self.P.CAL_QP:
            idx=MACRO_LIST.index('Cal QP')
        elif self.P.SPRINT:
            idx=MACRO_LIST.index('Sprint')
        elif self.P.CQ_WW:
            idx=MACRO_LIST.index('CQ WW')
        elif self.P.IARU:
            idx=MACRO_LIST.index('IARU HF')
        elif self.P.ARRL_DX:
            idx=MACRO_LIST.index('ARRL DX')
        elif self.P.ARRL_10m:
            idx=MACRO_LIST.index('ARRL 10m')
        elif self.P.ARRL_FD:
            idx=MACRO_LIST.index('ARRL Field Day')
        elif self.P.ARRL_VHF:
            idx=MACRO_LIST.index('ARRL VHF')
        elif self.P.NAQP:
            idx=MACRO_LIST.index('NAQP')
        elif self.P.SST:
            idx=MACRO_LIST.index('SST')
        elif self.P.CWops:
            idx=MACRO_LIST.index('CWops')
        elif self.P.WPX:
            idx=MACRO_LIST.index('CQ_WPX')
        else:
            idx=0
        self.MACRO_TXT.set(MACRO_LIST[idx])
        SB = OptionMenu(self.root,self.MACRO_TXT,*MACRO_LIST, \
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
        
        # Other buttons - any buttons we need to modify, we need to grab handle to them
        # before we try to pack them.  Otherwise, all we get is the results of the packing

        # Rig control sub-menu
        col += 2
        self.RigCtrlBtn = Button(self.root, text='Rig Ctrl', command=self.RigCtrlCB )
        self.RigCtrlBtn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(self.RigCtrlBtn,' Show/Hide Rig Control Frame ')
        self.rig = RIG_CONTROL(self.root,P.sock)
        
        # Add a tab to manage Rotor
        # This is actually rather difficult since there doesn't
        # appear to be a tk equivalent to QLCDnumber
        self.rotor_ctrl = ROTOR_CONTROL(self.rig.tabs,P.sock2)
        
        # Practice button
        col += 1
        self.PracticeBtn = Button(self.root, text='Practice', command=self.PracticeCB )
        self.PracticeBtn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(self.PracticeBtn,' Toggle Practice Mode ')
        P.PRACTICE_MODE = not P.PRACTICE_MODE
        self.PracticeCB()

        # Button to turn SIDETONE on and off
        col += 1
        self.SideToneBtn = Button(self.root, text='SideTone', command=self.SideToneCB )
        self.SideToneBtn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(self.SideToneBtn,' Toggle Sidetone Osc ')
        P.SIDETONE = not P.SIDETONE
        self.SideToneCB()

        # TUNE buttons
        col += 1
        self.TuneBtn = Button(self.root, text='Tune',bg='yellow',highlightbackground= 'yellow', \
                              command=self.Tune )
        self.TuneBtn.grid(row=row,column=col,sticky=E+W)
        tip = ToolTip(self.TuneBtn,' Key Radio to Ant Tuning ')

        # Set up a spin box to allow satellite logging
        row += 1
        col  = 0
        self.SAT_TXT = StringVar()
        Label(self.root, text='Satellites:').grid(row=row,column=col,sticky=E+W)
        SB = OptionMenu(self.root,self.SAT_TXT,*SATELLITE_LIST, \
                        command=self.set_satellite).grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        self.set_satellite('None')

        # Reset button
        col = 8
        if False:
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

        # Reset clarifier
        #self.sock.send('RC;RT0;XT0;')
        ClarReset(self)
        #self.sock.rit(0,0)

        # Some other info
        row += 1
        #Label(self.root, text="--- Spots ---",font=font1).grid(row=row,columnspan=ncols,column=0,sticky=E+W)
        self.rate_lab = Label(self.root, text="QSO Rate:",font=font1)
        self.rate_lab.grid(row=row,columnspan=4,column=0,sticky=W)
        Label(self.root, text="--- Spots ---",font=font1) \
            .grid(row=row,column=int(ncols/2),columnspan=2,sticky=E+W)
        
        # Buttons to allow quick store & return to spotted freqs
        row += 1
        self.spots=[]
        for i in range(12):
            if i<4:
                c='pale green'
            elif i<8:
                c='indian red'
            else:
                c='slateblue1'
            Grid.columnconfigure(self.root, i, weight=1,uniform='twelve')
            btn = Button(self.root, text='--' , background=c)
            #btn = Button(self.root, text='--' , background=c, \
            #             command=lambda j=i: self.Spots_cb(j,0) )
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
        self.set_macros(MACRO_LIST[idx])
        

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
        self.rst.delete(0, END)
        #rst=fields['RST_out']
        rst=fields['RST_in']
        if rst=='':
            rst='5nn'
        self.rst.insert(0,rst)
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
        rst =self.get_rst()
        cat=self.get_cat()

        prec=self.get_prec()
        check=self.get_check()
        
        exchange=self.get_exchange()
        fields = {'Call':call,'Name':name,'RST_in':rst,'QTH':qth,'Exchange':exchange, \
                  'Category':cat,'Prec':prec,'Check':check}
        if send2fldigi:
            self.sock.set_log_fields(fields)
        return fields

    # callback to wipe out log fields
    def Clear_Log_Fields(self):
        self.call.delete(0, END)
        self.name.delete(0, END)
        self.qth.delete(0, END)
        self.rst.delete(0, END)
        self.rst.insert(0,'5NN')
        self.cat.delete(0, END)

        self.prec.delete(0, END)
        self.check.delete(0, END)
        
        self.prefill=False
        self.prev_call=''

    # callback to look up a call on qrz.com
    def Web_LookUp(self):
        call = self.get_call()
        if len(call)>=3:
            print('WEB_LOOKUP: Looking up '+call+' on QRZ.com')
            link = 'https://www.qrz.com/db/' + call
            webbrowser.open(link, new=2)
        else:
            print('WEB_LOOKUP: Need a valid call first')            
            
    # callback for practice with computer text
    def PracticeCB(self):
        self.P.PRACTICE_MODE = not self.P.PRACTICE_MODE
        print("Practice ...",self.P.PRACTICE_MODE)
        if self.P.PRACTICE_MODE:
            self.PracticeBtn.configure(background='red',highlightbackground= 'red')
        else:
            self.PracticeBtn.configure(background='green',highlightbackground= 'green')

    # callback to turn sidetone on and off
    def SideToneCB(self):
        print("Toggling Sidetone ...")
        self.P.SIDETONE = not self.P.SIDETONE
        if self.P.SIDETONE:
            self.SideToneBtn.configure(background='red',highlightbackground= 'red')
        else:
            self.SideToneBtn.configure(background='green',highlightbackground= 'green')

    # Callback to bring up rig control menu
    def RigCtrlCB(self):
        print("^^^^^^^^^^^^^^Rig Control...")
        self.rig_ctrl = not self.rig_ctrl
        if self.rig_ctrl:
            # Show
            self.rig.win.update()
            self.rig.win.deiconify()
        else:
            # Hide
            self.rig.win.withdraw()

    # Callback to key/unkey TX for tuning
    def Tune(self):
        print("Tuning...")
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

    # Routine to substitute various keyer commands in macro text
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
            self.qth_out = self.P.SETTINGS['MY_GRID']
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
        if '[GDAY]' in txt:
            hour = datetime.now().hour
            if hour<12:
                txt = txt.replace('[GDAY]','GM' )
            elif hour<17:
                txt = txt.replace('[GDAY]','GA' )
            else:
                txt = txt.replace('[GDAY]','GE' )

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
        if self.P.NAQP or self.P.SST or self.P.CAL_QP or self.P.SPRINT or \
           self.P.CWops or self.P.WPX or self.P.IARU or self.P.CQ_WW or \
           self.P.ARRL_FD or self.P.ARRL_VHF or self.P.ARRL_10m:
            #print 'HIGHLIGHTING',arg
            if arg==0:
                self.btns1[1].configure(background='green',highlightbackground='green')
                self.btns1[2].configure(background='green',highlightbackground='green')
                self.call.focus_set()
            elif arg==1:
                if self.P.NAQP or self.P.CWops or self.P.SST:
                    self.name.focus_set()
                elif self.P.SPRINT or self.P.WPX or self.P.CAL_QP:
                    self.serial.focus_set()
                elif self.P.ARRL_FD:
                    self.cat.focus_set()
                elif self.P.ARRL_VHF:
                    self.exch.focus_set()
                elif self.P.IARU or self.P.CQ_WW or self.P.ARRL_10m:
                    self.qth.focus_set()
            elif arg==2:
                if self.P.SPRINT:
                    self.btns1[1].configure(background='pale green',highlightbackground=self.default_color)
                    self.btns1[2].configure(background='pale green',highlightbackground=self.default_color)
            elif arg==4:
                self.btns1[5].configure(background='red',highlightbackground= 'red')
                self.btns1[7].configure(background='red',highlightbackground= 'red')
                if self.P.NAQP or self.P.CWops or self.P.SST or \
                   self.P.ARRL_FD or self.P.ARRL_VHF or self.P.WPX or  self.P.ARRL_10m or \
                   self.P.IARU or self.P.SPRINT or self.P.CQ_WW:
                    self.btns1[1].configure(background='pale green',highlightbackground=self.default_color)
                    self.btns1[2].configure(background='pale green',highlightbackground=self.default_color)
                if self.P.SPRINT:
                    self.serial.focus_set()      
            elif arg==7:
                self.btns1[1].configure(background='pale green',highlightbackground=self.default_color)
                self.btns1[5].configure(background='indian red',highlightbackground=self.default_color)
                self.btns1[7].configure(background='indian red',highlightbackground=self.default_color)
                if self.P.SPRINT:
                    self.btns1[1].configure(background='green',highlightbackground='green')
                    self.btns1[2].configure(background='green',highlightbackground='green')
        
        self.macro_label = self.macros[arg]["Label"]
        print("\nSend_Marco:",arg,':',self.macro_label,txt)
        if '[SERIAL]' in txt:
            cntr = self.sock.get_serial_out()
            if cntr==0 or cntr=='':
                cntr=self.P.MY_CNTR
            #print('KEYER_GUI: cntr=',cntr,'\tndigits=',self.ndigits)
            self.cntr = cw_keyer.cut_numbers(cntr,ndigits=self.ndigits)
            txt = txt.replace('[SERIAL]',self.cntr)
            self.serial_out = self.cntr
            #print('KEYER_GUI: cntr=',self.cntr,'\ttxt=',txt,'\tndigits=',self.ndigits)

        # This should have already been handled when we loaded the macros
        #txt = self.Patch_Macro(txt)

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
        txt = txt.replace('[RST]', self.get_rst() )

        if '[EXCH]' in txt:
            txt = txt.replace('[EXCH]', '' )
            self.exch_out = txt

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
        self.rst_lab.grid_remove()
        self.rst.grid_remove()
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

    # Callback for Satellite list spinner
    def set_satellite(self,val):
        print('SET_SATELLITE: val=',val)
        #print SATELLITE_LIST
        #self.SAT_TXT.set(str(SATELLITE_LIST[val]))
        self.SAT_TXT.set(val)

    def get_satellite(self):
        return self.SAT_TXT.get()
        
    # Callback for Macro list spinner
    def set_macros(self,val):
        MY_CALL = self.P.SETTINGS['MY_CALL']
        
        print('SET_MACROS: val=',val,' - ',val[0:4])
        self.macros = self.MACROS[val]
        for i in range(12):
            if False:
                print(i,i in self.macros,i+12 in self.macros)
                print(self.macros[i]["Label"])
                print(self.macros[i+12]["Label"])
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

        # Turn on correct flag
        self.P.CW_SS    = val.find('ARRL CW SS')     >= 0
        self.P.CAL_QP   = val.find('Cal QP')         >= 0
        self.P.SPRINT   = val.find('Sprint')         >= 0
        self.P.CQ_WW    = val.find('CQ WW')          >= 0
        self.P.IARU     = val.find('IARU HF')        >= 0
        self.P.ARRL_DX  = val.find('ARRL DX')        >= 0
        self.P.ARRL_10m = val.find('ARRL 10m')       >= 0
        self.P.ARRL_FD  = val.find('ARRL Field Day') >= 0
        self.P.ARRL_VHF = val.find('ARRL VHF')       >= 0
        self.P.NAQP     = val.find('NAQP')           >= 0
        self.P.SST      = val.find('SST')            >= 0
        self.P.CWops    = val.find('CWops')          >= 0
        self.P.WPX      = val.find('CQ_WPX')         >= 0
        self.P.contest_name  = get_contest_name(self.P)

        #print( self.P.CONTEST)
        for key in self.P.CONTEST.keys():
            self.P.CONTEST[key]=False
        self.P.CONTEST[val] = True
        #print( self.P.CONTEST)
                
        # Enable the specific input boxes 
        if self.P.NAQP or self.P.CWops or self.P.SST:
            # Specific contest exchange for NAQP
            self.contest=True
            self.hide_all()

            self.name_lab.grid(columnspan=1,column=4,sticky=E+W)
            self.name.grid(column=4,columnspan=2)
            if self.P.CWops:
                self.exch_lab.grid(columnspan=1,column=6,sticky=E+W)
                self.exch.grid(column=6,columnspan=2)
            else:
                self.qth_lab.grid(columnspan=1,column=6,sticky=E+W)
                self.qth.grid(column=6,columnspan=2)

            self.boxes=[self.call]
            self.boxes.append(self.name)
            self.boxes.append(self.qth)

            if not self.P.NO_HINTS:
                self.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
                self.hint.grid(column=7,columnspan=3)
                self.boxes.append(self.hint)
            
        elif self.P.ARRL_VHF:
            # Specific contest exchange for ARRL VHF
            self.contest=True
            self.hide_all()

            self.exch_lab.grid()
            self.exch_lab.grid(columnspan=3)
            self.exch.grid(columnspan=3)

            self.boxes=[self.call]
            self.boxes.append(self.exch)
            
            if not self.P.NO_HINTS:
                self.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
                self.hint.grid(column=7,columnspan=3)
                self.boxes.append(self.hint)
            
        elif self.P.ARRL_FD:
            # Specific contest exchange for ARRL Field Day
            self.contest=True
            self.hide_all()

            self.cat_lab.grid(columnspan=1,column=4,sticky=E+W)
            self.cat.grid(column=4,columnspan=2)
            self.qth_lab.grid(columnspan=1,column=6,sticky=E+W)
            self.qth.grid(column=6,columnspan=2)

            self.boxes=[self.call]
            self.boxes.append(self.cat)
            self.boxes.append(self.qth)

            if not self.P.NO_HINTS:
                self.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
                self.hint.grid(column=7,columnspan=3)
                self.boxes.append(self.hint)
            
        elif self.P.ARRL_10m:
            # Specific contest exchange for ARRL 10m
            self.contest=True
            self.hide_all()

            self.rst_lab.grid(columnspan=1,column=4,sticky=E+W)
            self.rst.grid(column=4,columnspan=1)
            self.rst.delete(0,END)
            self.rst.insert(0,'5NN')
            
            self.qth_lab.grid(columnspan=1,column=5,sticky=E+W)
            self.qth.grid(column=5,columnspan=1)

            self.boxes=[self.call]
            self.boxes.append(self.rst)
            self.boxes.append(self.qth)

            if not self.P.NO_HINTS:
                self.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
                self.hint.grid(column=6,columnspan=2)
                self.boxes.append(self.hint)
            
        elif self.P.CW_SS:
            # Specific contest exchange for CW SS
            self.contest=True
            self.hide_all()
            self.ndigits=3

            self.serial_lab.grid()
            self.serial.grid()
            self.prec_lab.grid()
            self.prec.grid()
            self.call2_lab.grid()
            self.call2.grid()
            self.check_lab.grid()
            self.check.grid()
            #self.qth_lab.grid()
            #self.qth.grid()
            self.qth_lab.grid(columnspan=3,column=8,sticky=E+W)
            self.qth.grid(column=8,columnspan=2)

            self.boxes=[self.call]
            self.boxes.append(self.serial)
            self.boxes.append(self.prec)
            self.boxes.append(self.call2)
            self.boxes.append(self.check)
            self.boxes.append(self.qth)
            self.counter_lab.grid()
            self.counter.grid()

            if not self.P.NO_HINTS:
                self.call_lab.grid(column=0,columnspan=2)
                self.call.grid(column=0,columnspan=2)
                self.serial_lab.grid(column=2)
                self.serial.grid(column=2)
                self.prec_lab.grid(column=3)
                self.prec.grid(column=3)
                self.call2_lab.grid(column=4)
                self.call2.grid(column=4)
                self.check_lab.grid(column=5)
                self.check.grid(column=5)
                self.qth_lab.grid(column=6,columnspan=1)
                self.qth.grid(column=6,columnspan=1)

                self.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
                self.hint.grid(column=7,columnspan=3)
                self.boxes.append(self.hint)
                  
        elif self.P.CAL_QP:
            # Specific contest exchange for California QSO Party
            self.contest=True
            self.hide_all()
            self.ndigits=3

            col=0
            cspan=3
            self.call_lab.grid(column=col,columnspan=cspan)
            self.call.grid(column=col,columnspan=cspan)
            col+=cspan
            cspan=2
            self.serial_lab.grid(column=col,columnspan=cspan)
            self.serial.grid(column=col,columnspan=cspan)
            col+=cspan
            cspan=2
            self.qth_lab.grid(columnspan=cspan,column=col,sticky=E+W)
            self.qth.grid(column=col,columnspan=cspan)

            self.boxes=[self.call]
            self.boxes.append(self.serial)
            self.boxes.append(self.qth)
            self.counter_lab.grid()
            self.counter.grid()
            
            if not self.P.NO_HINTS:
                col+=cspan
                cspan=3
                self.hint_lab.grid(columnspan=cspan,column=col,sticky=E+W)
                self.hint.grid(column=col,columnspan=cspan,sticky=E+W)
                self.boxes.append(self.hint)

        elif self.P.WPX:
            # Specific contest exchange for CQ WPX
            self.contest=True
            self.hide_all()
            self.ndigits=3

            self.rst_lab.grid(columnspan=1,column=4,sticky=E+W)
            self.rst.grid(column=4,columnspan=1)
            self.rst.delete(0,END)
            self.rst.insert(0,'5NN')
            
            self.serial_lab.grid(columnspan=1,column=5,sticky=E+W)
            self.serial.grid(column=5,columnspan=1)
            self.counter_lab.grid()
            self.counter.grid()

            self.boxes=[self.call]
            self.boxes.append(self.rst)
            self.boxes.append(self.serial)

        elif self.P.IARU or self.P.CQ_WW:
            # Specific contest exchange for CQ WW and IARU HF Champs
            self.contest=True
            self.hide_all()
            self.ndigits=-3

            self.rst_lab.grid(columnspan=1,column=4,sticky=E+W)
            self.rst.grid(column=4,columnspan=1)
            self.rst.delete(0,END)
            self.rst.insert(0,'5NN')
            
            self.qth_lab.grid(columnspan=1,column=5,sticky=E+W)
            self.qth.grid(column=5,columnspan=1)

            self.boxes=[self.call]
            self.boxes.append(self.rst)
            self.boxes.append(self.qth)

            if not self.P.NO_HINTS:
                self.hint_lab.grid(columnspan=3,column=6,sticky=E+W)
                self.hint.grid(column=6,columnspan=3)
                self.boxes.append(self.hint)
            
        elif self.P.SPRINT:
            # Specific contest exchange for NCCC Sprints
            self.contest=True
            self.hide_all()
            self.ndigits=1

            self.serial_lab.grid()
            self.serial.grid()
            self.name_lab.grid(columnspan=1,column=5,sticky=E+W)
            self.name.grid(column=5,columnspan=1)
            self.qth_lab.grid(columnspan=1,column=6,sticky=E+W)
            self.qth.grid(column=6,columnspan=1)

            self.boxes=[self.call]
            self.boxes.append(self.serial)
            self.boxes.append(self.qth)
            self.counter_lab.grid()
            self.counter.grid()

            if not self.P.NO_HINTS:
                self.hint_lab.grid(columnspan=3,column=7,sticky=E+W)
                self.hint.grid(column=7,columnspan=3)
                self.boxes.append(self.hint)

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
            self.rst_lab.grid()
            self.rst.grid()

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

    # Read counter from the entry box
    def update_counter(self):
        cntr = self.counter.get()
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ UPDATE COUNTER ^^^^^^^^^^^^^^^^^^^^',cntr)
        try:
            self.P.MY_CNTR = int( cntr )
        except:
            print('*** KEYER_GUI  - ERROR *** Unable to convert counter entry to int:',cntr)
        return True

    # Read his call from the entry box
    def get_call(self):
        return self.call.get()

    # Read his name from the entry box
    def get_name(self):
        txt=self.name.get().strip()
        if txt=='' and not self.contest:
            txt='OM'
        return txt

    # Read outgoing RST from the entry box
    def get_rst(self):
        txt=self.rst.get().strip()
        if txt=='':
            txt='5NN'
        return txt

    # Read exchange data from the entry box
    def get_exchange(self):
        return self.exch.get()

    # Read qth from entry box
    def get_qth(self):
        return self.qth.get()

    # Read category from entry box
    def get_cat(self):
        return self.cat.get()

    # Read serial from entry box
    def get_serial(self):
        return self.serial.get()

    # Read prec from entry box
    def get_prec(self):
        return self.prec.get()

    # Read call2 from entry box
    def get_call2(self):
        return self.call2.get()

    # Read check from entry box
    def get_check(self):
        return self.check.get()

    # Get a hint
    def get_hint(self,call):

        if len(call)>=3 and not self.P.NO_HINTS:
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
        if age<60*MAX_AGE_HOURS:
            self.P.MY_CNTR = pickle.load(fp)
            print('RestoreState: Counter=',self.P.MY_CNTR)
            self.counter.delete(0, END)
            self.counter.insert(0,str(self.P.MY_CNTR))

        # If not too much time has elapsed, restore the spots 
        if age<30:
            spots = pickle.load(fp)
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
            result=messagebox.askyesno(lab,msg)
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
            self.root.destroy()
        except:
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

        MY_CALL     = self.P.SETTINGS['MY_CALL']
        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        MY_SEC      = self.P.SETTINGS['MY_SEC']
        MY_CAT      = self.P.SETTINGS['MY_CAT']
        MY_PREC     = self.P.SETTINGS['MY_PREC']
        MY_CHECK    = self.P.SETTINGS['MY_CHECK']
        MY_COUNTY   = self.P.SETTINGS['MY_COUNTY']
        MY_CQ_ZONE  = self.P.SETTINGS['MY_CQ_ZONE']
        MY_ITU_ZONE = self.P.SETTINGS['MY_ITU_ZONE']
        MY_GRID     = self.P.SETTINGS['MY_GRID']
        
        if self.contest:
            rst='599'
            if self.P.NAQP or self.P.SST:
                exch=name+','+qth
                valid = valid and len(name)>0 and len(qth)>0
            elif self.P.CWops:
                qth = self.get_exchange().upper()
                exch=name+','+qth
                valid = valid and len(name)>0 and len(qth)>0
            elif self.P.WPX:
                rst =self.get_rst().upper()
                serial = self.get_serial().upper()
                exch=str(rst) +','+ serial
            elif self.P.IARU or self.P.CQ_WW or self.P.ARRL_10m:
                rst =self.get_rst().upper()
                #qth = self.get_exchange().upper()
                exch=str(rst) +','+ qth
            elif self.P.CW_SS:
                serial = self.get_serial().upper()
                prec   = self.get_prec().upper()
                call2  = self.get_call2().upper()
                chk    = self.get_check().upper()
                sec    = qth
                exch   = serial+','+prec+','+call+','+chk+','+sec
                valid  = valid and len(exch)>0
            elif self.P.CAL_QP:
                serial = self.get_serial().upper()
                sec    = qth
                exch   = serial+','+sec
                valid  = valid and len(exch)>0
            elif self.P.ARRL_FD:
                cat    = self.get_cat().upper()
                sec    = qth
                exch   = cat+','+sec
                valid = valid and len(cat)>0 and len(qth)>0
            elif self.P.ARRL_VHF:
                exch   = self.get_exchange().upper()
                valid  = valid and len(exch)>=4
            elif self.P.SPRINT:
                serial = self.get_serial().upper()
                sec    = qth
                exch   = serial+','+name+','+sec
                valid  = valid and len(exch)>0
            else:
                exch=self.get_exchange().upper()
                valid = valid and len(exch)>0
        else:
            rst =self.get_rst().upper()
            exch=str(rst) +' '+ name
            print('name=',name)
            print('rst=',rst)
            print('exch=',exch)

        if valid:
            print('LOG IT!',self.contest)
            #print self.sock.run_macro(-1)

            # Get time stamp, freq, mode, etc.
            UTC       = pytz.utc
            now       = datetime.utcnow().replace(tzinfo=UTC)
            date_off  = now.strftime('%Y%m%d')
            time_off  = now.strftime('%H%M%S')
            satellite = self.get_satellite()
            
            if False:
                # This is dangerous since it relies on the watchdog
                freq_kHz = 1e-3*self.sock.freq
                freq     = int( freq_kHz )
                band     = self.sock.band
                mode     = self.sock.mode
            else:
                # Read the radio instead
                freq_kHz = 1e-3*self.sock.get_freq()
                freq     = int( freq_kHz )
                mode     = self.sock.get_mode()
                band     = str( self.sock.get_band() )
                if band[-1]!='m':
                    band += 'm'

            # Do some error checking                    
            if mode!=self.sock.mode and self.sock.connection!='NONE':
                txt='##### WARNING ##### Mode mismatch in keyer_gui - radio:'+mode+'\tWoof:'+self.sock.mode
                print(txt)                          # Print error msg to terminal ...
                self.txt.insert(END, txt+'\n')      # ... and put it in the console text window
                self.txt.see(END)

            if band!=self.sock.band and self.sock.connection!='NONE':
                txt='##### WARNING ##### Band mismatch in keyer_gui - radio:'+band+'\tWoof:'+self.sock.band
                print(txt)
                self.txt.insert(END, txt+'\n')
                self.txt.see(END)
            
            # Construct exchange out
            if self.contest and (self.P.NAQP or self.P.SST):
                self.exch_out = MY_NAME+','+MY_STATE
            elif self.contest and self.P.CWops:
                self.exch_out = MY_NAME+','+MY_STATE
            elif self.contest and self.P.CW_SS:
                self.exch_out = str(self.cntr)+','+MY_PREC+','+MY_CALL+','+MY_CHECK+','+MY_SEC
            elif self.contest and self.P.SPRINT:
                self.exch_out = self(self.cntr)+','+MY_NAME+','+MY_STATE
            elif self.contest and self.P.CAL_QP:
                self.exch_out = self(self.cntr)+','+MY_COUNTY
            elif self.contest and self.P.WPX:
                self.exch_out = '599,'+str(self.cntr)
            elif self.contest and self.P.IARU:
                self.exch_out = '599,'+MY_ITU_ZONE
            elif self.contest and self.P.CQ_WW:
                self.exch_out = '599,'+MY_CQ_ZONE
            elif self.contest and self.P.ARRL_10m:
                self.exch_out = '599,'+MY_STATE
            elif self.contest and self.P.ARRL_FD:
                self.exch_out = MY_CAT+','+MY_SEC
            elif self.contest and self.P.ARRL_VHF:
                self.exch_out = MY_GRID
                
            qso = dict( list(zip(['QSO_DATE_OFF','TIME_OFF','CALL','FREQ','BAND','MODE', \
                             'SRX_STRING','STX_STRING','NAME','QTH','SRX','STX','SAT_NAME'],  \
                           [date_off,time_off,call,str(1e-3*freq_kHz),band,mode, \
                            exch,self.exch_out,name,qth,str(serial),str(self.cntr),satellite] )))
                        
            if self.P.sock3.connection=='FLLOG':
                self.P.sock3.Add_QSO(qso)

            elif self.sock.connection=='FLDIGI' and not self.P.PRACTICE_MODE:
                fields = {'Call':call,'Name':name,'RST_out':rst,'QTH':qth,'Exchange':exch}
                self.sock.set_log_fields(fields)
                self.sock.set_mode('CW')
                self.sock.run_macro(47)

            # Reset clarifier
            #self.sock.send('RC;RT0;XT0;')
            ClarReset(self)
            #self.sock.rit(0,0)

            # Make sure partice exec gets what it needs
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
            self.rst.delete(0,END)
            self.rst.insert(0,'5NN')
            self.cat.delete(0,END)

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
                print("KEYER_GUI: ADIF writing QSO=",qso2)
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
            print('*** Missing one or more fields ***',self.contest,self.P.NAQP)
            print('Call=',call)
            if self.contest:
                print('Exch=',exch)

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
                date_off = datetime.strptime( qso["QSO_DATE_OFF"]+" "+qso["TIME_OFF"] , "%Y%m%d %H%M%S") \
                                   .replace(tzinfo=UTC)
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
                match2 = self.P.sock3.Dupe_Check(call,mode,MAX_AGE_HOURS*60,freq)
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
                    match2 = match2 or (age<MAX_AGE_HOURS*3600 and qso['BAND']==band and qso['MODE']==mode)
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

                    # JBA - Probably need to fix this for ARRL SS - JBA - P.CW_SS
                    if self.P.CW_SS:
                        match2 = match2 or (age<MAX_AGE_HOURS*3600 and qso['MODE']==mode)
                    else:
                        match2 = match2 or (age<MAX_AGE_HOURS*3600 and qso['BAND']==band and qso['MODE']==mode)
                    last_exch = qso['SRX_STRING']

        # If there was a dupe, change color of call entry box & show last exchange
        if match1:
            print('Call match:',call)
            if match2:
                self.call.configure(background="coral")
            if len( self.exch.get() )==0:
                self.prefill=True
                a=last_exch.split(',')
                print('a=',a)
                if self.P.NAQP or self.P.CWops or self.P.SST:
                    self.name.delete(0,END)
                    self.name.insert(0,a[0])
                    if len(a)>=2:
                        if self.P.CWops:
                            self.exch.delete(0,END)
                            self.exch.insert(0,a[1])
                        else:
                            self.qth.delete(0,END)
                            self.qth.insert(0,a[1])
                            
                elif self.P.CW_SS:
                    if match2:
                        self.serial.delete(0,END)
                        self.serial.insert(0,a[0])
                        if len(a)>=2:
                            self.prec.delete(0,END)
                            if not self.P.PRACTICE_MODE:
                                self.prec.insert(0,a[1])
                            if len(a)>=3:
                                self.call2.delete(0,END)
                                self.call2.insert(0,a[2])
                                if len(a)>=4:
                                    self.check.delete(0,END)
                                    self.check.insert(0,a[3])
                                    if len(a)>=5:
                                        self.qth.delete(0,END)
                                        self.qth.insert(0,a[4])
                elif self.P.ARRL_10m:
                    self.qth.delete(0,END)
                    self.qth.insert(0,a[1])
                elif self.P.ARRL_FD:
                    self.cat.delete(0,END)
                    self.cat.insert(0,a[0])
                    if len(a)>=2:
                        self.qth.delete(0,END)
                        self.qth.insert(0,a[1])
                elif self.P.ARRL_VHF:
                    self.exch.delete(0,END)
                    self.exch.insert(0,a[0])
                elif self.P.WPX:
                    self.serial.delete(0,END)
                elif self.P.IARU or self.P.CQ_WW:
                    self.qth.delete(0,END)  
                    if len(a)>=2:
                        self.qth.insert(0,a[1])
                elif self.P.CAL_QP:
                    self.serial.delete(0,END)
                    if len(a)>=2:
                        self.qth.delete(0,END)
                        self.qth.insert(0,a[1])
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
                if self.P.CWops:
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


    
    # Callback when a key is pressed in an entry box
    def key_press(self,event,id=None):

        key   = event.keysym
        num   = event.keysym_num
        ch    = event.char
        state = event.state

        print("Key Press:",key) #,ch,len(key),num

        # Modfiers
        shift     = ((state & 0x0001) != 0)
        #caps_lock = state & 0x0002
        control   = (state & 0x0004) != 0
        alt       = (state & 0x0088) != 0                 # Both left and right ALTs
        #num_lock  = state & 0x0010
        #mouse1 = state & 0x0100
        #mouse2 = state & 0x0200
        #mouse3 = state & 0x0400

        #print('State:',state,shift,control,alt)
        #print event

        # This should never happen
        if len(key)==0:
            return

        # Check for special keys
        if len(key)>=2 or alt or control:
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
            if (key=='Delete' and True) or (key=='w' and alt):
                print('Delete - clear box')
                if event.widget!=self.txt:
                    event.widget.delete(0,END)     # Clear the entry box
                    if event.widget==self.call:
                        self.call.configure(background=self.default_color)

                # Wipe all fields
                if (key=='w' or key=='e') and alt:
                    self.call.delete(0, END)
                    self.call2.delete(0, END)
                    self.cat.delete(0, END)
                    self.rst.delete(0, END)
                    self.rst.insert(0,'5NN')
                    self.exch.delete(0, END)
                    self.name.delete(0, END)
                    self.qth.delete(0, END)
                    self.serial.delete(0, END)
                    self.prec.delete(0, END)
                    self.hint.delete(0, END)
                    self.check.delete(0, END)

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
                if self.P.ARRL_FD:
                    self.cat.delete(0, END)
                    self.cat.insert(0,h[0])
                    self.qth.delete(0, END)
                    self.qth.insert(0,h[1])
                    
                elif self.P.ARRL_10m:
                    self.qth.delete(0, END)
                    self.qth.insert(0,h[0])
                    
                elif self.P.ARRL_VHF:
                    self.exch.delete(0, END)
                    self.exch.insert(0,h[0])
                    
                elif self.P.IARU or self.P.CQ_WW:
                    self.qth.delete(0, END)
                    self.qth.insert(0,h[0])
                    
                elif self.P.CAL_QP:
                    self.qth.delete(0, END)
                    self.qth.insert(0,h[0])
                    
                elif self.P.CW_SS:
                    self.check.delete(0, END)
                    self.check.insert(0,h[0])
                    self.qth.delete(0, END)
                    self.qth.insert(0,h[1])
                    
                elif self.P.NAQP or self.P.SPRINT or self.P.CWops or self.P.SST:
                    i=0
                    #if self.P.SPRINT:
                    #    i=1
                    self.name.delete(0, END)
                    self.name.insert(0,h[i])
                    if self.P.CWops:
                        self.exch.delete(0, END)
                        if len( h[i+2] )>0:
                            self.exch.insert(0,h[i+2])
                        else:
                            self.exch.insert(0,h[i+1])
                    else:
                        self.qth.delete(0, END)
                        self.qth.insert(0,h[i+1])

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
                    if (self.P.NAQP or self.P.CW_SS or self.P.CAL_QP or \
                        self.P.SPRINT or self.P.SST or self.P.ARRL_10m or \
                        self.P.ARRL_FD or self.P.IARU or self.P.CQ_WW) \
                        and event.widget==self.qth:
                        #print 'QTH box',key,len(key),key=='Tab'
                        self.call.focus_set()
                        return("break")
                    elif self.P.CWops and event.widget==self.exch:
                        self.call.focus_set()
                        return("break")
                    elif self.P.WPX and event.widget==self.serial:
                        self.call.focus_set()
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
                if self.contest and (self.P.NAQP or self.P.CWops or self.P.SST):
                    next_widget=self.name
                    self.Send_Macro(1)                     # Send reply

                elif self.contest and self.P.ARRL_FD:
                    next_widget=self.cat
                    self.Send_Macro(1)                     # Send reply

                elif self.contest and self.P.ARRL_VHF:
                    next_widget=self.exch
                    self.Send_Macro(1)                     # Send reply

                elif self.contest and self.P.WPX:
                    next_widget=self.serial
                    self.Send_Macro(1)                     # Send reply

                elif self.contest and (self.P.IARU or self.P.CQ_WW or self.P.ARRL_10m):
                    next_widget=self.qth
                    self.Send_Macro(1)                     # Send reply

                elif self.contest and self.P.CW_SS:
                    self.call2.delete(0, END)
                    self.call2.insert(0,call)
                    next_widget=self.serial
                    self.Send_Macro(1)                     # Send reply

                elif self.contest and self.P.SPRINT:
                    next_widget=self.serial
                    if self.P.LAST_MSG==0:
                        self.Send_Macro(1)                 # Send reply
                    else:
                        self.Send_Macro(4)                 # Send my call

                elif self.contest and self.P.CAL_QP:
                    next_widget=self.serial
                    self.Send_Macro(1)                     # Send reply

                    self.dx_station = Station(call)
                    #pprint(vars(self.dx_station))

            # Take care of hints
            if self.contest:
                self.get_hint(call)
                                        
            if self.P.CW_SS:
                #print 'boxes=',self.boxes
                #idx=self.boxes.index(self.call)
                #print 'idx=',idx
                if key=='Tab':
                    self.call2.delete(0, END)
                    self.call2.insert(0,call)
                    self.get_hint(call)
                    self.force_focus(self.serial)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.call2.delete(0, END)
                    self.call2.insert(0,call)
                    self.force_focus(self.qth)
                    return("break")
            
            elif self.P.ARRL_FD:
                if key=='Tab':
                    self.force_focus(self.cat)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")

            elif self.P.WPX:
                if key=='Tab':
                    self.force_focus(self.rst)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.serial)
                    return("break")

            elif self.P.IARU or self.P.CQ_WW or self.P.ARRL_10m:
                if key=='Tab':
                    self.force_focus(self.rst)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.qth)
                    return("break")

            elif self.P.CAL_QP or self.P.SPRINT:
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
                if self.contest and (self.P.NAQP or self.P.SPRINT or self.P.SST):
                    next_widget=self.qth
                elif self.contest and self.P.CWops:
                    next_widget=self.exch

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

            # If we're in a contest and the return key was pressed, send reply
            if key=='Return' or key=='KP_Enter':
                if self.contest:
                    next_widget=self.qth
                    if self.P.NAQP or self.P.CWops or self.P.SST or \
                       self.P.CW_SS or self.P.CAL_QP or self.P.ARRL_FD or \
                       self.P.IARU or self.P.CQ_WW or self.P.ARRL_10m:
                        self.Send_Macro(2)                     # Send TU

                    elif self.P.SPRINT:

                        if self.P.LAST_MSG==0:
                            self.Send_Macro(2)                     # Send TU
                        elif self.P.LAST_MSG==5:
                            self.Send_Macro(7)                     # Log the QSO
                            #self.Send_Macro(0)                    # Send CQ
                        else:
                            self.Send_Macro(5)                     # Send my excahnge

                    else:
                        print('!!!!!!!!!!!!! KEYER_GUI - should never get here !!!!!!!!!!')
                        
            if self.P.CW_SS:
                if key=='Tab':
                    self.force_focus(self.call)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.check)
                    return("break")

            elif self.P.SPRINT:
                if key=='Tab':
                    self.force_focus(self.call)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.name)
                    return("break")

            elif self.P.CAL_QP:
                if self.P.NO_HINTS:
                    h=None
                else:
                    h = hint.commie_fornia(self.dx_station,qth)
                    if h:
                        print('hint=',h)
                        self.hint.delete(0, END)
                        self.hint.insert(0,h)
                
                if key=='Tab':
                    self.force_focus(self.call)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.serial)
                    return("break")
            
        elif event.widget==self.cat:
            cat=self.get_cat().upper()
            #self.sock.set_log_fields({'RST_out':rst})
            if self.P.ARRL_FD:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.qth)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")

        elif event.widget==self.rst:
            rst=self.get_rst().upper()
            self.sock.set_log_fields({'RST_out':rst})
            if self.P.WPX:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.serial)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")
            elif self.P.ARRL_10m:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.qth)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")

        elif event.widget==self.exch:
            exch=self.get_exchange().upper()
            self.sock.set_log_fields({'Exchange':exch})

            # If we're in a contest and the return key was pressed, send reply
            if key=='Return' or key=='KP_Enter':
                if self.contest:
                    #next_widget=self.call
                    if self.P.CWops or self.P.ARRL_VHF:
                        self.Send_Macro(2)                     # Send TU

            
        elif event.widget==self.counter:
            print('^^^^^^^^^^^ Counter window',self.P.MY_CNTR)
            
        elif event.widget==self.serial:
            serial=self.get_serial().upper()
            
            self.sock.set_log_fields({'Serial_out':serial})
            if self.P.CW_SS:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.prec)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")
            elif self.P.CAL_QP:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.qth)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")
            elif self.P.WPX:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.call)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.rst)
                    return("break")
            elif self.P.SPRINT:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.name)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call)
                    return("break")
                
        elif event.widget==self.prec:
            prec=self.get_prec().upper()
            self.sock.set_log_fields({'Prec':prec})
            if self.P.CW_SS:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.call2)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.serial)
                    return("break")

        elif event.widget==self.call2:
            call2=self.get_call2().upper()
            self.sock.set_log_fields({'Call2':call2})
            if self.P.CW_SS:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.call.delete(0, END)
                    self.call.insert(0,call2)
                    self.force_focus(self.check)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.call.delete(0, END)
                    self.call.insert(0,call2)
                    self.force_focus(self.prec)
                    return("break")

        elif event.widget==self.check:
            print('!!!Check!!!')
            check=self.get_check().upper()
            self.sock.set_log_fields({'Check':check})
            if self.P.CW_SS:
                if key=='Tab' or key=='Return' or key=='KP_Enter':
                    self.force_focus(self.qth)
                    return("break")
                elif key=='ISO_Left_Tab':
                    self.force_focus(self.call2)
                    return("break")
            
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
