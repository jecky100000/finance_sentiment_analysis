import re

import requests
import json


# 从百度的php接口中获取到数据
def catch_url_from_baidu(calcultaion_year, month):
    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    param = {
        "query": str(calcultaion_year) + "年" + month + "月",
        "resource_id": "39043",
        "t": "1604395059555",
        "ie": "utf8",
        "oe": "gbk",
        "format": "json",
        "tn": "wisetpl",
        "cb": ""
    }
    # 抓取位置：百度搜索框搜索日历，上面的日历的接口，可以在页面上进行核对
    r = requests.get(url="https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php",
                     headers=header, params=param).text
    month_data = json.loads(r)["data"][0]["almanac"]
    work_day = []
    for one in month_data:
        if (one["cnDay"] != '日' and one["cnDay"] != '六'
                and ('status' not in one)):
            work_day.append(one)
    work_days = output_info(work_day)
    return work_days


# 输出格式，可以修改成insert语句进行输出
def output_info(work_day):
    work_days = []
    for one in work_day:
        date = one["year"] + '-' + one["month"] + '-' + one["day"]
        work_days.append(date)
    return work_days


# 先抓取全年交易日历，再提取需要的时间段
def trade_date(start_year, start_month, start_day, end_year, end_month, end_day):
    # 此处只能算当年之前的，因为国务院是每年12月份才会发布第二年的放假计划，所以此接口对于下一年的统计是错的。
    # eg：2020年11月4日，国务院没有发布21年的放假计划，那查询2021年元旦的时候，元旦那天不显示休息
    tradedates = []
    for year in range(start_year, end_year + 1):
        calculation_year = year
        # 因该接口传入的时间，查询了前一个月，当前月和后一个月的数据，所以只需要2、5、8、11即可全部获取到。比如查询5月份，则会查询4,5,6月分的数据
        calculation_month = ["2", "5", "8", "11"]
        for one_month in calculation_month:
            work_days = catch_url_from_baidu(calculation_year, one_month)
            for work_day in work_days:
                tradedates.append(work_day)
    start_date = str(start_year) + "-" + str(start_month) + "-" + str(start_day)
    end_date = str(end_year) + "-" + str(end_month) + "-" + str(end_day)
    for i in range(len(tradedates)):
        if start_date == tradedates[i]:
            start_num = i
        elif end_date == tradedates[i]:
            end_num = i
    try:
        date_get = tradedates[start_num:end_num]
        return date_get
    except:
        print("输入的数字不合规或不在工作日范围内。")
        print("起始日期应在如下日期中：", tradedates)


# 分别按年月日输入起始的工作日日期,一位数不需要加0
if __name__ == '__main__':
    date_get = trade_date(2021, 11, 1, 2022, 1, 28)
    print(date_get)







