#!/usr/bin/env -S uv run --script

# Script to add some qsos that somehow got lost back into log file

from fileio import *

LOG_FILE='sats.adif'

fp = open(LOG_FILE,"a+")

QSO= {'QSO_DATE_ON': '20260414', 'TIME_ON': '204738', 'QSO_DATE_OFF': '20260414', 'TIME_OFF': '204813', 'CALL': 'N6LN', 'FREQ': '145.9869', 'BAND': '2m', 'MODE': 'FM', 'SRX_STRING': '5,DM03,', 'STX_STRING': '5NN,DM12OX', 'NAME': '', 'QTH': 'DM03', 'SRX': '0', 'STX': '0', 'SAT_NAME': 'ISS', 'FREQ_RX': '437.8091', 'BAND_RX': '70cm', 'NOTES': '', 'RUNNING': '0', 'MY_RIG': 'IC9700', 'CONTEST_ID': ''}
write_adif_record(fp,QSO,None)

QSO= {'QSO_DATE_ON': '20260414', 'TIME_ON': '204852', 'QSO_DATE_OFF': '20260414', 'TIME_OFF': '204933', 'CALL': 'N6HA', 'FREQ': '145.9879', 'BAND': '2m', 'MODE': 'FM', 'SRX_STRING': '5,CM98,', 'STX_STRING': '5NN,DM12OX', 'NAME': '', 'QTH': 'CM98', 'SRX': '0', 'STX': '0', 'SAT_NAME': 'ISS', 'FREQ_RX': '437.8062', 'BAND_RX': '70cm', 'NOTES': '', 'RUNNING': '0', 'MY_RIG': 'IC9700', 'CONTEST_ID': ''}
write_adif_record(fp,QSO,None)

QSO= {'QSO_DATE_ON': '20260414', 'TIME_ON': '205146', 'QSO_DATE_OFF': '20260414', 'TIME_OFF': '205218', 'CALL': 'KJ7QEB', 'FREQ': '145.9929', 'BAND': '2m', 'MODE': 'FM', 'SRX_STRING': '5,?,', 'STX_STRING': '5NN,DM12OX', 'NAME': '', 'QTH': '?', 'SRX': '0', 'STX': '0', 'SAT_NAME': 'ISS', 'FREQ_RX': '437.7911', 'BAND_RX': '70cm', 'NOTES': '', 'RUNNING': '0', 'MY_RIG': 'IC9700', 'CONTEST_ID': ''}
write_adif_record(fp,QSO,None)

QSO= {'QSO_DATE_ON': '20260414', 'TIME_ON': '205414', 'QSO_DATE_OFF': '20260414', 'TIME_OFF': '205437', 'CALL': 'KJ5BAC', 'FREQ': '145.9933', 'BAND': '2m', 'MODE': 'FM', 'SRX_STRING': '5,EM10,', 'STX_STRING': '5NN,DM12OX', 'NAME': '', 'QTH': 'EM10', 'SRX': '0', 'STX': '0', 'SAT_NAME': 'ISS', 'FREQ_RX': '437.79', 'BAND_RX': '70cm', 'NOTES': '', 'RUNNING': '0', 'MY_RIG': 'IC9700', 'CONTEST_ID': ''}
write_adif_record(fp,QSO,None)

QSO= {'QSO_DATE_ON': '20260414', 'TIME_ON': '205442', 'QSO_DATE_OFF': '20260414', 'TIME_OFF': '205506', 'CALL': 'XE1YDK', 'FREQ': '145.9933', 'BAND': '2m', 'MODE': 'FM', 'SRX_STRING': '5,?,', 'STX_STRING': '5NN,DM12OX', 'NAME': '', 'QTH': '?', 'SRX': '0', 'STX': '0', 'SAT_NAME': 'ISS', 'FREQ_RX': '437.7899', 'BAND_RX': '70cm', 'NOTES': '', 'RUNNING': '0', 'MY_RIG': 'IC9700', 'CONTEST_ID': ''}
write_adif_record(fp,QSO,None)

fp.close()

