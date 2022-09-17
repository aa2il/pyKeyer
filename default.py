############################################################################################
#
# default.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Keying routines for default qsos
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
from dx.spot_processing import Station
import Levenshtein
from scp import *

############################################################################################

VERBOSITY=0

############################################################################################

# Base keying class for simple qsos
class DEFAULT_KEYING():

    def __init__(self,P,contest_name='CW Default',HISTORY=None):
        self.P=P
        self.contest_name  = contest_name 
        self.aux_cb=None
        self.number_key=None
        self.contest_duration = None

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
        self.SCP=SUPER_CHECK_PARTIAL()

    # Routient to set macros for this contest
    def macros(self):

        MACROS = OrderedDict()
        MACROS[0]  = {'Label' : 'CQ'      , 'Text' : 'CQ CQ CQ DE [MYCALL] [MYCALL] K '}
        MACROS[1]  = {'Label' : '[MYCALL]' , 'Text' : '[MYCALL] '}
        MACROS[2]  = {'Label' : 'Reply'   , 'Text' : 'RTU [RST] [MYSTATE] '}
        MACROS[3]  = {'Label' : 'OP'      , 'Text' : 'OP [MYNAME] [MYNAME] '}
        
        MACROS[4]  = {'Label' : 'QTH'     , 'Text' : 'QTH [MYSTATE] [MYSTATE] '}
        MACROS[5]  = {'Label' : '73'      , 'Text' : '73 '}
        MACROS[6]  = {'Label' : 'BK'      , 'Text' : 'BK '}
        MACROS[7]  = {'Label' : 'Call?'   , 'Text' : '[CALL]? '}
        
        MACROS[8]  = {'Label' : 'LOG it'  , 'Text' : '[LOG]'}
        MACROS[9]  = {'Label' : 'RST  '   , 'Text' : '[RST]'}
        MACROS[10] = {'Label' : 'V    '   , 'Text' : 'V'}
        MACROS[11] = {'Label' : 'Test '   , 'Text' : 'VVV [+10]VVV [-10]VVV'}

        return MACROS
        
    # Routine to generate a hint for a given call
    def hint(self,call):
        return None

    # Routine to get practice qso info
    def qso_info(self,HIST,call,iopt):

        if iopt==1:
            
            return True

        else:

            return ''
            
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
            gui.serial.focus_set()
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
        if 'Default' in contest or 'Ragchew' in contest or \
           'SATELLITES' in contest or 'DX-QSO' in contest_name:
            gui.contest=False
        else:
            gui.contest=True
        gui.ndigits=3
        gui.hide_all()
        self.macros=[1,None,2]
        #self.box_names=['call','serial','name']

        col=0
        cspan=3
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
        cspan=2
        gui.name_lab.grid(columnspan=cspan,column=col,sticky=E+W)
        gui.name.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.qth_lab.grid(column=col,columnspan=cspan)
        gui.qth.grid(column=col,columnspan=cspan)
        col+=cspan
        cspan=2
        gui.notes_lab.grid(column=col,columnspan=cspan)
        gui.notes.grid(column=col,columnspan=cspan)

        col+=cspan
        cspan=2
        gui.hint_lab.grid(column=col,columnspan=cspan,sticky=E+W)
        gui.hint.grid(column=col,columnspan=cspan)
        if self.P.NO_HINTS:
            gui.hint_lab.grid_remove()
            gui.hint.grid_remove()

        gui.boxes=[gui.call]
        gui.boxes.append(gui.rstout)
        gui.boxes.append(gui.rstin)
        gui.boxes.append(gui.name)
        gui.boxes.append(gui.qth)
        gui.boxes.append(gui.notes)
        gui.boxes.append(gui.hint)

        
    # Gather together logging info for this contest
    def logging(self):

        gui=self.P.gui

        # Form exchange from other station
        call=gui.get_call().upper()
        serial = gui.get_serial().upper()
        name = gui.get_name().upper()
        exch   = serial+','+name

        # Check validity of the exchange - in this case, just a valid call sign
        valid = len(call)>=3 

        # Form my exchagne tohim
        MY_NAME   = self.P.SETTINGS['MY_NAME']
        exch_out = str(gui.cntr)+','+MY_NAME

        # Any special fields for this particular contest
        qso2={}
        
        return exch,valid,exch_out,qso2
    
    # Dupe processing for this contest
    def dupe(self,a):

        gui=self.P.gui

        #gui.serial.delete(0,END)
        #gui.serial.insert(0,a[0])
        if len(a)>=2:
            gui.name.delete(0,END)
            gui.name.insert(0,a[1])

    # Hint insertion
    def insert_hint(self,h=None):

        gui=self.P.gui

        if h==None:
            h = gui.hint.get()
        if type(h) == str:
            h = h.split(' ')

        if len(h)>=1:
            gui.name.delete(0, END)
            gui.name.insert(0,h[0])
            if len(h)>=2:
                gui.qth.delete(0,END)
                gui.qth.insert(0,h[1])


    # Move on to next entry box & optionally play a macros
    def next_event(self,key,event):

        P   = self.P
        gui = P.gui

        if event.widget==gui.txt or event.widget==gui.txt2:
            #print('txt->call')
            next_widget = gui.call
        else:
            # Get current widget index
            idx=gui.boxes.index(event.widget)
            nn = len(gui.boxes)

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
            #print(idx,'->',idx2)
            next_widget = gui.boxes[idx2]

            # Send a macro if needed
            if key=='Return' or key=='KP_Enter':
                if P.PRACTICE_STATE<6 or event.widget!=gui.call:
                    #print('idx=',idx)
                    #print('macros=',self.macros)
                    n=self.macros[idx]
                    if n!=None:
                        gui.Send_Macro(n)

        # Do any extra stuff that might be special to this contest
        if self.aux_cb:
            self.aux_cb(key,event)
            
        next_widget.focus_set()
        return next_widget
            


    # Routine to do a "reverse call sign lookup" from a member number
    def reverse_call_lookup(self):

        P=self.P

        # This is a no-op for most contests
        if self.number_key==None:
            print('\nREVERSE_LOOKUP: Nothing to do for this contest')
            return

        # Get number from gui
        num = P.gui.get_exchange().upper()
        num = reverse_cut_numbers(num)
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
                print('call=',call,'home call=',call2)
                calls.append(call2)

        # Look for call closest to what we copied
        call_in=P.gui.get_call()
        print('CALL_IN=',call_in)

        # Find most common (i.e. "mode") of home calls
        print(calls)
        calls2 = list(set(calls))
        counts = []
        dist=[]
        for call in calls2:
            dx=Levenshtein.distance(call,call_in)
            dist.append(dx)
            cnt=calls.count(call)
            counts.append(cnt)
            #print(call,cnt)
        print('Known calls=',calls2)
        print('Distances=',dist)
        print('Counts=',counts)

        P.gui.txt.insert(END, '\n')
        P.gui.txt.insert(END, calls2)
        P.gui.txt.insert(END, '\n')
        P.gui.txt.insert(END, dist)
        P.gui.txt.insert(END, '\n')
        P.gui.txt.insert(END, counts)
        P.gui.txt.insert(END, '\n')
        P.gui.txt.see(END)

        # Put best call into call box
        if len(calls)>0:
            if len(call_in)>0:
                idx=dist.index(min(dist))
                m=calls2[idx]
            else:
                m=max(set(calls), key=calls.count)
            print('Most likely call=',m)
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
        print('REVERSE_LOOKUP: h=',h)
        
        #return m
        
        
