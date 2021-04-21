#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import time
import logging
import configparser

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


def transplant():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute('SELECT  * FROM origin_data;')
    orgin_data = cur.fetchall()
    # print(type(results))  # 返回<class 'tuple'> tuple元组类型

    for orgin in orgin_data:
        logging.info('————————————————————————————————————————————————————')
        logging.info('[获取到数据]' + str(orgin))

        # 获取表/新建表：受试者基本信息
        patient_id = orgin[0]
        logging.info('[受试者编号]' + str(patient_id))
        cur.execute('SELECT ID FROM patient where hzbh = %s;', patient_id)
        table_patient_id = cur.fetchone()
        if table_patient_id is None:
            xb = 1 if orgin[2] == '男' else 2
            try:
                cur.execute(
                    'INSERT INTO patient VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                    , (None, None, None, None, orgin[4], xb, None, None, None, None, None, None, 0, 0, None,
                       patient_id, None, None, None, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                logging.debug("[最新ID]" + str(cur.lastrowid))
                logging.debug("[插入数据的ID]" + str(conn.insert_id()))
                table_patient_id = conn.insert_id()
                conn.commit()
            except Exception as ex:
                logging.error('[插入异常]' + str(ex))
                conn.rollback()
                break

        # 获取表/新建表：common表
        cur.execute('SELECT ID FROM record_common2 where PATIENT_ID = %s;', table_patient_id)
        table_common_id = cur.fetchone()
        if table_common_id is None:
            try:
                cur.execute(
                    'INSERT INTO record_common2 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                    , (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), None, None, table_patient_id))
                logging.debug("[最新ID]" + str(cur.lastrowid))
                logging.debug("[插入数据的ID]" + str(conn.insert_id()))
                table_common_id = conn.insert_id()
                conn.commit()
            except Exception as ex:
                logging.error('[插入异常]' + str(ex))
                conn.rollback()
                break

        # 获取表/新建表：gxb表
        cur.execute('SELECT ID FROM record_gxb2 where COMMON_ID = %s;', table_common_id)
        table_gxb_id = cur.fetchone()
        if table_gxb_id is None:
            try:
                cur.execute(
                    'INSERT INTO record_gxb2 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                    , (None, table_common_id, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None))
                logging.debug("[最新ID]" + str(cur.lastrowid))
                logging.debug("[插入数据的ID]" + str(conn.insert_id()))
                table_gxb_id = conn.insert_id()
                conn.commit()
            except Exception as ex:
                logging.error('[插入异常]' + str(ex))
                conn.rollback()
                break

        # 转译数据
        logging.info('[patient表主键]' + str(table_patient_id[0]))
        logging.info('[common表主键]' + str(table_common_id[0]))
        logging.info('[gxb表主键]' + str(table_gxb_id[0]))
        # Holter
        if orgin[12] == '心律_心律：':
            if orgin[14] == '窦性心律':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_dxxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '室上性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_ssxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '室性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_sxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '室性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_sxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心房扑动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_xfpd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心房颤动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_xfcd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '房室交界性逸搏心律':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_fsjjxybxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '心律_传导阻滞：':
            if orgin[14] == 'Ⅰ度房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_1dfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == 'Ⅱ度Ⅰ型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_2d1xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == 'Ⅱ度Ⅱ型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_2d2xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == 'Ⅲ度房室传导阻滞:':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_3dfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '心律_期前收缩：':
            if orgin[14] == '房性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_fxqqss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '房室交界性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_fsjjxqqss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '室性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_sxqqass = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '平均心率：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET xl = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break
        # 一般情况
        if orgin[12] == '问寒_问寒:':
            if orgin[14] == '畏寒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_wh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '恶寒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_eh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '恶风':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_ef = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '寒战':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_hz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '发冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_fl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            # if orgin[14] == '身冷':
            #     try:
            #         cur.execute(
            #             'UPDATE record_gxb2 SET wh_sl = %s WHERE ID = %s;', (1, table_gxb_id))
            #         conn.commit()
            #     except Exception as ex:
            #         logging.error('[更新异常]' + str(ex))
            #         conn.rollback()
            #         break
            if orgin[14] == '手足不温':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_szbw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '四肢不温':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_sizbw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '身大寒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_sdh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_tl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '背冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_bl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心中寒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_xzh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腹冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_ful = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胃中寒冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_wzhl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胃怕凉':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_wpl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腰冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_yl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腰膝酸冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_yxsl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腰以下发凉':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_yyxfl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '形寒肢冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_xhzl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '骨节寒冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_gjhl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喜温':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_xw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '问热_问热:':
            if orgin[14] == '畏热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_wr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '恶热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_er = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_fr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '五心烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_wxfr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '手足心热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_szxr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_cr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '骨蒸潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_gzcr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '午后夜间潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_whyjcr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '壮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_zr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '日脯潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_rfcr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '身热夜甚':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_srys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_tr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头面热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_tmr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸中烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_xiozfr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心中烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_xinzfr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸中有热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_xzyr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '背热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_br = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胃中有热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_wzyr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '手背热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_sbr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '夜热早凉':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_yrzl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break






        # id = row[0]
        # name = row[1]
        # age = row[2]
        # print('id: ' + str(id) + '  name: ' + name + '  age: ' + str(age))
        # pass

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    transplant()
