#！/user/bin/env python
# _*_ coding:utf-8 _*_

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

import pytesseract
from PIL import Image
import os

import time
import random
import json
import requests

def tess(driver):
	timestamp = time.time()
	imageUrl = driver.find_element_by_tag_name('img').get_attribute('src')
	html = requests.get(imageUrl)
	imageName = 'tess//%s.jpg'%timestamp
	f = open(imageName, 'wb+')
	f.write(html.content)
	f.close()
	image = Image.open(imageName)
	code = pytesseract.image_to_string(image)
	element = driver.find_element_by_id('captchacharacters')
	element.send_keys(code)
	element.send_keys(Keys.ENTER)
	os.remove(imageName)
	return driver

#使用无图模式开启
#获取代理服务器和url
#def open_chrome(ip, port, xiey, url):
def open_chrome(url):
	try:
		'''
		#无界面模式
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless')
		chrome_options.add_argument('--ignore-certificate-errors')
		chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"')
		'''
		# 有界面无图模式
		chrome_options = webdriver.ChromeOptions()
		prefs = {"profile.managed_default_content_settings.images": 2}
		chrome_options.add_experimental_option("prefs", prefs)


		# chrome_options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
		driver = webdriver.Chrome(chrome_options=chrome_options)
		driver.set_window_size(1280, 800)
		if url.find('amazon.de') != -1:
			if len(url) > 25:
				url += '&language=en_GB'
		try:
			driver.get(url)
		except:
			try:
				time.sleep(5)
				driver.get(url)
			except:
				time.sleep(10)
				driver.get(url)
		while driver.title.find('Check') != -1:
			time.sleep(2)
			driver = tess(driver)
			print(driver.title)
		print('开启浏览器')
		return driver
	except:
		f = open('error.txt', 'a')
		# f.write('%s 获取代理服务器和url出错 ip为 %s\n' %(time.ctime(), ip))
		f.close()
		print('获取代理服务器和url出错')


# 在第一个页面时 填写搜查信息
def sendKey(key, url):
	driver = open_chrome(url)
	# time.sleep(30)
	try:
		element = driver.find_element_by_id('twotabsearchtextbox')
	except:
		element = driver.find_element_by_id('e')
	finally:
		pass
	element.send_keys(key)
	element.send_keys(Keys.ENTER)
	return driver


# 获得并返回第一页商品链接 进一步多线程爬取使用
# 可通过模拟点击下一页 再写入product_list
# def get_product_list(ip, port, xiey, key):
# 返回此关键词的所有链接
def get_product_list(key):
	try:
		url_US = 'https://www.amazon.com'
		url_DE = 'https://www.amazon.de'
		url_UK = 'https://www.amazon.co.uk'
		# driver = open_chrome(ip, port, xiey,url)
		product_urls_san = []
		for url in [url_US, url_DE, url_UK]:

        # for url in [url_US, url_UK]:
		# for url in [url_US]:
			try:
				driver = sendKey(key, url)
				#time.sleep(30)
				product_list = []
				while True:
						try:
								products = driver.find_elements_by_tag_name('h2')
								print('获取商品链接')
								for product in products:
										try:
												text = product.text
												product_s = driver.find_element_by_link_text(text)
												product_url = product_s.get_attribute('href')
												print(product_url)
												if product_url != None:
														product_list.append(product_url)
										except:
												print('商品链接无法获取 跳过')
								js = "window.scrollTo(0,document.body.scrollHeight)"
								driver.execute_script(js)
								driver.find_element_by_id('pagnNextLink').click()
								time.sleep(5)
						except:
								#限制爬取的数量
								product_urls_san+=product_list[:200]
								break
				driver.close()
				driver.quit()
			except:
					print('%s不能爬取', url)
	except:
		f = open('error.txt', 'a')
		f.write('%s 获取商品链接出错 链接为%s\n' % (time.ctime(), driver.current_url))
		f.close()
		print('获取商品链接出错')
	finally:
		return product_urls_san


