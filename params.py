################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
from rig_io import CONNECTIONS,RIGS,PRECS,STATES
from settings import *
import os
import platform
from utilities import find_resource_file
from collections import OrderedDict
import datetime
from dx.spot_processing import Station
from pprint import pprint

################################################################################

# Structure to contain basic info about various contests
CONTESTS = OrderedDict()
ALL=list(range(1,13))
CONTESTS['Default']      = {'Months' : ALL,     'Duration' : 9999}
CONTESTS['Ragchew']      = {'Months' : ALL,     'Duration' : 9999}
CONTESTS['CWT']          = {'Months' : ALL,     'Duration' : 1}
CONTESTS['MST']          = {'Months' : ALL,     'Duration' : 1}
CONTESTS['SST']          = {'Months' : ALL,     'Duration' : 1}
CONTESTS['AWT']          = {'Months' : ALL,     'Duration' : 1}
CONTESTS['NS']           = {'Months' : ALL,     'Duration' : 1}
CONTESTS['WRT']          = {'Months' : ALL,     'Duration' : 1}
CONTESTS['SKCC']         = {'Months' : ALL,     'Duration' : 2}
#CONTESTS['RANDOM CALLS'] = {'Months' : ALL,     'Duration' : 2}
CONTESTS['POTA']         = {'Months' : ALL,     'Duration' : 9999}
CONTESTS['CW Open']      = {'Months' : [9],     'Duration' : 4}
CONTESTS['ARRL-VHF']     = {'Months' : [1,6,9], 'Duration' : 33}
CONTESTS['CQ-VHF']       = {'Months' : [1,6,9], 'Duration' : 33}
CONTESTS['MAKROTHEN']    = {'Months' : [10],    'Duration' : 33}
CONTESTS['NAQP-CW']      = {'Months' : [1,8],   'Duration' : 12}
CONTESTS['NAQP-RTTY']    = {'Months' : [2,7],   'Duration' : 12}
CONTESTS['TEN-TEN']      = {'Months' : [],      'Duration' : 48}
CONTESTS['WINTER-FD']    = {'Months' : [1],     'Duration' : 30}
CONTESTS['WAG']          = {'Months' : [],      'Duration' : 48}
CONTESTS['SAC']          = {'Months' : [9],     'Duration' : 24}
CONTESTS['RAC']          = {'Months' : [6,12],  'Duration' : 24}
CONTESTS['BERU']         = {'Months' : [],      'Duration' : 48}
CONTESTS['CQP']          = {'Months' : [10],    'Duration' : 30}
CONTESTS['IARU-HF']      = {'Months' : [7],     'Duration' : 48}
CONTESTS['CQWW']         = {'Months' : [9,10,11], 'Duration' : 48}
CONTESTS['CQ-WPX-CW']    = {'Months' : [5],     'Duration' : 48}
CONTESTS['CQ-WPX-RTTY']  = {'Months' : [2],     'Duration' : 48}
CONTESTS['CQ-160M']      = {'Months' : [],      'Duration' : 48}
CONTESTS['ARRL-10M']     = {'Months' : [12],    'Duration' : 48}
CONTESTS['ARRL-160M']    = {'Months' : [],      'Duration' : 48}
CONTESTS['ARRL-DX']      = {'Months' : [2],     'Duration' : 30}
CONTESTS['ARRL-FD']      = {'Months' : [6],     'Duration' : 30}
CONTESTS['ARRL-SS-CW']   = {'Months' : [11],    'Duration' : 30}
CONTESTS['STEW PERRY']   = {'Months' : [],      'Duration' : 24}
CONTESTS['SATELLITES']   = {'Months' : ALL,     'Duration' : 9999}
CONTESTS['DX-QSO']       = {'Months' : ALL,     'Duration' : 9999}
CONTESTS['FOC-BW']       = {'Months' : [3],     'Duration' : 24}
CONTESTS['JIDX']         = {'Months' : [4],     'Duration' : 30}
CONTESTS['YURI']         = {'Months' : [4],     'Duration' : 24}
CONTESTS['SPDX']         = {'Months' : [4],     'Duration' : 24}
CONTESTS['CQMM']         = {'Months' : [4],     'Duration' : 48-9}
CONTESTS['HOLYLAND']     = {'Months' : [4],     'Duration' : 24}
CONTESTS['AADX']         = {'Months' : [6],     'Duration' : 48}
CONTESTS['IOTA']         = {'Months' : [7],     'Duration' : 24}
CONTESTS['MARAC']        = {'Months' : [7],     'Duration' : 48}
CONTESTS['SOLAR']        = {'Months' : [],      'Duration' : 10}
CONTESTS['OCDX']         = {'Months' : [],      'Duration' : 24}
CONTESTS['MARCONI']      = {'Months' : [7],     'Duration' : 24}
                   
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
        arg_proc.add_argument('-awt', action='store_true',
                              help='Japan AW Test')
        arg_proc.add_argument('-skcc', action='store_true',
                              help='SKCC')
        arg_proc.add_argument('-cwt', action='store_true',
                              help='CWops Mini Tests')
        arg_proc.add_argument('-cwopen', action='store_true',
                              help='CWops CW Open')
        arg_proc.add_argument('-pota', action='store_true',
                              help='POTA')
        arg_proc.add_argument('-wpx', action='store_true',
                              help='CQ WPX (CW or RTTY)')
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
        arg_proc.add_argument('-wfd', action='store_true',
                              help='Winter Field Day')
        arg_proc.add_argument('-fd', action='store_true',
                              help='ARRL Field Day')
        arg_proc.add_argument('-vhf', action='store_true',
                              help='ARRL VHF')
        arg_proc.add_argument('-mak', action='store_true',
                              help='Makrothen RTTY')
        arg_proc.add_argument('-stew', action='store_true',
                              help='Stew Parry')
        arg_proc.add_argument('-jidx', action='store_true',
                              help='JIDX CW')
        arg_proc.add_argument('-yuri', action='store_true',
                              help='Yuri Gagarin DX')
        arg_proc.add_argument('-spdx', action='store_true',
                              help='SP DX CW')
        arg_proc.add_argument('-ocdx', action='store_true',
                              help='OC DX CW')
        arg_proc.add_argument('-marconi', action='store_true',
                              help='Marconi Memorial')
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
        arg_proc.add_argument('-wrt', action='store_true',
                              help='Weekly RTTY Test')
        arg_proc.add_argument('-cqww', action='store_true',
                              help='CQ Worldwide')
        arg_proc.add_argument('-cqvhf', action='store_true',
                              help='CQ VHF')
        arg_proc.add_argument('-iaru', action='store_true',
                              help='IARU HF Championship')
        arg_proc.add_argument('-ten', action='store_true',
                              help='10-10 CW')
        arg_proc.add_argument('-foc', action='store_true',
                              help='FOC BW')
        arg_proc.add_argument('-wag', action='store_true',
                              help='Work All Germany')
        arg_proc.add_argument('-sac', action='store_true',
                              help='Scandinavia Activity')
        arg_proc.add_argument('-beru', action='store_true',
                              help='RSGB Commonwealth')
        arg_proc.add_argument('-rac', action='store_true',
                              help='RAC Summer or Winter QPs')
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
        arg_proc.add_argument("-wpm", help="Keyer Speed",type=int,default=25)
        arg_proc.add_argument("-farnsworth", help="Farnsworth Speed",type=int,default=None)
        arg_proc.add_argument("-paddles", help="Paddle Speed",type=int,default=22)
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
                              type=int,default=None)
        arg_proc.add_argument("-nrows", help="No. STO/RCL rows",
                              type=int,default=1)
        arg_proc.add_argument("-keyer", help="Keyer Type",
                              type=str,default=None,
                              choices=['NONE','NANO','K3NG','WINKEY','ANY'])
        arg_proc.add_argument('-nano', action='store_true',
                              help="Use Nano IO Interface")
        arg_proc.add_argument('-k3ng', action='store_true',
                              help="Use K3NG IO Interface")
        arg_proc.add_argument('-winkeyer', action='store_true',
                              help="Use Winkeyer IO Interface")
        arg_proc.add_argument('-noecho', action='store_true',
                              help="Don't Echo response from Nano IO to text box")
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
        arg_proc.add_argument('-digi', action='store_true',
                              help='RTTY or other Digi Contest')
        arg_proc.add_argument('-wfonly', action='store_true',
                              help='FLDIGI is in Waterfall Only mode')
        arg_proc.add_argument('-geo',type=str,default=None,
                              help='Geometry')
        arg_proc.add_argument('-desktop',type=int,default=None,
                              help='Desk Top Work Space No.')
        arg_proc.add_argument('-special', action='store_true',
                              help='Special settings for VHF work')
        args = arg_proc.parse_args()

        self.CONTEST_ID    = ''
        self.OP_STATE      = 0
        self.SPRINT        = args.sprint
        self.SHADOW        = args.shadow
        self.CAPTURE       = args.capture
        self.FORCE         = args.force
        self.AGGRESSIVE    = args.aggressive
        self.TEST_MODE     = args.test
        self.RX_Clar_On    = True
        self.DESKTOP       = args.desktop

        self.SENDING_PRACTICE = args.sending
        self.WINKEYER      = args.winkeyer or args.keyer=='WINKEY'
        self.K3NG_IO       = args.k3ng or args.keyer=='K3NG'
        self.NANO_IO       = args.nano or args.keyer=='NANO'
        self.FIND_KEYER    = args.keyer=='ANY'
        self.USE_KEYER     = self.NANO_IO or self.K3NG_IO or \
            self.WINKEYER or self.FIND_KEYER
        self.NANO_ECHO     = self.USE_KEYER and not args.noecho
        self.CW_IO         = args.cwio
        self.LOCK_SPEED    = args.lock
        self.SPECIAL       = args.special
        self.GEO           = args.geo
        self.DIGI          = args.digi
        self.WF_ONLY       = args.wfonly
        
        self.AUTOFILL      = args.autofill
        self.PRACTICE_MODE = args.practice or args.rig[0]=="NONE"
        self.ADJUST_SPEED  = args.adjust and args.practice
        self.NO_HINTS      = not args.hints
        self.CA_ONLY       = args.ca_only
        
        self.WPM           = args.wpm
        self.WPM2          = args.wpm
        self.FARNSWORTH    = args.farnsworth!=None
        if self.FARNSWORTH:
            self.FARNS_WPM   = args.farnsworth
        else:
            self.FARNS_WPM   = 10     # 18
        self.PADDLE_WPM    = args.paddles
        
        self.INIT_MODE     = args.mode
        if self.INIT_MODE==None and self.DIGI:
            self.INIT_MODE     = 'RTTY'
        self.LOG_FILE      = args.log
        
        self.connection    = args.rig[0]
        if len(args.rig)>=2:
            self.rig       = args.rig[1]
        else:
            self.rig       = None
        self.PORT          = args.port
        self.keyer_device  = None
            
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
        self.SPLIT_VFOs    = False
        self.GPS           = args.gps
        self.CWOPS_MEMBERS = None

        # Overrride as these are depricated
        #self.USE_LOG_HISTORY  = args.use_log_hist
        #self.USE_ADIF_HISTORY = args.use_adif_hist
        self.USE_LOG_HISTORY  = False
        self.USE_ADIF_HISTORY = True        
        
        self.SIDETONE      = args.sidetone or self.PORT==1 or \
            (self.PRACTICE_MODE and not self.USE_KEYER)

        self.MY_CNTR       = 1
        self.PRECS         = PRECS
        self.SHUTDOWN      = False
        self.DIRTY         = False
        self.KEYING        = None
        self.SCORING       = None
        self.USE_SCP       = args.scp
        self.AUTO_COMPLETE = args.autocomplete # or self.USE_SCP
        self.HIST          = {}
        self.PTT           = False

        self.STATE_LIST=args.state
        self.STATE_QPs = ['BCQP','ONQP','QCQP','W1QP','W7QP','CPQP']
        for state in STATES:
            self.STATE_QPs.append(state+'QP')

        now = datetime.datetime.utcnow()
        self.CONTEST_LIST = []
        for contest in CONTESTS.keys():
            if now.month in CONTESTS[contest]['Months']:
                self.CONTEST_LIST.append(contest)
            
        if args.state!=None:
            for state in args.state:
                self.CONTEST_LIST.append(state+'QP')

        self.SHOW_TEXT_BOX2=args.split

        if self.SPRINT:
            self.contest_name='NS'
        elif args.pota:
            self.contest_name='POTA'
        elif args.cwt:
            self.contest_name='CWT'
        elif args.sst:
            self.contest_name='SST'
        elif args.wrt:
            self.contest_name='WRT'
        elif args.mst:
            self.contest_name='MST'
        elif args.awt:
            self.contest_name='AWT'
        elif args.ten:
            self.contest_name='TEN-TEN'
        elif args.foc:
            self.contest_name='FOC-BW'
        elif args.jidx:
            self.contest_name='JIDX'
        elif args.yuri:
            self.contest_name='YURI'
        elif args.spdx:
            self.contest_name='SPDX'
        elif args.ocdx:
            self.contest_name='OCDX'
        elif args.marconi:
            self.contest_name='MMC'
        elif args.solar:
            self.contest_name='SE'
        elif args.cqmm:
            self.contest_name='CQMM'
        elif args.holy:
            self.contest_name='HOLYLAND'
        elif args.marac:
            self.contest_name='MARAC'
        elif args.iota:
            self.contest_name='IOTA'
        elif args.aa:
            self.contest_name='AADX'
        elif args.wag:
            self.contest_name='WAG'
        elif args.sac:
            self.contest_name='SAC'
        elif args.beru:
            self.contest_name='BERU'
        elif args.rac:
            self.contest_name='RAC'
        elif args.skcc:
            self.contest_name='SKCC'
        elif args.calls:
            self.contest_name='RANDOM CALLS'
        elif args.vhf:
            self.contest_name='ARRL-VHF'
        elif args.cqvhf:
            self.contest_name='CQ-VHF'
        elif args.mak:
            self.contest_name='MAKROTHEN'
        elif args.naqp:
            if self.DIGI:
                self.contest_name='NAQP-RTTY'
            else:
                self.contest_name='NAQP-CW'
        elif args.ss:
            self.contest_name='ARRL-SS-CW'
        elif args.cqp:
            self.contest_name='CQP'
        elif args.state!=None:
            self.contest_name=args.state[0].upper()+'QP'
        elif args.cwopen:
            self.contest_name='CW Open'
        elif args.wfd:
            self.contest_name='WINTER-FD'
        elif args.fd:
            self.contest_name='ARRL-FD'
        elif args.stew:
            self.contest_name='STEW PERRY'
        elif args.iaru:
            self.contest_name='IARU-HF'
        elif args.cqww:
            self.contest_name='CQWW'
        elif args.wpx:
            if self.DIGI:
                self.contest_name = 'CQ-WPX-RTTY'
            else:
                self.contest_name = 'CQ-WPX-CW'
        elif args.arrl_10m:
            self.contest_name = 'ARRL-10M'
        elif args.arrl_160m:
            self.contest_name = 'ARRL-160M'
        elif args.cq160m:
            self.contest_name = 'CQ-160M'
        elif args.arrl_dx:
            self.contest_name = 'ARRL-DX'
        elif args.sat:
            self.contest_name='SATELLITES'
        elif args.ragchew:
            self.contest_name='Ragchew'
        elif args.dx:
            self.contest_name='DX-QSO'
        else:
            self.contest_name='Default'

        if self.contest_name not in self.CONTEST_LIST:
            self.CONTEST_LIST.append(self.contest_name)            
            
        if args.max_age!=None:
            MAX_AGE_HOURS = args.max_age
        elif self.contest_name in CONTESTS.keys():
            MAX_AGE_HOURS = CONTESTS[self.contest_name]['Duration']
        else:
            MAX_AGE_HOURS=48
        print('MAX_AGE_HOURS=',MAX_AGE_HOURS)

        self.ROTOR_CONNECTION = args.rotor
        self.PORT9            = args.port9
        self.Immediate_TX     = args.immediate
        self.MAX_AGE          = MAX_AGE_HOURS*60       # In minutes

        # Read config file
        self.read_config_file()

        # Where to find/put data files
        self.PLATFORM=platform.system()
        self.HIST_DIR=os.path.expanduser('~/Python/data/')
        if not os.path.isdir(self.HIST_DIR):
            fname=find_resource_file('master.csv')
            self.HIST_DIR=os.path.dirname(fname)+'/'
        self.HISTORY = self.HIST_DIR+'master.csv'

    # Function to read config file and adjust various params accordingly
    def read_config_file(self):
        
        # Read config file
        self.SETTINGS,self.RCFILE = read_settings('.keyerrc')

        # Automajically include /6 if we're in the CQP
        call = self.SETTINGS['MY_CALL']
        if self.contest_name=='CQP' and '/' not in call:
            print('Checking call for CQP ... call=',call)
            station = Station(call)
            #pprint(vars(station))
            n = station.call_number
            #print('n=',n)
            if n!='6':
                self.SETTINGS['MY_CALL'] = call+'/6'
            print('call2=',self.SETTINGS['MY_CALL'])
            print('op=',self.SETTINGS['MY_OPERATOR'])
            #sys.exit(0)

        # Update location info
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

        # Select working directory
        #MY_CALL2 = self.SETTINGS['MY_CALL'].split('/')[0]
        MY_CALL2 = self.SETTINGS['MY_OPERATOR'].split('/')[0]
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

