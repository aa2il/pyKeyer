#! /usr/bin/python3 -u
################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Command line param parser for pyKeyer.
#
################################################################################
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
################################################################################

import argparse
from rig_io.ft_tables import CONNECTIONS,RIGS,PRECS,STATES
from settings import *
import os
import platform
from utilities import find_resource_file
from collections import OrderedDict
import datetime

################################################################################

# Structure to contain basic info about various contests
CONTESTS = OrderedDict()
ALL=list(range(1,13))
CONTESTS['Default']    = {'Months' : ALL}
CONTESTS['Ragchew']    = {'Months' : ALL}
CONTESTS['CWT']        = {'Months' : ALL}
CONTESTS['MST']        = {'Months' : ALL}
CONTESTS['SST']        = {'Months' : ALL}
CONTESTS['NS']         = {'Months' : ALL}
CONTESTS['SKCC']       = {'Months' : ALL}
CONTESTS['POTA']       = {'Months' : ALL}
CONTESTS['CW Open']    = {'Months' : [10]}
CONTESTS['ARRL-VHF']   = {'Months' : [1,6,9]}
CONTESTS['NAQP-CW']    = {'Months' : [1,8]}
CONTESTS['TEN-TEN']    = {'Months' : []}
CONTESTS['WAG']        = {'Months' : []}
CONTESTS['SAC']        = {'Months' : []}
CONTESTS['RAC']        = {'Months' : [12]}
CONTESTS['BERU']       = {'Months' : []}
CONTESTS['CQP']        = {'Months' : [10]}
CONTESTS['IARU-HF']    = {'Months' : [7]}
CONTESTS['CQWW']       = {'Months' : [11]}
CONTESTS['CQ-WPX-CW']  = {'Months' : [5]}
CONTESTS['CQ-160M']    = {'Months' : []}
CONTESTS['ARRL-10M']   = {'Months' : [12]}
CONTESTS['ARRL-160M']  = {'Months' : []}
CONTESTS['ARRL-DX']    = {'Months' : [2]}
CONTESTS['ARRL-FD']    = {'Months' : [6]}
CONTESTS['ARRL-SS-CW'] = {'Months' : [11]}
CONTESTS['STEW PERRY'] = {'Months' : []}
CONTESTS['SATELLITES'] = {'Months' : ALL}
CONTESTS['DX-QSO']     = {'Months' : ALL}
CONTESTS['FOC-BW']     = {'Months' : []}
CONTESTS['JIDX']       = {'Months' : []}
CONTESTS['CQMM']       = {'Months' : []}
CONTESTS['HOLYLAND']   = {'Months' : []}
CONTESTS['AADX']       = {'Months' : []}
CONTESTS['IOTA']       = {'Months' : []}
CONTESTS['MARAC']      = {'Months' : []}
CONTESTS['SOLAR']      = {'Months' : []}
CONTESTS['OCDX']       = {'Months' : []}
#CONTESTS[]= {'Months' : []}
#CONTESTS[]= {'Months' : []}
                   
# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument('-ss', action='store_true',
                              help='ARRL Sweepstakes')
        arg_proc.add_argument('-naqp', action='store_true',
                              help='NAQP')
        arg_proc.add_argument('-cq160m', action='store_true',
                              help='CQ 160m CW')
        arg_proc.add_argument('-sst', action='store_true',
                              help='K1USN SST')
        arg_proc.add_argument('-mst', action='store_true',
                              help='ICWC MST')
        arg_proc.add_argument('-skcc', action='store_true',
                              help='SKCC')
        arg_proc.add_argument('-cwt', action='store_true',
                              help='CWops Mini Tests')
        arg_proc.add_argument('-cwopen', action='store_true',
                              help='CWops CW Open')
        arg_proc.add_argument('-pota', action='store_true',
                              help='POTA')
        arg_proc.add_argument('-wpx', action='store_true',
                              help='CQ WPX')
        arg_proc.add_argument('-arrl_dx', action='store_true',
                              help='ARRL Intl DX')
        arg_proc.add_argument('-arrl_10m', action='store_true',
                              help='ARRL 10m')
        arg_proc.add_argument('-arrl_160m', action='store_true',
                              help='ARRL 160m')
        arg_proc.add_argument('-cqp', action='store_true',
                              help='California QP')
        arg_proc.add_argument('-state', help='State QP',
                              type=str,default=None,nargs='*')
        arg_proc.add_argument('-aa', action='store_true',
                              help='All Asia DX')
        arg_proc.add_argument('-fd', action='store_true',
                              help='ARRL Field Day')
        arg_proc.add_argument('-vhf', action='store_true',
                              help='ARRL VHF')
        arg_proc.add_argument('-stew', action='store_true',
                              help='Stew Parry')
        arg_proc.add_argument('-jidx', action='store_true',
                              help='JIDX CW')
        arg_proc.add_argument('-ocdx', action='store_true',
                              help='OC DX CW')
        arg_proc.add_argument('-solar', action='store_true',
                              help='Solar Eclipse')
        arg_proc.add_argument('-cqmm', action='store_true',
                              help='CQMM DX')
        arg_proc.add_argument('-holy', action='store_true',
                              help='Holyland DX')
        arg_proc.add_argument('-iota', action='store_true',
                              help='RSGB IOTA')
        arg_proc.add_argument('-marac', action='store_true',
                              help='MARAC US Counties')
        arg_proc.add_argument('-sat', action='store_true',
                              help='Satellites')
        arg_proc.add_argument('-sprint', action='store_true',
                              help='NCCC CW Sprint')
        arg_proc.add_argument('-cqww', action='store_true',
                              help='CQ Worldwide')
        arg_proc.add_argument('-cqvhf', action='store_true',
                              help='CQ VHF')
        arg_proc.add_argument('-iaru', action='store_true',
                              help='IARU HF Championship')
        arg_proc.add_argument('-ten', action='store_true',
                              help='10-10 CW')
        arg_proc.add_argument('-bw', action='store_true',
                              help='FOC BW')
        arg_proc.add_argument('-wag', action='store_true',
                              help='Work All Germany')
        arg_proc.add_argument('-sac', action='store_true',
                              help='Scandinavia Activity')
        arg_proc.add_argument('-beru', action='store_true',
                              help='RSGB Commonwealth')
        arg_proc.add_argument('-rac', action='store_true',
                              help='RAC Winter QP')
        arg_proc.add_argument('-ragchew', action='store_true',
                              help='Regular Ragchew QSO')
        arg_proc.add_argument('-dx', action='store_true',
                              help='DX QSO')
        arg_proc.add_argument('-calls', action='store_true',
                              help='Random Calls')
        arg_proc.add_argument('-default', action='store_true',
                              help='Default (quick) QSO')
        arg_proc.add_argument('-sending', action='store_true',
                              help='Sending Practice')
        arg_proc.add_argument('-autofill', action='store_true',
                              help='Auto fill known information')
        arg_proc.add_argument('-autocomplete', action='store_true',
                              help='Auto Complete Partial Callsigns')
        arg_proc.add_argument('-test', action='store_true',
                              help='Disable TX')
        arg_proc.add_argument('-practice', action='store_true',
                              help='Practice mode')
        arg_proc.add_argument('-immediate', action='store_true',
                              help='Send text immediately')
        arg_proc.add_argument('-sidetone', action='store_true',
                              help='Sidetone Osc')
        arg_proc.add_argument('-split', action='store_true',
                              help='Split Text Window')
        arg_proc.add_argument('-hints', action='store_true',
                              help='Show hints')
        arg_proc.add_argument('-capture', action='store_true',
                              help='Record Rig Audio')
        arg_proc.add_argument('-aggressive', action='store_true',
                              help='Aggressively keep main window on top')
        arg_proc.add_argument('-force', action='store_true',
                              help='Force rig connection (debugging)')
        arg_proc.add_argument('-ca_only', action='store_true',
                              help='Only use California Stations for Practice')
        arg_proc.add_argument("-wpm", help="CW speed",type=int,default=20)
        arg_proc.add_argument('-adjust', action='store_true',
                              help='Adjust speed based on correct copy')
        arg_proc.add_argument('-scp', action='store_true',
                              help='Enable Super Check partial')
        arg_proc.add_argument("-rig", help="Connection Type - 1st rig",
                              type=str,default=["NONE"],nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port", help="Connection Port - 1st rig",
                              type=int,default=0)
        arg_proc.add_argument("-rig2", help="Connection Type - 2nd rig",
                              type=str,default=["NONE"],nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port2", help="Connection Port - 2nd rig",
                              type=int,default=0)
        arg_proc.add_argument("-rig3", help="Connection Type - 3rd rig",
                              type=str,default=["NONE"],nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port3", help="Connection Port - 2nd rig",
                              type=int,default=0)
        arg_proc.add_argument("-max_age", help="Max age in hours",
                              type=int,default=9999)
        arg_proc.add_argument("-nrows", help="No. STO/RCL rows",
                              type=int,default=1)
        arg_proc.add_argument('-nano', action='store_true',
                              help="Use Nano IO Interface")
        arg_proc.add_argument('-k3ng', action='store_true',
                              help="Use K3NG IO Interface")
        arg_proc.add_argument('-winkeyer', action='store_true',
                              help="Use Winkeyer IO Interface")
        arg_proc.add_argument('-echo', action='store_true',
                              help="Echo response from Nano IO to text box")
        arg_proc.add_argument('-cwio', action='store_true',
                              help="Use FLRIG or HAMLIB for CW IO")
        arg_proc.add_argument('-lock', action='store_true',
                              help="Lock Paddle Speed to Computer Speed")
        arg_proc.add_argument("-mode", help="Rig Mode",
                              type=str,default=None,
                              choices=[None,'CW','SSB','RTTY'])
        arg_proc.add_argument("-log", help="Log file name",
                              type=str,default=None)
        arg_proc.add_argument("-rotor", help="Rotor connection Type",
                              type=str,default="NONE",
                              choices=['HAMLIB','NONE'])
        arg_proc.add_argument("-port9", help="Rotor connection Port",
                              type=int,default=0)
        arg_proc.add_argument('-server', action='store_true',
                              help='Start hamlib server')
        arg_proc.add_argument('-udp', action='store_true',
                              help='Start UDP server')
        arg_proc.add_argument('-shadow', action='store_true',
                              help='Shadow helper')
        arg_proc.add_argument('-gps', action='store_true',
                              help='Read GPS info from .gpsrc file')
        arg_proc.add_argument('-use_log_hist', action='store_true',
                              help='Use history from log')
        arg_proc.add_argument('-use_adif_hist', action='store_true',
                              help='Use history from adif log')
        arg_proc.add_argument('-geo',type=str,default=None,
                              help='Geometry')
        arg_proc.add_argument('-desktop',type=int,default=None,
                              help='Desk Top Work Space No.')
        arg_proc.add_argument('-special', action='store_true',
                              help='Special settings for VHF work')
        args = arg_proc.parse_args()

        self.OP_STATE      = 0
        self.SPRINT        = args.sprint
        self.SHADOW        = args.shadow
        self.CAPTURE       = args.capture
        self.RIG_AUDIO_IDX = None
        self.FORCE         = args.force
        self.AGGRESSIVE    = args.aggressive
        self.TEST_MODE     = args.test
        self.RX_Clar_On    = True
        self.DESKTOP       = args.desktop
        
        self.SENDING_PRACTICE = args.sending
        self.WINKEYER      = args.winkeyer
        self.K3NG_IO       = args.k3ng
        self.NANO_IO       = args.nano # or args.sending
        self.USE_KEYER     = self.NANO_IO or self.K3NG_IO or self.WINKEYER
        self.NANO_ECHO     = self.USE_KEYER and args.echo
        self.CW_IO         = args.cwio
        self.LOCK_SPEED    = args.lock
        self.SPECIAL       = args.special
        self.GEO           = args.geo
        
        self.AUTOFILL      = args.autofill
        self.PRACTICE_MODE = args.practice or args.rig[0]=="NONE"
        self.ADJUST_SPEED  = args.adjust and args.practice
        self.NO_HINTS      = not args.hints
        self.CA_ONLY       = args.ca_only
        self.WPM           = args.wpm
        self.INIT_MODE     = args.mode
        self.LOG_FILE      = args.log
        
        self.connection    = args.rig[0]
        if len(args.rig)>=2:
            self.rig       = args.rig[1]
        else:
            self.rig       = None
        self.PORT          = args.port
            
        self.connection2   = args.rig2[0]
        if len(args.rig2)>=2:
            self.rig2      = args.rig2[1]
        else:
            self.rig2      = None
        self.PORT2         = args.port2
            
        self.connection3   = args.rig3[0]
        if len(args.rig3)>=2:
            self.rig3      = args.rig3[1]
        else:
            self.rig3      = None
        self.PORT3         = args.port3
            
        self.NUM_ROWS      = args.nrows
        self.HAMLIB_SERVER = args.server
        self.UDP_SERVER    = args.udp
        self.udp_server    = None
        self.SO2V          = False
        self.DXSPLIT       = False
        self.GPS           = args.gps
        self.USE_LOG_HISTORY  = args.use_log_hist
        self.USE_ADIF_HISTORY = args.use_adif_hist
        self.SIDETONE      = args.sidetone or self.PORT==1 or \
            (self.PRACTICE_MODE and not self.USE_KEYER)

        self.MY_CNTR       = 1
        self.PRECS         = PRECS
        self.SHUTDOWN      = False
        self.DIRTY         = False
        self.KEYING        = None
        self.USE_SCP       = args.scp
        self.AUTO_COMPLETE = args.autocomplete # or self.USE_SCP
        self.HIST          = {}

        self.STATE_LIST=args.state
        self.STATE_QPs = ['BCQP','ONQP','QCQP','W1QP','W7QP','CPQP']
        for state in STATES:
            self.STATE_QPs.append(state+'QP')

        """
        self.CONTEST_LIST=['Default','Ragchew','CWT','SST','MST','NS','SKCC','CW Open',
                           'ARRL-VHF','NAQP-CW', 'TEN-TEN','WAG', 'SAC', 'RAC', 'BERU',
                           'CQP','IARU-HF','CQWW','CQ-WPX-CW','CQ-VHF','CQ-160M',
                           'ARRL-10M','ARRL-160M','ARRL-DX', 'ARRL-FD','ARRL-SS-CW',
                           'STEW PERRY','SATELLITES','DX-QSO','FOC-BW',
                           'JIDX','CQMM','HOLYLAND','AADX','IOTA','MARAC',
                           'SOLAR','OCDX','POTA']
        """
        #self.CONTEST_LIST = CONTESTS.keys()

        now = datetime.datetime.utcnow()
        self.CONTEST_LIST = []
        for contest in CONTESTS.keys():
            if now.month in CONTESTS[contest]['Months']:
                self.CONTEST_LIST.append(contest)
            
        if args.state!=None:
            for state in args.state:
                self.CONTEST_LIST.append(state+'QP')

        self.SHOW_TEXT_BOX2=args.split
        MAX_AGE_HOURS = args.max_age
        if self.SPRINT:
            self.contest_name='NS'
            MAX_AGE_HOURS=1
        elif args.pota:
            self.contest_name='POTA'
        elif args.cwt:
            self.contest_name='CWT'
        elif args.sst:
            self.contest_name='SST'
        elif args.mst:
            self.contest_name='MST'
        elif args.ten:
            self.contest_name='TEN-TEN'
            MAX_AGE_HOURS=48
        elif args.bw:
            self.contest_name='FOC-BW'
            MAX_AGE_HOURS=24
        elif args.jidx:
            self.contest_name='JIDX'
            MAX_AGE_HOURS=30
        elif args.ocdx:
            self.contest_name='OCDX'
            MAX_AGE_HOURS=24
        elif args.solar:
            self.contest_name='SE'
            MAX_AGE_HOURS=10
        elif args.cqmm:
            self.contest_name='CQMM'
            MAX_AGE_HOURS=48-9
        elif args.holy:
            self.contest_name='HOLYLAND'
            MAX_AGE_HOURS=24
        elif args.marac:
            self.contest_name='MARAC'
            MAX_AGE_HOURS=48
        elif args.iota:
            self.contest_name='IOTA'
            MAX_AGE_HOURS=24
        elif args.aa:
            self.contest_name='AADX'
            MAX_AGE_HOURS=48
        elif args.wag:
            self.contest_name='WAG'
            MAX_AGE_HOURS=48
        elif args.sac:
            self.contest_name='SAC'
            MAX_AGE_HOURS=48
        elif args.beru:
            self.contest_name='BERU'
            MAX_AGE_HOURS=48
        elif args.rac:
            self.contest_name='RAC'
            MAX_AGE_HOURS=24
        elif args.skcc:
            self.contest_name='SKCC'
            MAX_AGE_HOURS=2
            #self.SHOW_TEXT_BOX2=True
        elif args.calls:
            self.contest_name='RANDOM CALLS'
            MAX_AGE_HOURS=2
        elif args.vhf:
            self.contest_name='ARRL-VHF'
            MAX_AGE_HOURS=33
        elif args.cqvhf:
            self.contest_name='CQ-VHF'
            MAX_AGE_HOURS=33
        elif args.naqp:
            self.contest_name='NAQP-CW'
            MAX_AGE_HOURS=12
        elif args.ss:
            self.contest_name='ARRL-SS-CW'
            if MAX_AGE_HOURS==9999:
                MAX_AGE_HOURS=30
        elif args.cqp:
            self.contest_name='CQP'
            MAX_AGE_HOURS=30
        elif args.state!=None:
            self.contest_name=args.state[0].upper()+'QP'
            MAX_AGE_HOURS=48
        elif args.cwopen:
            self.contest_name='CW Open'
            MAX_AGE_HOURS=4
        elif args.fd:
            self.contest_name='ARRL-FD'
            MAX_AGE_HOURS=48  #??
        elif args.stew:
            self.contest_name='STEW PERRY'
            MAX_AGE_HOURS=24  #??
        elif args.iaru:
            self.contest_name='IARU-HF'
            MAX_AGE_HOURS=48  #??
        elif args.cqww:
            self.contest_name='CQWW'
            MAX_AGE_HOURS=48
        elif args.wpx:
            self.contest_name = 'CQ-WPX-CW'
            MAX_AGE_HOURS=48
        elif args.arrl_10m:
            self.contest_name = 'ARRL-10M'
            MAX_AGE_HOURS=48    #??
        elif args.arrl_160m:
            self.contest_name = 'ARRL-160M'
            MAX_AGE_HOURS=42
        elif args.cq160m:
            self.contest_name = 'CQ-160M'
            MAX_AGE_HOURS=48    #??
        elif args.arrl_dx:
            self.contest_name = 'ARRL-DX'
            MAX_AGE_HOURS=48    #??
        elif args.sat:
            self.contest_name='SATELLITES'
            MAX_AGE_HOURS=9999
            #self.SHOW_TEXT_BOX2=True
        elif args.ragchew:
            self.contest_name='Ragchew'
            MAX_AGE_HOURS=9999
            #self.SHOW_TEXT_BOX2=True
        elif args.dx:
            self.contest_name='DX-QSO'
            #self.SHOW_TEXT_BOX2=True
            MAX_AGE_HOURS=9999
        else:
            self.contest_name='Default'
            #self.SHOW_TEXT_BOX2=True
        self.ROTOR_CONNECTION = args.rotor
        self.PORT9            = args.port9
        self.Immediate_TX     = args.immediate
        self.MAX_AGE          = MAX_AGE_HOURS*60       # In minutes

        # Read config file
        self.SETTINGS,self.RCFILE = read_settings('.keyerrc')
        self.SETTINGS['MY_QTH']=self.SETTINGS['MY_CITY']+', '+self.SETTINGS['MY_STATE']
        print('grid=',self.SETTINGS['MY_GRID'])
        if self.GPS:
            [lat,lon,alt,gridsq]=read_gps_coords()
            print('loc=',[lat,lon,alt,gridsq])
            #self.MY_GRID = latlon2maidenhead(lat,lon,12)
            self.MY_GRID = gridsq[:4]
        
            self.SETTINGS['MY_LAT'] = lat        
            self.SETTINGS['MY_LON'] = lon
            self.SETTINGS['MY_ALT'] = alt        
            self.SETTINGS['MY_GRID'] = self.MY_GRID        
            print('grid=',self.SETTINGS['MY_GRID'])

        # Where to find/put data files
        self.PLATFORM=platform.system()
        #MY_CALL = self.SETTINGS['MY_CALL'].replace('/','_')
        MY_CALL2 = self.SETTINGS['MY_CALL'].split('/')[0]
        self.HIST_DIR=os.path.expanduser('~/'+MY_CALL2+'/')
        if not os.path.isdir(self.HIST_DIR):
            fname=find_resource_file('master.csv')
            self.HIST_DIR=os.path.dirname(fname)+'/'
        self.HISTORY = self.HIST_DIR+'master.csv'
            
        self.WORK_DIR=os.path.expanduser('~/'+MY_CALL2+'/')
        if not os.path.isdir(self.WORK_DIR):
            HOME=os.path.expanduser('~/')
            print('HOME=',HOME)
            CURRENT=os.path.expanduser('./')
            print('CURRENT=',CURRENT)
            if CURRENT in HOME:
                self.WORK_DIR=CURRENT
            else:
                self.WORK_DIR=HOME
        print('WORK_DIR=',self.WORK_DIR)
                    
        #sys,exit(0)

