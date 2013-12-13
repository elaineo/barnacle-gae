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


#
# BARNACLE
#

BOT_LIST = ['Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
 'A6-Indexer/1.0 (http://www.a6corp.com/a6-web-scraping-policy/)',
 'AdnormCrawler www.adnorm.com/crawler',
 'Apache-HttpClient/4.3 (java 1.5)',
 'DoCoMo/2.0 P900i(c100;TB;W24H11) (compatible; ichiro/mobile goo;+http://search.goo.ne.jp/option/use/sub4/sub4-1/)',
 'EventMachine HttpClient',
 'Luminator 2.0',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)',
 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MDDR; .NET4.0C; .NET4.0E; .NET CLR 1.1.4322; Tablet PC 2.0)',
 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MDDR; .NET4.0C; .NET4.0E; .NET CLR 1.1.4322; Tablet PC 2.0); 360Spider',
 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6 (FlipboardProxy/1.1; +http://flipboard.com/browserproxy)',
 'Mozilla/5.0 (Windows NT 5.1; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.5) Gecko/2008120122 Firefox/3.0.5',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; )  Firefox/1.5.0.11; 360Spider',
 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:14.0; ips-agent) Gecko/20100101 Firefox/14.0.1',
 'Mozilla/5.0 (compatible; AhrefsBot/5.0; +http://ahrefs.com/robot/)',
 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
 'Mozilla/5.0 (compatible; Butterfly/1.0; +http://labs.topsy.com/butterfly/) Gecko/2009032608 Firefox/3.0.8',
 'Mozilla/5.0 (compatible; Ezooms/1.0; ezooms.bot@gmail.com)',
 'Mozilla/5.0 (compatible; Genieo/1.0 http://www.genieo.com/webfilter.html)',
 'Mozilla/5.0 (compatible; GrapeshotCrawler/2.0; +http://www.grapeshot.co.uk/crawler.php)',
 'Mozilla/5.0 (compatible; MJ12bot/v1.4.3; http://www.majestic12.co.uk/bot.php?+)',
 'Mozilla/5.0 (compatible; MJ12bot/v1.4.4; http://www.majestic12.co.uk/bot.php?+)',
 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; chromeframe/19.0.1084.52)',
 'Mozilla/5.0 (compatible; NetSeer crawler/2.0; +http://www.netseer.com/crawler.html; crawler@netseer.com)',
 'Mozilla/5.0 (compatible; SISTRIX Crawler; http://crawler.sistrix.net/)',
 'Mozilla/5.0 (compatible; SiteExplorer/1.0b; +http://siteexplorer.info/)',
 'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
 'Mozilla/5.0 (compatible; aiHitBot/2.8; +http://endb-consolidated.aihit.com/)',
 'Mozilla/5.0 (compatible; archive.org_bot +http://archive.org/details/archive.org_bot)',
 'Mozilla/5.0 (compatible; archive.org_bot +http://www.archive.org/details/archive.org_bot)',
 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
 'Mozilla/5.0 (compatible; meanpathbot/1.0; +http://www.meanpath.com/meanpathbot.html)',
 'Mozilla/5.0 (compatible; proximic; +http://www.proximic.com/info/spider.php)',
 'Mozilla/5.0 (compatible; spbot/4.0.1; +http://www.seoprofiler.com/bot )',
 'Mozilla/5.0 (compatible; spbot/4.0.2; +http://www.seoprofiler.com/bot )',
 'Mozilla/5.0 (compatible; spbot/4.0.3; +http://www.seoprofiler.com/bot )',
 'Mozilla/5.0 (compatible; spbot/4.0; +http://www.seoprofiler.com/bot )',
 'Mozilla/5.0 (compatible; special_archiver/3.1.1 +http://www.archive.org/details/archive.org_bot)',
 'NextGenSearchBot 1 (for information visit http://www.zoominfo.com/About/misc/NextGenSearchBot.aspx)',
 'PagesInventory (robot http://www.pagesinvenotry.com)',
 'Screaming Frog SEO Spider/2.20',
 'ShowyouBot (http://showyou.com/crawler)',
 'Twitterbot/1.0',
 'YisouSpider',
 'crawler4j (http://code.google.com/p/crawler4j/)',
 'ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)',
 'ia_archiver(OS-Wayback)',
 'msnbot-media/1.1 (+http://search.msn.com/msnbot.htm)',
 'msnbot/2.0b (+http://search.msn.com/msnbot.htm)',
 'panscient.com',
 'rogerbot/1.0 (http://moz.com/help/pro/what-is-rogerbot-, rogerbot-crawler+shiny@moz.com)']

def is_static_request(request):
    if re.findall('GET /static', request):
        return True
    return False

def remove_static_request(df):
    flag = [not is_static_request(r) for r in  df.request]
    return df[flag]

def is_google_bot(agent):
    if 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' == agent:
        return True
    return False

def is_bot(agent):
    if agent in BOT_LIST:
        return True
    return False

def remove_google_bot(df):
    flag = [not is_google_bot(a) for a in df.agent]
    return df[flag]

def remove_bots(df):
    flag = [not is_bot(a) for a in df.agent]
    return df[flag]

def find_bot_candidates(df):
    robot_request = 'GET /robots.txt HTTP/1.1'
    flag = [r == robot_request for r in df.request]
    return unique(df[flag].agent.tolist())
