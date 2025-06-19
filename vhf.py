############################################################################################
#
# vhf.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Keying routines for ARRL VHF, CQ VHF and Stew Perry 160m contests
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

from tkinter import END,E,W
from collections import OrderedDict
import sys
from default import DEFAULT_KEYING
from utilities import error_trap
from latlon2maiden import distance_maidenhead
from scoring import VHF_SCORING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for ARRL & CQ VHF contests
class VHF_KEYING(DEFAULT_KEYING):

    def __init__(self,P,contest_name):
        DEFAULT_KEYING.__init__(self,P,contest_name,'ARRLVHF*.txt')
        P.CONTEST_ID=contest_name
        self.contest_duration = 5*8
        P.MAX_AGE = self.contest_duration *60
        print('VHF KEYING: CONTEST_ID=',P.CONTEST_ID)

        self.BANDS = ['MW','160m','80m','40m','20m','15m','10m']         # Need MW for practice mode
        grids  = []
        self.NQSOS = OrderedDict()
        self.POINTS = OrderedDict()
        self.NSTATES = OrderedDict()
        for b in self.BANDS:
            grids.append((b,set([])))
            self.NQSOS[b]=0
            self.POINTS[b]=0
            self.NSTATES[b]=0
        self.grids = OrderedDict(grids)
        self.MY_GRID = P.SETTINGS['MY_GRID'][:4]
        self.all_grids=set([])

        self.NAME = ''
        self.NUM  = ''

        # On-the-fly scoring
        P.SCORING    = VHF_SCORING(P,None,False)

        
    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        if not self.P.DIGI:
            # VHF
            MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
            MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYGRID] '}
            MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 [MYCALL] [LOG]'}
            MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] GL [NAME] EE [LOG]'}
        else:
            # Makrothen
            MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ MAK [MYCALL] [MYCALL] '}
            MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU [MYGRID] [MYGRID] [CALL] '}
            MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL] TNX AGN [NAME] 73 [MYCALL] CQ [LOG]'}
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL] 73 [MYCALL] CQ [LOG]'}
            MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL] GL [NAME] DIT DIT [MYCALL] CQ [LOG]'}
            
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'CALL?'     , 'Text' : 'CALL? '}
        
        if not self.P.DIGI:
            MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
            MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
            MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYGRID]'}
            #MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : 'TU [MYGRID] [MYGRID] '}
            MACROS[5+12]  = {'Label' : 'S&P Reply' , 'Text' : 'TU [NAME] [MYGRID]'}
        else:
            MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] [MYCALL] '}
            MACROS[4+12]  = {'Label' : '[MYCALL] 4x', 'Text' : '[MYCALL] [MYCALL] \n[MYCALL] [MYCALL] '}
            MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [MYGRID] [MYGRID] '}
            MACROS[5+12]  = {'Label' : 'S&P 4x'    , 'Text' : '[MYGRID] [MYGRID] [MYGRID] [MYGRID] '}
            
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        MACROS[8]     = {'Label' : 'Grid 2x'   , 'Text' : '[-2][MYGRID] [MYGRID] [+2]'}
        if not self.P.DIGI:
            MACROS[8+12]  = {'Label' : 'EE'        , 'Text' : 'EE '}
        MACROS[9]     = {'Label' : 'Grid 4x'   , 'Text' : '[-2][MYGRID] [MYGRID] [MYGRID] [MYGRID] [+2]'}
        MACROS[10]    = {'Label' : 'GRID?  '   , 'Text' : 'GRID? '}
        MACROS[11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}
        
        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        try:
            gridsq    = P.MASTER[call]['grid']
            self.NAME = P.MASTER[call]['name']
            self.NUM  = P.MASTER[call]['cwops']
        except:
            gridsq    = ''
            self.NAME = ''
            self.NUM  = ''
        
        return gridsq+' '+self.NAME+' '+self.NUM

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        grid=HIST[call]['grid']
        
        if iopt==1:
            
            done = len(grid)==4
            return done

        else:

            self.call = call
            self.qth  = grid
            
            txt2   = ' '+grid
            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.qth==qth2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent:'+self.call+'\t- received:'+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='Grid sent: '+self.qth+'\t-\treceived: '+qth2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            

    # Specific contest exchange for ARRL VHF
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()
        self.macros=[1,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.qth_lab.grid(column=col,columnspan=cspan)
        gui.qth.grid(column=col,columnspan=cspan)

        col+=cspan
        cspan=2
        gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
        gui.hint.grid(column=7,columnspan=3)
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()
        else:
            col+=cspan

        gui.boxes=[gui.call]
        gui.boxes.append(gui.qth)
        gui.boxes.append(gui.hint)
            
        if False:
            # Debug name insertion
            col+=cspan
            cspan=2
            gui.name_lab.grid(column=col,columnspan=cspan,sticky=E+W)
            gui.name.grid(column=col,columnspan=cspan)
        
            
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call = gui.get_call().upper()
        qth = gui.get_qth().upper()
        valid = len(call)>=3 and len(qth)>=4

        MY_GRID     = self.P.SETTINGS['MY_GRID']
        exch_out = MY_GRID

        qso2={}
        
        return qth,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.qth.delete(0,END)
        gui.qth.insert(0,a[0])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')
        
        gui.qth.delete(0, END)
        gui.qth.insert(0,h[0])

        gui.info.delete(0, END)
        #gui.info.insert(0,self.NAME)
        if len(h)>1:
            print('VHF INSERT HINT: h4=',h[1:])
            gui.info.insert(0,' '.join(h[1:]))


    # On-the-fly scoring
    def scoring(self,qso):
        print("\nSCORING: qso=",qso)
        self.nqsos+=1        

        call = qso['CALL']
        band = qso["BAND"]
        idx  = self.BANDS.index(band)

        srx = qso['SRX_STRING'].split(',')
        try:
            grid  = srx[0]
        except:
            self.P.gui.status_bar.setText('Unrecognized/invalid section!')
            error_trap('VHF->SCORING - Unrecognized/invalid section!\t'+
                       call+'\t'+band+'\t',srx)
            return

        dx_km  = int( distance_maidenhead(self.MY_GRID,grid,False) +0.5 ) 
        if dx_km > self.max_km:
            self.max_km=dx_km
            #self.longest=qso

        if dx_km==0:
            dx_km=100
            mult=1
        elif band=='80m':
            mult=2
        elif band=='40m':
            mult=1.5
        else:
            mult=1
            
        self.total_km += dx_km
        self.total_score += mult*dx_km
        print("SCORING: score=",self.total_score,self.nqsos,dx_km)

        txt='{:3d} QSOs, {:6d} km total = {:6d} \t\t{:6d} km\t\t Last Worked: {:s}' \
            .format(self.nqsos,int(self.total_km),int(self.total_score),
                    int(dx_km),call)
        self.P.gui.status_bar.setText(txt)
    
        
            
