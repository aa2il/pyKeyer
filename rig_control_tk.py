############################################################################################
#
# Rig Control GUI - Tk version - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
from rig_io.ft_tables import *
from ft_keypad import *
from functools import partial
from os import system

################################################################################

class RIG_CONTROL():
    def __init__(self,P):
        self.P = P
        parent = P.root
        self.sock = P.sock

        self.win=Toplevel(parent)
        self.win.title("Rig Control")
        self.tabs = ttk.Notebook(self.win)          # Create Tab Control
        self.win.withdraw()
        self.win.protocol("WM_DELETE_WINDOW", self.hide)

        if self.sock.connection == 'NONE':
            return None
        
        # Legacy compatibility
        self.station   = IntVar(parent)
        self.status    = StringVar(parent)
        self.frequency = 0  

        # Add a tab for basic rig control
        tab1 = ttk.Frame(self.tabs)            # Create a tab 
        self.tabs.add(tab1, text='Rig Ctrl')   # Add the tab
        self.tabs.pack(expand=1, fill="both")  # Pack to make visible

        # Create a frame with buttons to select operating band
        self.band = StringVar(parent)
        BandFrame = Frame(tab1)
        BandFrame.pack(side=TOP)
        Label(BandFrame, textvariable=self.status ).pack(side=TOP)
        for b in bands:
            
            # Only show bands that the connected rig supports
            if ((b=='10m')   and (self.sock.rig_type2=='TS850'   )) or \
               ((b=='2m' )   and (self.sock.rig_type2=='FTdx3000')) or \
               ((b=='2m' )   and (self.sock.rig_type2=='IC7300'))   or \
               ((b=='1.25m') and (self.sock.rig_type2=='IC706'   )) or \
               ((b=='33cm')  and (self.sock.rig_type2=='FT991a'  )) or \
               ((b=='GEN')   and (self.sock.rig_type2=='IC9700'  )):
                break
            if ((b in CONTEST_BANDS) or (b in NON_CONTEST_BANDS)) and \
               (self.sock.rig_type2=='IC9700'  ):
                continue
            if (b=='1.25m') or (b=='33cm'):
                continue

            Radiobutton(BandFrame, 
                        text=b,
                        indicatoron = 0,
                        variable=self.band, 
                        command=lambda: SelectBand(self),
                        value=b).pack(side=LEFT,anchor=W)

        # Create a frame with buttons to select operating mode
        self.mode    = StringVar(parent)
        ModeFrame = Frame(tab1)
        ModeFrame.pack(side=TOP)
        for m in modes:
            Radiobutton(ModeFrame, 
                        text=m,
                        indicatoron = 0,
                        variable=self.mode, 
                        command=lambda: SelectMode(self),
                        value=m).pack(side=LEFT,anchor=W)

        # Create a frame with buttons to select antenna
        self.ant     = StringVar(parent)
        AntFrame = Frame(tab1)
        AntFrame.pack(side=TOP)
        for a in [1,2,3]:
            Radiobutton(AntFrame, 
                        text='Ant'+str(a),
                        indicatoron = 0,
                        variable=self.ant, 
                        command=lambda: SelectAnt(self),
                        value=a).pack(side=LEFT,anchor=W)

        # Create a frame with sliders to adjust tx power, mic and monitor gains
        SliderFrame = Frame(tab1)
        SliderFrame.pack(side=TOP)

        self.slider0 = Scale(SliderFrame, 
                             from_=0, to=100, 
                             orient=HORIZONTAL,
                             length=300,
                             label="TX Power",
                             command=self.Slider0CB )
        self.slider0.pack()
        read_tx_pwr(self)
        print(("POWER: %d" % self.tx_pwr))
        self.slider0.set(self.tx_pwr)

        self.slider1 = Scale(SliderFrame, 
                             from_=0, to=100, 
                             orient=HORIZONTAL,
                             length=300,
                             label="Mic Gain",
                             command=self.Slider1CB )
        self.slider1.pack()
        read_mic_gain(self)
        print(("GAIN: %d" % self.gain))
        self.slider1.set(self.gain)

        Button(SliderFrame,
               text="Auto Adj Mic", 
               command=lambda: Auto_Adjust_Mic_Gain(self) ).pack()

        self.slider2 = Scale(SliderFrame, 
                             from_=0, to=100, 
                             orient=HORIZONTAL,
                             length=300,
                             label="Monitor Level",
                             command=self.Slider2CB )
        self.slider2.pack()
        read_monitor_level(self)
        print(("LEVEL: %d" % self.mon_level))
        self.slider2.set(self.mon_level)

        # Create a frame with buttons to support other misc functions
        MiscFrame = Frame(tab1)
        MiscFrame.pack(side=TOP)

        Button(MiscFrame,
               text="Contest",   
               command=self.ToggleContest   ).pack(side=LEFT,anchor=W)
        self.ContestMode=False
        Button(MiscFrame,
               text="CLAR Reset",
               command=lambda: ClarReset(self) ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="<<",         
               command=lambda: SetSubBand(self,1) ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="||",         
               command=lambda: SetSubBand(self,2) ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text=">>",         
               command=lambda: SetSubBand(self,3) ).pack(side=LEFT,anchor=W)
        #Button(MiscFrame,
        #       text="Keypad",     
        #       command=self.ProgramKeypadMsgs).pack(side=LEFT,anchor=W)

        Button(MiscFrame,
               text="VFO A",     
               command=lambda: SetVFO(self,'A') ).pack(side=LEFT,anchor=S)
        Button(MiscFrame,
               text="VFO B",     
               command=lambda: SetVFO(self,'B') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="A-->B",     
               command=lambda: SetVFO(self,'A->B') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="B-->A",     
               command=lambda: SetVFO(self,'B->A') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="A<-->B",     
               command=lambda: SetVFO(self,'A<->B') ).pack(side=LEFT,anchor=W)
        #Button(MiscFrame,
        #       text="Split",     
        #       command=lambda: SetVFO(self,'SPLIT') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="TXW",     
               command=lambda: SetVFO(self,'TXW') ).pack(side=LEFT,anchor=W)
        
        # Add a tab for key pad
        if self.sock.rig_type1=='Yaesu':
            tab2 = ttk.Frame(self.tabs)              # Create a tab 
            self.tabs.add(tab2, text='Key Pad')      # Add the tab
            self.tabs.pack(expand=1, fill="both")    # Pack to make visible
            self.ProgramKeypadMsgs(tab2)

        # Add a tab to manage VFOs
        tab3 = ttk.Frame(self.tabs)                  # Create a tab 
        self.tabs.add(tab3, text='VFO & PL')         # Add the tab
        self.tabs.pack(expand=1, fill="both")        # Pack to make visible
        self.ManageVFOs(tab3)
        
        # Add a tab for satellite mode control
        if False:
            tab5 = ttk.Frame(self.tabs)                  # Create a tab 
            self.tabs.add(tab5, text='Satellites')       # Add the tab
            self.tabs.pack(expand=1, fill="both")        # Pack to make visible
            self.SatModes(tab5)
        
        # Ready to rock & roll
        self.hide()
        get_status(self)

    def show(self):
        print('Show Rig Control Window ...')
        self.win.update()
        self.win.deiconify()
        
    def hide(self):
        print('Hide Rig Control Window ...')
        self.win.withdraw()
        
        
    ############################################################################################

    def CloseWindow(self):
        print('Close window')
        self.P.gui.RigCtrlCB()
        
    ############################################################################################

    def ToggleContest(self):
        self.ContestMode = 1-self.ContestMode
        print("Content mode=",self.ContestMode)
        SetFilter(self)

    ############################################################################################

    def Read_Meter_Test(self):
        s=self.sock
        print("\nRead Meter Test ...")
    
        for i in range(9):
            val = Read_Meter(self,i)
            print("val= ",val)
        print("Done.")

    ############################################################################################

    def SatModes(self,SatWin,row=0):
        
        col=0
        Label(self.vfowin, text='Satellites:').grid(row=row,column=col)
        for mode in ['FM','USB-INV','USB','LSB-INV','LSB','CW','CW-INV','CW/USB', \
                     'PKT-INV','PKT-USB','PKT-FM']:

            # Align buttons according to voice, CW and packet modes
            if mode=='FM' or mode=='CW' or mode=='PKT-INV':
                row+=1
                col=0
            else:
                col+=1
            Button(SatWin,text=mode, command=partial(self.SetSatMode,mode) ) \
                .grid(row=row,column=col)
            #.pack(side=LEFT,anchor=W)

    def SetSatMode(self,mode):

        # Init
        print("\nRIG_CONTROL_TK: Set Sat Mode ...",mode)

        # Set Split mode
        self.sock.split_mode(1)

        mode1=mode
        if mode=='FM':
            #cmd='rigctl -m 2 -r localhost:4532 M FM 0 X FM 0'
            mode2='FM'
        elif mode=='USB-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M USB 0 X LSB 0'
            mode1='USB'
            mode2='LSB'
        elif mode=='USB':
            #cmd='rigctl -m 2 -r localhost:4532 M USB 0 X USB 0'
            mode2='USB'
        elif mode=='LSB':
            #cmd='rigctl -m 2 -r localhost:4532 M LSB 0 X LSB 0'
            mode2='LSB'
        elif mode=='LSB-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M LSB 0 X USB 0'
            mode1='LSB'
            mode2='USB'
        elif mode=='CW':
            #cmd='rigctl -m 2 -r localhost:4532 M CW 0 X CW 0'
            mode2='CW'
        elif mode=='CW-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M CW 0 X CW 0'
            mode1='CW'
            mode2='CW-R'
        elif mode=='CW/USB':
            # Not sure what this all about?
            #cmd='rigctl -m 2 -r localhost:4532 M USB 0 X CW 0'
            mode1='USB'
            mode2='CW'
        elif mode=='PKT-INV':
            #cmd='rigctl -m 2 -r localhost:4532 M PKTUSB 0 X PKTLSB 0'
            mode1='PKTUSB'
            mode2='PKTLSB'
        elif mode=='PKT-USB':
            #cmd='rigctl -m 2 -r localhost:4532 M PKTUSB 0 X PKTUSB 0'
            mode1='PKTUSB'
            mode2='PKTUSB'
        elif mode=='PKT-FM':
            cmd='rigctl -m 2 -r localhost:4532 M PKTFM 0 X PKTFM 0'
            mode1='PKTFM'
            mode2='PKTFM'
        else:
            print('SET SAT MODE: Unknwon mode',mode)
            return

        #print('Set_Sat_mode: cmd=',cmd)
        #system(cmd)
        self.sock.set_mode(mode1,VFO='A')
        self.SB_A_TXT.set(mode1)
        self.sock.set_mode(mode2,VFO='B')
        self.SB_B_TXT.set(mode2)

    ############################################################################################

    def ManageVFOs(self,vfowin):

        # Init
        print("\nRIG_CONTROL_TK: Manage VFOs ...")
        self.vfowin=vfowin

        # Declare vars to hold spinner values
        # The trace/partial construct calls the callback when the value changes
        self.SB_A_TXT = StringVar()
        self.SB_A_TXT.trace('w', partial( self.set_vfo_mode, 'A' ))
        self.SB_B_TXT = StringVar()
        self.SB_B_TXT.trace('w', partial( self.set_vfo_mode, 'B' ))
        self.SB_PL_TXT = StringVar()
        self.SB_PL_TXT.trace('w', partial( self.set_pl_tone, 0 ))

        # Set up a spin boxes to control select macro set
        row=0
        col=0
        self.MODE_LIST = ['FM','USB','LSB','CW','CW-R','PKTUSB','PKTLSB','AM']
        print('MODES:',self.MODE_LIST)

        Label(self.vfowin, text='VFO A:').grid(row=row,column=col,sticky=E+W)
        self.SB_A = OptionMenu(self.vfowin,self.SB_A_TXT,*self.MODE_LIST) \
            .grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        self.set_vfo_mode('A')
                               
        row +=1
        Label(self.vfowin, text='VFO B:').grid(row=row,column=col,sticky=E+W)
        self.SB_B = OptionMenu(self.vfowin,self.SB_B_TXT,*self.MODE_LIST) \
            .grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        self.set_vfo_mode('B')
        #sys.exit(0)

        # Buttons for VFO Ops
        row+=2
        Button(self.vfowin, text="VFO A",           \
               command=lambda: SetVFO(self,'A') )   \
               .grid(row=row,column=0,columnspan=1,sticky=E+W)
        Button(self.vfowin, text="VFO B",           \
               command=lambda: SetVFO(self,'B') )   \
               .grid(row=row,column=1,columnspan=1,sticky=E+W)
        row+=1
        Button(self.vfowin, text="A->B",           \
               command=lambda: SetVFO(self,'A->B') )   \
               .grid(row=row,column=0,columnspan=1,sticky=E+W)
        Button(self.vfowin, text="B->A",           \
               command=lambda: SetVFO(self,'B->A') )   \
               .grid(row=row,column=1,columnspan=1,sticky=E+W)
        Button(self.vfowin, text="A<->B",           \
               command=lambda: SetVFO(self,'A<->B') )   \
               .grid(row=row,column=2,columnspan=1,sticky=E+W)
        
        # Setup a spinbox to select PL tone
        col+=4
        row=0
        self.TONE_LIST = ['None'] + [str(pl) for pl in PL_TONES]
        print('PL TONES:',self.TONE_LIST)

        Label(self.vfowin, text='PL Tone:').grid(row=row,column=col,sticky=E+W)
        self.SB_PL = OptionMenu(self.vfowin,self.SB_PL_TXT,*self.TONE_LIST) \
            .grid(row=row,column=col+1,columnspan=2,sticky=E+W)
        self.set_pl_tone(-1)

        # For convenience, put up a few buttone with the most common tones
        col+=1
        for tone in ['None','67.0','74.4','88.5','107.2']:
            row+=1
            Button(self.vfowin, text=tone ,
                   command=partial(self.set_pl_tone,tone) ).grid(row=row, column=col)

        # Satellite mode selectors
        if True:
            row+=1
            col=0
            self.SatModes(self.vfowin,row)
            

    # Callback for VFO Mode list spinner
    def set_pl_tone(self,*args):

        print('\nRIG_CONTROL_TK: SET_PL_TONE Spinner callback:',len(args), args)
        cmd=args[0]
        print('cmd=',cmd,self.SB_PL_TXT.get())

        # Set/Get PL tone
        if cmd==-1:

            # Read radio and set spin box accordingly
            print('SET_PL_TONE: Reading radio vfo ...')
            tone = self.sock.get_PLtone()
            if tone==0:
                tone='None'
            print('Current tone=',tone)
            self.SB_PL_TXT.set(str(tone))

        else:
            
            # Set radio according to spin box value
            if cmd==0:
                tone=self.SB_PL_TXT.get()
            else:
                tone=cmd
            if tone=='None':
                tone=0
            else:
                tone=float(tone)
            print('SET_PL_TONE: Setting PL tone to',tone,' Hz ...')
            self.sock.set_PLtone(tone)

        
        
    # Callback for VFO Mode list spinner
    def set_vfo_mode(self,*args):

        print('\nRIG_CONTROL_TK: SET_VFO_MODE Spinner callback:',len(args), args)
        vfo=args[0]
        if vfo=='A':
            val=self.SB_A_TXT.get()
        elif vfo=='B':
            val=self.SB_B_TXT.get()
        else:
            print('SET_VFO_MODE: Unknwon VFO',vfo)
            return

        print('SET_VFO_MODE: vfo/val=',vfo,val)
        
        # Set/Get mode
        if len(val)==0:

            # Read radio and set spin box accordingly
            print('SET_VFO_MODE: Reading radio vfo ...')
            mode = self.sock.get_mode(VFO=vfo)
            #####idx  = self.MODE_LIST.index(mode)
            print('Current mode=',mode)
            if vfo=='A':
                self.SB_A_TXT.set(mode)
            else:
                self.SB_B_TXT.set(mode)

        else:
            
            # Set radio according to spin box value
            split = self.sock.split_mode(-1)
            sat = self.sock.sat_mode(-1)
            dual = self.sock.dual_watch(-1)
            print('SET_VFO_MODE: Setting radio vfo ...',vfo,val,'\tsplit=',split,\
                  '\tsat=',sat,'\tdual=',dual)
            if vfo in 'AM' or split or sat or dual:
                self.sock.set_mode(val,VFO=vfo)
        
        
    ############################################################################################

    def ProgramKeypadMsgs(self,keywin):

        # Init
        print("\nProgramming keypad ...")
        self.ekeyer=[];
        self.Keyer = ['','','','','','']
        self.keywin=keywin

        # See what's in the keypad
        GetKeyerMemory(self)

        for i in range(6):
            print("Programming Keypad ",i)
            if i<5:
                txt=str(i+1)+":"
            else:
                txt="#:"

            Label(keywin, text=txt).grid(row=i, column=0)
            self.ekeyer.append( Entry(keywin) )
            self.ekeyer[i].grid(row=i, column=1,columnspan=2)
            self.ekeyer[i].insert(0,self.Keyer[i])

            Button(keywin, text="ARRL DX" ,
                   command=lambda: KeyerMemoryDefaults(self,1) ).grid(row=6, column=0)
            Button(keywin, text="NAQP"    ,
                   command=lambda: KeyerMemoryDefaults(self,2) ).grid(row=6, column=1)
            Button(keywin, text="IARU"    ,
                   command=lambda: KeyerMemoryDefaults(self,3) ).grid(row=6, column=2)
            Button(keywin, text="CQ WW"   ,
                   command=lambda: KeyerMemoryDefaults(self,4) ).grid(row=6, column=3)
            Button(keywin, text="CQ WPX"  ,
                   command=lambda: KeyerMemoryDefaults(self,5) ).grid(row=6, column=4)
            Button(keywin, text="ARRL 160m" ,
                   command=lambda: KeyerMemoryDefaults(self,6) ).grid(row=6, column=5)

            Button(keywin, text="Field Day" ,
                   command=lambda: KeyerMemoryDefaults(self,7) ).grid(row=7, column=0)
            Button(keywin, text="Defaults",
                   command=lambda: KeyerMemoryDefaults(self,0) ).grid(row=7, column=1)
            Button(keywin, text="Test",
                   command=lambda: KeyerMemoryDefaults(self,99)).grid(row=7, column=2)
            Button(keywin, text="Update"  ,
                   command=lambda: UpdateKeyerMemory(self)     ).grid(row=7, column=5)

    ############################################################################################

    def Restart(self):
        self.sock.close()
        self.sock=open_socket(self.port,self.port)
        get_status(self)

    #def Update(self):
    #    get_status(self)

    def Slider0CB(self,arg):
        print('\nSlider 0 CallBack: ...')
        self.tx_pwr=arg
        set_tx_pwr(self)
        print('... Slider 0 CallBack Done.\n')

    def Slider1CB(self,arg):
        print('\nSlider 1 CallBack: ...')
        self.gain=arg
        set_mic_gain(self)
        print('... Slider 1 CallBack Done.\n')

    def Slider2CB(self,arg):
        print('\nSlider 2 CallBack: ...')
        self.mon_level = arg
        set_mon_level(self)
        print('... Slider 2 CallBack Done.\n')