#  返回此品牌名的所有链接
def get_product_list2(key):
	try:
		url_US = 'https://www.amazon.com'
		url_DE = 'https://www.amazon.de'
		url_UK = 'https://www.amazon.co.uk'
		product_urls_san = []
		for url in [url_US, url_DE, url_UK]:
			try:
				driver = sendKey(key, url)
				text = driver.find_element_by_tag_name('h2').text
				product_url = driver.find_element_by_link_text(text).get_attribute('href')
				driver.get(product_url)
				brand = driver.find_element_by_id('bylineInfo_feature_div')
				if brand.text.lower() == key.lower():
					brand.find_element_by_tag_name('a').click()
					product_urls = []
					try:
						# 情况1 缩图式
						try:
							classify = driver.find_element_by_class_name('style__dropdowns__12fQH').find_elements_by_tag_name('a')
						except:
							classify = driver.find_element_by_class_name(
								'style__navList__Igck2').find_elements_by_tag_name('a')
						classify_urls = [kind.get_attribute('href') for kind in classify]
						for kindUrl in classify_urls:
							driver.get(kindUrl)
							# 如果是未完全页面 则会点击按钮
							while True:
								try:
									driver.find_element_by_class_name('style__gridMoreButton__6Prpe').click()
								except:
									break
							product_urls += [i.find_element_by_tag_name('a').get_attribute('href') for i in driver.find_elements_by_class_name('style__item__3gM_7')]
					except:
						#情况2 列表式
						while True:
							try:
								for liElement in driver.find_element_by_class_name('s-result-list').find_elements_by_tag_name('li'):
									try:
										product_urls.append(liElement.find_element_by_tag_name('a').get_attribute('href'))
									except:
										pass
								time.sleep(5)
								js = "window.scrollTo(0,document.body.scrollHeight)"
								driver.execute_script(js)
								driver.find_element_by_id('pagnNextLink').click()
							except:
								break
					product_urls_san += product_urls
				else:
					print('找不到此品牌名')
			except:
				print('此站点找不到此品牌')
			finally:
				driver.close()
				driver.quit()
	except:
		print('获取品牌%s链接出错'%(key))
	finally:
		print(product_urls_san)
		product_urls_san = list(set(product_urls_san))
		return product_urls_san


# 进入商品所在页面 可以获取各种信息 : 名称 价格 图片 简介 评论 星级等
# 商品名称
def get_product_name(driver):
	try:
		try:
			name_expand = driver.find_element_by_id('expandTitleToggle')
			name_expand.click()
		except:
			print('商品名不过长不用以上代码')
		name = driver.find_element_by_id('productTitle')
		name = name.text
		print('商品名称：%s' % (name))
		return name
	except:
		f = open('error.txt', 'a')
		f.write('%s 获取商品名称出错 url为 %s\n' %(time.ctime(), driver.current_url))
		f.close()
		print('当前页面url：%s  获取商品名称出错'%(driver.current_url))
		return ''


# 添加至购物车 以便不同size color商品价格和总量的获取
def add_to_cart(driver):
	try:
		if driver.current_url.find('amazon.com') != -1:
			color_size, price_totalnum = get_color_3(driver)
		else:
			color_size, price_totalnum = get_color_4(driver)
		return color_size, price_totalnum
	except:
		try:
			color_size, price_totalnum = get_size_color_2(driver)
			return color_size,price_totalnum
		except:
				try:
						while True:
								if driver.current_url.find('view.html') != -1:
										driver.back()
						add_cart = driver.find_element_by_id('add-to-cart-button')
						add_cart.click()
						color_size = {'size': [], 'color': []}
						priceTotalnum = get_product_price_totalnum(driver)
						price_totalnum = {'price': priceTotalnum[0], 'totalnum': priceTotalnum[1]}
						return color_size, price_totalnum
				except:
						return {'size': [], 'color': []}, {'price':[],'totalnum': []}

#当只能选择color 不能选择size时运行
def get_size_color_2(driver):
	time.sleep(random.randint(3, 10))
	color_num = len(driver.find_elements_by_class_name('swatchAvailable')) + len(driver.find_elements_by_class_name('swatchSelect')) + len(driver.find_elements_by_class_name('swatchUnavailable'))
	color_size = {'size': [], 'color': []}
	price_totalnum = {'price': [], 'totalnum': []}
	for color in range(color_num):
		color_size['size'].append('')
		color_select = driver.find_element_by_id('color_name_' + str(color))
		color_select.click()
		time.sleep(3)
		if color_select.get_attribute('class') == 'swatchSelect':
			color_hao = color_select.find_element_by_tag_name('img').get_attribute('alt')
		else:
			color_hao = ''
		color_size['color'].append(color_hao)
		#time.sleep(random.randint(3, 10))
		add_cart = driver.find_element_by_id('add-to-cart-button')
		add_cart.click()
		time.sleep(random.randint(3, 10))
		if not driver.current_url.find('view') == -1:
			driver.back()
			time.sleep(random.randint(3, 10))
		else:
			pass
	price_totalnum_list = get_product_price_totalnum(driver, color_num)
	price_list = list(reversed(price_totalnum_list[0]))
	totalnum_list = list(reversed(price_totalnum_list[1]))
	price_totalnum['price'] += price_list
	price_totalnum['totalnum'] += totalnum_list
	return color_size,price_totalnum

