import urllib2

def gen_account_links(user_prefs):
    response = urllib2.urlopen('http://www.zimride.com/users/1744333')
    html = response.read()
