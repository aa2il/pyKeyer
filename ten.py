############################################################################################
#
# ten.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Keying routines for ARRL 10m, ARRL Intl DX and CQ 160m contests.
#
# Notes:
#  - For 10m contest, mults are States+Provvinces+Mexican States+DXCCs
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
from tkinter import END,E,W
from collections import OrderedDict
from default import DEFAULT_KEYING
from rig_io import arrl_sec2state
from dx import Station
from datetime import datetime
from rig_io.ft_tables import TEN_METER_SECS
import numpy as np
from utilities import error_trap
from scoring import ARRL_RTTY_RU_SCORING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for ARRL 10m and Intl DX contests
class TEN_METER_KEYING(DEFAULT_KEYING):

    def __init__(self,P,contest_name):
        DEFAULT_KEYING.__init__(self,P,contest_name)

        if self.P.contest_name=='ARRL-DX':
            now = datetime.utcnow()
            if now.month==3:
                self.mode='SSB'
            else:
                self.mode='CW'
            P.CONTEST_ID='ARRL-DX-'+self.mode
            P.sock.set_mode(self.mode)
        elif self.P.contest_name=='ARRL-10M':
            P.CONTEST_ID='ARRL-10'
        elif self.P.contest_name=='CQ-160M':
            P.CONTEST_ID='CQ-160M'
        else:
            print('TEN METER KEYING - Unknown contest',self.P.contest_name)
            sys.exit(0)
        self.contest_duration = 48
        P.MAX_AGE = self.contest_duration *60

        # On-the-fly scoring
        P.SCORING = ARRL_RTTY_RU_SCORING(P,'ARRL-10')

        """
        self.nqsos=0
        dxccs  = []
        if self.P.contest_name=='ARRL-10M':
            #self.BANDS = ['10m']
            self.secs = TEN_METER_SECS
            self.sec_cnt  = np.zeros(len(self.secs),dtype=int)
            self.dxccs = set(dxccs)
            self.scoring = self.scoring_10              # Override
        elif self.P.contest_name=='ARRL-DX':
            self.BANDS = ['160m','80m','40m','20m','15m','10m']
            for b in self.BANDS:
                dxccs.append((b,set([])))
            self.dxccs = OrderedDict(dxccs)
            self.scoring = self.scoring_dx              # Override
        self.init_scoring()
        """
        
    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRZ? '     , 'Text' : 'QRZ? '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [MYSTATE] '}
        #MACROS[1+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC [NAME] EE [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [MYSTATE] '}
        MACROS[5+12]  = {'Label' : 'S&P Reply' , 'Text' : 'MC [NAME] 5NN [MYSTATE] '}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}

        MACROS[8]     = {'Label' : 'My QTH 2x' , 'Text' : '[-2][MYSTATE] [MYSTATE] [+2]'}
        MACROS[9]     = {'Label' : ' '         , 'Text' : ' '}
        MACROS[10]    = {'Label' : 'NR? '      , 'Text' : 'NR? '}
        MACROS[11]    = {'Label' : 'QTH? '     , 'Text' : 'QTH? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}
        
        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        try:
            if self.P.contest_name=='ARRL-DX':
                state=''
            else:
                state = P.MASTER[call]['state']
                if state=='':
                    # Try deciphering from section info
                    sec   = P.MASTER[call]['fdsec']
                    state=arrl_sec2state(sec)
            self.NAME = P.MASTER[call]['name']
        except:
            state=''
            self.NAME = ''
            
        return state

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        state=HIST[call]['state']

        if iopt==1:
            
            done = len(state)>0
            return done

        else:

            self.call = call
            self.rst = '5NN'
            self.qth = state
            
            txt2  = ' 5NN '+state
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
            

    # Specific contest exchange for ARRL 10m
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()
        self.macros=[1,None,2]

        col=0
        cspan=4
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        
        col+=cspan
        cspan=1
        gui.rstin_lab.grid(column=col,columnspan=cspan,sticky=E+W)
        gui.rstin.grid(column=col,columnspan=cspan)
        gui.rstin.delete(0,END)
        gui.rstin.insert(0,'5NN')
        
        col+=cspan
        cspan=1
        gui.qth_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.qth.grid(column=col,columnspan=cspan)

        col+=cspan
        cspan=12-col
        gui.scp_lab.grid(column=col,columnspan=cspan)
        gui.scp.grid(column=col,columnspan=cspan)
        if not self.P.USE_SCP:
            gui.scp_lab.grid_remove()
            gui.scp.grid_remove()
            
        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.qth)

        if not gui.P.NO_HINTS:
            gui.hint_lab.grid(column=7,columnspan=1,sticky=E+W)
            gui.hint.grid(column=6,columnspan=2)
            
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui
        
        call = gui.get_call().upper()
        rst  = gui.get_rst_in().upper()
        qth = gui.get_qth().upper()
        valid = len(call)>=3 and len(rst)>0 and len(qth)>0
        exch = rst+','+qth

        MY_STATE = self.P.SETTINGS['MY_STATE']
        exch_out = '599,'+MY_STATE

        qso2={}
        
        return exch,valid,exch_out,qso2
    
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

        call=gui.get_call()
        dx_station = Station(call)
        country = dx_station.country
        
        print('TEN->INSERT HINT: h=',h,'\tName=',self.NAME,'\tCountry=',country)
        gui.qth.delete(0, END)
        gui.qth.insert(0,h[0])

        if True:
            gui.info.delete(0, END)
            if self.NAME and len(self.NAME)>0:
                if country:
                    gui.info.insert(0,self.NAME+' - '+dx_station.country)
                else:
                    gui.info.insert(0,self.NAME)
            elif country and len(country)>0:
                gui.info.insert(0,dx_station.country)
        
    # On-the-fly scoring for intl dx contest
    def scoring_dx(self,qso):
        print("\nTEN SCORING DX: qso=",qso)
        if self.P.contest_name!='ARRL-DX':
            print('TEN SCORING: Whoops - need to update scoring routine for this contest!',self.P.contest_name)
            return

        call=qso['CALL']
        dx_station = Station(call)
        if dx_station.country in ['United States','Canada']:
            return
        band = qso["BAND"]
        self.dxccs[band].add(dx_station.country)
        self.nqsos+=1        

        mults = 0
        for b in self.BANDS:
            mults+=len( self.dxccs[b] )

        score=self.nqsos * mults
        print("SCORING: score=",score,self.nqsos,mults)

        txt='{:5,d} QSOs  x {:5,d} Mults = {:8,d} \t\t\t Last Worked: {:s}' \
            .format(self.nqsos,mults,score,call)
        self.P.gui.status_bar.setText(txt)

        
    # On-the-fly scoring for 10m contest
    def scoring_10(self,qso):
        print("\nTEN SCORING: qso=",qso)
        if self.P.contest_name!='ARRL-10M':
            print('TEN SCORING: Whoops - need to update scoring routine for this contest!',self.P.contest_name)
            return

        call=qso['CALL']
        qth = qso['QTH']
        dx_station = Station(call)
        if dx_station.country in ['United States','Canada','Mexico']:
            try:
                idx1 = self.secs.index(qth)
                self.sec_cnt[idx1] = 1
            except:
                print('\tInvalid section:',qth)
            dx=False
        else:
            self.dxccs.add(dx_station.country)
            dx=True
        self.nqsos+=1        

        mults =len( self.dxccs ) + int( np.sum(self.sec_cnt) )

        score=self.nqsos * mults
        print("SCORING: score=",score,self.nqsos,mults)

        txt='{:5,d} QSOs  x {:5,d} Mults = {:8,d} \t\t\t Last Worked: {:s}' \
            .format(self.nqsos,mults,score,call)
        self.P.gui.status_bar.setText(txt)
            
