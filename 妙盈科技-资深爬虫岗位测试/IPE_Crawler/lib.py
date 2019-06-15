from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
import time


def save_data(data, filename):
    """
    保存数据文件（Cookies，采集位置记录等）
    :param data: 需要保存的数据
    :param filename: 数据文件名
    """
    with open("{}.txt".format(filename), 'w+') as fw:
        fw.write(str(data))


def load_data(filename):
    """
    读取数据文件（Cookies，采集位置记录等）
    :param filename: 数据文件名
    """
    with open("{}.txt".format(filename), 'r+') as fr:
        data = eval(fr.read())
    return data


def fast_get(browser, url):
    """
    通过预设driver.set_page_load_timeout()实现快速请求，避免无谓的资源等待
    :param browser: 浏览器driver
    :param url: 请求地址
    """
    try:
        browser.get(url)
    except TimeoutException:
        return


def data_loaded(browser):
    """
    供WebDriverWait使用的预定义函数，用于判断企业数据列表是否加载完毕
    :param browser: 浏览器driver
    :return: 判断结果
    """
    try:
        browser.find_element_by_xpath("//p[@id='industry_id']/span[contains(text(), '(加载中...)')]")
        # print('Loading')
        return False
    except NoSuchElementException:
        # print('Load Success')
        return True


def action_confirm(browser, action, confirm):
    """
    用于浏览器交互动作是否正确执行，如果交互未完成，将自动重做
    :param browser: 浏览器driver
    :param action: 需要执行的交互动作
    :param confirm: 用于判断动作执行状态的条件
    """
    def not_confirm(_browser, _confirm):
        try:
            result = _confirm(_browser)
            if result is False:
                return True
            return False
        except NoSuchElementException:
            return True
    while not_confirm(browser, confirm):
        action(browser)
        time.sleep(0.5)
    else:
        return


def extract_main_list_data(browser):
    """
    在搜索企业列表时，输出列表和条件筛选信息
    :param browser: 浏览器driver
    """
    province = Select(browser.find_element_by_xpath("//select[@id='province_0']")).first_selected_option
    city = Select(browser.find_element_by_xpath("//select[@id='city_0']")).first_selected_option
    year = Select(browser.find_element_by_xpath("//select[@id='start_year_0']")).first_selected_option
    industry = Select(browser.find_element_by_xpath("//select[@id='industry_0']")).first_selected_option
    result_num = int(
        browser.find_element_by_xpath("//p[@id='industry_id']/span[@id='spanrecordcount']").text)
    print("搜索结果包含{}家企业，筛选条件：".format(result_num), province.text, city.text, year.text, industry.text)


def detail_data_spider(browser, collection):
    """
    依次进入企业详情页，采集监管记录并清洗，存入MongoDB中
    :param browser: 浏览器driver
    :param collection: MongoDB的集合实例
    """
    company_list = browser.find_elements_by_xpath("//table[@class='table-list']/tbody/tr")
    print("解析到的公司列表长度：", len(company_list))
    for company in company_list:
        company_name = company.find_element_by_xpath("./td[2]").text
        company_location = company.find_element_by_xpath("./td[3]").text
        company_record_year = company.find_element_by_xpath("./td[4]").text
        company_record_num = company.find_element_by_xpath("./td[5]").text
        company_data = {'company_name': company_name,
                        'company_location': company_location,
                        'company_record_year': company_record_year,
                        'company_record_num': company_record_num}
        company.find_element_by_xpath("./td").click()  # 打开企业详情页
        browser.switch_to.window(browser.window_handles[1])  # 把浏览器driver切换到企业详情页
        WebDriverWait(browser, 8, 0.5).until(lambda x: x.find_element_by_xpath("//h1[@id='nowYear']"))  # 等待数据加载
        content_list_years = browser.find_elements_by_xpath("//ul[@class='record-list clearfix']/li")
        print("解析到监管记录分布在{}个不同的年份中".format(len(content_list_years)))
        years_of_logs = []
        for i in content_list_years:
            year = i.find_element_by_xpath("./span").text  # 获得监管记录的年份
            log = []  # 用于存放一年内的监管记录
            count = 0
            while True:
                i.click()  # 点开特定年份的监管记录表
                content_list_in_one_year = i.find_elements_by_xpath("./div/a")
                list_length = len(content_list_in_one_year)
                content_list_in_one_year[count].click()
                time.sleep(1)
                content = browser.find_element_by_xpath(
                    "//div[@class='record-content record-information record-content_j']")
                content_data = content.screenshot_as_png  # 采集内容，此处可做更细致的解析处理
                log.append(content_data)
                time.sleep(2)
                count += 1
                if count >= list_length:
                    break
            years_of_logs.append({year: log})  # 多年的监管记录
        company_data['regulatory_records'] = years_of_logs
        collection.insert_one(company_data)
        browser.close()
        browser.switch_to.window(browser.window_handles[0])  # 回到企业列表页
