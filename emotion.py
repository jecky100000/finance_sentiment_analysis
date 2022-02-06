import re
import datetime
import time
import pymysql
import jieba
import jieba.posseg as pseg
import collections


def NewStopWords():
    # 生成新停用词词典，过滤掉否定词及程序副词
    stopwords = set()
    f = open("dict/停用词2462.txt", "r", encoding="utf-8")
    for word in f:
        stopwords.add(word.strip())  # 去除周围空格
    f.close()
    # 读取否定词
    not_word_file = open("dict/否定词.txt", "r", encoding="utf-8")
    not_word_list = not_word_file.readlines()
    not_word_list = [wo.strip() for wo in not_word_list]
    not_word_file.close()

    # 读取程序副词
    degree_file = open("dict/程度副词.txt", "r", encoding="utf_8")
    degree_list = degree_file.readlines()
    degree_list = [de.strip() for de in degree_list]
    degree_file.close()

    # 生成新的停用词表
    with open("dict/停用词2462.txt", "w", encoding="utf-8") as f:
        for word in stopwords:
            if word not in not_word_list and word not in degree_list:
                f.write(word + "\n")


# 使用jieba分词并去除停用词
def seg_word(sentence):
    seg_list = jieba.cut(sentence)
    seg_result = []
    for i in seg_list:
        seg_result.append(i)
    stopwords = set()
    with open("dict/停用词2462.txt", "r", encoding="utf-8") as f:
        for i in f:
            stopwords.add(i.strip())
    return list(filter(lambda x: x not in stopwords, seg_result))


# 找出文本中情感词、否定词和程度副词
def classify_words(word_list):
    # 读取情感词典文件
    sen_file = open("dict/BosonNLP_sentiment_score.txt", "r+", encoding="utf-8")
    sen_list = sen_file.readlines()
    # 创建情感字典
    sen_dict = collections.defaultdict()
    for i in sen_list:
        if len(i.split(' ')) == 2:
            sen_dict[i.split(" ")[0]] = i.split(" ")[1].strip()

    # 读取否定词
    not_word_file = open("dict/否定词.txt", "r", encoding="utf-8")
    not_word_list = not_word_file.readlines()
    not_word_list = [wo.strip() for wo in not_word_list]

    # 读取程序副词
    degree_file = open("dict/程度副词.txt", "r", encoding="utf_8")
    degree_list = degree_file.readlines()
    degree_dict = collections.defaultdict()
    for i in degree_list:
        degree_dict[i.split(",")[0]] = i.split(",")[1].strip()

    sen_word = dict()
    not_word = dict()
    degree_word = dict()

    # 分类
    for i in range(len(word_list)):
        word = word_list[i]
        if word in sen_dict.keys() and word not in not_word_list and word not in degree_dict.keys():
            # word只在情感词典中
            sen_word[i] = sen_dict[word]
        elif word in not_word_list and word not in degree_dict.keys():
            # word在否定词中
            not_word[i] = -1
        elif word in degree_dict.keys():
            # word在程度副词中
            degree_word[i] = degree_dict[word]
    sen_file.close()
    not_word_file.close()
    degree_file.close()

    return sen_word, not_word, degree_word


# 计算情感分数
def sentiment_score(sen_word, not_word, degree_word, seg_result):
    # 权重初始化为1
    w = 1
    score = 0
    # 情感词下标初始化
    sentiment_index = -1
    # 情感词下标集合
    sentiment_index_list = list(sen_word.keys())
    for word in range(0, len(seg_result)):
        # 如果是情感词
        if word in sen_word.keys():
            # 权重 * 情感得分
            score += w * float(sen_word[word])
            # 情感词下标加一 获取下一个情感词位置
            sentiment_index += 1
            if sentiment_index < len(sentiment_index_list) - 1:
                # 判断当前情感词与下一个情感词间是否有程度副词或否定词
                for j in range(sentiment_index_list[sentiment_index], sentiment_index_list[sentiment_index + 1]):
                    # 更新权重 如有否定词 权重取反
                    if j in not_word.keys():
                        w *= -1
                    elif j in degree_word.keys():
                        w *= float(degree_word[j])
        # 定位下一个情感词
        if sentiment_index < len(sentiment_index_list) - 1:
            word = sentiment_index_list[sentiment_index + 1]
    return score


# 主程序
def main():
    NewStopWords()
    scores = []
    db = pymysql.connect(host='localhost', port=3306, user='root', password='', database='spider',
                         charset='utf8')
    cur = db.cursor()
    # 数据去重
    sql = "SELECT title FROM test WHERE score = 0"
    cur.execute(sql)
    titles = cur.fetchall()
    for i in range(len(titles)):
        word_list = seg_word(titles[i][0])
        sen_word, not_word, degree_word = classify_words(word_list)
        score = sentiment_score(sen_word, not_word, degree_word, word_list)
        scores.append(score)
        cur.execute('UPDATE test SET score = %s WHERE title = %s ', (score, str(titles[i][0])))
        db.commit()
    cur.close()


if __name__ == '__main__':
    try:
        main()
        print("情感评分完成。")
    except:
        print("情感评分出错。")
