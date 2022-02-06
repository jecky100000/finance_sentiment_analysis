import datetime
import time
import tradedate  # 获取交易日历
import pandas as pd
import pymysql
import pandas

companys = ['隆基股份', '森特股份', '三峡能源']
work_days = tradedate.catch_url_from_baidu('2022', '1')
db = pymysql.connect(host='localhost', port=3306, user='root', password='', database='spider',
                     charset='utf8')
cur = db.cursor()
names = locals()
i = 0
for company in companys:
    avgs = []
    for work_day in work_days:
        sql = "SELECT score FROM test WHERE DATE(date)= '" + str(work_day) + "' AND company = %s"
        cur.execute(sql, company)
        score = cur.fetchall()
        scores = []
        try:
            for i in range(len(score)):
                scores.append(score[i][0])
            avg = sum(scores) / len(scores)
            avgs.append(avg)
        except:
            print(work_day, score, company)
    names['avg_' + str(i)] = avgs
    i += 1
db.close()
print(avgs_0, avgs_1, avgs_2)



