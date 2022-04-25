#! /usr/bin/python3 -u
################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
from rig_io.ft_tables import CONNECTIONS,RIGS,PRECS
from settings import *
import os
import platform

################################################################################

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
        arg_proc.add_argument('-wpx', action='store_true',
                              help='CQ WPX')
        arg_proc.add_argument('-arrl_dx', action='store_true',
                              help='ARRL DX')
        arg_proc.add_argument('-arrl_10m', action='store_true',
                              help='ARRL 10m')
        arg_proc.add_argument('-cqp', action='store_true',
                              help='California QP')
        arg_proc.add_argument('-fd', action='store_true',
                              help='ARRL Field Day')
        arg_proc.add_argument('-vhf', action='store_true',
                              help='ARRL VHF')
        arg_proc.add_argument('-stew', action='store_true',
                              help='Stew Parry')
        arg_proc.add_argument('-sat', action='store_true',
                              help='Satellites')
        arg_proc.add_argument('-sprint', action='store_true',
                              help='NCCC CW Sprint')
        arg_proc.add_argument('-cqww', action='store_true',
                              help='CQ Worldwide')
        arg_proc.add_argument('-iaru', action='store_true',
                              help='IARU HF Championship')
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
        arg_proc.add_argument('-test', action='store_true',
                              help='Disable TX')
        arg_proc.add_argument('-practice', action='store_true',
                              help='Practice mode')
        arg_proc.add_argument('-sidetone', action='store_true',
                              help='Sidetone Osc')
        arg_proc.add_argument('-split', action='store_true',
                              help='Split Text Window')
        arg_proc.add_argument('-nohints', action='store_true',
                              help='No hints')
        arg_proc.add_argument('-capture', action='store_true',
                              help='Record Rig Audio')
        arg_proc.add_argument('-force', action='store_true',
                              help='Force rig connection (debugging)')
        arg_proc.add_argument('-master', action='store_true',
                              help='Use Master History File')
        arg_proc.add_argument('-ca_only', action='store_true',
                              help='Only use California Stations')
        arg_proc.add_argument("-wpm", help="CW speed",type=int,default=20)
        arg_proc.add_argument('-adjust', action='store_true',
                              help='Adjust speed based on correct copy')
        arg_proc.add_argument("-rig", help="Connection Type - 1st rig",
                              type=str,default=["ANY"],nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port", help="Connection Port - 1st rig",
                              type=int,default=0)
        arg_proc.add_argument("-rig2", help="Connection Type - 2nd rig",
                              type=str,default=["NONE"],nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port2", help="Connection Port - 2nd rig",
                              type=int,default=0)
        arg_proc.add_argument("-max_age", help="Max age in hours",
                              type=int,default=9999)
        arg_proc.add_argument("-nrows", help="No. STO/RCL rows",
                              type=int,default=2)
        arg_proc.add_argument('-nano', action='store_true',
                              help="Use Nano IO Interface")
        arg_proc.add_argument("-mode", help="Rig Mode",
                              type=str,default=None,
                              choices=[None,'CW','SSB'])
        arg_proc.add_argument("-log", help="Log file name",
                              type=str,default=None)
        arg_proc.add_argument("-rotor", help="Rotor connection Type",
                              type=str,default="NONE",
                              choices=['HAMLIB','NONE'])
        arg_proc.add_argument("-port3", help="Rotor onnection Port",
                              type=int,default=0)
        arg_proc.add_argument('-server', action='store_true',
                              help='Start hamlib server')
        arg_proc.add_argument('-udp', action='store_true',
                              help='Start UDP server')
        arg_proc.add_argument('-gps', action='store_true',
                              help='Read GPS info from .gpsrc file')
        arg_proc.add_argument('-use_log_hist', action='store_true',
                              help='Use history from log')
        arg_proc.add_argument('-use_adif_hist', action='store_true',
                              help='Use history from adif log')
        args = arg_proc.parse_args()

        self.SPRINT        = args.sprint
        self.CAPTURE       = args.capture
        self.RIG_AUDIO_IDX = None
        self.FORCE         = args.force
        self.TEST_MODE     = args.test
        self.NANO_IO       = args.nano
        self.SENDING_PRACTICE = args.sending
        self.AUTOFILL      = args.autofill
        self.PRACTICE_MODE = args.practice
        self.ADJUST_SPEED  = args.adjust and args.practice
        self.NO_HINTS      = args.nohints
        self.USE_MASTER    = args.master or True      # Always set this for now - cant think of a reason not to?
        self.CA_ONLY       = args.ca_only
        #self.DIRECT_CONNECT = args.direct
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
            
        self.NUM_ROWS      = args.nrows
        self.HAMLIB_SERVER = args.server
        self.UDP_SERVER    = args.udp
        self.GPS           = args.gps
        self.USE_LOG_HISTORY  = args.use_log_hist
        self.USE_ADIF_HISTORY = args.use_adif_hist
        self.SIDETONE      = args.sidetone or self.PORT==1

        #self.CONTEST       = CONTEST
        #self.MACROS        = MACROS
        self.MY_CNTR       = 1
        self.PRECS         = PRECS
        self.SHUTDOWN      = False
        self.DIRTY         = False

        self.KEYING=None

        self.CONTEST_LIST=['Default','Ragchew','CWT','SST','MST','SKCC','CW Open',
                           'ARRL VHF','NAQP-CW', \
                           'CQP','IARU-HF','CQWW','CQ-WPX-CW','ARRL-10M','ARRL-DX' \
                           'ARRL-FD','ARRL-SS-CW','STEW PERRY','SATELLITES','DX-QSO']
        self.SHOW_TEXT_BOX2=args.split
        if self.SPRINT:
            print('NEED TO FIX THIS!!!!!!!!!!!!!')
            sys.exit(0)
            self.KEYING=SPRINT_KEYING(self)
            MAX_AGE_HOURS=1
        elif args.cwt:
            self.contest_name='CWT'
            MAX_AGE_HOURS=1
        elif args.sst:
            self.contest_name='SST'
            MAX_AGE_HOURS=1
        elif args.mst:
            self.contest_name='MST'
            MAX_AGE_HOURS=1
        elif args.skcc:
            self.contest_name='SKCC'
            MAX_AGE_HOURS=2
            self.SHOW_TEXT_BOX2=True
        elif args.calls:
            self.contest_name='RANDOM CALLS'
            MAX_AGE_HOURS=2
        elif args.vhf:
            self.contest_name='ARRL VHF'
            MAX_AGE_HOURS=33
        elif args.naqp:
            self.contest_name='NAQP-CW'
            MAX_AGE_HOURS=12
        elif args.ss:
            self.contest_name='ARRL-SS-CW'
            MAX_AGE_HOURS=30
        elif args.cqp:
            self.contest_name='CQP'
            MAX_AGE_HOURS=48 #??
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
        elif args.arrl_dx:
            self.contest_name = 'ARRL-DX'
            MAX_AGE_HOURS=48    #??
        elif args.sat:
            self.contest_name='SATELLITES'
            MAX_AGE_HOURS=9999
            self.SHOW_TEXT_BOX2=True
        elif args.ragchew:
            self.contest_name='Ragchew'
            MAX_AGE_HOURS=9999
            self.SHOW_TEXT_BOX2=True
        elif args.dx:
            self.contest_name='DX-QSO'
            self.SHOW_TEXT_BOX2=True
            MAX_AGE_HOURS=9999
        else:
            self.contest_name='Default'
            MAX_AGE_HOURS=9999
            self.SHOW_TEXT_BOX2=True
        self.ROTOR_CONNECTION = args.rotor
        self.PORT3            = args.port3

        # Compute length of contest
        if args.max_age!=9999:
            self.MAX_AGE       = args.max_age*60        # In minutes
        else:
            self.MAX_AGE       = MAX_AGE_HOURS*60       # In minutes
            
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
        MY_CALL = self.SETTINGS['MY_CALL'].replace('/','_')
        self.HIST_DIR=os.path.expanduser('~/'+MY_CALL+'/')
        self.DATA_DIR=os.path.expanduser('~/'+MY_CALL+'/')
        if self.USE_MASTER:
            self.HISTORY = self.HIST_DIR+'master.csv'
                    
        #sys,exit(0)

