import re
import datetime
import time
import pymysql
import requests


# 爬取百度新闻内容
def baidu_news(company):
    url = 'https://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=' + company + '&medium=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
    res = requests.get(url, headers=headers).text
    p_href = r'<h3 class="news-title_1YtI1"><a href="(.*?)" target="_blank"'
    href = re.findall(p_href, res, re.S)
    p_title = r'<h3 class="news-title_1YtI1">.*?aria-label="标题：(.*?)" data-click'
    title = re.findall(p_title, res, re.S)
    p_source = r'<h3 class="news-title_1YtI1">.*?<span class="c-color-gray c-font-normal c-gap-right" aria-label="新闻来源：(.*?)">'
    source = re.findall(p_source, res, re.S)
    p_date = r'<h3 class="news-title_1YtI1">.*?发布于：(.*?)">'
    date = re.findall(p_date, res, re.S)
    check_date(date)
    # 存入数据库
    db = pymysql.connect(host='localhost', port=3306, user='root', password='', database='spider',
                         charset='utf8')
    cur = db.cursor()
    # 数据去重
    sql = 'SELECT * FROM test WHERE company = %s'
    cur.execute(sql, company)
    data_all = cur.fetchall()
    title_all = []
    href_all = []
    for j in range(len(data_all)):
        title_all.append(data_all[j][1])
        href_all.append(data_all[j][2])
    for i in range(len(title)):
        if title[i] not in title_all and href[i] not in href_all:
            # 数据存储
            cur.execute('INSERT INTO test(company, title, href, date, source, score) VALUES (%s, %s, %s, %s, %s, %s)',
                        (company, title[i], href[i], date[i], source[i], 0))
        else:
            continue
    db.commit()
    cur.close()
    db.close()
    return


# 爬取新浪新闻内容
def xinlang_news(company):
    url = 'https://search.sina.com.cn/?country=usstock&q=' + company + '&name=' + company + '&t=&c=news&k=' + company + '&range=all&col=1_7&from=channel&ie=utf-8'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
    res = requests.get(url, headers=headers).text
    p_href = r'<div class="box-result clearfix" data-sudaclick="blk_result_index_3">.*?<a href="(.*?)" target'
    href = re.findall(p_href, res, re.S)
    p_title = r'<div class="box-result clearfix" data-sudaclick="blk_result_index_3">.*?target="_blank">(.*?)</a>'
    title = re.findall(p_title, res, re.S)
    for i in range(len(title)):
        title[i] = re.sub('<.*?>', '', title[i])
    p_source = r'<div class="box-result clearfix" data-sudaclick="blk_result_index_3">.*?<span class="fgray_time">(.*?) '
    source = re.findall(p_source, res, re.S)
    p_date = r'<div class="box-result clearfix" data-sudaclick="blk_result_index_3">.*?<span class="fgray_time">.*? (.*?)</span>'
    date = re.findall(p_date, res, re.S)
    check_date(date)
    # 存入数据库
    db = pymysql.connect(host='localhost', port=3306, user='root', password='', database='spider',
                         charset='utf8')
    cur = db.cursor()
    # 过滤不含目标的新闻内容
    check_news(company, title, href, date, source)
    # 数据去重
    sql = 'SELECT * FROM test WHERE company = %s'
    cur.execute(sql, company)
    data_all = cur.fetchall()
    title_all = []
    href_all = []
    for j in range(len(data_all)):
        title_all.append(data_all[j][1])
        href_all.append(data_all[j][2])
    for i in range(len(title)):
        if title[i] not in title_all and href[i] not in href_all:
            # 数据存储
            cur.execute('INSERT INTO test(company, title, href, date, source, score) VALUES (%s, %s, %s, %s, %s, %s)',
                        (company, title[i], href[i], date[i], source[i], 0))
        else:
            continue
    db.commit()
    cur.close()
    db.close()
    return


