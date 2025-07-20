############################################################################################
#
# iaru.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Keying routines for IARU HF Chanpionships
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
from dx import Station
from utilities import error_trap
from scoring import IARU_HF_SCORING

############################################################################################

VERBOSITY=0

############################################################################################

# Keyin class for IARU HF championship
class IARU_KEYING(DEFAULT_KEYING):

    def __init__(self,P):
        DEFAULT_KEYING.__init__(self,P,'IARU-HF')
        P.CONTEST_ID='IARU-HF'

        # On-the-fly scoring - NEW!
        P.SCORING    = IARU_HF_SCORING(P,False)
        
    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]     = {'Label' : 'CQ'        , 'Text' : 'CQ TEST [MYCALL] '}
        MACROS[0+12]  = {'Label' : 'QRS '      , 'Text' : 'QRS PSE QRS '}
        MACROS[1]     = {'Label' : 'Reply'     , 'Text' : '[CALL] TU 5NN [MYITUZ] '}
        MACROS[1+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] TNX AGN [NAME] EE [LOG]'}
        MACROS[2]     = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] 73 [MYCALL] [LOG]'}
        MACROS[2+12]  = {'Label' : 'TU/QRZ?'   , 'Text' : '[CALL_CHANGED] GL [NAME] EE [LOG]'}
        MACROS[3]     = {'Label' : 'Call?'     , 'Text' : '[CALL]? '}
        MACROS[3+12]  = {'Label' : 'Call?'     , 'Text' : 'CALL? '}
        
        MACROS[4]     = {'Label' : '[MYCALL]'  , 'Text' : '[MYCALL] '}
        MACROS[4+12]  = {'Label' : 'His Call'  , 'Text' : '[CALL] '}
        MACROS[5]     = {'Label' : 'S&P Reply' , 'Text' : 'TU 5NN [MYITUZ]'}
        #MACROS[5+12]  = {'Label' : 'S&P 2x'    , 'Text' : 'TU 5NN [MYITUZ] [MYITUZ]'}
        MACROS[5+12]  = {'Label' : 'S&P Reply' , 'Text' : 'TU [NAME] 5NN [MYITUZ]'}
        MACROS[6]     = {'Label' : '? '        , 'Text' : '? '}
        MACROS[6+12]  = {'Label' : 'AGN?'      , 'Text' : 'AGN? '}
        MACROS[7]     = {'Label' : 'Log QSO'   , 'Text' : '[LOG] '}
        MACROS[7+12]  = {'Label' : 'RR'        , 'Text' : 'RR '}

        MACROS[8]     = {'Label' : 'My Zone 3x'   , 'Text' : '[-2][MYITUZ] [MYITUZ] [MYITUZ] [+2]'}
        MACROS[9]     = {'Label' : 'My Zone 2x'   , 'Text' : '[-3][MYITUZ] [MYITUZ] [+3]'}
        MACROS[10]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[11]    = {'Label' : 'NR?'       , 'Text' : 'NR? '}
        MACROS[11+12] = {'Label' : 'QRL? '     , 'Text' : 'QRL? '}

        return MACROS

    # Routine to generate a hint for a given call
    def hint(self,call):
        P=self.P

        qth  = P.MASTER[call]['ituz']
        return qth

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        qth = HIST[call]['ituz']

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
            


    # Specific contest exchange for IARU HF Champs
    def enable_boxes(self,gui):

        gui.contest=True
        gui.ndigits=-3
        gui.hide_all()
        self.macros=[1,None,2]

        col=0
        cspan=3
        gui.call_lab.grid(column=col,columnspan=cspan)
        gui.call.grid(column=col,columnspan=cspan)
        
        col+=cspan
        cspan=1
        gui.rstin_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.rstin.grid(column=col,columnspan=cspan)
        gui.rstin.delete(0,END)
        gui.rstin.insert(0,'5NN')
        
        col+=cspan
        cspan=2
        gui.qth_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.qth.grid(column=col,columnspan=cspan)

        col+=cspan
        cspan=2
        gui.hint_lab.grid(column=col,columnspan=cspan)
        gui.hint.grid(column=col,columnspan=cspan)
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()
        else:
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
        gui.boxes.append(gui.hint)
        gui.boxes.append(gui.scp)
        
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
        rst  = gui.get_rst_in().upper()
        qth = gui.get_qth().upper()
        exch='5NN,'+qth
        valid = len(call)>=3 and len(rst)>0 and len(qth)>0

        MY_ITU_ZONE = self.P.SETTINGS['MY_ITU_ZONE']
        exch_out = '599,'+MY_ITU_ZONE

        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        gui.qth.delete(0,END)
        if len(a)>=2:
            gui.qth.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h=None):

        print('IARU->INSERT_HINTa: h=',h)

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')
        print('IARU->INSERT_HINTb: h=',h)
        if h[0] in ['DX','HI']:
            h = [str( gui.dx_station.ituz )]
        
        print('IARU->INSERT_HINTc: h=',h)
        gui.qth.delete(0, END)
        gui.qth.insert(0,h[0])

        if False:
            gui.name.delete(0, END)
            gui.name.insert(0,self.NAME)
        if False:
            gui.info.delete(0, END)
            gui.info.insert(0,self.NAME)

        if False:
            gui.info.delete(0, END)
            if len(h)>1:
                print('CQP INSERT HINT: h4=',h[1:])
                gui.info.insert(0,''.join(h[1:]))
            
