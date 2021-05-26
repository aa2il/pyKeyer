############################################################################################

# Hints - J.B.Attili - 2019

# Routines for generating hints from past past contest logs and/or contacts.

############################################################################################

from rig_io.ft_tables import CA_COUNTIES,arrl_sec2state

############################################################################################

# Routine to sift through previous contest lists to get a hint of qth
def master(P,call,dx_station=None):

    # Check for DX calls
    if (call not in P.calls) and dx_station and ('/' in call):
        call=dx_station.homecall
    
    if call in P.calls:
        print('MASTER:',call,' is in master list')
        print(P.MASTER[call])
        if P.CAL_QP:
            state=P.MASTER[call]['state']
            if state=='CA':
                county=P.MASTER[call]['county']
                return county
            else:
                return state
        elif P.CQ_WW:
            zone=P.MASTER[call]['CQz']
            return zone
        elif P.CW_SS:
            sec=P.MASTER[call]['sec']
            if sec=='':
                sec=P.MASTER[call]['state']
            if sec=='KP4':
                sec='PR'
            chk=P.MASTER[call]['check']
            return chk+' '+sec
        elif P.CWops or P.SST:
            name  = P.MASTER[call]['name']
            state = P.MASTER[call]['state']
            num = P.MASTER[call]['CWops']
            print(name+' '+state+' '+num)
            return name+' '+state+' '+num
        elif P.NAQP or P.SPRINT:
            name  = P.MASTER[call]['name']
            state = P.MASTER[call]['state']
            return name+' '+state
        elif P.ARRL_FD:
            cat   = P.MASTER[call]['FDcat']
            sec   = P.MASTER[call]['FDsec']
            return cat+' '+sec
        elif P.ARRL_VHF:
            gridsq = P.MASTER[call]['grid']
            return gridsq
        elif P.ARRL_10m:
            state = P.MASTER[call]['state']
            if state=='':
                # Try deciphering from section info
                sec   = P.MASTER[call]['FDsec']
                state=arrl_sec2state(sec)
            return state
        else:
            print('HINT.MASTER: No hints available for this contest')
            return None

    else:
        print('HINT.MASTER:',call,' is NOT in master list')
        if dx_station:
            if P.CQ_WW:
                return dx_station.cqz
        return None


    

# Routine to give a hint of QTH of a CA station
def commie_fornia(dx_station,qth):
    if dx_station.country=='United States' and dx_station.cqz==3:
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
    
# Routine to give a hint of QTH of a Canadian station
def oh_canada(dx_station):

    """ Prefixes	Province/Territory
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
    NT """

    CQP_VE_CALL_AREAS = ['??','MR','QC','ON','MB','SK','AB','BC','NT']

    if dx_station.country=='Canada':
        if (dx_station.prefix=='VO2' or dx_station.prefix=='VY2'):
            qth='MR'
        else:
            num=int( dx_station.call_number )
            qth=CQP_VE_CALL_AREAS[num]
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
    
