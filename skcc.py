############################################################################################
#
# skcc.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for skcc sprints.
# Note - we only use this logging since we must use straight ley for tx!!!
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
from random import random
from rig_io.ft_tables import SST_SECS
from default import DEFAULT_KEYING

############################################################################################

VERBOSITY=0

############################################################################################

# Keying class for skcc sprints tests  - inherits base class
class SKCC_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'SKCC Sprint','skcclist.txt')

        P.CONTEST_ID='SKCC'
        self.number_key='skccnr'

        
    # Routine to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ SKCC [MYCALL] '}
        #MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] [RST] [MYSTATE] [MYNAME] [MYSKCC]'}
        MACROS[1+12]  = {'Label' : 'NIL'       , 'Text' : 'NIL '}
        if self.P.PRACTICE_MODE or True:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] RTU SKCC [MYCALL] [LOG]'}
        else:
            MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] HNY EE [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ'    , 'Text' : '[CALL_CHANGED] 73 [NAME] SKCC [MYCALL] [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'   , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU [NAME] UR  [RST] [MYSTATE] [MYNAME] [MYSKCC] '}
        #MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : '[MYNAME] [MYNAME] [MYSTATE] [MYSTATE]'}
        MACROS[6]     = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[6+12]  = {'Label' : '? '        , 'Text' : '? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}

        MACROS[8]     = {'Label' : 'Name 2x'   , 'Text' : '[MYNAME] [MYNAME] '}
        MACROS[9]     = {'Label' : 'State 2x'  , 'Text' : '[MYSTATE] [MYSTATE] '}
        MACROS[10]    = {'Label' : 'NAME?  '   , 'Text' : 'NAME? '}
        MACROS[11]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}

        return MACROS
        
    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P
        name  = P.MASTER[call]['name']
        state = P.MASTER[call]['state']
        num   = P.MASTER[call]['skccnr']
        if VERBOSITY>0:
            print('SKCC_KEYEING - Hint:',name+' '+state+' '+num)
        return name+' '+state+' '+num

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        print('QSO_INFO: call=',call,'\tiopt=',iopt,'\nhist=',HIST[call])

        name  = HIST[call]['name'].split(' ')
        name  = name[0]
        qth   = HIST[call]['state']
                
        if iopt==1:
            
            num   = HIST[call]['skccnr']
            done = len(name)>0  and len(qth)>0 and len(num)>0
                
            return done

        else:

            self.call = call
            self.name = name
            self.qth  = qth

            num = HIST[call]['skccnr']
            self.num    = num
            #self.serial = qth
            
            txt2  = ' '+qth+' '+name+' '+num
            return txt2

    # Error checking
    def error_check(self):
        P=self.P

        call2 = P.gui.get_call().upper()
        qth2  = P.gui.get_qth().upper()
        name2 = P.gui.get_name().upper()
        num2  = P.gui.get_exchange().upper()
        match = self.call==call2 and self.name==name2 and self.qth==qth2 and self.num==num2

        if not match:
            txt='********************** ERROR **********************'
            print(txt)
            P.gui.txt.insert(END, txt+'\n')

            print('Call sent:',self.call,' - received:',call2)
            P.gui.txt.insert(END,'Call sent: '+self.call+' - received: '+call2+'\n')
            
            print('Name sent:',self.name,' - received:',name2)
            P.gui.txt.insert(END,'Name sent: '+self.name+' - received: '+name2+'\n')

            print('QTH  sent:',self.qth,' - received:',qth2)
            P.gui.txt.insert(END,'QTH  sent: '+self.qth+ ' - received: '+qth2+'\n')

            print('NR   sent:',self.num,' - received:',num2)
            P.gui.txt.insert(END,'NR   sent: '+self.num+ ' - received: '+num2+'\n')

            print(txt+'\n')
            P.gui.txt.insert(END, txt+'\n')
            P.gui.txt.see(END)
            
        return match
    

    # Specific contest exchange for skcc
    def enable_boxes(self,gui):

        gui.contest=True
        gui.hide_all()

        col=0
        cspan=2
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.rstout_lab.grid(column=col,columnspan=cspan)
        gui.rstout.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.rstin_lab.grid(column=col,columnspan=cspan)
        gui.rstin.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.qth_lab.grid(column=col,columnspan=cspan)
        gui.qth.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=1
        gui.name_lab.grid(column=col,columnspan=cspan)
        gui.name.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.exch_lab.grid(column=col,columnspan=cspan)
        gui.exch.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=3
        gui.hint_lab.grid(column=col,columnspan=cspan,sticky=E+W)
        gui.hint.grid(column=col,columnspan=cspan)
        
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()

        # Indicate which macro to fire if return key is pressed while in each entry bos
        self.macros=[1,None,None,None,None,2]

        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstout)
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.qth)
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.exch)
        gui.boxes.append(gui.hint)
            

    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        call  = gui.get_call().upper()
        rstin = gui.get_rst_in().upper()
        qth   = gui.get_qth().upper()
        name  = gui.get_name().upper()
        num   = gui.get_exchange().upper()
        exch  = rstin+','+qth+','+name+','+num
        valid = len(call)>=3 and len(name)>0 and len(qth)>0
        
        rstout   = gui.get_rst_out().upper()
        MY_NAME  = self.P.SETTINGS['MY_NAME']
        MY_STATE = self.P.SETTINGS['MY_STATE']
        MY_SKCC  = self.P.SETTINGS['MY_SKCC']
        exch_out = rstout+','+MY_STATE+','+MY_NAME+','+MY_SKCC

        qso2 = {'SKCC':num}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.name.delete(0,END)
        gui.name.insert(0,a[0])
        if len(a)>=2:
            gui.exch.delete(0,END)
            gui.exch.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h):

        gui=self.P.gui

        gui.name.delete(0, END)
        gui.name.insert(0,h[0])
        
        gui.qth.delete(0, END)
        if len( h[1] )>0:
            gui.qth.insert(0,h[1])
            
        gui.exch.delete(0, END)
        if len( h[2] )>0:
            gui.exch.insert(0,h[2])


