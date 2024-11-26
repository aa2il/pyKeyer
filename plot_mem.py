#! /usr/bin/python3 -u

from fileio import read_csv_file
from datetime import datetime
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
import csv

###############################################################################

dirname='/tmp/'
#dirname='junk3/'
#dirname=''

fname1=dirname+'BANDMAP_MEMORY.TXT'
fname2=dirname+'SDR_MEMORY.TXT'
fname3=dirname+'KEYER_MEMORY.TXT'
fname4=dirname+'BANDMAP_MEMORY_WSJT.TXT'

fname5=dirname+'LOG2.TXT'
tag='AF'

###############################################################################

try:
    data,hdr=read_csv_file(fname1,FLAT_DATA=True,VERBOSITY=0)
    print('\n',fname1,'\thdr=',hdr)
    #print('data=',data)
    
    t1=data[:,0]/60.
    bm=data[:,1]
except:
    t1=[]
    bm=[]

try:
    data,hdr=read_csv_file(fname2,FLAT_DATA=True,VERBOSITY=0)
    print('\n',fname2,'\thdr=',hdr)
    #print('data=',data)

    t2=data[:,0]/60.
    sdr=data[:,1]
except:
    t2=[]
    sdr=[]

try:
    data,hdr=read_csv_file(fname3,FLAT_DATA=True,VERBOSITY=0)
    print('\n',fname3,'\thdr=',hdr)
    #print('data=',data)

    t3=data[:,0]/60.
    keyer=data[:,1]
except:
    t3=[]
    keyer=[]

try:
    data,hdr=read_csv_file(fname4,FLAT_DATA=True,VERBOSITY=0)
    print('\n',fname4,'\thdr=',hdr)
    #print('data=',data)

    t4=data[:,0]/60.
    bm2=data[:,1]
except:
    t4=[]
    bm2=[]

fig, ax = plt.subplots()
if len(t1)>0:
    ax.plot(t1,bm,color='red',label='Bandmap')
if len(t2)>0:
    ax.plot(t2,sdr,color='blue',label='SDR')
if len(t3)>0:
    ax.plot(t3,keyer,color='green',label='Keyer')
if len(t4)>0:
    ax.plot(t1,bm,color='magenta',label='Bandmap 2')
    
ax.grid(True)
ax.set_title('Memory Usage')
ax.set_xlabel('Time (Min.)')
ax.set_ylabel('RSS Memory (Mb)')
ax.legend(loc='lower right')

plt.show()


t0=None
t5=[]
nsamps=[]
with open(fname5, mode ='r') as f:
    csvFile = csv.reader(f)
    for line in csvFile:
        #print(line)
        if line[0]==tag:
            if t0==None:
                t0=float(line[1])
            t5.append(float(line[1])-t0)
            nsamps.append(int(line[2]))

if len(t5)>0:
    fig, ax = plt.subplots()
    ax.plot(t5,nsamps,color='red',label=tag)
plt.show()

sys.exit(0)

