#! /usr/bin/python3 -u
#########################################################################################
#
# qrz.py - Rev. 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
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
if sys.version_info[0]==3:
    from tkinter import *
    import tkinter.font
    import tkinter.ttk as ttk
else:
    from Tkinter import *
    import tkFont
import time
from collections import OrderedDict

#########################################################################################

class CALL_INFO_GUI():
    def __init__(self,root,P,call,qso):
        self.P = P
        
        try:
            info=P.MASTER[call]
            print('CALL_LOOKUP:',call,' is in master list')
        except:
            print('CALL_LOOKUP:',call,' is not in master list')
            info = OrderedDict()
        #print('info=',info)

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
        
#########################################################################################

# If this file is called as main, run as independent exe
if __name__ == '__main__':
    import argparse
    from settings import read_settings
    from load_history import load_history
    from fileio import *

    # Structure to contain processing params
    class QRZ_PARAMS:
        def __init__(self):
            
            # Read config file
            self.SETTINGS,RCFILE = read_settings('.keyerrc')

            # Load master call list
            print('Reading master history file ...')
            MY_CALL2 = self.SETTINGS['MY_CALL'].split('/')[0]
            self.HIST_DIR=os.path.expanduser('~/'+MY_CALL2+'/')
            self.MASTER,fname9 = load_history(self.HIST_DIR+'master.csv')
            self.calls = list(self.MASTER.keys())
            
    # Command line args
    arg_proc = argparse.ArgumentParser(description='QRZ???')
    arg_proc.add_argument('call',type=str)
    arg_proc.add_argument('-cwops', action='store_true',
                              help='CWops Reverse Lookup')
    args = arg_proc.parse_args()
    call = args.call.upper()
    print('call=',call)

    # Reverse member no. lookup for CWops
    if args.cwops or call.isdigit():
        MASTER,junk = load_history('~/Python/history/data/Shareable CWops data.xlsx')
        calls=[]
        num=call
        for c in MASTER.keys():
            num2 = MASTER[c]['cwops']
            if num==num2:
                calls.append(c)
        print(calls)
        call=calls[0]

    # Read config file
    P=QRZ_PARAMS()
    #print('SETTINGS=',P.SETTINGS)

    # Read adif input file(s)
    QSOs=[]
    fnames=['~/Python/pyKeyer/'+P.SETTINGS['MY_CALL']+'.adif']
    last_qso=None
    for f in fnames:
        fname=os.path.expanduser( f )
        print('Reading log file:',fname)

        p,n,ext=parse_file_name(fname)
        if ext=='.csv':
            print('Reading CSV file ...')
            qsos1,hdr=read_csv_file(fname)
        else:
            qsos1 = parse_adif(fname)

        for qso in qsos1:
            if qso['call']==call:
                last_qso=qso
            
        QSOs = QSOs + qsos1
    
    print("\nThere are ",len(QSOs)," input QSOs ...")
    
    qrzWin = CALL_INFO_GUI(None,P,call,last_qso)
    mainloop()

