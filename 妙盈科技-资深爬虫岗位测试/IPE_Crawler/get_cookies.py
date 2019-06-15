from selenium import webdriver
from lib import save_data
import time


"""
手动登录，提取用于模拟登录的Cookies
账号：17121170980 172839
"""
options = webdriver.FirefoxOptions()
options.headless = False
browser = webdriver.Firefox(options=options)
# browser = webdriver.Chrome()
url = 'http://www.ipe.org.cn'
browser.get(url)
cookies = browser.get_cookies()
print(cookies)  # 打印初始Cookies
time.sleep(30)  # 手动登录
cookies = browser.get_cookies()
print(cookies)  # 打印验证Cookies
save_data(cookies, 'cookies')
browser.quit()
