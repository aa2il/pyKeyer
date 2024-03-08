#! /usr/bin/python3 -u
#########################################################################################
#
# qrz.py - Rev. 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
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
from dx import Station
from datetime import datetime

#########################################################################################

class CALL_INFO_GUI():
    def __init__(self,root,P,calls,qso):
        self.P = P

        infos=[]
        for call in calls:
            call=call.replace(',','')
            if call in P.MASTER.keys():
                print('CALL_LOOKUP:',call,' is in master list')
                info=P.MASTER[call]
            else:
                print('CALL_LOOKUP:',call,' is not in master list')
                info = OrderedDict()
                if '/' in call:
                    dx_station = Station(call)
                    call2=dx_station.homecall
                    if call2 in P.MASTER.keys():
                        print('CALL_LOOKUP:',call2,' is in master list')
                        info=P.MASTER[call2]
            infos.append(info)
        #print('infos=',infos,len(infos))

        if root:
            self.win=Toplevel(root)
        else:
            self.win = Tk()
        self.win.title("Call Info -".join(calls))

        self.book = ttk.Notebook(self.win)
        self.tabs=[]
        for call,info in zip(calls,infos):
            call=call.replace(',','')
            
            #print('info=',info)
            tab = Frame(self.book)
            self.tabs.append(tab)
            self.book.add(tab, text='Info')

            # Info from master list
            row=0
            lb=Label(tab, text='Call: ',justify=LEFT)
            lb.grid(row=row,column=0,sticky=W)
            self.call = Entry(tab,justify=CENTER)
            self.call.grid(row=row,column=1,sticky=E+W)
            self.call.insert(0,call)

            for key in info.keys():
                row+=1
                txt=key.title()
                lb=Label(tab, text=txt,justify=LEFT)
                lb.grid(row=row, column=0,sticky=W)
                e = Entry(tab,justify=CENTER)
                e.grid(row=row,column=1,sticky=E+W)
                e.insert(0,info[key])
        
            row+=1
            button = Button(tab, text="Dismiss",command=self.Dismiss)
            button.grid(row=row,column=0,columnspan=2,sticky=E+W)

        # Info from last qso
        if qso:
            tab = Frame(self.book)
            self.book.add(tab, text='Last QSO')
            
            row=0
            for key in qso.keys():
                txt=key.replace('_',' ').title()
                lb=Label(tab, text=txt,justify=LEFT)
                lb.grid(row=row, column=0,sticky=W)
                e = Entry(tab,justify=CENTER)
                e.grid(row=row,column=1,sticky=E+W)

                txt2=qso[key]
                if 'date' in key:
                    date = datetime.strptime(txt2,'%Y%m%d')
                    txt2 = date.strftime('%m-%d-%Y')
                elif 'time' in key:
                    date = datetime.strptime(txt2,'%H%M%S')
                    txt2 = date.strftime('%H:%M:%S')
                e.insert(0,txt2)
                row+=1
                
            button = Button(tab, text="Dismiss",command=self.Dismiss)
            button.grid(row=row,column=0,columnspan=2,sticky=E+W)
        
        self.book.pack(expand=1, fill="both")
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
            t0=time.time()
            print('Reading master history file ...')
            MY_CALL2 = self.SETTINGS['MY_CALL'].split('/')[0]
            self.HIST_DIR=os.path.expanduser('~/'+MY_CALL2+'/')
            self.MASTER,fname9 = load_history(self.HIST_DIR+'master.csv')
            self.calls = list(self.MASTER.keys())
            print('Read time=',time.time()-t0)
            
    # Command line args
    arg_proc = argparse.ArgumentParser(description='QRZ???')
    #arg_proc.add_argument('call',type=str)
    arg_proc.add_argument("call", help="Call(s) worked",
                          type=str,default=None,nargs='*')
    arg_proc.add_argument('-cwops', action='store_true',
                              help='CWops Reverse Lookup')
    args = arg_proc.parse_args()
    calls = list(map(str.upper,args.call))   #.upper()
    print('calls=',calls)

    # Reverse member no. lookup for CWops
    if args.cwops or calls[0].isdigit():
        MASTER,junk = load_history('~/Python/history/data/Shareable CWops data.xlsx')
        num=calls[0]
        calls=[]
        for c in MASTER.keys():
            num2 = MASTER[c]['cwops']
            if num==num2:
                calls.append(c)
        print('calls=',calls,calls[0],len(calls))
        print(calls[0])
        #sys.exit(0)

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
            if qso['call'] in calls:
                last_qso=qso
            
        QSOs = QSOs + qsos1
    
    print("\nThere are ",len(QSOs)," input QSOs ...")
    
    qrzWin = CALL_INFO_GUI(None,P,calls,last_qso)
    mainloop()

