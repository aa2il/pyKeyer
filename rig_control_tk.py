############################################################################################

# Rig Control - J.B.Attili - 2019

# Portion of GUI related to rig controls - Tk version

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
    def __init__(self,parent,sock):
        self.sock = sock

        self.win=Toplevel(parent)
        self.win.title("Rig Control")
        self.tabs = ttk.Notebook(self.win)          # Create Tab Control
        self.win.withdraw()

        if sock.connection == 'NONE':
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
               ((b=='1.25m') and (self.sock.rig_type2=='IC706'   )) or \
               ((b=='33cm')  and (self.sock.rig_type2=='FT991a'  )):
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
               text="A->B",     
               command=lambda: SetVFO(self,'A->B') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="B->A",     
               command=lambda: SetVFO(self,'B->A') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="A<->B",     
               command=lambda: SetVFO(self,'A<->B') ).pack(side=LEFT,anchor=W)
        
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
        get_status(self)
        #self.win.withdraw()
            
        
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
        for mode in ['FM','USB-INV','USB','LSB-INV','LSB','CW','CW/USB','PKT-INV','PKT-USB','PKT-FM']:
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

        if mode=='FM':
            cmd='rigctl -m 2 -r localhost:4532 M FM 0 X FM 0'
        elif mode=='USB-INV':
            cmd='rigctl -m 2 -r localhost:4532 M USB 0 X LSB 0'
        elif mode=='USB':
            cmd='rigctl -m 2 -r localhost:4532 M USB 0 X USB 0'
        elif mode=='LSB':
            cmd='rigctl -m 2 -r localhost:4532 M LSB 0 X LSB 0'
        elif mode=='LSB-INV':
            cmd='rigctl -m 2 -r localhost:4532 M LSB 0 X USB 0'
        elif mode=='CW':
            cmd='rigctl -m 2 -r localhost:4532 M CW 0 X CW 0'
        elif mode=='CW/USB':
            cmd='rigctl -m 2 -r localhost:4532 M USB 0 X CW 0'
        elif mode=='PKT-INV':
            cmd='rigctl -m 2 -r localhost:4532 M PKTUSB 0 X PKTLSB 0'
        elif mode=='PKT-USB':
            cmd='rigctl -m 2 -r localhost:4532 M PKTUSB 0 X PKTUSB 0'
        elif mode=='PKT-FM':
            cmd='rigctl -m 2 -r localhost:4532 M PKTFM 0 X PKTFM 0'
        print('Set_Sat_mode: cmd=',cmd)

        system(cmd)
        
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
        self.MODE_LIST = ['FM','USB','LSB','CWUSB','CWLSB','PKTUSB','PKTLSB','AM']
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
            print('SET_VFO_MODE: Setting radio vfo ...',vfo,val)
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