#美国站点模拟点击获取价格的方法
def get_color_3(driver):
	time.sleep(random.randint(5, 10))
	select_size = driver.find_element_by_id('dropdown_selected_size_name')
	time.sleep(3)
	select_size.click()
	time.sleep(random.randint(10, 15))
	size_num = len(driver.find_elements_by_class_name('a-dropdown-item'))
	driver.find_element_by_id('native_dropdown_selected_size_name_0').click()
	color_size = {'size': [], 'color': []}
	price_totalnum = {'price': [], 'totalnum': []}
	for size in range(1, size_num):
		select_size = driver.find_element_by_id('dropdown_selected_size_name')
		select_size.click()
		time.sleep(3)
		select_x = driver.find_element_by_id('native_dropdown_selected_size_name_' + str(size))
		size_hao = select_x.text
		select_x.click()
		time.sleep(3)
		color_list = driver.find_elements_by_class_name('swatchAvailable') + driver.find_elements_by_class_name('swatchSelect')
		color_len = len(color_list)
		color_id_list = [each.get_attribute('id') for each in color_list]
		if color_list != []:
			for color_id in color_id_list:
				color = driver.find_element_by_id(color_id)
				time.sleep(3)
				color.click()
				time.sleep(5)
				color_hao = color.find_element_by_tag_name('img').get_attribute('alt')
				color_size['size'].append(size_hao)
				color_size['color'].append(color_hao)
				print(size_hao, color_hao)
				try:
					add_cart = driver.find_element_by_id('add-to-cart-button')
					add_cart.click()
					driver.back()
				except:
					color_size['size'].pop()
					color_size['color'].pop()
					color_len -= 1
		else:
			color_hao = ''
			color_len = 1
			color_size['size'].append(size_hao)
			color_size['color'].append(color_hao)
			add_cart = driver.find_element_by_id('add-to-cart-button')
			add_cart.click()
			driver.back()
		try:
			price_totalnum_list = get_product_price_totalnum(driver, color_len)
			price_list = list(reversed(price_totalnum_list[0]))
			totalnum_list = list(reversed(price_totalnum_list[1]))
			price_totalnum['price']+=(price_list)
			price_totalnum['totalnum']+=(totalnum_list)
			print(color_size, price_totalnum)
		except:
			pass
	return color_size, price_totalnum

#其余两个站点模拟点击的方法
def get_color_4(driver):
	import re
	color_size = {'size': [], 'color': []}
	price_totalnum = {'price': [], 'totalnum': []}
	s = driver.find_element_by_name('dropdown_selected_size_name')
	select_list = re.sub('\n\s+', '\n', s.text).strip().split('\n')
	select_num = len(select_list)
	for sele in range(1, select_num):
		s = driver.find_element_by_name('dropdown_selected_size_name')
		Select(s).select_by_index(sele)
		size_hao = driver.find_element_by_id('native_size_name_' + str(sele-1)).text.strip()
		color_list = driver.find_elements_by_class_name('swatchAvailable') + driver.find_elements_by_class_name('swatchSelect')
		color_len = len(color_list)
		color_id_list = [each.get_attribute('id') for each in color_list]
		if color_list != []:
			for color_id in color_id_list:
				color = driver.find_element_by_id(color_id)
				time.sleep(3)
				color.click()
				time.sleep(5)
				color_hao = color.find_element_by_tag_name('img').get_attribute('alt')
				color_size['size'].append(size_hao)
				color_size['color'].append(color_hao)
				print(size_hao, color_hao)
				try:
					add_cart = driver.find_element_by_id('add-to-cart-button')
					add_cart.click()
					driver.back()
				except:
					color_size['size'].pop()
					color_size['color'].pop()
					color_len -= 1
		else:
			color_hao = ''
			color_len = 1
			color_size['size'].append(size_hao)
			color_size['color'].append(color_hao)
			add_cart = driver.find_element_by_id('add-to-cart-button')
			add_cart.click()
			driver.back()
		try:
			price_totalnum_list = get_product_price_totalnum(driver, color_len)
			price_list = list(reversed(price_totalnum_list[0]))
			totalnum_list = list(reversed(price_totalnum_list[1]))
			price_totalnum['price']+=(price_list)
			price_totalnum['totalnum']+=(totalnum_list)
			print(color_size, price_totalnum)
		except:
			pass
	return color_size, price_totalnum

