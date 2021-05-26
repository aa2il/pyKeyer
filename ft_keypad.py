############################################################################################

# FT Keypad - J.B.Attili - 2020

# Functions related to programming the Yaesu keypad

# To do - there are other version of this same thing floating around, combine them.

############################################################################################

import sys
if sys.version_info[0]==3:
    from tkinter import END
else:
    from Tkinter import END
from rig_io.ft_tables import *

############################################################################################

def GetKeyerMemory(self):
    s=self.sock

    print("\nReading Keyer Memory ...")
    for i in range(6):
        print("GetKeyerMemory: i=",i)
        if i<5:
            if s.connection=='HAMLIB' and False:
                cmd='w KM'+str(i+1)+'\n'
            else:
                cmd='KM'+str(i+1)+';'
        else:
            if s.connection=='HAMLIB' and False:
                cmd='w EX025\n'
            else:
                cmd='EX025;'

        ntries=0
        while ntries<5:
            ntries+=1
            buf=s.get_response(cmd)
            if len(buf)>0:
                break
            
        print("GetKeyerMemory: buf=",buf)
        if i<5:
            j=buf.index('}')
            self.Keyer[i]=buf[3:j]
        else:
            j=buf.index(';')
            self.Keyer[i]=buf[5:j]

        print("Done.")



def KeyerMemoryDefaults(self,arg):
    print("\Setting Keypad Defaults ",arg)

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

