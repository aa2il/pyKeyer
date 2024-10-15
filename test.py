#! /usr/bin/python3

# importing libraries
import sys
from utilities import *
from fileio import *
import copy
import pandas as pd
from pympler import asizeof
from collections import OrderedDict ,ChainMap

#from memory_profiler import profile

#@profile


class QSO:
    def __init__(self,qso):

        keys=qso.keys()
        for key in keys:
            setattr(self, key, qso[key] )

        return
        

        self.call=qso['CALL']
        self.band=qso['BAND']
        self.freq=qso['FREQ']
        self.mode=qso['MODE']
        self.qso_date=qso['QSO_DATE']
        self.time_off=qso['TIME_OFF']
    
    
# Function to read list of qsos from input file
def parse_adif99(fname,line=None,upper_case=False,verbosity=0,REVISIT=False):
    logbook = []

    if verbosity>0:
        print('PARSE_ADIF: Reading',fname,'...')

    try:

        # Open adif file
        if line==None:
            if verbosity>0:
                print('PARSE_ADIF: Opening',fname,'...')
            fp=codecs.open(fname, 'r', encoding='utf-8',
                           errors='ignore')
            raw1 = re.split('(?i)<eoh>',fp.read() )
            if verbosity>0:
                print('PARSE_ADIF: raw1=',raw1)
            if not REVISIT:
                fp.close()
                fp=None
        else:
            raw1 = re.split('(?i)<eoh>',line )
            
    except:
        
        error_trap('FILE_IO->PARSE_ADIF: *** Unable to open file or other error')
        print('fname=',fname)
        return logbook
        
    raw = copy.copy( re.split('(?i)<eor>',raw1[-1] ) )
    if verbosity>0:
        print('PARSE_ADIF: raw=',raw)

    nrecs=0
    for record in raw:
        nrecs+=1
        if verbosity>0:
            print('PARSE_ADIF: Rec No.',nrecs,len(record),'rec=\n',record)
        if len(record)<=1:
            continue
        
        qso = OrderedDict() 
        tags = copy.copy( re.findall('<(.*?):(\d+).*?>([^<]+)',record) )

        if '# FLAG IT!' in record:
            #print('# FLAG ON THE FIELD!')
            #logbook[-1]['flagged']='1'
            #print(logbook[-1])
            pass

        for tag in tags:
            if upper_case:
                qso[copy.deepcopy(tag[0].upper())] = copy.deepcopy( tag[2][:int(tag[1])] )
            else:
                qso[copy.deepcopy(tag[0].lower())] = copy.deepcopy( tag[2][:int(tag[1])] )

        if 'call' in qso or 'CALL' in qso:
            if upper_case:
                if 'QSO_DATE_OFF' not in qso:
                    qso['QSO_DATE_OFF'] = qso['QSO_DATE']
                if 'TIME_OFF' not in qso:
                    qso['TIME_OFF'] = qso['TIME_ON']
            else:
                if 'qso_date_off' not in qso:
                    qso['qso_date_off'] = qso['qso_date']
                if 'time_off' not in qso:
                    qso['time_off'] = qso['time_on']
            logbook.append( copy.copy(qso) )
            #logbook =logbook.new_child( copy.copy(qso) )

        #else:
        #    print('Empty record:\n',record)

    return logbook




MEM = Memory_Monitor('/tmp/KEYER_MEMORY.TXT')
MEM.take_snapshot()
LOG_FILE='AA2IL.adif'

"""
q={'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6}

q={'BAND': '15m', 'BAND_RX': '15m', 'CALL': 'W0ABE', 'FREQ': '21.038', 'FREQ_RX': '21.038', 'MODE': 'CW', 'MY_CITY': 'RAMONA, CA', 'MY_GRIDSQUARE': 'DM12OX', 'NAME': 'FIN', 'QSO_DATE': '20240101', 'QSO_DATE_OFF': '20240101', 'QSO_DATE_ON': '20240101', 'RST_RCVD': '599', 'RST_SENT': '599', 'RUNNING': '0', 'SRX': '0', 'SRX_STRING': '2,FIN', 'STATION_CALLSIGN': 'AA2IL', 'STX': '1', 'STX_STRING': '1,JOE', 'TIME_OFF': '190115', 'TIME_ON': '190115', 'CONTEST_ID': 'ICWC-MST'}

b=sys.getsizeof(q)
print(q,b)
sys.exit(0)
"""

qsos = parse_adif99(LOG_FILE,upper_case=True,verbosity=0)
print('asize=',asizeof.asizeof(qsos)/1024**2)

mb=sys.getsizeof(qsos)/(1024**2)
nqsos=len(qsos)
print('len=',nqsos,'\tmb=',mb)
if nqsos>0 and False:
    q=copy.copy(qsos[0])
    print(q)
    mb=sys.getsizeof(q) /(1024**2)
    print('mb=',mb,nqsos*mb)

MEM.take_snapshot()

# Calling DataFrame constructor on list
print('Data frame')
df = pd.DataFrame(copy.deepcopy(qsos))
print(df)
print('asize=',asizeof.asizeof(df)/1024**2)
df.to_csv('junk.csv')

print('--------------')
df2 = pd.read_csv('junk.csv')
print(df2)
print('asize=',asizeof.asizeof(df2)/1024**2)

MEM.take_snapshot()

#print('Delete')
#del qsos

qsos2=[]
total=0
for qso in qsos:
    kb=asizeof.asizeof(qso)/1024
    total+=kb
    qsos2.append( QSO(qso) )
total/=1024
print('total=',total)
print('asize=',asizeof.asizeof(qsos2)/1024**2)

kb=asizeof.asizeof(qsos[0])/1024
print(qsos[0])
print('kb=',kb)

kb2=asizeof.asizeof(qsos2[0])/1024
print(qsos2[0])
print('kb=',kb2)

MEM.take_snapshot()

sys.exit(0)


fname='Book.txt'
Done=False
with open(fname,encoding='utf8') as f:
    while not Done:
        line=f.readline()
        print(line)
        if not line:
            Done=True