#获取商品图片链接
def get_product_image_url(driver):
	try:
		if driver.current_url.find('https://www.amazon.co.uk')!= -1:
			image_url_json = driver.find_element_by_id('imgTagWrapperId').find_element_by_tag_name('img').get_attribute('data-a-dynamic-image')
			image_url = list(json.loads(image_url_json).keys())[0]
		else:
			image_url = list(json.loads(driver.find_element_by_id('landingImage').get_attribute('data-a-dynamic-image')).keys())[0]

		print('图片链接：%s' % (image_url))
		if image_url == None:
			image_url = '无'
		return image_url
	except:
		f = open('error.txt', 'a')
		f.write('%s 获取商品图片出错 url为 %s\n' %(time.ctime(), driver.current_url))
		f.close()
		print('当前页面url：%s   获取商品图片出错'%(driver.current_url))
		pass
		return ''

#获取商品合身度
def get_product_fit(driver):
	try:
		fit = driver.find_element_by_id('fitRecommendationsLinkRatingText').text.split('(')[-1].split(')')[0]
		print('fit : %s'%fit)
		if fit == None:
			fit = '0%'
		return fit
	except:
		fit = "0%"
		return  fit

#获取商品asin和上架日期
def get_product_asin_and_date(driver):
        try:
                try:
                        try:
                                description_one_to_four = driver.find_element_by_id('detailBullets_feature_div').text.split('\n')
                                #date_first_list = description_one_to_four[4].split(':')[-1].strip()
                        except:
                                description_one_to_four = driver.find_element_by_id('detail-bullets_feature_div').text.split('\n')
                        date_first_list = [each for each in description_one_to_four if each.find('first') != -1][0].split(':')[-1]
                except:
                        date_first_list = driver.find_element_by_class_name('date-first-available').find_element_by_class_name('value').text
                asin = driver.find_element_by_id('cerberus-data-metrics').get_attribute('data-asin')

                print('asin:%s  date_first_list:%s'%(asin, date_first_list))
                if asin == None:
                        asin = ''
                if date_first_list == None:
                        asin = ''
                return [asin, date_first_list]
        except:
                return['获取asin出错', None]

#获取排行
def get_product_ranks(driver):
	sort_by = []
	rank = []
	try:
		sellers_rank = driver.find_element_by_id('dpx-amazon-sales-rank_feature_div').text.split('\n')
		for sell_rank in sellers_rank:
			sort_by.append(sell_rank.split(' in ')[-1].split(')')[0])
			rank.append(sell_rank.split(' in ')[0].split('#')[-1])

	except:
                
		sellers_rank = driver.find_element_by_id('SalesRank').text.split(':')[-1].split('\n')
		for sell_rank in sellers_rank:
			sort_by.append(sell_rank.split(' in ')[-1].split(')')[0])
			rank.append(sell_rank.split(' in ')[0].split('#')[-1])
	finally:
		print(sort_by + rank)
		return (sort_by + rank)


#获取评价客户数 和 对应的星数
def get_product_customer_stars(driver):
    try:
        customer_number_ele = driver.find_element_by_id('acrCustomerReviewText')
        customer_number = customer_number_ele.text.split(' ')[0]
        average = driver.find_element_by_id('acrPopover').get_attribute('title').split(' ')[0]
    except:
        customer_number = '0'
        average = '0'
    finally:
        return [customer_number, average]

