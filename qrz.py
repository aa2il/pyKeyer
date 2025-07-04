#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "chardet",
#     "levenshtein",
#     "openpyxl",
#     "pandas",
#     "psutil",
#     "pyaudio",
#     "pyautogui",
#     "pygame",
#     "pyhamtools",
#     "pyserial",
#     "pyudev",
#     "scipy",
#     "unidecode",
#     "xlrd",
# ]
# ///

#
#! /home/joea/miniconda3/envs/aa2il/bin/python -u
#
# NEW: /home/joea/miniconda3/envs/aa2il/bin/python -u
# OLD: /usr/bin/python3 -u 
#########################################################################################
#
# qrz.py - Rev. 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
    from tkinter import simpledialog
else:
    from Tkinter import *
    import tkFont
import time
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from dx import ChallengeData,Station,load_cty_info
from pprint import pprint

#########################################################################################

class CALL_INFO_GUI():
    def __init__(self,root,P,calls,qso,nqsos=None):
        self.P = P

        infos=[]
        for call in calls:
            call=call.replace(',','')
            dx_station = Station(call)

            print('\nInfo for',call,':')
            pprint(vars(dx_station))
            print(' ')

            """
            # Playpen
            utc = datetime.now(timezone.utc)
            print('utc=',utc)
            local = utc.astimezone(timezone(timedelta(hours=-dx_station.offset)))
            print('local=',local,'\thour=',local.hour)
            print(' ')
            """
            
            if call in P.MASTER.keys():
                print('CALL_LOOKUP:',call,' is in master list')
                info=P.MASTER[call]
            else:
                print('CALL_LOOKUP:',call,' is not in master list')
                info = OrderedDict()
                if '/' in call:
                    call2=dx_station.homecall
                    if call2 in P.MASTER.keys():
                        print('CALL_LOOKUP:',call2,' is in master list')
                        info=P.MASTER[call2]
            if dx_station.country!=None:
                info['Country']=dx_station.country
            else:
                info['Country']=''

            if qso!=None and qso[0]!=None:
                if nqsos!=None:
                    idx=calls.index(call)
                    n=nqsos[idx]
                else:
                    n=0
                if n>0:
                    print('CALL_LOOKUP:',call,' has been worked',n,
                          'times this year')
                else:
                    print('CALL_LOOKUP:',call,' has been worked this year')
                    print(qso)
            else:
                print('CALL_LOOKUP:',call,' has been NOT worked this year')
                        
            if P.CWOPS_MEMBERS!=None and call in P.CWOPS_MEMBERS:
                num = int( info['cwops'] )
                print('CALL_LOOKUP:',call,' is in CWops roster - number',num)
                if call in P.data.cwops_worked:
                    print('CALL_LOOKUP:',call,' has NOT been credited')
                elif num in P.data.cwops_nums:
                    print('CALL_LOOKUP: CWops no.',num,' has been credited this year')
                else:
                    print('CALL_LOOKUP:',call,'/',num,' has NOT been credited year')
            
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
                #print('\nkey=',key)
                #print('info=',info[key])
                e.insert(0,info[key])
        
            row+=1
            button = Button(tab, text="Dismiss",command=self.Dismiss)
            button.grid(row=row,column=0,columnspan=2,sticky=E+W)

            # Info from last qso
            idx=calls.index(call)
            if qso[idx]:
                tab = Frame(self.book)
                self.book.add(tab, text='Last QSO')
            
                row=0
                for key in qso[idx].keys():
                    txt=key.replace('_',' ').title()
                    lb=Label(tab, text=txt,justify=LEFT)
                    lb.grid(row=row, column=0,sticky=W)
                    e = Entry(tab,justify=CENTER)
                    e.grid(row=row,column=1,sticky=E+W)

                    txt2=qso[idx][key]
                    if 'Date' in txt:
                        date = datetime.strptime(txt2,'%Y%m%d')
                        txt2 = date.strftime('%m-%d-%Y')
                    elif 'Time' in txt:
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
    from settings import read_settings,SETTINGS_GUI
    from load_history import load_history
    from fileio import *

    # Structure to contain processing params
    class QRZ_PARAMS:
        def __init__(self):

            self.CWOPS_MEMBERS=None
            
            # Read config file
            self.SETTINGS,RCFILE = read_settings('.keyerrc')

            # Take care of non-standard location of support files
            load_cty_info(DIR=self.SETTINGS['MY_DATA_DIR'])
                        
            # Load master call list
            t0=time.time()
            print('Reading master history file ...')
            #MY_CALL2 = self.SETTINGS['MY_CALL'].split('/')[0]
            MY_CALL2 = self.SETTINGS['MY_OPERATOR'].split('/')[0]
            self.HIST_DIR=os.path.expanduser('~/Python/data/')
            self.MASTER,fname9 = load_history(self.HIST_DIR+'master.csv')
            self.calls = list(self.MASTER.keys())
            print('Read time=',time.time()-t0)

    # Command line args
    arg_proc = argparse.ArgumentParser(description='QRZ???')
    arg_proc.add_argument("call", help="Call(s) worked",
                          type=str,default=None,nargs='*')    # was + (require at least one)
    arg_proc.add_argument('-cwops', action='store_true',
                              help='CWops Reverse Lookup')
    arg_proc.add_argument('-cw', action='store_true',
                              help='Look only for CW QSOs')
    arg_proc.add_argument('-settings',action='store_true',
                          help='Open setting window')
    args = arg_proc.parse_args()

    # Grab list of call signs
    calls1 = list(map(str.upper,args.call))

    # If no call sign was given, ask for one
    while len(calls1)==0:
        c = simpledialog.askstring("Call?","Enter one or more callsigns:")
        print(c)
        if c==None:
            print('Bye Bye!')
            sys.exit(0)
        elif len(c)>3:
            calls1=[c.upper()]
    print('calls1=',calls1)

    # Convert list of callsigns into format we can digest
    calls=[]
    for c in calls1:
        calls2=c.split(',')
        for cc in calls2:
            for ccc in cc.split(' '):
                calls.append(ccc)
    print('calls=',calls)

    # Read config file
    P=QRZ_PARAMS()
    #print('SETTINGS=',P.SETTINGS)

    # Bring up setting dialog if requested
    if args.settings:
        SettingsWin = SETTINGS_GUI(None,P,BLOCK=True)
        
    # Reverse member no. lookup for CWops
    if args.cwops or calls[0].isdigit():
        print('Reading CWops member roster ...')
        MASTER,junk = load_history('~/Python/history/data/Shareable CWops data.xlsx')
        P.CWOPS_MEMBERS=MASTER
        num=calls[0]
        calls=[]
        for c in MASTER.keys():
            num2 = MASTER[c]['cwops']
            if num==num2:
                calls.append(c)
        print('calls=',calls,calls[0],len(calls))
        print(calls[0])

        print('Reading STATES.XLS ...')
        MY_CALL3          = P.SETTINGS['MY_OPERATOR'].split('/')[0]
        DATA_DIR          = os.path.expanduser('~/'+MY_CALL3+'/')
        P.CHALLENGE_FNAME = DATA_DIR+'/states.xls'
        P.data = ChallengeData(P.CHALLENGE_FNAME)
        #print('\nCWops members worked:\n',P.data.cwops_worked)
        #print('\nCWops member no.s worked:\n',P.data.cwops_nums)
        #sys.exit(0)

    # Read adif input file(s)
    QSOs=[]
    fnames=['~/Python/pyKeyer/'+P.SETTINGS['MY_CALL']+'.adif']
    last_qso=[None]*len(calls)
    nqsos=[0]*len(calls)
    print(nqsos)
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
            call=qso['call']
            mode=qso['mode']
            if call in calls and (not args.cw or mode=='CW'):
                idx=calls.index(call)
                last_qso[idx]=qso
                nqsos[idx]+=1
            
        QSOs = QSOs + qsos1
    
    print("\nThere are ",len(QSOs)," input QSOs ...")
    
    qrzWin = CALL_INFO_GUI(None,P,calls,last_qso,nqsos)
    mainloop()

