#########################################################################################
#
# qrz.py - Rev. 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Gui to display what we know about a call.
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
#########################################################################################

import sys
import os
#import json
if sys.version_info[0]==3:
    from tkinter import *
    import tkinter.font
else:
    from Tkinter import *
    import tkFont
from dx.cluster_connections import get_logger
from dx.spot_processing import Station
import time
from collections import OrderedDict

#########################################################################################

class CALL_INFO_GUI():
    def __init__(self,root,P,call,qso):
        self.P = P
        
        if call in P.calls:
            print('CALL_LOOKUP:',call,' is in master list')
            info=P.MASTER[call]
        else:
            print('CALL_LOOKUP:',call,' is not in master list')
            #print(P.calls)
            #return
            info = OrderedDict()
        print(info)

        if root:
            self.win=Toplevel(root)
        else:
            self.win = Tk()
        self.win.title("Call Info -"+call)

        self.tabs = ttk.Notebook(self.win)
        self.tab1 = Frame(self.tabs)
        self.tabs.add(self.tab1, text='Info')
        if qso:
            self.tab2 = Frame(self.tabs)
            self.tabs.add(self.tab2, text='Last QSO')
        self.tabs.pack(expand=1, fill="both")

        # Info from master list
        row=0
        lb=Label(self.tab1, text='Call: ',justify=LEFT)
        lb.grid(row=row,column=0,sticky=W)
        self.call = Entry(self.tab1,justify=CENTER)
        self.call.grid(row=row,column=1,sticky=E+W)
        #self.call.delete(0, END)
        self.call.insert(0,call)

        for key in info.keys():
            row+=1
            txt=key[0].upper() + key[1:] +': '
            lb=Label(self.tab1, text=txt,justify=LEFT)
            lb.grid(row=row, column=0,sticky=W)
            e = Entry(self.tab1,justify=CENTER)
            e.grid(row=row,column=1,sticky=E+W)
            e.insert(0,info[key])
        
        row+=1
        button = Button(self.tab1, text="Dismiss",command=self.Dismiss)
        button.grid(row=row,column=0,columnspan=2,sticky=E+W)

        # Info from last qso
        if qso:
            row=0
            for key in qso.keys():
                lb=Label(self.tab2, text=key,justify=LEFT)
                lb.grid(row=row, column=0,sticky=W)
                e = Entry(self.tab2,justify=CENTER)
                e.grid(row=row,column=1,sticky=E+W)
                e.insert(0,qso[key])
                row+=1
                
            button = Button(self.tab2, text="Dismiss",command=self.Dismiss)
            button.grid(row=row,column=0,columnspan=2,sticky=E+W)
        
        self.win.protocol("WM_DELETE_WINDOW", self.Dismiss)        

        
    def Dismiss(self):
        self.win.destroy()