#获取商品价格和总量
def get_product_price_totalnum(driver, color_len):
    if driver.current_url.find('https://www.amazon.com') != -1:
        driver.get('https://www.amazon.com/gp/cart/view.html/')
    elif driver.current_url.find('https://www.amazon.de') != -1:
        driver.get('https://www.amazon.de/gp/cart/view.html/')
    else:
        driver.get('https://www.amazon.co.uk/gp/cart/view.html/')

    shopping_cart = driver.find_element_by_id('sc-active-cart')
    label = shopping_cart.find_elements_by_class_name('a-list-item')
    label_num = int(len(label) / 4)
    #color_size_list = []
    price_list = []
    price = driver.find_elements_by_class_name('a-spacing-small')
    totalnum_list = []
    number = 999
    i = 1

    for order in range(color_len):
        #print(label[order * 4].text.split('(')[-1].split(')')[0])
        #color_size_list.append(label[order * 4].text.split('(')[-1].split(')')[0])
        price_list.append(price[order].text)

    quantityBox = driver.find_elements_by_class_name('a-dropdown-prompt')[0:color_len]
    inp = 0
    for quantity_box in quantityBox:
        availability = driver.find_elements_by_class_name('sc-product-availability')
        if availability[inp].text.find('left') != -1:
            totalnum = int(availability[inp].text.split(' ')[1])
            i += 0
        else:
            time.sleep(random.randint(3, 5))
            quantityBox = driver.find_elements_by_class_name('a-dropdown-prompt')[0:color_len]
            element = quantityBox[inp]
            element.click()
            time.sleep(random.randint(3, 5))
            quantity_n = driver.find_element_by_id('dropdown' + str(i) + '_9')
            quantity_n.click()
            time.sleep(random.randint(3, 5))

            input_box = driver.find_elements_by_name('quantityBox')[inp]
            input_box.clear()
            input_box.send_keys(number)
            input_box.send_keys(Keys.ENTER)
            time.sleep(random.randint(3, 5))
            # warn = driver.find_element_by_link_text('product detail page')
            quantity = driver.find_elements_by_name('quantityBox')[inp]
            totalnum = quantity.get_attribute('value')
            time.sleep(random.randint(3, 5))
            # 这里需要一个删除 要不然购物车的上限只能1000
            #这里后来出现错误 delete按键的xpath被修改
            '''
            try:
                driver.find_element_by_xpath('//*[@id="activeCartViewForm"]/div[2]/div/div[4]/div/div[1]/div/div/div[2]/div/span[1]').click()
                //*[@id="activeCartViewForm"]/div[1]/div[1]/div[2]/div/div/div[1]/div[4]/div/div[1]/div/div/div[2]/div/span[1]/span/input
            except:
                driver.find_element_by_xpath('//*[@id="activeCartViewForm"]/div[1]/div[1]/div[2]/div/div/div/div[4]/div[2]/div[1]/div/div/div[2]/div/span[1]').click()
            '''
            remove_totalnum(driver, element, i, int(totalnum), inp)
            time.sleep(random.randint(5,15))
            if int(totalnum) >=10:
                i += 1
            else:
                i += 2
        totalnum_list.append(totalnum)
        print(totalnum)
        inp += 1
    time.sleep(3)
    while driver.current_url.find('view') !=-1:
        driver.back()
    time.sleep(3)
    return price_list, totalnum_list

def remove_totalnum(driver, element, i, totalnum, inp):
    if totalnum <= 9:
        quantityBox = driver.find_elements_by_class_name('a-dropdown-prompt')
        element = quantityBox[inp]
        element.click()
        driver.find_element_by_id('dropdown' + str(i+1) + '_0').click()
    else:
        input_box = driver.find_elements_by_name('quantityBox')[inp]
        input_box.clear()
        input_box.send_keys(1)
        input_box.send_keys(Keys.ENTER)

def get_minute_stars(driver):
	minute_stars = {}
	try:
		stars_list = driver.find_element_by_id('histogramTable').text.split('\n')
		star5 = stars_list[1].split('%')[0]
		star4 = stars_list[3].split('%')[0]
		star3 = stars_list[5].split('%')[0]
		star2 = stars_list[7].split('%')[0]
		star1 = stars_list[9].split('%')[0]
	except:
		star1 = star2 = star3 = star4 = star5 = '0'
	finally:
		minute_stars['fiveStars'] = int(star5)
		minute_stars['fourStars'] = int(star4)
		minute_stars['threeStars'] = int(star3)
		minute_stars['twoStars'] = int(star2)
		minute_stars['oneStars'] = int(star1)
		return minute_stars

def get_brand(driver):
	try:
		brandName = driver.find_element_by_id('bylineInfo_feature_div').text
		return brandName
	except:
		print('获取品牌错误')
		return ''

def main():
	pass

if __name__ == '__main__':
    main()
