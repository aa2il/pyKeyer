#! /usr/bin/python3
#######################################################################################

# Program to split up a wave file

import wave
import sys
import argparse
import datetime

CHUNK = 1024

#######################################################################################

# Get command line args
arg_proc = argparse.ArgumentParser()
arg_proc.add_argument("-i", help="Input WAVE file",
                              type=str,default=None)
args = arg_proc.parse_args()

# Work on input file
fname_in = args.i
print('fname_in=',fname_in)
if not fname_in:
    print("Plays a wave file.\n\nUsage: %s -i filename.wav" % sys.argv[0])
    sys.exit(-1)

a=fname_in.split('_')
b=a[2].split('.')
print(a)
print(b)

#start_time=b[0]
start_time = datetime.datetime.strptime( a[1]+' '+b[0], "%Y%m%d %H%M%S")
print('start_time=',start_time)

# Open wave file
wf = wave.open(fname_in, 'rb')
fs=wf.getframerate()
width=wf.getsampwidth()
channels=wf.getnchannels()

print('fs=',fs)
dt=CHUNK/fs
print('dt=',dt)

# Read data
data = wf.readframes(CHUNK)
t=start_time
hour=-1
wf2=None
while len(data) > 0:
    data = wf.readframes(CHUNK)
    if t.hour!=hour:
        fname_out = t.strftime("split_%Y%m%d_%H%M%S.wav")
        print('t=',t,hour,'\t',fname_out)
        hour=t.hour

        if wf2:
            wf2.writeframes(data)
            wf2.close()
        wf2 = wave.open(fname_out, 'wb')
        wf2.setnchannels(channels)
        wf2.setsampwidth(width)
        wf2.setframerate(fs)
        
    wf2.writeframes(data)
    t += datetime.timedelta(seconds=dt)

wf2.close()
sys.exit(0)

    
