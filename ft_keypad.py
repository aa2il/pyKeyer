############################################################################################
#
# ft_keypad.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Functions related to programming the Yaesu keypad
#
# To do - there are other version of this same thing floating around in
# this mess, combine them.
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

import sys
if sys.version_info[0]==3:
    from tkinter import END
else:
    from Tkinter import END

############################################################################################

def GetKeyerMemory(self):
    s=self.sock

    print("\nReading Keyer Memory ...")
    for i in range(6):
        print("GetKeyerMemory: i=",i)
        if i<5:
            cmd='KM'+str(i+1)+';'
        else:
            cmd='EX025;'

        ntries=0
        while ntries<5:
            ntries+=1
            buf=s.get_response(cmd)
            if buf and len(buf)>0:
                break
            
        print("GetKeyerMemory: buf=",buf,len(buf))
        if buf and len(buf)>0:
            if i<5:
                j=buf.index('}')
                self.Keyer[i]=buf[3:j]
            else:
                j=buf.index(';')
                self.Keyer[i]=buf[5:j]

        print("Done.")



def KeyerMemoryDefaults(self,arg):
    print("\Setting Keypad Defaults ",arg)
    
    MY_CALL     = self.P.SETTINGS['MY_CALL']
    MY_NAME     = self.P.SETTINGS['MY_NAME']
    MY_STATE    = self.P.SETTINGS['MY_STATE']
    MY_SEC      = self.P.SETTINGS['MY_SEC']
    MY_CAT      = self.P.SETTINGS['MY_CAT']
    MY_PREC     = self.P.SETTINGS['MY_PREC']
    MY_CHECK    = self.P.SETTINGS['MY_CHECK']
    MY_COUNTY   = self.P.SETTINGS['MY_COUNTY']
    MY_CQ_ZONE  = self.P.SETTINGS['MY_CQ_ZONE']
    MY_ITU_ZONE = self.P.SETTINGS['MY_ITU_ZONE']
    MY_GRID     = self.P.SETTINGS['MY_GRID']
    
    if arg==1:
        # ARRL Intl DX Contest & CQ 160m
        Keyer=[MY_CALL,'TU 5NN '+MY_STATE,MY_STATE+' '+MY_STATE,'73','AGN?','0001']
    elif arg==2:
        # NAQP
        Keyer=[MY_CALL,'TU '+MY_NAME+' '+MY_STATE,MY_NAME+' '+MY_NAME,MY_STATE+' '+MY_STATE,'AGN?','0001']
    elif arg==3:
        # IARU HF Champ
        Keyer=[MY_CALL,'TU 5NN '+MY_ITU_ZONE,'T6 T6','73','AGN?','0001']
    elif arg==4:
        # CQ WW
        Keyer=[MY_CALL,'TU 5NN '+MY_CQ_ZONE,'T3 T3','73','AGN?','GL']
    elif arg==5:
        # CQ WPX
        Keyer=[MY_CALL,'TU 5NN 1','001 001','73','AGN?','0001']
    elif arg==6:
        # ARRL 160m
        Keyer=[MY_CALL,'TU 5NN '+MY_SEC,MY_SEC+' '+MY_SEC,'73','AGN?','0001']
    elif arg==7:
        # ARRL Field Day
        Keyer=[MY_CALL,'TU '+MY_CAT+' '+MY_SEC,MY_CAT+' '+MY_CAT,MY_SEC+' '+MY_SEC,'AGN?','0001']
    elif arg==99:
        # Test
        Keyer=['TEST1','2','3','4','5','0001']
    else:
        # Regular quick exchanges
        Keyer=[MY_CALL,'TU 5NN '+MY_STATE,'OP '+MY_NAME,'73','BK','0001']

    for i in range(6):
        self.ekeyer[i].delete(0,END)
        self.ekeyer[i].insert(0,Keyer[i])

    self.Keyer=Keyer;
    print("Done.")

def UpdateKeyerMemory(self):
    s=self.sock;

    print("\nUpdating keypad ...")
    for i in range(6):
        self.Keyer[i] = self.ekeyer[i].get()
        if i<5:
            if s.connection=='HAMLIB':
                cmd='w BY;KM'+str(i+1)+self.Keyer[i]+'}\n'
            else:
                cmd='KM'+str(i+1)+self.Keyer[i]+'};'
        else:
            if s.connection=='HAMLIB':
                cmd='w BY;EX025'+self.Keyer[i]+'\n'
            else:
                cmd='EX025'+self.Keyer[i]+';'
        print("cmd=",cmd)
        #buf=get_response(s,cmd)
        buf=self.sock.get_response(cmd)

    print("Done.")

