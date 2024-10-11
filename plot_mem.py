#! /usr/bin/python3 -u

from fileio import read_csv_file
from datetime import datetime
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

###############################################################################

dirname='/tmp'
#dirname='CWT0300'
#dirname='CWT0700'
#dirname='NOUDP'

fname1=dirname+'/BANDMAP_MEMORY.TXT'
fname2=dirname+'/SDR_MEMORY.TXT'
fname3=dirname+'/KEYER_MEMORY.TXT'

###############################################################################

data,hdr=read_csv_file(fname1,FLAT_DATA=True,VERBOSITY=0)
print('\n',fname1,'\thdr=',hdr)
#print('data=',data)

t1=data[:,0]/60.
bm=data[:,1]

data,hdr=read_csv_file(fname2,FLAT_DATA=True,VERBOSITY=0)
print('\n',fname2,'\thdr=',hdr)
#print('data=',data)

t2=data[:,0]/60.
sdr=data[:,1]

data,hdr=read_csv_file(fname3,FLAT_DATA=True,VERBOSITY=0)
print('\n',fname3,'\thdr=',hdr)
#print('data=',data)

t3=data[:,0]/60.
keyer=data[:,1]

fig, ax = plt.subplots()
ax.plot(t1,bm,color='red',label='Bandmap')
ax.plot(t2,sdr,color='blue',label='SDR')
ax.plot(t3,keyer,color='green',label='Keyer')
    
ax.grid(True)
ax.set_title('Memory Usage')
ax.set_xlabel('Time (Min.)')
ax.set_ylabel('RSS Memory (Mb)')
ax.legend(loc='lower right')


plt.show()
