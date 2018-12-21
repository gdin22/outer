from concurrent.futures import ThreadPoolExecutor
import time
import scrapy2
import random
from pymongo import MongoClient
import requests
import sys
import datetime
import re
import make_excel

#保存照片
def save_image(image_url):
    try:
        html = requests.get(image_url)
        html.encoding = html.apparent_encoding
        picture_name = image_url.split('/')[-1]
        f = open('picture//'+picture_name, 'wb')
        f.write(html.content)
        f.close()
    except:
        print("保存照片错误")

#不完整的月份补全
def egMonthToCom(month):
    if month.find('Ap') != -1:
        month = 'April'
    elif month.find('Au') != -1:
        month = 'August'
    elif month.find('D') != -1:
        month = 'December'
    elif month.find('F') != -1:
        month = 'February'
    elif month.find('Ja') != -1:
        month = 'January'
    elif month.find('Jul') != -1:
        month = 'July'
    elif month.find('Jun') != -1:
        month = 'June'
    elif month.find('Mar') != -1:
        month = 'March'
    elif month.find('May') != -1:
        month = 'May'
    elif month.find('N') != -1:
        month = 'November'
    elif month.find('O') != -1:
        month = 'October'
    else:
        month = 'September'
    return month

#日期转换成时间戳
def replaceDate2TimeStamp(date):
    try:
        day = re.match(r'.*? (\d{1,2}).*?', date, re.M|re.I).group(1)
        month = re.match(r'.*?([a-zA-Z]+).*?', date, re.M|re.I).group(1)
        year = re.match(r'.*(\d{4}).*', date, re.M|re.I).group(1)
        month = egMonthToCom(month)
        monthDayYear = '%s %s,%s'%(month, day, year)
        time_format = time.strptime(monthDayYear, '%B %d,%Y')
        timeStamp = int(time.mktime(time_format)*1000)
    except:
        timeStamp = time.time()*1000
    return timeStamp

#字符串转整型 中间有，
def string2Int(string):
    try:
        if ',' in string:
            return int(''.join(string.split(',')))
        else:
            return int(''.join(string.split('.')))
    except:
        return 0

def scrapy_inf(url, product, num, specTimestamp):
    start_time = time.time()
    time.sleep(random.randint(1, 160))
    try:
        driver = scrapy2.open_chrome(url)
        product_url = driver.current_url
        product_name = scrapy2.get_product_name(driver)
        product_fit = scrapy2.get_product_fit(driver)
        brand = scrapy2.get_brand(driver)
        product_image_url = scrapy2.get_product_image_url(driver)
        #写入图片
        save_image(product_image_url)
        asin_date = scrapy2.get_product_asin_and_date(driver)
        asin_date[1] = replaceDate2TimeStamp(asin_date[1])
        customer_stars = scrapy2. get_product_customer_stars(driver)
        minute_stars = scrapy2.get_minute_stars(driver)
        ranks = scrapy2.get_product_ranks(driver)
        #color_size = scrapy2.add_to_cart(driver)
        color_size,price_totalnum = scrapy2.add_to_cart(driver)
        print(color_size, price_totalnum)
        hou_zhui = re.match(r'.*amazon.(.*?)/.*', product_url, re.M|re.I).group(1)
        if hou_zhui == 'com':
            state = 'USA'
        elif hou_zhui == 'de':
            state = 'DE'
        else:
            state = 'UK'
        print('爬取完成')

        try:
            #print('type:%s'%(type(color_price_total)))
            #timestamp = time.time()
            #product.insert({'time_stamp':timestamp})
            product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy.' + str(num):{}}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.productUrl':product_url}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.state':state}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.productName':product_name}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.productFit': product_fit}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.productImageUrl':product_image_url}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.productAsin': asin_date[0]}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.productDate': asin_date[1]}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.customerReviews.number':string2Int(customer_stars[0])}})
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.customerReviews.stars': float(customer_stars[1])}})
            if ranks == None:
                pass
            else:
                ranks_num = len(ranks)
                for each_num in range(int(ranks_num/2)):
                    product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy.'+str(num)+'.sellersRanks.'+ str(ranks[each_num]): string2Int(ranks[int(ranks_num/2 + each_num)])}})

            '''
            color_size = {'size': [], 'color': []}
            price_totalnum = {'price':[], 'totalnum':[]}
            '''
            color_list = color_size['color']
            size_list = color_size['size']
            price_list = price_totalnum['price']
            totalnum_list = price_totalnum['totalnum']

            product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy.' + str(num) + '.colorSizePrice': []}})

            i= 0
            for color, size in zip(color_list, size_list):
                if size == 'Select':
                    pass
                else:
                    product.update({'specTimestamp':specTimestamp},{'$set': {'scrapy.' + str(num) + '.colorSizePrice.' + str(i): {}}})
                    product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy.'+str(num)+'.colorSizePrice.' + str(i) + '.color': color}})
                    product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy.'+str(num)+'.colorSizePrice.' + str(i) + '.size': size}})
                    i += 1
            i = 0
            for price, totalnum in zip(price_list, totalnum_list):
                product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy.'+str(num)+'.colorSizePrice.' + str(i) + '.price': price}})
                product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy.'+str(num)+'.colorSizePrice.' + str(i) + '.totalNum': int(totalnum)}})
                i += 1

            #插入详细的评星信息
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+str(num)+'.minuteStars.fiveStars':minute_stars['fiveStars']}})
            product.update({'specTimestamp':specTimestamp},{'$set': {'scrapy.' + str(num) + '.minuteStars.fourStars': minute_stars['fourStars']}})
            product.update({'specTimestamp':specTimestamp},{'$set': {'scrapy.' + str(num) + '.minuteStars.threeStars': minute_stars['threeStars']}})
            product.update({'specTimestamp':specTimestamp},{'$set': {'scrapy.' + str(num) + '.minuteStars.twoStars': minute_stars['twoStars']}})
            product.update({'specTimestamp':specTimestamp},{'$set': {'scrapy.' + str(num) + '.minuteStars.oneStars': minute_stars['oneStars']}})

            #插入品牌名
            product.update({'specTimestamp':specTimestamp}, {'$set':{'scrapy.'+ str(num) + '.brand': brand}})
        except:
            print('插入数据错误')

    except:
        print('爬取错误')

    finally:
        driver.close()
        driver.quit()
        end_time = time.time()
        print("爬取时长%s"%(end_time-start_time))



