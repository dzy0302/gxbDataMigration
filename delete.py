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
logfile = 'logs/logs.txt'
fh = logging.FileHandler(logfile, mode='a', encoding='utf-8')
fh.setLevel(logging.DEBUG)  # 用于写到file的等级开关

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

    cur.execute('SELECT patientID FROM origin_data;')
    patientid_list = cur.fetchall()
    for patientid in patientid_list:
        patientID = patientid[0]
        cur.execute('SELECT MAX(fieldRecordDate) FROM origin_data where patientID = %s;', patientID)
        max_recordtime = cur.fetchone()
        maxRecordTime = max_recordtime[0]
        print(str(maxRecordTime))
        result = cur.execute('DELETE FROM origin_data where patientID = %s and fieldRecordDate < %s;', (patientID, maxRecordTime))
        print(result)
        conn.commit()

    cur.close()
    conn.close()



if __name__ == '__main__':
    delete()