# 爬取新浪财经内容
def xinlang_finance(company, company_code, page):
    url = 'https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php?symbol=sh' + company_code + "&Page=" + str(page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
    res = requests.get(url, headers=headers).text
    p_href = r"&nbsp;&nbsp;&nbsp;&nbsp.*?&nbsp;&nbsp;<a target='_blank' href='(.*?)'"
    href = re.findall(p_href, res, re.S)
    p_title = r"&nbsp;&nbsp;&nbsp;&nbsp.*?&nbsp;&nbsp;<a target='_blank' href=.*?>(.*?)</a>"
    title = re.findall(p_title, res, re.S)
    for i in range(len(title)):
        title[i] = re.sub('<.*?>', '', title[i])
    source = '新浪财经'
    # 时间数据处理
    p_date_1 = r"&nbsp;&nbsp;&nbsp;&nbsp;(.*?)&nbsp;&nbsp;<a target='_blank' href="
    date_1 = re.findall(p_date_1, res, re.S)
    p_date_2 = r'(.*?)&nbsp;(.*)'
    date = []
    now = datetime.datetime.now()
    for i in range(len(date_1)):
        date_2 = re.findall(p_date_2, date_1[i])
        date_3 = datetime.datetime.strftime(now, date_2[0][0] + " " + date_2[0][1] + ":%S")
        date_3 = datetime.datetime.strptime(date_3, "%Y-%m-%d %H:%M:%S")
        date.append(date_3)
    # 存入数据库
    db = pymysql.connect(host='localhost', port=3306, user='root', password='', database='spider',
                         charset='utf8')
    cur = db.cursor()
    # 过滤不含目标的新闻内容
    for i in range(len(title)):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
            article = requests.get(href[i], headers=headers, timeout=10).text
        except:
            article = '爬取失败'
        company_re = company[0] + company[1] + '.{0,5}'
        if len(re.findall(company_re, article)) < 1 and len(re.findall(company_re, title[i])) < 1:
            title[i] = ''
            href[i] = ''
            date[i] = ''
    while '' in title:
        title.remove('')
    while '' in href:
        href.remove('')
    while '' in date:
        date.remove('')
    # 数据去重
    sql = 'SELECT * FROM test WHERE company = %s'
    cur.execute(sql, company)
    data_all = cur.fetchall()
    title_all = []
    href_all = []
    for j in range(len(data_all)):
        title_all.append(data_all[j][1])
        href_all.append(data_all[j][2])
    for i in range(len(title)):
        if title[i] not in title_all and href[i] not in href_all:
            # 数据存储
            cur.execute('INSERT INTO test(company, title, href, date, source, score) VALUES (%s, %s, %s, %s, %s, %s)',
                        (company, title[i], href[i], date[i], source, 0))
        else:
            continue
    db.commit()
    cur.close()
    db.close()
    return


# 转换不规范的日期格式
def check_date(date):
    for i in range(len(date)):
        p_a = r'(.*?)秒前'
        p_b = r'(.*?)分钟前'
        p_c = r'(.*?)小时前'
        p_d = r'(.*?)天前'
        p_e = r'昨天(.*)'
        p_f = r'前天(.*)'
        p_g = r'(.*?)月(.*?)日'
        a = re.findall(p_a, date[i])
        b = re.findall(p_b, date[i])
        c = re.findall(p_c, date[i])
        d = re.findall(p_d, date[i])
        e = re.findall(p_e, date[i])
        f = re.findall(p_f, date[i])
        g = re.findall(p_g, date[i])
        now = datetime.datetime.now()
        if len(a) != 0:
            delta = datetime.timedelta(seconds=int(a[0]))
            date[i] = now - delta
        elif len(b) != 0:
            delta = datetime.timedelta(minutes=int(b[0]))
            date[i] = now - delta
        elif len(c) != 0:
            delta = datetime.timedelta(hours=int(c[0]))
            date[i] = now - delta
        elif len(d) != 0:
            delta = datetime.timedelta(days=int(d[0]))
            date[i] = now - delta
        elif len(e) != 0:
            if e[0] == '':
                delta = datetime.timedelta(days=1)
                date[i] = now - delta
            else:
                code = 'date[i] = datetime.datetime.strftime(now, "%Y-%m-%d ' + e[0] + ':%S")'
                exec(code)
                date[i] = datetime.datetime.strptime(date[i], "%Y-%m-%d %H:%M:%S")
                delta = datetime.timedelta(days=1)
                date[i] = date[i] - delta
        elif len(f) != 0:
            if f[0] == '':
                delta = datetime.timedelta(days=2)
                date[i] = now - delta
            else:
                code = 'date[i] = datetime.datetime.strftime(now, "%Y-%m-%d ' + f[0] + ':%S")'
                exec(code)
                date[i] = datetime.datetime.strptime(date[i], "%Y-%m-%d %H:%M:%S")
                delta = datetime.timedelta(days=2)
                date[i] = date[i] - delta
        elif len(g) != 0:
            code = 'date[i] = datetime.datetime.strftime(now, "%Y-' + g[0][0] + '-' + g[0][1] + ' %H:%M:%S")'
            exec(code)
            date[i] = datetime.datetime.strptime(date[i], "%Y-%m-%d %H:%M:%S")
        else:
            date[i] = datetime.datetime.strptime(date[i], "%Y-%m-%d %H:%M:%S")


# 过滤不含目标的新闻内容
def check_news(company, title, href, date, source):
    for i in range(len(title)):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
            article = requests.get(href[i], headers=headers, timeout=10).text
        except:
            article = '爬取失败'
        company_re = company[0] + company[1] + '.{0,5}'
        if len(re.findall(company_re, article)) < 1 or len(re.findall(company_re, title[i])) < 1:
            title[i] = ''
            href[i] = ''
            date[i] = ''
            source[i] = ''
    while '' in title:
        title.remove('')
    while '' in href:
        href.remove('')
    while '' in date:
        date.remove('')
    while '' in source:
        source.remove('')


if __name__ == '__main__':
    while True:
        companys = ['隆基股份', '森特股份', '三峡能源']
        company_codes = ['601012', '603098', '600905']
        for company in companys:
            try:
                xinlang_news(company)
                print(company + ' 新浪新闻爬取完成。')
            except:
                print(company + ' 新浪新闻爬取失败。')
            try:
                baidu_news(company)
                print(company + ' 百度新闻爬取完成。')
            except:
                print(company + ' 百度新闻爬取失败。')
        for i in range(len(companys)):
            for j in range(4):
                try:
                    xinlang_finance(companys[i], company_codes[i], j+1)
                    print(companys[i] + ' 新浪财经page' + str(j+1) + '爬取成功。')
                except:
                    print(companys[i] + ' 新浪财经page' + str(j+1) + '爬取成功。')
        time.sleep(10800)
