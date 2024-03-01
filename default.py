############################################################################################
#
# default.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for default qsos, most state QSO parties and some other contests.
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

import os
from tkinter import END,E,W
from collections import OrderedDict
from random import randint
from utilities import cut_numbers,reverse_cut_numbers
from dx import Station
from datetime import datetime
import Levenshtein
from scp import *

from datetime import datetime, date, tzinfo
import time
import pytz
UTC = pytz.utc

############################################################################################

VERBOSITY=0

############################################################################################

# Base keying class for simple qsos
class DEFAULT_KEYING():

    def __init__(self,P,contest_name='CW Default',HISTORY=None,SCP_FNAME=None):

        print('DEFAULT KEYING INIT ... SCP_FNAME=',SCP_FNAME)
        self.P=P
        self.contest_name  = contest_name 
        self.aux_cb=None
        self.number_key=None
        self.contest_duration = None
        self.LAB1=None
        self.LAB2=None
        self.LAB3=None
        self.key1=None
        self.key2=None
        self.NAME=''
        self.Uses_Serial=False

        P.CONTEST_ID=''
        P.HISTORY = P.HIST_DIR+'master.csv'
        if HISTORY==None:
            P.HISTORY = P.HIST_DIR+'master.csv'
        elif HISTORY:
            P.HISTORY = P.HIST_DIR+HISTORY
        else:
            P.HISTORY = None
        P.HISTORY=os.path.expanduser(P.HISTORY)
        P.HISTORY2 = P.HISTORY
        
        # Init super check partial
        self.SCP=SUPER_CHECK_PARTIAL(SCP_FNAME)
        

    # Routient to set macros for this contest
    def macros(self):

        print('DEFAULT MACROS: contest_name=',self.contest_name)
        self.key1=None
        self.key2=None
        #EXCH1 = ''
        #EXCH2 = ''
        
        MACROS = OrderedDict()
        if self.contest_name=='CW Default':
            
            MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
            MACROS[1]     = {'Label' : 'Reply'     , 'Text' : 'TU [RST] [MYSTATE] '}
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 [MYCALL] [LOG]'}
            MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TU [NAME] 73EE [LOG]'}
            MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
            MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
            
            MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
            MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
            MACROS[5]     = {'Label' : 'Reply'     , 'Text' : 'TU [RST] [MYSTATE] '}
            #MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[RST] [MYSTATE] [MYSTATE] '}
            MACROS[5+12]  = {'Label' : 'S&P DX1'    , 'Text' : 'R FB [NAME] GUD TO MEET U '}
            MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
            #MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
            MACROS[6+12]  = {'Label' : 'S&P DX2'    , 'Text' : 'UR [RST] [RST] IN [MYSTATE] [MYSTATE] '}
            MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
            MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
            
            MACROS[8]     = {'Label' : 'OP'      , 'Text' : 'OP [MYNAME] [MYNAME] '}
            MACROS[8+12]  = {'Label' : '73'      , 'Text' : '73 '}
            MACROS[9]     = {'Label' : 'RST  '   , 'Text' : '[RST] [RST] '}
            MACROS[9+12]  = {'Label' : '73 DX'   , 'Text' : 'R [NAME] TNX FER FB QSO ES GUD DX 73 73 GB SK EE '}
            MACROS[10]    = {'Label' : 'QTH'     , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
            MACROS[10+12] = {'Label' : 'Test '   , 'Text' : 'VVV [+10]VVV [-10]VVV'}
            MACROS[11]    = {'Label' : 'BK'      , 'Text' : 'BK '}
            MACROS[11+12] = {'Label' : 'V    '   , 'Text' : 'V'}

        else:

            CONTEST=self.contest_name 
            LAB2=None
            EXCH2=''
            LAB3=None
            EXCH3=''
            if self.contest_name in ['OCDX','WAG','RAC','BERU','HOLYLAND',
                                     'IOTA','SAC']:
                
                # RST + Serial No.
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'NR'
                EXCH2 = '[SERIAL]'
                self.Uses_Serial=True
                self.P.CONTEST_ID=self.contest_name+'-QSO-PARTY'
                
            elif self.contest_name in ['ARRL-160M']:

                # RST + Section
                CONTEST = 'TEST'
                LAB1    = 'RST'
                EXCH1   = '5NN'
                LAB2    = 'QTH'
                EXCH2   = '[MYSEC]'
                #self.key1 = 'rst'
                #self.key2 = 'sec'
                self.P.CONTEST_ID=self.contest_name
                
            elif self.contest_name in ['NVQP']:
                
                # RST + Section - Not sure why not combined with above???
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'QTH'
                EXCH2 = '[MYSEC]'
                #self.key1 = 'rst'
                #self.key2 = 'qth'
                self.P.CONTEST_ID=self.contest_name[0:2]+'-QSO-PARTY'
                
            elif self.contest_name in ['ALQP','ARQP','AZQP','COQP','DEQP',
                                       'GAQP','HIQP','IAQP','ILQP','INQP',
                                       'KSQP','KYQP','LAQP','MEQP','MIQP',
                                       'MOQP','MSQP','NCQP','NDQP','NEQP',
                                       'NHQP','NJQP','NMQP','NYQP','OHQP',
                                       'OKQP','SCQP','SDQP','TNQP','TXQP',
                                       'VTQP','WAQP','WVQP',
                                       'BCQP','ONQP','QCQP',
                                       'W1QP','W7QP','CPQP']:

                # RST + State
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE]'
                self.P.CONTEST_ID=self.contest_name[0:2]+'-QSO-PARTY'
                
            elif self.contest_name in ['IDQP','WIQP']:

                # State only - but they seem to send 5NN also so go with it
                #LAB1  = 'QTH'
                #EXCH1 = '[MYSTATE]'
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE]'
                self.P.CONTEST_ID=self.contest_name[0:2]+'-QSO-PARTY'
                
            elif self.contest_name in ['MDQP','MDCQP']:

                # Entry Class + State - need to put this in .rc file params
                LAB1  = 'CLASS'
                EXCH1 = 'F'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE]'
                self.P.CONTEST_ID=self.contest_name[0:2]+'-QSO-PARTY'
                
            elif self.contest_name in ['MARAC']:

                # RST State + County 
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE] SDGO'
                self.P.CONTEST_ID=self.contest_name+'-QSO-PARTY'
                
            elif self.contest_name in ['PAQP']:
                
                # Serial No. + Section
                LAB1  = 'NR'
                EXCH1 = '[SERIAL]'
                LAB2  = 'QTH'
                EXCH2 = '[MYSEC]'
                self.Uses_Serial=True
                self.P.CONTEST_ID=self.contest_name[0:2]+'-QSO-PARTY'
                
            elif self.contest_name in ['VAQP']:
                
                # Serial No. + Section
                LAB1  = 'NR'
                EXCH1 = '[SERIAL]'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE]'
                self.Uses_Serial=True
                self.P.CONTEST_ID=self.contest_name[0:2]+'-QSO-PARTY'
                
            elif self.contest_name in ['MNQP']:
                
                # Name + State
                LAB1  = 'NAME'
                EXCH1 = '[MYNAME]'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE]'
                self.P.CONTEST_ID=self.contest_name[0:2]+'-QSO-PARTY'
                
            elif self.contest_name in ['TEN-TEN']:

                # RST + 10-10 No. + State
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'NR'
                EXCH2 = '0'
                LAB3  = 'QTH'
                EXCH3 = '[MYSTATE]'
                self.P.CONTEST_ID=self.contest_name
                
            elif self.contest_name in ['FOC-BW']:

                # RST + Name + Member No.
                CONTEST = 'BW'
                LAB1    = 'RST'
                EXCH1   = '[NAME] 5NN'
                LAB2    = 'NAME'
                EXCH2   = '[MYNAME]'
                LAB3    = 'NR'
                EXCH3   = 'GL'
                self.P.CONTEST_ID=self.contest_name
                
            elif self.contest_name in ['JIDX']:
                
                # RST + CQ Zone
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'NR'
                EXCH2 = '[MYCQZ]'
                self.P.CONTEST_ID=self.contest_name[0:2]
                
            elif self.contest_name in ['AADX']:
                
                # RST + Age
                CONTEST = 'AA'
                LAB1    = 'RST'
                EXCH1   = '5NN'
                LAB2    = 'NR'
                EXCH2   = '[MYAGE]'
                self.P.CONTEST_ID=self.contest_name[0:2]
                
            elif self.contest_name in ['CQMM']:
                
                # RST + Continent
                CONTEST = 'MM'
                LAB1    = 'RST'
                EXCH1   = '5NN'
                LAB2    = 'QTH'
                EXCH2   = 'NA'
                self.P.CONTEST_ID=self.contest_name
                
            elif self.contest_name in ['SOLAR']:
                
                # RST + Grid
                CONTEST = 'SE'
                LAB1    = 'RST'
                EXCH1   = '5NN'
                LAB2    = 'QTH'
                EXCH2   = '[MYGRID]'
                self.P.CONTEST_ID=self.contest_name
                
            elif self.contest_name in ['POTA']:

                # RST + State 2x
                LAB1  = 'RST'
                EXCH1 = '[RST]'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE]'
                LAB3  = 'QTH'
                EXCH3 = '[MYSTATE]'
                self.P.CONTEST_ID=self.contest_name
                
            else:

                # RST + State
                LAB1  = 'RST'
                EXCH1 = '5NN'
                LAB2  = 'QTH'
                EXCH2 = '[MYSTATE]'
                self.P.CONTEST_ID=self.contest_name

            print('LAB2=',LAB2,'\tEXCH2=',EXCH2)
            self.LAB1=LAB1
            self.key1 = self.LAB1.lower()
            if LAB2!=None:
                self.LAB2=LAB2
                self.key2 = self.LAB2.lower()
            else:
                self.LAB2=LAB1
                LAB2=LAB1
            self.LAB3=LAB3
            print('self.LAB2=',self.LAB2,'\tEXCH2=',EXCH2)

            MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ '+CONTEST+' [MYCALL] '}
            #MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
            MACROS[0+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}
            MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU '+EXCH1+' '+EXCH2+' '}
            MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] [+2]73 EE [-2] [LOG]'}

            # Check date for any special greetings
            # Consider "GBA" for week around July 4?
            now = datetime.utcnow()
            if now.month==12 and now.day>=11 and now.day<28:
                MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC [MYCALL] [LOG]'}
                MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] MC [NAME] EE [LOG]'}
            elif now.month==12 and now.day>=28:
                MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY [MYCALL] [LOG]'}
                MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY [NAME] EE [LOG]'}
            elif now.month==1 and now.day<=14:
                MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY [MYCALL] [LOG]'}
                MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY [NAME] EE [LOG]'}
            else:            
                MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 [MYCALL] [LOG]'}
                MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] GL [NAME] EE [LOG]'}
            
            MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
            MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
            MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
            MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
            MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU '+EXCH1+' '+EXCH2+' '+EXCH3+' '}
            MACROS[5+12]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [NAME] '+EXCH1+' '+EXCH2+' '+EXCH3+' GL '.replace('  ',' ')}
            #MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : 'TU '+EXCH1+' '+EXCH1+' '+EXCH2+' '+EXCH2+' '}
            MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
            MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
            MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
            MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}
        
            MACROS[8]     = {'Label' : 'My '+self.LAB1+' 2x' , 'Text' : '[-2]'+EXCH1+' '+EXCH1+' [+2]'}
            MACROS[8+12]  = {'Label' : 'My Exch 2x'          , 'Text' : '[-2]'+EXCH1+' '+EXCH2+' '+EXCH1+' '+EXCH2+' [+2]'}
            MACROS[9]     = {'Label' : 'My '+self.LAB2+' 2x' , 'Text' : '[-2]'+EXCH2+' '+EXCH2+' [+2]'}
            MACROS[9+12]  = {'Label' : self.LAB1+'73'        , 'Text' : '73 GL '}
            MACROS[10]    = {'Label' : self.LAB1+'?'         , 'Text' : self.LAB1+'? '}
            MACROS[11]    = {'Label' : self.LAB2+'? '        , 'Text' : self.LAB2+'? '}
            if self.LAB3:
                MACROS[10+12]    = {'Label' : self.LAB3+'?'         , 'Text' : self.LAB3+'? '}
            if self.LAB1=='NR' or self.LAB2=='NR' or self.LAB3=='NR':
                MACROS[11+12]    = {'Label' : 'His #?'       , 'Text' : '[SERIAL_IN]? '}

        # Put up QRL? macro also
        MACROS[11+12] = {'Label' : 'QRL? '          , 'Text' : 'QRL? '}

        return MACROS

    
        
    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P
        gui=self.P.gui

        print('DEFAULFT HINT: call=',call,self.key1,self.key2)

        txt=''
        qth=''
        if self.key1!=None and self.key1!='rst':
            txt+='TBD '

        if self.key2!=None and self.key2 in ['sec','qth']:
            if self.key2=='qth':
                key2='state'
            else:
                key2=self.key2
            qth = P.MASTER[call][key2]
            print('DEFAULFT HINT: key2=',key2,'\tqth=',qth)
            txt += qth
            
        gui.name.delete(0,END)
        gui.info.delete(0,END)
        self.NAME = ''
        try:
            self.NAME = P.MASTER[call]['name']
            gui.name.delete(0,END)
            gui.name.insert(0,self.NAME)
            cwops = P.MASTER[call]['cwops']
            if len(cwops)>0:
                name=self.NAME+' '+cwops
            else:
                name=self.NAME
            gui.info.delete(0,END)
            gui.info.insert(0,name)
            gui.qth.delete(0,END)
            gui.qth.insert(0,qth)
        except Exception as e: 
            print('DEFAULT HINT: Unable to retrieve NAME')
            print( str(e) )

        print('DEFAULFT HINT: txt=',txt)
        return txt

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        if self.key2!=None:
            qth   = HIST[call][self.key2]
        else:
            qth=''
            
        if iopt==1:
            
            done = len(qth)>0
            return done

        else:

            self.call = call
            self.rst = '5NN'
            self.qth = qth

            txt=''
            if self.key1!=None:
                if self.key1=='rst':
                    txt+=self.rst+' '

            if self.key2!=None:
                if self.key2 in ['sec']:
                    txt+=self.qth
            
            return txt

        
    # Routine to process qso element repeats
    def repeat(self,label,exch2):
            
        if 'CALL' in label:
            txt2=self.call+' '+self.call
        elif 'NR?' in label:
            txt2=self.serial+' '+self.serial
        elif 'NAME?' in label:
            txt2=self.name+' '+self.name
        elif 'QTH?' in label or 'GRID?' in label:
            txt2=self.qth+' '+self.qth
        elif 'PREC?' in label:
            txt2=self.prec+' '+self.prec
        elif 'CHECK?' in label:
            txt2=self.chk+' '+self.chk
        elif 'SEC?' in label:
            txt2=self.sec+' '+self.sec
        else:
            txt2=exch2

        return txt2

    # Error checking
    def error_check(self):
        P=self.P

        return True
            

    # Highlight function keys that make sense in the current context
    def highlight(self,gui,arg):
        
        if arg==0:
            gui.btns1[1].configure(background='green',highlightbackground='green')
            gui.btns1[2].configure(background='green',highlightbackground='green')
            gui.call.focus_set()
        elif arg==1:
            gui.serial_box.focus_set()
        elif arg==4:
            gui.btns1[5].configure(background='red',highlightbackground= 'red')
            gui.btns1[7].configure(background='red',highlightbackground= 'red')
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[2].configure(background='pale green',highlightbackground=gui.default_color)
        elif arg==7:
            gui.btns1[1].configure(background='pale green',highlightbackground=gui.default_color)
            gui.btns1[5].configure(background='indian red',highlightbackground=gui.default_color)
            gui.btns1[7].configure(background='indian red',highlightbackground=gui.default_color)
        

    # Specific contest exchange for default qsos
    def enable_boxes(self,gui):

        contest=self.contest_name 
        print('DEFAULT ENABLE BOXES: contest_name=',self.contest_name)

        if 'Default' in contest or 'Ragchew' in contest or \
           'SATELLITES' in contest or 'DX-QSO' in contest or 'POTA' in contest:
            gui.contest=False
        else:
            gui.contest=True
        gui.ndigits=1
        gui.hide_all()
        self.macros=[1,None,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        gui.boxes=[gui.call]

        if not gui.contest:
            col+=cspan
            cspan=1
            gui.rstout_lab.grid(column=col,columnspan=cspan)
            gui.rstout.grid(column=col,columnspan=cspan)
            gui.boxes.append(gui.rstout)

        if not gui.contest or self.LAB1=='RST':
            col+=cspan
            cspan=1
            gui.rstin_lab.grid(column=col,columnspan=cspan)
            gui.rstin.grid(column=col,columnspan=cspan)
            gui.boxes.append(gui.rstin)

        if self.LAB2=='NAME':
            col+=cspan
            cspan=2
            gui.name_lab.grid(column=col,columnspan=cspan,sticky=E+W)
            gui.name.grid(column=col,columnspan=cspan)
            
        if self.LAB1=='NR' or self.LAB2=='NR' or self.LAB3=='NR':
            col+=cspan
            cspan=2
            if gui.contest and self.LAB1=='RST' and (self.LAB2=='NR' or self.LAB3=='NR'):
                gui.exch_lab.grid(column=col,columnspan=cspan)
                gui.exch.grid(column=col,columnspan=cspan)
                gui.boxes.append(gui.exch)
            else:
                gui.serial_lab.grid(column=col,columnspan=cspan)
                gui.serial_box.grid(column=col,columnspan=cspan)
                gui.boxes.append(gui.serial_box)
                gui.counter_lab.grid()
                gui.counter.grid()
            
        if not gui.contest:
            col+=cspan
            cspan=2
            gui.name_lab.grid(columnspan=cspan,column=col,sticky=E+W)
            gui.name.grid(column=col,columnspan=cspan)
            gui.boxes.append(gui.name)

        if not gui.contest or self.LAB1=='QTH' or self.LAB2=='QTH':
            col+=cspan
            cspan=2
            gui.qth_lab.grid(column=col,columnspan=cspan)
            gui.qth.grid(column=col,columnspan=cspan)
            gui.boxes.append(gui.qth)
        
        if not gui.contest:
            col+=cspan
            cspan=2
            gui.notes_lab.grid(column=col,columnspan=cspan)
            gui.notes.grid(column=col,columnspan=cspan)
            gui.boxes.append(gui.notes)

        col+=cspan
        cspan=max(min(2,12-col),1)
        gui.hint_lab.grid(column=col,columnspan=cspan,sticky=E+W)
        gui.hint.grid(column=col,columnspan=cspan)
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()
        else:
            gui.boxes.append(gui.hint)

        if gui.contest and self.LAB2!='NAME' and False:
            # Debug name insertion
            col+=cspan
            cspan=2
            gui.name_lab.grid(column=col,columnspan=cspan,sticky=E+W)
            gui.name.grid(column=col,columnspan=cspan)

        if self.Uses_Serial:
            gui.counter_lab.grid()
            gui.counter.grid()
            gui.inc_btn.grid()
            gui.dec_btn.grid()
            
        print('DEFAULT ENABLE BOXES: col=',col,'\tcspan=',cspan)
        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        # Get his call
        call    = gui.get_call().upper()
        valid = len(call)>=3 

        # Form exchange to & from other station
        exch_in  = ''
        exch_out = ''
        if gui.cntr==0:
            cntr = self.P.MY_CNTR
        else:
            cntr=gui.cntr
        if gui.rstin in gui.boxes:
            exch_in  += gui.get_rst_in()   + ','
            exch_out += gui.get_rst_out()  + ','
        if gui.serial_box in gui.boxes:
            exch_in  += gui.get_serial()   + ','
            exch_out += str(cntr)          + ','
        if gui.exch in gui.boxes:
            exch_in  += gui.get_exchange() + ','
            exch_out += str(cntr)          + ','
        if gui.name in gui.boxes:
            exch_in  += gui.get_name().upper()     + ','
            exch_out += self.P.SETTINGS['MY_NAME'] + ','
        if gui.qth in gui.boxes:
            exch_in  += gui.get_qth().upper()     + ','
            exch_out += self.P.SETTINGS['MY_STATE'] + ','

        # Any special fields for this particular contest
        qso2={}
        
        return exch_in,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        if len(a)>=2:
            gui.name.delete(0,END)
            gui.name.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h=None):

        print('DEFAULT INSERT HINT B4: h=',h,'\tname=',self.NAME)
        gui=self.P.gui

        if h==None:
            self.NAME=''
            h = gui.hint.get()              # Read hint box
            if h=='':
                h = gui.get_hint()          # Nothing in hint box, try getting a hint
                print('DEFAULT INSERT HINT DURING: h=',h,'\tname=',self.NAME)
                if h==None:
                    return

        if type(h) == str:
            h = h.split(' ')
        print('DEFAULT INSERT HINT AFTER: h=',h,'\tname=',self.NAME)

        if len(h)>=1:

            idx=0
            if self.key1!=None and self.key1=='name':
                gui.name.delete(0, END)
                gui.name.insert(0,h[idx])
                idx+=1
            else:
                gui.name.delete(0, END)
                gui.name.insert(0,self.NAME)

            if self.key2!=None and len(h)>idx:
                if (self.key2 in ['sec','qth','state']) or \
                   (self.contest_name=='RAC' and gui.dx_station and gui.dx_station.country=='Canada'):
                    gui.qth.delete(0,END)
                    gui.qth.insert(0,h[idx])
                    idx+=1
                elif self.key2 in ['exch']:
                    gui.exch.delete(0,END)
                    gui.exch.insert(0,h[idx])
                    idx+=1

    # Move on to next entry box & optionally play a macros
    def next_event(self,key,event):

        P   = self.P
        gui = P.gui
        DEBUG = 0

        if event.widget==gui.txt or event.widget==gui.txt2:
            
            # We're in one of the big text boxes - jump to call entry box
            #print('txt->call')
            next_widget = gui.call
            
        else:
            
            # Get current widget index
            idx=gui.boxes.index(event.widget)
            nn = len(gui.boxes)
            if DEBUG:
                print('NEXT EVENT: idx=',idx,'\tnn=',nn)

            # Determine adjacent (next) widget
            if key in ['Tab','Return','KP_Enter']:
                idx2 = (idx+1) % nn
                if gui.boxes[idx2]==gui.hint or (gui.contest and gui.boxes[idx2]==gui.rstin):
                    idx2 = (idx2+1) % nn
                if gui.boxes[idx2]==gui.scp:
                    idx2 = (idx2+1) % nn
            elif key=='ISO_Left_Tab':
                idx2 = (idx-1) % nn
                if gui.boxes[idx2]==gui.scp:
                    idx2 = (idx2-1) % nn
                if gui.boxes[idx2]==gui.hint:
                    idx2 = (idx2-1) % nn
                print(idx,idx2,nn)
            else:
                print('We should never get here!!',idx,key,nn)
                idx2=idx
                
            if DEBUG:
                print('NEXT EVENT: idx2=',idx2)
            next_widget = gui.boxes[idx2]

            # Send a macro if needed
            if key=='Return' or key=='KP_Enter':
                if DEBUG:
                    print('NEXT EVENT: Return\tOP_STATE=',P.OP_STATE)
                call = gui.get_call()
                if event.widget==gui.call and len(call)==0:

                    # We're in the Call Entry box
                    # If there is nothing here, call CQ
                    next_widget=event.widget
                    gui.Send_Macro(0)
                        
                else:    # if (P.OP_STATE & 32)==0 or event.widget!=gui.call
                    if DEBUG:
                        print('idx=',idx,'\tmacros=',self.macros)

                    n=self.macros[idx]
                    if n!=None:
                        gui.Send_Macro(n,event.state)

        # Do any extra stuff that might be special to this contest
        if self.aux_cb:
            self.aux_cb(key,event)

        if DEBUG:
            print('NEXT EVENT current widget=',event.widget,'\tnext widget=',next_widget)
        next_widget.focus_set()
        if DEBUG:
            print('NEXT EVENT Done: idx=',idx,'\tnn=',nn,'\tidx2=',idx2)
        return next_widget
            


    # Routine to do a "reverse call sign lookup" from a member number
    def reverse_call_lookup(self):

        P=self.P
        DEBUG=0

        # This is a no-op for most contests
        if self.number_key==None:
            print('\nREVERSE_LOOKUP: Nothing to do for this contest')
            return

        # Get number from gui
        num = P.gui.get_exchange().upper()
        num = reverse_cut_numbers(num)
        if DEBUG:
            print('\nREVERSE_LOOKUP: num=',num)
        if num=='':
            return

        # Look at all known calls
        calls=[]
        for call in P.MASTER.keys():
            num2 = P.MASTER[call][self.number_key]
            if num==num2:
                dx_station = Station(call)
                call2 = dx_station.homecall
                #print('call=',call,'home call=',call2)
                calls.append(call2)

        if DEBUG:
            print('\nREVERSE_LOOKUP: num=',num,'\tcalls=',calls)

        # Look for call closest to what we copied
        call_in=P.gui.get_call()
        #print('CALL_IN=',call_in)

        # Find most common (i.e. "mode") of home calls
        #print(calls)
        calls2 = list(set(calls))
        counts = []
        dist=[]
        for call in calls2:
            dx=Levenshtein.distance(call,call_in)
            dist.append(dx)
            cnt=calls.count(call)
            counts.append(cnt)
            #print(call,cnt)
        #print('Known calls=',calls2)
        #print('Distances=',dist)
        #print('Counts=',counts)

        P.gui.txt.insert(END, '\n')
        P.gui.txt.insert(END, calls2)
        P.gui.txt.insert(END, '\n')
        P.gui.txt.insert(END, dist)
        P.gui.txt.insert(END, '\n')
        P.gui.txt.insert(END, counts)
        P.gui.txt.insert(END, '\n')
        P.gui.txt.see(END)

        # Put best call into call box
        m=''
        if len(calls)>0:
            if len(call_in)>0:
                idx=dist.index(min(dist))
                m=calls2[idx]
            else:
                m=max(set(calls), key=calls.count)
            #print('Most likely call=',m)
            P.gui.call.delete(0, END)
            P.gui.call.insert(0,m)
            P.gui.dup_check(m)

        # Plug in hints also
        if True:
            # Fill in fields
            h=P.gui.get_hint(m)
            self.insert_hint(h)
        else:
            # Just fill in hint box
            h=P.gui.get_hint(m)
        #print('REVERSE_LOOKUP: h=',h)
        
        return m
        
        
    # On-the-fly scoring
    def scoring(self,qso):
        print("DEFAULTS SCORING: qso=",qso)

    # Routine to restore scoring if exited during a contest
    def init_scoring(self):
        P=self.P
        print('INIT SCORING: There are',len(P.gui.log_book),' QSOs in the log book.')
        now = datetime.utcnow().replace(tzinfo=UTC)
        MAX_AGE = 60*P.MAX_AGE       # In seconds
        for qso in P.gui.log_book:
            if ('CONTEST_ID' in qso) and (qso['CONTEST_ID']==P.CONTEST_ID):
                date_off = datetime.strptime( qso["QSO_DATE_OFF"]+" "+qso["TIME_OFF"] , "%Y%m%d %H%M%S") \
                                       .replace(tzinfo=UTC)
                age = (now - date_off).total_seconds() # In seconds
                #print('qso=',qso)
                #print('age=',age)
                if age<MAX_AGE:
                    self.scoring(qso)
        
    
