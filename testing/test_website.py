from requests import session
import json
import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


PORT = '8080'
DOMAIN = 'localhost'


def epoch_now():
    return time.mktime(time.gmtime())


with session() as c:
    d = { "id" : '12345',
                "first_name" : 'Fred',
                "last_name" : 'Low',
                "email" : 'fredlow340@yahoo.com',
                "location" : 'Mountain View, CA' }
    headers = {'content-type': 'application/json'}
    request = c.post('http://localhost:8080/signup/fb', data=json.dumps(d), headers=headers)

driver = webdriver.Firefox()
driver.get("http://127.0.0.1:8080/")
driver.add_cookie({'name':'key', 'value':'value', 'path':'/'})
for cookie in request.cookies:
    driver.add_cookie({'name' : cookie.name, 'value': cookie.value, 'path':'/', 'domain' : '127.0.0.1'})

all_cookies = driver.get_cookies()

driver.get("http://127.0.0.1:8080/")
driver.save_screenshot('screenshot-%i.png' % epoch_now())
time.sleep(3)

for navitem in ['navicoreqs', 'navicoroutes', 'navicosearch']:
    elem = driver.find_element_by_class_name(navitem)
    elem.click()
    driver.save_screenshot('screenshot-%i.png' % epoch_now())
    time.sleep(3)

#navicoroutes
#navicosearch

#driver.get("http://www.gobarnacle.com/post/request")

driver.close()

