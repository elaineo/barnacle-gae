import re
import pandas as pd
from datetime import datetime, timedelta

  # Regex for the Apache common log format.
parts = [r'(?P<host>[\S:]+)',                   # host %h
r'\S+',                             # indent %l (unused)
r'(?P<user>\S+)',                   # user %u
r'\[(?P<time>.+)\]',                # time %t
r'"(?P<request>.*)"',               # request "%r"
r'(?P<status>[0-9]+)',              # status %>s
r'(?P<size>\S+)',                   # size %b (careful, can be '-')
r'(?P<referrer>"[\S\s]+"|-)',              # referrer "%{Referer}i"
r'(?P<agent>".*"|-)',                 # user agent "%{User-agent}i"
]
pattern = re.compile(r'\s+'.join(parts) + r'\s*\Z')


def read_apache_log(filename):
    l = []
    with open(filename) as f:
        for line in f:
            try:
                m = pattern.match(line)
                d = m.groupdict()
                timestamp = d['time']
                for key in ['request', 'referrer', 'agent']:
                    d[key] = d[key].strip('"')
                d['time'] = datetime.strptime(
                    timestamp[0:19], '%d/%b/%Y:%H:%M:%S') - timedelta(minutes=int(d['time'][21:]))
                l.append(d)
            except:
                print line
    return pd.DataFrame(l)
