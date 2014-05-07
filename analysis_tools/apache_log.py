import re
import pandas as pd
import numpy as np
from numpy import unique
from datetime import datetime, timedelta

# GET /favicon.ico HTTP/1.1

# appcfg.py request_logs ./ barnacle-`date +%s`.log -n 0
# appcfg.py request_logs ./ --severity=0 -n 0 20140120-level0.txt
# appcfg.py --append --num_days=0 --include_all request_logs /path/to/your/app/ /var/log/gae/yourapp.log


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


GOOGLE_BOT_USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

REQUEST_TO_IGNORE = ['GET /favicon.ico HTTP/1.1']

#
# BARNACLE
#

RUSSIAN_BOT = ['Mozilla/2.0 (compatible; MSIE 3.02; Windows CE; 240x320)',
 'Mozilla/4.0 (compatible- MSIE 6.0- Windows NT 5.1- SV1- .NET CLR 1.1.4322',
 'Mozilla/4.0 (compatible; MSIE 5.0; Windows 3.1)',
 'Mozilla/4.0 (compatible; MSIE 5.0; Windows NT; DigExt)',
 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 4.0)',
 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 4.0; .NET CLR 1.0.2914)',
 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)',
 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0; .NET CLR 1.1.4322)',
 'Mozilla/4.0 (compatible; MSIE 6.0; AOL 9.0; Windows NT 5.1)',
 'Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 4.0) Opera 7.0 [en]',
 'Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.0) Opera 7.02 Bork-edition [en]',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322; Alexa Toolbar; (R1 1.5))',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322; FDM)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Crazy Browser 1.0.5)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FREE; .NET CLR 1.1.4322)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; MRA 4.3 (build 01218); .NET CLR 1.1.4322)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; MRA 4.6 (build 01425))',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322) NS8/0.9.6',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; XMPP Tiscali Communicator v.10.0.2; .NET CLR 2.0.50727)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; FunWebProducts)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; FunWebProducts; .NET CLR 1.1.4322; PeoplePal 6.2)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; FunWebProducts; MRA 4.6 (build 01425); .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; InfoPath.1)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; MRA 4.6 (build 01425); MRSPUTNIK 1, 5, 0, 19 SW)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 8.00',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; Win64; x64; SV1; .NET CLR 2.0.50727)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT) ::ELNSB50::000061100320025802a00111000000000507000900000000',
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322)',
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.1)',
 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729)',
 'Mozilla/4.0 (compatible; Powermarks/3.5; Windows 95/98/2000/NT)',
 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ru; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12',
 'Mozilla/5.0 (compatible; Add Catalog/2.1;)',
 'Mozilla/5.0 (compatible; news bot /2.1)',
 'Opera/8.00 (Windows NT 5.1; U; en)',
 'Opera/8.01 (Windows NT 5.1)',
 'Opera/9.0 (Windows NT 5.1; U; en)',
 'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.2.15 Version/10.10',
 'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.6.30 Version/10.63']

BOT_LIST = RUSSIAN_BOT + ['Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
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
 'rogerbot/1.0 (http://moz.com/help/pro/what-is-rogerbot-, rogerbot-crawler+shiny@moz.com)',
 '-',
 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
 'AppEngine-Google; (+http://code.google.com/appengine)',
 'AppEngine-Google; (+http://code.google.com/appengine; appid: s~getfavicon27)',
  'ContextAd Bot 1.0',
 'Crowsnest/0.5 (+http://www.crowsnest.tv/)',
 'Google-HTTP-Java-Client/1.17.0-rc (gzip)',
 'Google-remote_api/1.0 Darwin/12.4.1 Python/2.7.2.final.0 gzip',
 'Google-remote_api/1.0 win32/6.2.9200.2 Python/2.7.3.final.0 gzip',
 'Google_Analytics_Snippet_Validator',
 'Googlebot',
 'Googlebot-Image/1.0',
 'HTTPClient/1.0 (2.3.3, ruby 1.9.3 (2013-02-22))',
 'HTTP_Request2/2.1.1 (http://pear.php.net/package/http_request2) PHP/5.3.27',
 'JS-Kit URL Resolver, http://js-kit.com/',
 'Java/1.4.1_04',
 'Java/1.6.0_37',
 'Java/1.7.0_13',
 'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)',
 'M',
 'MailChimp.com Site Checker',
 'Mechanize/2.7.1 Ruby/1.9.3p194 (http://github.com/sparklemotion/mechanize/)',
 'Mechanize/2.7.2 Ruby/1.9.3p194 (http://github.com/sparklemotion/mechanize/)',
 'MetaURI API/2.0 +metauri.com',
  'Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/534.34 (KHTML, like Gecko) PhantomJS/1.9.1 Safari/534.34',
   'Mozilla/5.0 (Windows NT 5.1; rv:2.0b13pre) Gecko/20110223 Firefox/4.0b13pre',
    'Mozilla/5.0 (Windows NT 5.1; rv:6.0) Gecko/20100101 Firefox/6.0 FirePHP/0.6',
 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.12 (KHTML, like Gecko) Maxthon/3.0 Chrome/18.0.966.0 Safari/535.12',
 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) KomodiaBot/1.0',

