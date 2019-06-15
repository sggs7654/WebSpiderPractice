from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from lib import data_loaded, load_data, save_data, fast_get, extract_main_list_data, action_confirm, detail_data_spider
import time
import pymongo


REQUEST_INTERVAL = 2  # 请求时间间隔（反爬需要）


client = pymongo.MongoClient("localhost", 27017)
db = client.test
collection = db['ipe']
options = webdriver.FirefoxOptions()
options.headless = False
browser = webdriver.Firefox(options=options)
browser.set_page_load_timeout(2)
url = 'http://www.ipe.org.cn/IndustryRecord/Regulatory.html?keycode=4543j9f9ri334233r3rixxxyyo12'

"""
覆盖Cookies，模拟登陆
"""
fast_get(browser, "http://www.ipe.org.cn/")
browser.delete_all_cookies()
c = load_data('cookies')
for i in c:
    browser.add_cookie(i)
fast_get(browser, url)
WebDriverWait(browser, 8, 0.5).until(data_loaded)  # 等待数据加载


"""
预备工作：更改列表显示数目，展开筛选条件，只搜索有不良记录的企业
"""
Select(browser.find_element_by_xpath(
    "//select[@class='select select-small']")).select_by_index("2")  # 更改每页显示数目为50
action_confirm(browser,
               lambda x: x.find_element_by_xpath("//a[@class='float-end scree-btn']").click(),  # 展开筛选条件
               lambda x: x.find_element_by_xpath("//a[@class='float-end scree-btn arrow-top']"))  # 确认筛选条件正确展开
browser.find_element_by_xpath("//span[contains(text(), '无不良记录')]").click()  # 更改筛选条件：有不良记录


"""
开始采集数据：按照省，市，年份，行业的顺序依次细分
"""
Select(browser.find_element_by_xpath("//select[@id='country_0']")).select_by_index("1")  # 更改筛选条件：中国
time.sleep(0.5)
cur_province_index = 1
max_province_index = len(Select(browser.find_element_by_xpath("//select[@id='province_0']")).options)
cur_city_index = 1
max_city_index = None
try:  # 如果有采集记录，则从上次采集中止的位置开始继续
    log_province_index, log__city_index = load_data('Resume')
    if log_province_index >= 1 and log__city_index >= 1:
        print("发现采集记录，上次采集至：第{}个省份,第{}个城市，从该位置开始继续采集数据".format(
            log_province_index, log__city_index
        ))
        cur_province_index = log_province_index
        cur_city_index = log__city_index
except FileNotFoundError:
    print("未发现采集记录，将从头开始采集数据")
    pass
while cur_province_index < max_province_index:
    Select(browser.find_element_by_xpath("//select[@id='province_0']")).select_by_index(cur_province_index)  # 选择省份
    time.sleep(0.5)
    max_city_index = len(Select(browser.find_element_by_xpath("//select[@id='city_0']")).options)
    while cur_city_index < max_city_index:
        Select(browser.find_element_by_xpath("//select[@id='city_0']")).select_by_index(cur_city_index)  # 选择城市
        browser.find_element_by_xpath("//input[@class='btn submit-btn float-end']").click()  # 点击筛选按钮
        WebDriverWait(browser, 8, 0.5).until(data_loaded)  # 等待数据加载
        result_num = int(
            browser.find_element_by_xpath("//p[@id='industry_id']/span[@id='spanrecordcount']").text)
        if result_num > 50:  # 如果选择城市后结果数量大于50
            print(Select(browser.find_element_by_xpath("//select[@id='province_0']")).first_selected_option.text,
                  Select(browser.find_element_by_xpath("//select[@id='city_0']")).first_selected_option.text,
                  "下的检索结果数量为{}，超过列表显示范围(50)，进一步加入年份条件进行筛选".format(result_num))
            max_year_index = len(Select(browser.find_element_by_xpath("//select[@id='start_year_0']")).options)
            for year in range(1, max_year_index):  # 选择年份
                Select(browser.find_element_by_xpath("//select[@id='start_year_0']")).select_by_index(year)
                time.sleep(0.5)
                Select(browser.find_element_by_xpath("//select[@id='end_year_0']")).select_by_index(year)
                browser.find_element_by_xpath("//input[@class='btn submit-btn float-end']").click()  # 点击筛选按钮
                WebDriverWait(browser, 8, 0.5).until(data_loaded)  # 等待数据加载
                result_num = int(
                    browser.find_element_by_xpath("//p[@id='industry_id']/span[@id='spanrecordcount']").text)
                if result_num > 50:  # 如果选择年份后结果数量大于50
                    print(
                        Select(browser.find_element_by_xpath("//select[@id='province_0']")).first_selected_option.text,
                        Select(browser.find_element_by_xpath("//select[@id='city_0']")).first_selected_option.text,
                        Select(browser.find_element_by_xpath("//select[@id='start_year_0']")).first_selected_option.text,
                        "下的检索结果数量为{}，超过列表显示范围(50)，进一步加入行业条件进行筛选".format(result_num))
                    action_confirm(browser,
                                   lambda x: x.execute_script("arguments[0].focus();",  # 设置焦点才能得到行业选项内容
                                                              x.find_element_by_xpath("//select[@id='industry_0']")),
                                   lambda x:  # 确认行业选项正确加载
                                   len(Select(x.find_element_by_xpath("//select[@id='industry_0']")).options) > 1)
                    max_industry_index = len(
                        Select(browser.find_element_by_xpath("//select[@id='industry_0']")).options)
                    for industry in range(1, max_industry_index):  # 选择行业类别
                        Select(browser.find_element_by_xpath("//select[@id='industry_0']")).select_by_index(industry)
                        browser.find_element_by_xpath("//input[@class='btn submit-btn float-end']").click()  # 点击筛选按钮
                        WebDriverWait(browser, 8, 0.5).until(data_loaded)  # 等待数据加载
                        result_num = int(
                            browser.find_element_by_xpath(
                                "//p[@id='industry_id']/span[@id='spanrecordcount']").text)  # 结果数量
                        if result_num > 0:
                            extract_main_list_data(browser)
                            time.sleep(REQUEST_INTERVAL)
                            detail_data_spider(browser, collection)
                else:
                    if result_num > 0:
                        extract_main_list_data(browser)
                        time.sleep(REQUEST_INTERVAL)
                        detail_data_spider(browser, collection)
        else:
            if result_num > 0:
                extract_main_list_data(browser)
                time.sleep(REQUEST_INTERVAL)
                detail_data_spider(browser, collection)
        cur_city_index += 1
        save_data((cur_province_index, cur_city_index), 'Resume')
    cur_province_index += 1





