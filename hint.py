############################################################################################
#
# hint.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for generating hints from past contest logs and/or contacts.
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

from rig_io import CA_COUNTIES   

############################################################################################

# Routine to sift through previous contest lists to get a hint of exhcange
# info (qth, member no. etc.)
def master(P,call,dx_station=None,VERBOSITY=0):

    call=call.upper()
    if VERBOSITY>0:
        print('HINT-MASTER: call=',call,len(P.calls))
    
    # Check for DX calls
    if (call not in P.calls) and dx_station and ('/' in call):
        call=dx_station.homecall
    
    if call in P.calls:
        if VERBOSITY>0:
            print('HINT-MASTER:',call,' is in master list')
        if P.KEYING:
            h=P.KEYING.hint(call)
            try:
                print(call,'\tmaster=',P.MASTER[call],'\nhint=',h)
            except:
                print('HINT MASTER - I dont know what I am doing here',call)
            return h
        else:
            print('HINT.MASTER: No hints available for this contest')
            return None

    else:
        if VERBOSITY>0:
            print('HINT.MASTER:',call,' is NOT in master list')
        if dx_station:
            if P.contest_name=='CQWW':
                return dx_station.cqz
        return None


# Routine to give a hint of QTH of a CA station
def commie_fornia(dx_station,qth):
    if dx_station.country=='United States' and dx_station.cqz==3:
        if VERBOSITY>0:
            print('Commie-fornia')
        #print CA_COUNTIES
        #hints= [s for s in CA_COUNTIES if qth in s]
        hints=[]
        n=len(qth)
        for s in CA_COUNTIES:
            if qth==s[0:n]:
                hints.append(s)
        return ' '.join(hints)
    else:
        return None

"""    
# Routine to give a hint of QTH of a Canadian station
def oh_canada(dx_station):

    Prefixes	Province/Territory
    VE1 VA1	Nova Scotia
    VE2 VA2	Quebec	
    VE3 VA3	Ontario	
    VE4 VA4	Manitoba	
    VE5 VA5	Saskatchewan	
    VE6 VA6	Alberta	
    VE7 VA7	British Columbia	
    VE8	Northwest Territories	
    VE9	New Brunswick	
    VE0*	International Waters
    VO1	Newfoundland
    VO2	Labrador
    VY1	Yukon	
    VY2	Prince Edward Island
    VY9**	Government of Canada
    VY0	Nunavut	
    CY0***	Sable Is.[16]	
    CY9***	St-Paul Is.[16]	

    For the CQP:
    MR      Maritimes
    QC      Quebec
    ON      Ontario
    MB      Manitoba
    SK      Saskatchewan
    AB      Alberta
    BC      British Columbia
    NT 

    # For Cali QSO Party:
    # MR = Maritime provinces plus Newfoundland and Labrador (NB, NL, NS, PE)
    CQP_VE_CALL_AREAS = ['??','MR','QC','ON','MB','SK','AB','BC','NT']

    if dx_station.country=='Canada':
        #if (dx_station.prefix=='VO2' or dx_station.prefix=='VY2'):
        if dx_station.prefix in ['VO2','VY2','VE9']:
            qth='MR'
        else:
            num=int( dx_station.call_number )
            if num>=0 and num<len( CQP_VE_CALL_AREAS ):
                qth=CQP_VE_CALL_AREAS[num]
            else:
                y
                qth=''
                print('**** ERROR *** HINTS - Oh Canada - having trouble with',\
                      dx_station.call,dx_station.call_number,num)
                
    elif dx_station.country=='Alaska':
        qth='AK'
    elif dx_station.country=='Hawaii':
        qth='HI'
    elif dx_station.country=='Puerto Rico':
        qth='PR'
    elif dx_station.country=='US Virgin Islands':
        qth='VI'
    elif dx_station.country and dx_station.country!='United States':
        qth='DX'
    else:
        qth=None
        
    return qth
    

"""