'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre',
 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:24.0) Gecko/20100101 Firefox/24.0 Waterfox/24.0',
  'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko/20100101 Firefox/12.0',
 'Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20110814 Firefox/6.0',
 'Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20110814 Firefox/6.0 Google (+https://developers.google.com/+/web/snippet/)',
 'Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20110814 Firefox/6.0 Google favicon',
  'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9) Gecko/2008052906 Firefox/3.0',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.2) Firefox/3.5.2',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9b4) Gecko/2008030714 Firefox/3.0b4',
  'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3',
 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB6 (.NET CLR 3.5.30729)',
 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)',
 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3',
 'Mozilla/5.0 (Windows; Windows NT 5.1; es-ES; rv:1.9.2a1pre) Gecko/20090402 Firefox/3.6a1pre',
 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.11 (KHTML, like Gecko) DumpRenderTree/0.0.0.0 Safari/536.11',
'Mozilla/5.0 (X11; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
'Mozilla/5.0 (compatible; PaperLiBot/2.1; http://support.paper.li/entries/20023257-what-is-paper-li)',
 'Mozilla/5.0 (compatible; TweetmemeBot/3.0; +http://tweetmeme.com/)',
 'Mozilla/5.0 (compatible; WASALive-Bot ; http://blog.wasalive.com/wasalive-bots/)',
 'Mozilla/5.0 (compatible; WebThumbnail/3.x; Website Thumbnail Generator; +http://webthumbnail.org)',
 'PagesInventory (robot +http://www.pagesinventory.com)',
 'Python-urllib/2.7',
 'Python-urllib/2.7 AppEngine-Google; (+http://code.google.com/appengine; appid: s~pulseapi)',
 'Quora 3.1.1 rv:136 (iPhone; iPhone OS 7.0.2; en_US)',
 'Quora Link Preview/1.0 (http://www.quora.com)',
 'Ruby',
 'Opera/7.11 (Windows NT 5.1; U) [en]',
 'Opera/9.80 (Android; Opera Mini/7.5.33361/32.1024; U; en) Presto/2.8.119 Version/11.10',
 'Opera/9.80 (BlackBerry; Opera Mini/7.1.32723/31.1475; U; en) Presto/2.8.119 Version/11.10',
 'Opera/9.80 (Windows NT 6.0; U; de) Presto/2.2.15 Version/10.00',
 'Opera/9.80 (Windows NT 6.1) Presto/2.12.388 Version/12.11',
 'Opera/9.80 (Windows NT 6.1) Presto/2.12.388 Version/12.16',
 'Opera/9.80 (Windows NT 6.1; Edition Yx) Presto/2.12.388 Version/12.11',
 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16',
 'Opera/9.80 (Windows NT 6.1; WOW64; Edition Yx) Presto/2.12.388 Version/12.10',
 'Opera/9.80 (Windows NT 6.2; WOW64; MRA 8.0 (build 5784)) Presto/2.12.388 Version/12.11',
 'SEOstats 2.1.0 https://github.com/eyecatchup/SEOstats',
 'ScreenerBot Crawler Beta 2.0 (+http://www.ScreenerBot.com)',
 'Slurp',
 'UnwindFetchor/1.0 (+http://www.gnip.com/)',
 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.2.28) Gecko/20120306 Firefox/3.6.28 GTB7.1',
 'User-Agent\\tMozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
 'W3C_Validator/1.3 http://validator.w3.org/services',
 'WordPress/3.6; http://www.dlpedia.com',
 'WordPress/3.7-alpha-25157; http://elaineou.wordpress.com',
 'WordPress/3.8-alpha; http://soshitech.com',
 'Yahoo:LinkExpander:Slingstone',
 "\\'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)\\'",
 'android-async-http/1.4.1 (http://loopj.com/android-async-http)',
 'blogtop.us crawler - http://blogtop.us/',
 'bot-pge.chlooe.com/1.0.0 (+http://www.chlooe.com/)',
 'curl/7.24.0',
 'domainsbot (+http://www.domainsbot.com)',
 'ee://aol/http',
 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
 'http://Anonymouse.org/ (Unix)',
 'python-requests/1.2.3 CPython/2.6.8 Linux/3.4.43-43.43.amzn1.x86_64',
 'wscheck.com/1.0.0 (+http://wscheck.com/)',
 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9) Gecko Minefield/3.0',
 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8',
 'Mozilla/5.0 (X11; U; OpenBSD i386; en-US; rv:1.9.2.8) Gecko/20101230 Firefox/3.6.8',
 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.186 Safari/535.1 solfo-linkchecker/1.0 (http://solfo.com/linkbot.html)',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.6) Gecko/20100625 Firefox/3.6.6',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:x.x.x) Gecko/20041107 Firefox/x.x',
 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru-RU; rv:1.7.12) Gecko/20050919 Firefox/1.0.7',
  'Mozilla/5.0 (Windows; U; MSIE 8.0; WIndows NT 9.0; en-US))',
 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)',
 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Netscape/8.0.4',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; T312461)']

