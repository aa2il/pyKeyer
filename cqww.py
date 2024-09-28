############################################################################################
#
# cqww.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for CQ World Wide contests.  For CW & SSB, exchange is RS(T) + CQ ZONE.
# For RTTY, also include STATE for domestic stations
#
# To Do - nothing urgent:
#     - Put NAME in INFO box
#     - Enable SCP
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
from default import DEFAULT_KEYING
import numpy as np
from utilities import error_trap
from dx.spot_processing import Station

############################################################################################

VERBOSITY=0

############################################################################################

# Keyin class for CQ World Wide
class CQWW_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'CQWW')

        if not P.DIGI:
            P.CONTEST_ID='CW-WW-CW'
        else:
            P.CONTEST_ID='CW-WW-RTTY'
        self.contest_duration = 48
        P.MAX_AGE = self.contest_duration *60

        # On-the-fly scoring
        self.nqsos=0
        self.total_points = 0
        self.BANDS = ['MW','160m','80m','40m','20m','15m','10m']         # Need MW for practice mode
        mults  = []
        states = []
        zones  = []
        dxccs  = []
        self.NQSOS = OrderedDict()
        self.POINTS = OrderedDict()
        self.NSTATES = OrderedDict()
        for b in self.BANDS:
            mults.append((b,set([])))
            states.append((b,set([])))
            zones.append((b,set([])))
            dxccs.append((b,set([])))
            self.NQSOS[b]=0
            self.POINTS[b]=0
            self.NSTATES[b]=0
        self.mults = OrderedDict(mults)
        self.states = OrderedDict(states)
        self.zones = OrderedDict(zones)
        self.dxccs = OrderedDict(dxccs)
        self.MY_CQ_ZONE = int( P.SETTINGS['MY_CQ_ZONE'] )
        self.init_scoring()
        
    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'       , 'Text' : 'CQ WW [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRS '     , 'Text' : 'QRS PSE QRS '}
        if not self.P.DIGI:
            # CQ WW CW - RST & ZONE
            MACROS[1] = {'Label' : 'Reply'    , 'Text' : '[CALL] TU 5NN [MYCQZ] '}
        else:
            # CQ WW RTTY - RST & ZONE & STATE
            MACROS[1]    = {'Label' : 'Reply'    , 'Text' : '[CALL] TU 599 [MYCQZ] [MYSTATE] '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'  , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}
        MACROS[2]     = {'Label' : 'TU/QRZ?'  , 'Text' : '[CALL_CHANGED] 73 WW [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'  , 'Text' : '[CALL_CHANGED] GL [NAME] EE [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'    , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'    , 'Text' : 'CALL? '}

        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        if not self.P.DIGI:
            MACROS[4+12]  = {'Label' : 'His Call' , 'Text' : '[CALL] '}
            MACROS[5]    = {'Label' : 'S&P Reply', 'Text' : 'TU 5NN [MYCQZ] '}
            MACROS[5+12] = {'Label' : 'S&P 2x'   , 'Text' : '5NN [MYCQZ] [MYCQZ] '}
        else:
            MACROS[4+12] = {'Label' : '[MYCALL] 2x', 'Text' : '[MYCALL] [MYCALL] '}
            MACROS[5]    = {'Label' : 'S&P Reply', 'Text' : 'TU 599 [MYCQZ] [MYSTATE] [MYSTATE] '}
            MACROS[5+12] = {'Label' : 'S&P 2x'   , 'Text' : '599 [MYCQZ] [MYCQZ] [MYSTATE] [MYSTATE] '}
        MACROS[6]     = {'Label' : '? '       , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'     , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'  , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
        if not self.P.DIGI:
            MACROS[8]    = {'Label' : 'Zone 2x'  , 'Text' : '[MYCQZ] [MYCQZ] '}
            MACROS[8+12] = {'Label' : 'Zone 4x'  , 'Text' : '[MYCQZ] [MYCQZ] [MYCQZ] [MYCQZ] '}
        else:
            MACROS[8]    = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
            MACROS[8+12] = {'Label' : 'State 4x'  , 'Text' : '[MYSTATE] [MYSTATE] [MYSTATE] [MYSTATE] '}
            MACROS[10]   = {'Label' : 'State ?'   , 'Text' : 'STATE ? '}
        MACROS[9]     = {'Label' : 'NR?'      , 'Text' : 'NR? '}
        
        MACROS[11]    = {'Label' : '[MYCALL] 3x'      , 'Text' : '[MYCALL] [MYCALL] [MYCALL]'}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        zone = P.MASTER[call]['cqz']
        qth  = P.MASTER[call]['state']
            
        return zone+' '+qth

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        qth = HIST[call]['cqz']

        if iopt==1:
            
            done = len(qth)>0
            return done

        else:

            self.call = call
            self.rst = '5NN'
            self.qth = qth

            txt2  = ' 5NN '+qth
            return txt2
            
    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        rst2  = P.gui.get_rst_in().upper()
        qth2  = P.gui.get_qth().upper()
        match = self.call==call2 and self.rst==rst2 and self.qth==qth2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            txt2='Call sent:'+self.call+'\t- received:'+call2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='RST sent:'+self.rst+'\t- received:'+rst2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')
            
            txt2='QTH sent:'+self.qth+'\t- received:'+qth2
            print(txt2)
            P.gui.txt.insert(END, txt2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
            


    # Specific contest exchange for CQ World Wide
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=-1
        gui.hide_all()
        self.macros=[1,None,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        gui.boxes=[gui.call]

        col+=cspan
        cspan=1
        gui.rstin_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.rstin.grid(column=col,columnspan=cspan)
        gui.rstin.delete(0,END)
        gui.rstin.insert(0,'599')
        gui.boxes.append(gui.rstin)
        
        if self.P.DIGI:
            col+=cspan
            cspan=1
            gui.exch_lab.grid(columnspan=cspan,column=col,sticky=E+W)
            gui.exch.grid(column=col,columnspan=cspan)
            gui.boxes.append(gui.exch)
            
        col+=cspan
        cspan=1
        gui.qth_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.qth.grid(column=col,columnspan=cspan)
        gui.boxes.append(gui.qth)

        col+=cspan
        cspan=2
        gui.hint_lab.grid(column=col,columnspan=cspan)
        gui.hint.grid(column=col,columnspan=cspan)
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()
        else:
            col+=cspan
        gui.boxes.append(gui.hint)
                    
        cspan=12-col
        gui.scp_lab.grid(column=col,columnspan=cspan)
        gui.scp.grid(column=col,columnspan=cspan)
        if not self.P.USE_SCP:
            gui.scp_lab.grid_remove()
            gui.scp.grid_remove()
        gui.boxes.append(gui.scp)
        
            
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call = gui.get_call().upper()
        rst  = gui.get_rst_in().upper()
        qth = gui.get_qth().upper()
        if not self.P.DIGI:
            exch_in = '5NN,'+qth
            valid   = len(call)>=3 and len(rst)>0 and len(qth)>0
        else:
            zone    = gui.get_exchange().upper()
            exch_in = '599,'+zone+','+qth
            valid = len(call)>=3 and len(rst)>0 and len(zone)>0

        MY_CQ_ZONE = self.P.SETTINGS['MY_CQ_ZONE']
        if not self.P.DIGI:
            exch_out = '599,'+MY_CQ_ZONE
        else:
            MY_STATE   = self.P.SETTINGS['MY_STATE']
            exch_out = '599,'+MY_CQ_ZONE+','+MY_STATE

        qso2={}
        
        return exch_in,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.exch.delete(0,END)
        gui.qth.delete(0,END)
        if len(a)>=2:
            if not self.P.DIGI:
                gui.qth.insert(0,a[1])
            else:
                gui.exch.insert(0,a[1])
                if len(a)>=3:
                    gui.qth.insert(0,a[2])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')

        gui.exch.delete(0,END)
        gui.qth.delete(0, END)
        
        if len(h)>=1:
            if not self.P.DIGI:
                gui.qth.insert(0,h[0])
            else:
                gui.exch.insert(0,h[0])
                if len(h)>=2:
                    gui.qth.insert(0,h[1])


    # On-the-fly scoring
    def scoring(self,qso):
        print("\nSCORING: qso=",qso)
        self.nqsos+=1        

        call=qso['CALL']
        dx_station = Station(call)
        
        band = qso["BAND"]
        idx = self.BANDS.index(band)

        srx = qso['SRX_STRING'].split(',')
        try:
            zone  = srx[1]
            if len(srx)>=3:
                state = srx[2]
            else:
                state = ''
            #idx1 = NAQP_SECS.index(qth)
        except:
            self.P.gui.status_bar.setText('Unrecognized/invalid section!')
            error_trap('CQWW->SCORING - Unrecognized/invalid section!')
            return

        if state=='' or zone in [1,31] or dx_station.country in ['Puerto Rico']:
            state='DX'

        if dx_station.country=='United States':
            if self.P.DIGI:
                qso_points=1
            else:
                qso_points=0
        elif dx_station.continent=='NA':
            qso_points=2
        else:
            qso_points=3
        self.total_points += qso_points

        self.mults[band].add(str(zone))
        self.mults[band].add(dx_station.country)
        if state!='DX':
            self.mults[band].add(state)

        mults=0
        for b in self.BANDS:
            m = list( self.mults[b] )
            mults+=len(m)

        score=self.nqsos * mults
        print("SCORING: score=",score,self.nqsos,mults)

        txt='{:3d} QSOs  x {:3d} Mults = {:6,d} \t\t\t Last Worked: {:s}' \
            .format(self.nqsos,mults,score,call)
        self.P.gui.status_bar.setText(txt)
    
            