def scrapy(key, keyWordOrBrand):
    todayDatetime = datetime.date.today()
    timestamp = int(time.mktime(time.strptime(str(todayDatetime), '%Y-%m-%d'))*1000)
    #具体的时间戳 用来区别不同的商品
    specTimestamp = time.time()

    conn = MongoClient('localhost', port=27017)
    db = conn.amazon
    product = db.amazon
    product.insert({'specTimestamp':specTimestamp})
    product.update({'specTimestamp':specTimestamp}, {'$set':{'timestamp':timestamp}})
    product.update({'specTimestamp':specTimestamp}, {'$set':{'key':key}})
    product.update({'specTimestamp':specTimestamp}, {'$set': {'scrapy': []}})

    #线程池 生成列表
    if keyWordOrBrand == 'keyWord':
        product_url_list = scrapy2.get_product_list(key)
    else:
        product_url_list = scrapy2.get_product_list2(key)
    product_list = [product]*len(product_url_list)
    #timestamp_list = [timestamp]*len(product_url_list)
    specTimestamp_list = [specTimestamp]*len(product_url_list)
    num_list = list(range(len(product_url_list)))

    with ThreadPoolExecutor(7) as executor1:
        executor1.map(scrapy_inf, product_url_list, product_list, num_list, specTimestamp_list)

    #写入数据库后 删除为None的数据
    product.update({'specTimestamp':specTimestamp}, {'$pullAll':{'scrapy':[None]}})

    #写入excel
    year = time.localtime().tm_year
    mon = time.localtime().tm_mon
    day = time.localtime().tm_mday
    keyword = key
    excel_name = 'excel\%s-%s-%s_%s.xlsx' % (str(year), str(mon), str(day), keyword)
    make_excel.work(specTimestamp, excel_name)



if __name__ == '__main__':
    scrapy()

'''
爬取中断
https://www.amazon.com/gp/product/B077D4N85F/ref=ox_sc_act_title_1?smid=A1FIC4M8WXRNS8&psc=1
https://www.amazon.com/gp/product/B079P3TDQH/ref=ox_sc_act_title_1?smid=A3KQ3G8XN978OJ&psc=1

https://www.amazon.com
https://www.amazon.de
https://www.amazon.co.uk
https://images-na.ssl-images-amazon.com/images/I/91khwqXV-rL._UY500_.jpg
https://images-na.ssl-images-amazon.com/images/I/81ax2OAfqKL._UY606_.jpg
https://www.amazon.com/Metme-Vintage-Inspired-Fringed-Evening/dp/B07917BRBT/ref=sr_1_177?ie=UTF8&qid=1532963872&sr=8-177&keywords=1920+dress
'''
