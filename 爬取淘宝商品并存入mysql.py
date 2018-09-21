from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from lxml import etree
import pymysql


#启动浏览器并设置chrome-headless模式
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)

def index_page(page):
    print("正在爬取第",page,"页")
    try:
        url = "https://s.taobao.com/search?q=ipad"
        driver.get(url)
        driver.refresh()
        if page > 1:
            #设置隐性等待
            driver.implicitly_wait(20)
            #模拟淘宝上跳页的步骤
            driver.find_element_by_xpath('//*[@id="mainsrp-pager"]//div/div[2]/input').clear()
            driver.find_element_by_xpath('//*[@id="mainsrp-pager"]//div/div[2]/input').send_keys(page)
            driver.find_element_by_xpath('//*[@id="mainsrp-pager"]/div/div/div/div[2]/span[3]').click()
        get_products()
    except TimeoutException:
        index_page(page)

def get_products():
    html = driver.page_source
    tree = etree.HTML(html)
    items = tree.xpath('//*[@id="mainsrp-itemlist"]/div/div/div[1]/div')
    for item in items:
        try:
            price = item.xpath('.//strong/text()')[0]
            title = item.xpath('string(.//div[@class="row row-2 title"]/a)').replace("\n","").replace("\r","").strip()
            # print(type(title))
            # print(title)
            shop = item.xpath('.//div[@class="shop"]//span[last()]/text()')[0]
            product = {
                "price":price,
                "title":title,
                "shop": shop
            }
            print(product)
            save_to_mysql(price, title, shop)
        except IndexError:
            print("error")
def save_to_mysql(price,title,shop):
    db = pymysql.connect(host="localhost",user="root",password="992198",port=3306,db="crawlspider")
    cursor = db.cursor()
    #mysql的插入语句
    sql = "INSERT INTO test1(price,title,shop) VALUES(%s,%s,%s)"
    try:
        cursor.execute(sql,(price,title,shop))
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()

def main():
    max_page = 100
    for i in range(1, max_page+1):
        index_page(i)
    driver.close()
if __name__ == '__main__':
    main()
