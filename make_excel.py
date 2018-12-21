import xlwt
from xlutils.copy import copy
import xlrd
from pymongo import MongoClient

def set_style(name, height, bold=False):
	style = xlwt.XFStyle()

	font = xlwt.Font()
	font.name = name
	font.bold = bold
	font.color_index = 4
	font.height = height

	style.font = font

	return style

def write_excel(excel_name):
	f = xlwt.Workbook()
	sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)
	list = ['id', '时间戳','关键词，品牌名', '商品链接' ,'站点', '商品名称', '合身率', '商品图片链接' ,'asin', '商品上架时间','排行', '各品类价格', '具体评价']
	for i in range(len(list)-3):
		sheet1.write(0, i, list[i], set_style('Arial', 220, True))
	sheet1.write_merge(0,0,i+1, i+2, list[-3], set_style('Arial', 220, True))
	sheet1.write_merge(0,0,i+3, i+6, list[-2], set_style('Arial', 220, True))
	sheet1.write_merge(0, 0, i + 7, i + 8, list[-1], set_style('Arial', 220, True))
	f.save(excel_name)

def write_product(product, pre, excel_name):
	book1 = xlrd.open_workbook(excel_name)
	book2 = copy(book1)
	sheet1 = book1.sheet_by_index(0)
	row = sheet1.nrows + 1
	sheet = book2.get_sheet(0)

	product_e = []
	product_e.append(pre['_id'])
	product_e.append(pre['timestamp'])
	product_e.append(pre['key'])
	product_e.append(product['productUrl'])
	product_e.append(product['state'])
	product_e.append(product['productName'])
	product_e.append(product['productFit'])
	product_e.append(product['productImageUrl'])
	product_e.append(product['productAsin'])
	product_e.append(product['productDate'])
	for i in range(len(product_e)):
		sheet.write(row,i,str(product_e[i]), set_style('Times New Roman',220,True))
	try:
		ranks_num = len(product['sellersRanks'])
		for lie in range(ranks_num):
			key = list(product['sellersRanks'].keys())[lie]
			sheet.write(row+lie, i+1, key, set_style('Times New Roman',220,True))
			sheet.write(row+lie, i+2, product['sellersRanks'][key], set_style('Times New Roman', 200, True))
	except:
		ranks_num = 1
		sheet.write(row, i + 1, 'null', set_style('Times New Roman', 220, True))
		sheet.write(row, i + 2, 'null', set_style('Times New Roman', 200, True))

	he_num = 0

	lie = 0
	try:
		col_size_num = len(product['colorSizePrice'])
		for lie in range(col_size_num):
			color = product['colorSizePrice'][lie]['color']
			size = product['colorSizePrice'][lie]['size']
			price = product['colorSizePrice'][lie]['price']
			total_num = product['colorSizePrice'][lie]['totalNum']
			he_num += int(total_num)
			sheet.write(row+lie, i+3, color, set_style('Times New Roman',220,True))
			sheet.write(row+lie, i+4, size, set_style('Times New Roman',220,True))
			sheet.write(row+lie, i+5, price, set_style('Times New Roman',220,True))
			sheet.write(row+lie, i+6, total_num, set_style('Times New Roman',220,True))
	except:
		col_size_num = lie+1

	try:
		minute_stars_num = 5
		minute_stars = product['minuteStars']
		sheet.write(row + 0, i + 7, '5星', set_style('Times New Roman', 220, True))
		sheet.write(row + 0, i + 8, minute_stars['fiveStars'], set_style('Times New Roman', 220, True))
		sheet.write(row + 1, i + 7, '4星', set_style('Times New Roman', 220, True))
		sheet.write(row + 1, i + 8, minute_stars['fourStars'], set_style('Times New Roman', 220, True))
		sheet.write(row + 2, i + 7, '3星', set_style('Times New Roman', 220, True))
		sheet.write(row + 2, i + 8, minute_stars['threeStars'], set_style('Times New Roman', 220, True))
		sheet.write(row + 3, i + 7, '2星', set_style('Times New Roman', 220, True))
		sheet.write(row + 3, i + 8, minute_stars['twoStars'], set_style('Times New Roman', 220, True))
		sheet.write(row + 4, i + 7, '5星', set_style('Times New Roman', 220, True))
		sheet.write(row + 4, i + 8, minute_stars['oneStars'], set_style('Times New Roman', 220, True))
	except:
		minute_stars_num = 0

	max_num = max(ranks_num, col_size_num, minute_stars_num)
	row = row + max_num
	sheet.write(row, i+5, '合计', set_style('Times New Roman',220,True)) 
	sheet.write(row, i+6, he_num, set_style('Times New Roman',220,True))
	book2.save(excel_name)

def work(specTimestamp, excel_name):
    write_excel(excel_name)
    conn = MongoClient('localhost', port=27017)
    db = conn.amazon
    product = db.amazon
    scrapy = product.find_one({'specTimestamp':specTimestamp})['scrapy']
    pre = product.find_one({'specTimestamp':specTimestamp})
    for i in scrapy:
        try:
            write_product(i, pre, excel_name)
        except:
            print('excel写入出错')
