import dateutil.parser
from datetime import *
                
def parse_date(indate):
    try:
        pdate = datetime.strptime(indate,'%m/%d/%Y')
    except:
        pdate = dateutil.parser.parse(indate)
    return pdate
    
def parse_rate(rate):
    if rate and float(rate) >=0:
        r = int(round(float(rate)))
    else:
        r = 0
    return r
    
def parse_unit(unit):
    if unit:
        u = int(unit)
    else:
        u = 0
    return u    