def remove_image_request(df):
    return df[~df.request.str.contains('/img/')]

def remove_static_request(df):
    df = df[~df.request.str.startswith('HEAD /static')]
    return df[~df.request.str.contains('GET /static')]

def remove_robot_request(df):
    df_robot = df[df.request.str.startswith('GET /robots.txt HTTP/1.1')]
    robot_hosts = set(df_robot.host)
    return df[[h not in robot_hosts for h in df.host]]

def remove_pages_i_dont_care_about(df):
    return remove_google_bot(remove_robot_request(remove_image_request(remove_static_request(df))))

def google_crawl(df):
    """return dictionary (date, set(pages) crawled"""
    df = df[df.agent == GOOGLE_BOT_USER_AGENT]
    df = df[df.host.str.startswith('66.249')]
    df = remove_static_request(df)
    df = df[~df.request.str.startswith('GET /robots.txt HTTP/1.1')]
    return df[~df.request.str.contains('GET /sitemap.xml HTTP/1.1')]

def is_google_bot(agent):
    if 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' == agent:
        return True
    return False

def is_bot(agent):
    if agent in BOT_LIST:
        return True
    return False

def remove_google_bot(df):
    flag = [is_google_bot(a) for a in df.agent]
    google_hosts = set(df[flag].host)
    return df[[h not in google_hosts for h in df.host]]

def remove_bots(df):
    flag = [not is_bot(a) for a in df.agent]
    return df[flag]

def remove_russian(df):
    russian_hosts = set(df[df.referrer.str.endswith(r'.ru/')].host)
    df = df[[host not in russian_hosts for host in df.host]]
    return df

def find_bot_candidates(df):
    robot_request = 'GET /robots.txt HTTP/1.1'
    flag = [r == robot_request for r in df.request]
    return unique(df[flag].agent.tolist())

def refer_by_russian(df):
    def is_russian_referer(r):
        if re.findall('\.ru', r):
            return True
        else:
            return False
    flag = [is_russian_referer(r) for r in df.referrer]
    return df[flag]


def generic_filter(regex, field):
    def filter_by(df):
        def is_true(agent):
            if re.findall(regex, agent):
                return True
            return False
        flag = [is_true(a) for a in df[field]]
        not_flag = [not f for f in flag]
        return df[flag], df[not_flag]
    return filter_by

def ipsort(l):
    """sort ip address for easier viewing"""
    l = list(l)
    def mykey(x):
        s = x.split('.')
        return int(s[0])*16777216 + int(s[1])*65536 + int(s[2])*256 + int(s[3])
    l.sort(key = mykey)
    return l


filter_iphone = generic_filter('iPhone', 'agent')
filter_ipad = generic_filter('iPad', 'agent')
filter_craigslist = generic_filter('craigslist', 'referrer')
