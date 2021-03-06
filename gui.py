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
#import pickle
from fileio import *
from threading import enumerate

from cwt import *
from cwopen import *
from sst import *
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
from sidetone import init_sidetone
from utilities import cut_numbers

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

        # Create spash screen
        self.splash  = Toplevel(self.root)
        self.splash.title("Splish Splash")
        if P.PLATFORM=='Linux':
            self.splash.attributes("-topmost", True,'-type', 'splash')
        elif P.PLATFORM=='Windows':
            self.splash.attributes("-topmost", True)
        else:
            print('GUI INIT: Unknown OS',P.PLATFORM)
            sys.exit(0)

        pic = tk.PhotoImage(file='keyer_splash.png')
        lab=tk.Label(self.splash, bg='white', image=pic)
        #lab=tk.Label(self.splash, image=pic)
        lab.pack()
        self.root.withdraw()
        self.splash.deiconify()

        #self.root.eval('tk::PlaceWindow . Center')
        #splash.after(4000, splash.destroy)
        self.root.update_idletasks()

        # Init
        self.Done=False
        self.contest = False
        self.P = P
        self.P.LAST_MSG = -1
        self.P.root = self.root
        self.text_buff=''

    # Function to actually construct the gui
    def construct_gui(self):
        P=self.P

        # More inits
        self.keyer=P.keyer;
        self.start_time = None
        self.time_on = None
        print('TiMe On=',self.time_on)
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
        fname = P.DATA_DIR+MY_CALL.replace('/','_')+".LOG"
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
                else:
                    call=qso['CALL']
                    if not call in P.calls:
                        #print('Call not in Master list:',call,'\t- Adding it')
                        self.log_book.append(qso)
                        P.calls.append(call)
        except:
            pass

        # Read adif log also
        if P.LOG_FILE==None:
            P.LOG_FILE = P.DATA_DIR+MY_CALL.replace('/','_')+".adif"
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
        self.fp_txt = open(P.DATA_DIR+MY_CALL.replace('/','_')+".TXT","a+")

        # Create pop-up window for Settings and Paddle Practice - Need these before we can create the menu
        self.SettingsWin = SETTINGS_GUI(self.root,self.P)
        self.SettingsWin.hide()
        self.PaddlingWin = PADDLING_GUI(self.root,self.P)
        if P.SENDING_PRACTICE:
            self.PaddlingWin.show()
        else:
            self.PaddlingWin.hide()
        
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
        self.rstin.grid(row=row+1,rowspan=2,column=8,columnspan=1,sticky=E+W)

        self.rstout_lab = Label(self.root, text="RST out",font=font1)
        self.rstout_lab.grid(row=row,columnspan=1,column=9,sticky=E+W)
        self.rstout = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.rstout.grid(row=row+1,rowspan=2,column=9,columnspan=1,sticky=E+W)
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
        self.qth.grid(row=row+1,rowspan=2,column=8,columnspan=2,sticky=E+W)

        self.serial_lab = Label(self.root, text="Serial",font=font1)
        self.serial_lab.grid(row=row,columnspan=1,column=4,sticky=E+W)
        self.serial = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.serial.grid(row=row+1,rowspan=2,column=4,columnspan=1,sticky=E+W)

        self.prec_lab = Label(self.root, text="Prec",font=font1)
        self.prec_lab.grid(row=row,columnspan=1,column=5,sticky=E+W)
        self.prec = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.prec.grid(row=row+1,rowspan=2,column=5,columnspan=1,sticky=E+W)

        self.cat_lab = Label(self.root, text="Category",font=font1)
        self.cat_lab.grid(row=row,columnspan=1,column=5,sticky=E+W)
        self.cat = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.cat.grid(row=row+1,rowspan=2,column=5,columnspan=1,sticky=E+W)

        self.call2_lab = Label(self.root, text="Call",font=font1)
        self.call2_lab.grid(row=row,columnspan=1,column=6,sticky=E+W)
        self.call2 = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.call2.grid(row=row+1,rowspan=2,column=6,columnspan=1,sticky=E+W)

        self.check_lab = Label(self.root, text="Check",font=font1)
        self.check_lab.grid(row=row,columnspan=1,column=7,sticky=E+W)
        self.check = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd)
        self.check.grid(row=row+1,rowspan=2,column=7,columnspan=1,sticky=E+W)
        
        self.notes_lab = Label(self.root, text="Notes",font=font1)
        self.notes_lab.grid(row=row,columnspan=1,column=8,sticky=E+W)
        self.notes = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd,fg='blue')
        self.notes.grid(row=row+1,rowspan=2,column=8,columnspan=1,sticky=E+W)

        self.hint_lab = Label(self.root, text="Hint",font=font1)
        self.hint_lab.grid(row=row,columnspan=1,column=8,sticky=E+W)
        self.hint = Entry(self.root,font=font2,validate='focusin',validatecommand=vcmd,fg='blue')
        self.hint.grid(row=row+1,rowspan=2,column=8,columnspan=1,sticky=E+W)

        self.scp_lab = Label(self.root, text="Super Check Partial",font=font1)
        self.scp_lab.grid(row=row,columnspan=1,column=9,sticky=E+W)
        self.scp = Entry(self.root,font=font2,validate='focusin',
                         validatecommand=vcmd,fg='blue')
        self.scp.grid(row=row+1,rowspan=2,column=9,columnspan=1,sticky=E+W)

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

        # Make sure all columns are adjusted when we resize the width of the window
        for i in range(12):
            Grid.columnconfigure(self.root, i, weight=1,uniform='twelve')

        # Set up two text entry box with a scroll bar
        # The upper box is so we can type in what we receive
        row+=3
        self.txt2_row=row
        self.txt2 = Text(self.root, height=5, width=80, bg='white')
        self.txt2.grid(row=row,column=0,columnspan=ncols,stick=N+S+E+W)
        self.S2 = Scrollbar(self.root)
        self.S2.grid(row=row,column=ncols,sticky=N+S)
        self.S2.config(command=self.txt2.yview)
        self.txt2.config(yscrollcommand=self.S2.set)
        self.txt2.bind("<Tab>", self.key_press )
        self.show_hide_txt2()
            
        # The lower box is so we can type in what we want to send
        row+=1
        Grid.rowconfigure(self.root, row, weight=1)             # Allows resizing
        self.txt = Text(self.root, height=5, width=80, bg='white')
        self.txt.grid(row=row,column=0,columnspan=ncols,stick=N+S+E+W)
        self.S = Scrollbar(self.root)
        self.S.grid(row=row,column=ncols,sticky=N+S)
        self.S.config(command=self.txt.yview)
        self.txt.config(yscrollcommand=self.S.set)
        self.txt.bind("<Tab>", self.key_press )

        # Bind a callback to be called whenever a key is pressed
        self.root.bind("<Key>", self.key_press )
        #self.root.bind("all", self.key_press )

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
        SB = OptionMenu(self.root, \
                        self.MACRO_TXT, \
                        *self.P.CONTEST_LIST, \
                        command=self.set_macros)
        SB.grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        col += 3

        # Set up a spin box to control keying speed (WPM)
        self.WPM_TXT = StringVar()
        Label(self.root, text='Speed:').grid(row=row,column=col,sticky=E+W)
        SB = Spinbox(self.root,                 \
                     from_=cw_keyer.MIN_WPM,    \
                     to=cw_keyer.MAX_WPM,       \
                     textvariable=self.WPM_TXT, \
                     bg='white',                \
                     command=lambda j=0: self.set_wpm(0))
        SB.grid(row=row,column=col+1,columnspan=1,sticky=E+W)
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

        # Enable/Disable TX button - should be sufficient to just press <CR> in the txt box
        # Put in a pull-down menu if we really need this
        if True:
            self.P.Immediate_TX = True
            self.SendBtn = Button(self.root, text='Send',command=self.Toggle_Immediate_TX,\
                                  takefocus=0 ) 
            self.SendBtn.grid(row=row,column=ncols-2)
            tip = ToolTip(self.SendBtn, ' Enable/Disable Immediate Text Sending ' )
            self.Toggle_Immediate_TX()
        
        # QRZ button
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
        
        # Reset clarifier
        ClarReset(self)

        # Some other info
        #row += 1
        #col=0
        col=8
        self.rate_lab = Label(self.root, text="QSO Rate:",font=font1)
        self.rate_lab.grid(row=row,columnspan=4,column=col,sticky=W)

        # Other capabilities accessed via menu
        self.rig = RIG_CONTROL(P)
        
        # Add a tab to manage Rotor
        # This is actually rather difficult since there doesn't
        # appear to be a tk equivalent to QLCDnumber
        self.rotor_ctrl = ROTOR_CONTROL(self.rig.tabs,P)

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
        self.root.deiconify()
        #splash.withdraw()
        self.splash.destroy()
        self.root.update_idletasks()


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
        self.call.configure(fg='black')
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
        print("You selected radio " + str(iRadio),'\tP.sock=',self.P.sock)
        rig=P.sock.rig_type2
        self.root.title("pyKeyer by AA2IL"+rig)
        
    # Callback to toggle sending of text
    def Toggle_Immediate_TX(self):
        self.P.Immediate_TX = not self.P.Immediate_TX 
        print('Toggle_Text_TX:',self.P.Immediate_TX,self.text_buff)
        if self.P.Immediate_TX:
            self.SendBtn.configure(background='red',highlightbackground= 'red')
            self.q.put(self.text_buff)
            self.text_buff=''
        else:
            self.SendBtn.configure(background='Green',highlightbackground= 'Green')
        
    # Callback to look up a call on qrz.com
    def Call_LookUp(self):
        call = self.get_call()
        if len(call)>=3:
            print('CALL_LOOKUP: Looking up '+call+' on QRZ.com')
            if True:
                link = 'https://www.qrz.com/db/' + call
                webbrowser.open(link, new=2)

            self.qrzWin = CALL_INFO_GUI(self.root,self.P,call,self.last_qso)
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
            
    # Callback to bring up rig control menu
    def RigCtrlCB(self):
        print("^^^^^^^^^^^^^^Rig Control...")
        self.rig.show()

    # Callback to key/unkey TX for tuning
    def Tune(self):
        print("Tuning...")
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
            self.qth_out = self.P.SETTINGS['MY_CQ_ZONE']
            txt = txt.replace('[MYCQZ]', self.qth_out )
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
        
        his_name=self.get_name().replace('?','')
        if '?' in his_name:
            his_name=' '
        txt = txt.replace('[NAME]',his_name )
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
            self.cntr = cut_numbers(cntr,ndigits=self.ndigits)
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
        self.notes_lab.grid_remove()
        self.notes.grid_remove()
        self.hint_lab.grid_remove()
        self.hint.grid_remove()
        self.scp_lab.grid_remove()
        self.scp.grid_remove()
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

        print('SET_MACROS: val=',val)
        if not val:
            val=self.P.contest_name
            self.MACRO_TXT.set(val)
        print('SET_MACROS: val=',val)

        #idx = self.P.CONTEST_LIST.index(val)
        #print('SET_MACROS: val=',val,'\tidx=',idx,'\t)

        # Initiate keying module for this contest
        if val=='CWT':
            self.P.KEYING=CWOPS_KEYING(self.P)
        elif val=='SST':
            self.P.KEYING=SST_KEYING(self.P)
        elif val=='MST':
            self.P.KEYING=MST_KEYING(self.P)
        elif val=='SKCC':
            self.P.KEYING=SKCC_KEYING(self.P)
        elif val=='CALLS':
            self.P.KEYING=CALLS_KEYING(self.P)
        elif val=='CW Open':
            self.P.KEYING=CWOPEN_KEYING(self.P)
        elif val=='SATELLITES':
            self.P.KEYING=SAT_KEYING(self.P)
        elif val=='ARRL-VHF' or val=='CQ-VHF' or val=='STEW PERRY':
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
        elif val=='RANDOM CALLS':
            self.P.KEYING=RANDOM_CALLS_KEYING(self.P)
        else:
            print('SET_MACROS: *** ERROR *** Cant figure which contest !')
            print('val=',val)
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
        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ UPDATE COUNTER ^^^^^^^^^^^^^^^^^^^^',cntr)
        try:
            if cntr=='':
                self.P.MY_CNTR = 1
                self.counter.delete(0, END)
                self.counter.insert(0,str(self.P.MY_CNTR))
            else:
                self.P.MY_CNTR = int( cntr )
        except Exception as e: 
            print('*** GUI  - ERROR *** Unable to convert counter entry to int:',cntr)
            print( str(e) )
            
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
        #print('GET_HINT: call=',call)

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
        #print('GET_HINT: h=',h)
        if h:
            self.hint.insert(0,h)
        self.last_hint=h

        return h


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
        now = datetime.utcnow().replace(tzinfo=UTC)

        #obj.strftime('%Y-%m-%d %H:%M:%S')
        
        STATE={'now' : now.strftime('%Y-%m-%d %H:%M:%S'), 
               'bookmark' : self.PaddlingWin.bookmark-1,
               'serial' : self.P.MY_CNTR,
               'spots' : spots,
               'freqs' : frqs,
               'fields' : flds }
        print('STATE=',STATE)
        with open('state.json', "w") as outfile:
            json.dump(STATE, outfile)

        """
        fp = open('state.pcl', 'wb')
        pickle.dump(now, fp)
        pickle.dump(self.PaddlingWin.bookmark-1, fp)
        pickle.dump(self.P.MY_CNTR, fp)
        pickle.dump(spots, fp)
        pickle.dump(frqs, fp)
        pickle.dump(flds, fp)
        fp.close()
        """
        
        self.P.DIRTY=False
        print('SaveState: cntr=',self.P.MY_CNTR)
        #print('SaveState:',spots)
        #print('SaveState:',frqs)
        #print('SaveState:',flds)

    # Clear store/recall butons
    def ClearState(self):

        for i in range(len(self.spots)):
            self.spots[i]['Button']['text'] = '--'
            self.spots[i]['Freq']=None
            self.spots[i]['Fields']=None
            self.P.DIRTY = True
                
    
    # Restore program state
    def RestoreState(self):
        try:
            #fp = open('state.pcl', 'rb')
            with open('state.json') as json_data_file:
                STATE = json.load(json_data_file)
            print('STATE=',STATE)
        except:
            print('RestoreState: state.json not found')
            return
            
        now        = datetime.utcnow().replace(tzinfo=UTC)

        #time_stamp = pickle.load(fp)
        time_stamp = datetime.strptime( STATE['now'] , '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC)
        
        age = (now - time_stamp).total_seconds()/60  
        print('RestoreState: now=',now,'\ntime_stamp=',time_stamp,
              '\nAge=',age,' mins.')

        # Restore the book mark
        #self.PaddlingWin.bookmark = max( pickle.load(fp) ,0 )
        #print('BOOKMARK=',self.PaddlingWin.bookmark)
        #sys.exit(0)
        self.PaddlingWin.bookmark = max( STATE['bookmark'] ,0 )
        print('RestoreState: Bookmark=',self.PaddlingWin.bookmark)

        # If we're in a long contest, restore the serial counter
        if age<self.P.MAX_AGE:
            #self.P.MY_CNTR = pickle.load(fp)
            self.P.MY_CNTR = STATE['serial']
            print('RestoreState: Counter=',self.P.MY_CNTR)
            self.counter.delete(0, END)
            self.counter.insert(0,str(self.P.MY_CNTR))

        # If not too much time has elapsed, restore the spots 
        if age<30:
            #spots = pickle.load(fp)
            spots = STATE['spots']
            if len(spots)>12*self.P.NUM_ROWS:
                spots=spots[:12*self.P.NUM_ROWS]
            print('RestoreState: Spots=',spots)
            #frqs = pickle.load(fp)
            #flds = pickle.load(fp)
            frqs = STATE['freqs']
            flds = STATE['fields']
            for i in range(len(spots)):
                print(i,len(spots),len(self.spots))
                self.spots[i]['Button']['text'] = spots[i]
                self.spots[i]['Freq']=frqs[i]
                self.spots[i]['Fields']=flds[i]
                
        #fp.close()
        self.P.DIRTY=False
        #sys.exit(0)

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
        try:
            self.keyer.abort()     
            if not self.q.empty():
                self.q.get(False)
                self.q.task_done()
        except:
            pass                

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
        notes =self.get_notes()
        print('LOG_QSO:',call,name,qth)
        serial=0

        MY_NAME     = self.P.SETTINGS['MY_NAME']
        MY_STATE    = self.P.SETTINGS['MY_STATE']
        
        if self.contest:
            rst='5NN'
            exch,valid,self.exch_out,qso2 = self.P.KEYING.logging()
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
            #UTC       = pytz.utc
            now       = datetime.utcnow().replace(tzinfo=UTC)
            if not self.start_time:
                self.start_time = now
            date_off  = now.strftime('%Y%m%d')
            time_off  = now.strftime('%H%M%S')
            if self.P.contest_name=='Ragchew':
                print('TIME ON=',self.time_on)
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
            mode     = self.sock.get_mode()
            if mode=='FMN':
                mode='FM'
            elif mode=='AMN':
                mode='AM'
            band     = str( self.sock.get_band() )
            if band=='None':
                print('*** WARNING - Cant determine band - no rig connection?')
            elif band[-1]!='m':
                band += 'm'

            # For satellites, read vfo B also  - MOVE THIS TO LOGGING() IN SATS.PY
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

            # Construct QSO record
            qso = dict( list(zip(['QSO_DATE_ON','TIME_ON',
                                  'QSO_DATE_OFF','TIME_OFF',
                                  'CALL','FREQ','BAND','MODE', 
                                  'SRX_STRING','STX_STRING','NAME','QTH','SRX',
                                  'STX','SAT_NAME','FREQ_RX','BAND_RX','NOTES'],
                                 [date_on,time_on,date_off,time_off,
                                  call,str(1e-3*freq_kHz),band,mode, 
                                  exch,self.exch_out,name,qth,str(serial),
                                  str(self.cntr),satellite,
                                  str(1e-3*freq_kHz_rx),band_rx,notes] )))
            qso.update(qso2)

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
            ClarReset(self)

            # Make sure practice exec gets what it needs
            if self.P.PRACTICE_MODE:
                print('LOG_QSO - PRACTICE MODE: Waiting for handshake ...',\
                      self.keyer.evt.isSet(),\
                      '\nIf you want to log an actual contact, exit PRACTICE_MODE and try again')
                while self.keyer.evt.isSet():
                    #print( self.keyer.evt.isSet(), self.keyer.stop )
                    time.sleep(0.1)
                print('LOG_QSO: Got handshake ...',\
                      self.keyer.evt.isSet(), self.keyer.stop )

            # Clear fields
            self.prefill=False
            self.call.delete(0,END)
            self.prev_call=''
            self.call.focus_set()
            self.call.configure(bg=self.default_color,fg='black')
            self.name.delete(0,END)
            self.qth.delete(0,END)
            self.notes.delete(0,END)
            self.hint.delete(0,END)
            self.scp.delete(0,END)
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
        self.time_on = datetime.utcnow().replace(tzinfo=UTC)
        #print('Time on=',self.time_on)

        # Look for dupes
        self.match1=False                # True if there is matching call
        self.match2=False                # True if the match is within the last 48 hours on current band and mode
        last_exch=''
        self.last_qso=None
        now = datetime.utcnow().replace(tzinfo=UTC)
        if self.P.sock3.connection=='FLLOG' and True:
            freq   = self.sock.get_freq()
            mode   = self.sock.get_mode()
            self.match1 = self.P.sock3.Dupe_Check(call)
            print('match1=',self.match1)
            if self.match1:
                self.match2 = self.P.sock3.Dupe_Check(call,mode,self.P.MAX_AGE,freq)
                print('match2=',self.match2)
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
                    self.match2 = self.match2 or (age<self.P.MAX_AGE*60 and qso['BAND']==band and qso['MODE']==mode)
                    print('match 1 & 2:',self.match1,self.match2)

        else:

            for qso in self.log_book:
                if qso['CALL']==call:
                    self.match1 = True
                    self.last_qso=qso
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
                            match4 = qth==qso['QTH']
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
        if self.match1:
            print('Call match:',call)
            if self.match2:
                self.call.configure(bg="coral")
            else:
                self.call.configure(bg="lemon chiffon")
                
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

        # Well this is screwy - there seems to be a difference between
        # linux and windoz
        if platform.system()=='Linux':
            #alt       = (state & 0x0088) != 0     # Both left and right ALTs
            alt       = (state & 0x0008) != 0 
            #num_lock  = state & 0x0010
        elif platform.system()=='Windows':
            alt       = (state & 0x20000) != 0 
            #num_lock  = state & 0x008
            
        #mouse1 = state & 0x0100
        #mouse2 = state & 0x0200
        #mouse3 = state & 0x0400

        if True:
            print("Key Press:",key,'\tState:',hex(state),shift,control,alt)
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

            if key=='Prior':
                print('WPM Up')
                self.set_wpm(dWPM=+WPM_STEP)
                
            if key=='Next':
                print('WPM Down')
                self.set_wpm(dWPM=-WPM_STEP)

            # Quick way to send '?'
            if key in ['slash','question'] and (alt or control):
                self.q.put('?')
                return("break")

            # Reverse call sign lookup
            if key=='r' and (alt or control):
                self.P.KEYING.reverse_call_lookup()

            # This works but seemed problematic in normal operating??
            if (key=='Delete' and False) or (key=='w' and (alt or control)):
                #print('DELETE - CLEAR BOX ...')
                if event.widget==self.txt or event.widget==self.txt2:
                    #print('Text Box ...')
                    event.widget.delete(1.0,END)     # Clear the entry box
                    return("break")
                else:
                    #print('Not in Text Box ...')
                    event.widget.delete(0,END)     # Clear the entry box
                    if event.widget==self.call:
                        self.call.configure(background=self.default_color)

                # Wipe all fields Alt-w
                if (key=='w' or key=='e') and (alt or control):
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
                    self.serial.delete(0, END)
                    self.prec.delete(0, END)
                    self.hint.delete(0, END)
                    self.check.delete(0, END)
                    self.qsl_rcvd.set(0)

                    next_widget=self.call
                    self.call.focus_set()
                    return("break")

            # Copy hints to fields
            if key=='Insert' or (key=='i' and (alt or control)):
                if False:
                    h = self.hint.get()
                    print('h=',h,len(h))
                    if len(h)==0:
                        return "break"
                    h = h.split(' ')
                    print('h=',h)
                    
                self.P.KEYING.insert_hint()
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
                self.fp_txt.write('ESCAPE!!!!!\n')
                self.fp_txt.flush()
                
                self.keyer.abort()     
                if not self.q.empty():
                    self.q.get(False)
                    self.q.task_done()

            # Move to next entry box
            if key=='Tab':
                if event.widget==self.txt:
                    self.txt2.focus_set()
                elif event.widget==self.txt2:
                    self.txt.focus_set()
                elif event.widget==self.txt or event.widget==self.txt2:
                    print('Text box',key,len(key),key=='Tab')
                    self.call.focus_set()
                elif self.contest:
                    self.P.KEYING.next_event(key,event)
                return("break")

            elif key=='ISO_Left_Tab':
                if event.widget==self.txt:
                    self.txt2.focus_set()
                elif event.widget==self.txt2:
                    self.txt.focus_set()
                elif event.widget==self.txt or event.widget==self.txt2:
                    self.call.focus_set()
                else:
                    self.P.KEYING.next_event(key,event)
                return("break")
                    
            # Return key in the text box - nothing to do
            if (key=='Return' or key=='KP_Enter') and \
               event.widget!=self.txt and event.widget!=self.txt2 and True:
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

        # Are we in a text window?
        next_widget=event.widget             # Next widget is by default the current widget
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
            # Upper text window 
            #print('UPPER TEXT WINDOW')
            pass

        # Update info in fldigi
        elif event.widget==self.call:
            call=self.get_call().upper()
            self.sock.set_log_fields({'Call':call})
            self.dup_check(call)
            if self.P.USE_SCP:
                scps=self.P.KEYING.SCP.match(call)
                self.scp.delete(0, END)
                self.scp.insert(0, scps)
                if len(scps)>0 and call==scps[0]:
                    self.call.configure(fg='red')
                else:
                    self.call.configure(fg='black')
                

            # If we're in a contest and the return key was pressed,
            # send response and get ready for the exchange
            if (key=='Return' or key=='KP_Enter') and len(call)>0:
                print('*_*_*_*_*_*_*_*_*_* PRACTICE_STATE=',self.P.PRACTICE_STATE)
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
                if self.P.AUTOFILL:
                    self.P.KEYING.insert_hint()
                
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
            if key=='Return' or key=='KP_Enter':
                next_widget = self.P.KEYING.next_event(key,event)

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

    # Callback for practice with computer text
    def PracticeCB(self):
        self.P.PRACTICE_MODE = not self.P.PRACTICE_MODE

    # Callback to toggle auto filling of hints info
    def AutoFillCB(self):
        self.P.AUTOFILL = not self.P.AUTOFILL

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
        if self.P.SIDETONE and not self.P.q2:
            init_sidetone(self.P)

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
        else:
            self.scp_lab.grid_remove()
            self.scp.grid_remove()
               
############################################################################################
    
    # Function to create menu bar
    def create_menu_bar(self):
        print('Creating Menubar ...')
                   
        menubar = Menu(self.root)
        Menu1 = Menu(menubar, tearoff=0)

        Menu1.add_command(label="Settings ...", command=self.SettingsWin.show)
        Menu1.add_command(label="Rig Control ...", command=self.RigCtrlCB)
        Menu1.add_command(label="Paddling ...", command=self.PaddlingWin.show)
        Menu1.add_command(label="Clear Stores ...", command=self.ClearState)
        Menu1.add_separator()
        
        self.Capturing = BooleanVar(value=self.P.CAPTURE)
        Menu1.add_checkbutton(
            label="Capture Audio",
            underline=0,
            variable=self.Capturing,
            command=self.P.capture.CaptureAudioCB
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
        
        self.SplitTxt = BooleanVar(value=self.P.SHOW_TEXT_BOX2)
        Menu1.add_checkbutton(
            label="Split Text Win",
            underline=0,
            variable=self.SplitTxt,
            command=self.SplitTextCB
        )
        
        Menu1.add_separator()
        Menu1.add_command(label="Exit", command=self.Quit)
        menubar.add_cascade(label="File", menu=Menu1)

        self.root.config(menu=menubar)


        
        
