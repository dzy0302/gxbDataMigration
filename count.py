#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import time
import logging
import configparser
import datetime

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log等级总开关

# 第二步，创建一个handler，用于写入日志文件
logfile = 'logs/logs_count.txt'
fh = logging.FileHandler(logfile, mode='a', encoding='utf-8')
fh.setLevel(logging.INFO)  # 用于写到file的等级开关

# 第三步，再创建一个handler,用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关

# 第四步，定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 第五步，将logger添加到handler里面
logger.addHandler(fh)
logger.addHandler(ch)


def get_conn():
    config = configparser.RawConfigParser()
    config.read('configs/db.ini')
    conn = pymysql.connect(host=config.get('database-mysql', 'host'),
                           port=config.getint('database-mysql', 'port'),
                           user=config.get('database-mysql', 'username'),
                           passwd=config.get('database-mysql', 'password'),
                           db=config.get('database-mysql', 'dbname'))
    return conn


def delete():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute('SELECT * FROM vw_common2_gxb2;')
    description_tuples = cur.description
    for description in description_tuples:
        logging.debug(description[0])
        sql = "SELECT count(*) FROM vw_common2_gxb2 where " + description[0] + " is not null;"
        logging.debug(sql)
        cur.execute(sql)
        logging.info("字段名：" + description[0] + "  " + "该字段有值病例数：" + str(cur.fetchone()[0]))
    cur.close()
    conn.close()



if __name__ == '__main__':
    delete()
