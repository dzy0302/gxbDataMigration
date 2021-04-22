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
        if orgin[12] == '问汗_问汗:':
            if orgin[14] == '自汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_zih = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '盗汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_daoh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_dah = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '多汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_duh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '汗少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '汗闭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '汗臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '冷汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_lh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '热汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_rh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '黄汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '油汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_yh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '汗沾衣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hzy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '绝汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_jh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '战汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_zh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '食已汗出':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_sjhc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '醒后汗出':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_xhhc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '额汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_eh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_th = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_xh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '身汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_sh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '手足心汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_szxh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '烘热汗出':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hrhc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '渴饮症状_渴饮症状:':
            if orgin[14] == '口干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '烦渴':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_fk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口渴欲饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kkyy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '渴喜热饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kxry = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口渴多饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kkdy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '渴喜冷饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kxly = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口不渴饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kbky = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '渴不欲饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kbyy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '渴不多饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kbdy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '不欲饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_byy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '饮水多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_ysd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '饮水则呛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_yszq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '引入即吐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_yrjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喜冷饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_xly = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喜热饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_xry = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '食纳症状_食纳症状:':
            if orgin[14] == '食欲减退':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_syjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '厌食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '饥不欲食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_jbzs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '食少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '饮食过度':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ysgd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '消谷善饥':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_xgsj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '恶闻食臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ewsc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '夜食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_yes = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '口味症状_口味症状:':
            if orgin[14] == '口淡':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口甜':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口黏腻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_knn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_ks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口苦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口涩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kse = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口咸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kxian = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口香':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kxiang = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口辛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kxin = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '有尿味':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_ynw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口气浊臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kqzc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '口味偏嗜_口味偏嗜:':
            if orgin[14] == '偏嗜肥甘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_psfg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '偏嗜辛辣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_psxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '偏食生冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_pssl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喜热食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_xrs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喜食异物':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_xsyw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '睡眠症状_睡眠症状:':
            if orgin[14] == '不易入眠':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_byrm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '不寐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_bm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '不能卧':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_bnw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '眠而不寐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_mebm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '多梦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_dm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '易醒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_yx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '醒后不能再寐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_xhbnzm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '时寐时醒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_smsx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '夜卧不安':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_ywba = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '嗜睡':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_ss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '食后困顿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_shkd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '鼾眠':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_hm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '睡眠倒错':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_smdc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '梦言症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_myz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '梦游':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_my = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '大便症状_便次:':
            if orgin[14] == '便秘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bc_bm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '泄泻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bc_xx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '上吐下泻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bc_stxx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '五更泻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bc_wgx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '大便症状_便质:':
            if orgin[14] == '完谷不化':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_wgbh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '溏结不调':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_tjbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '便溏':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便不实':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbbs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便变形':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbbx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便质粘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbzn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便质硬':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbzy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便水样':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbsy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便腥臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbxc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便臭秽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbch = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '便血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_bx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便夹泡沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbjpm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '粪便食物残渣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_fbswcz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '脓血便':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_nxb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '大便症状_便感:':
            if orgin[14] == '肛门灼热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_gmzr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '里急后重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_ljhz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '排便不爽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_pbbs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '便意频频':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_bypp = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便不通':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '泻下不爽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_xxbs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '排便无力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_pbwl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '泻下如注':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_xxrz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便失禁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbsj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '大便滑脱':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbht = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            # 一般情况-大便症状-矢气 ？
        if orgin[12] == '小便症状_尿量:':
            if orgin[14] == '多尿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nl_dn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '少尿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nl_sn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '无尿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nl_wn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '小便症状_尿次:':
            if orgin[14] == '尿频':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nc_np = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '夜尿多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nc_ynd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '遗尿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nc_yn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿潴留':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nc_nzl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '小便症状_尿感:':
            if orgin[14] == '小便刺痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbct = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便灼热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbzr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便不利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbbl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便不通':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便无力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbwl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便失禁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbsj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便先少后多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbxshd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便中断':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbzd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿急':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_nj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿涩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_ns = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_nt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿后余沥':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_nhyl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '小便症状_尿质:':
            if orgin[14] == '小便短黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbdh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便短少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbds = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便清':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便清长':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbqc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便有泡沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbypm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便夹精':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbjj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '小便浑浊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbhz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_nc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿中砂石':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_nzss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '尿血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_nx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '平素情志_平素情志：':
            if orgin[14] == '急躁易怒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_jzyn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '善悲':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '善惊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '善恐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '善疑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '善忧思':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '自卑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_zb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '抑郁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_yy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        # 中医病机 ？
        # 中药处方 ？
        # 主症
        if orgin[12] == '主症_诱因：':
            if orgin[14] == '遇冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_yl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '情志':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_qt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '劳力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_ll = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '劳神':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_ls = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '食积':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_sj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '饮酒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_yj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '主症_主症：':
            if orgin[14] == '头晕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_ty = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_tt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸闷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_xm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心悸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_xj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_fz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '乏力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_fl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '眩晕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_xy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_tz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '背痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喘促':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_cc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        # 伴随症状
        if orgin[12] == '伴随症状_五官症状:':
            if orgin[14] == '耳聋':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_el = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '耳鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_em = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '听力减退':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_tljt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '流涎':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_lx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '鼻衄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_bn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '流涕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '目痒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_my = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '目涩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_ms = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            # 目昏/头昏 ？
            if orgin[14] == '目昏':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_th = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '少泪':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_sl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '目干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_mg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '目痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_mt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '舌干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_sg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '唇干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_cg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口唇焦裂':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_kcjl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口唇脱屑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_kctx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '齿衄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_cn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '舌衄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_sn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '牙痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_yt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_头部症状:':
            if orgin[14] == '头晕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ty = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头项僵':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_txj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '眩晕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_xy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头昏':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_th = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头紧':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头胀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头身困重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tskz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tzho = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头重脚轻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tzjq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头重如裹':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tzrg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '脑鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_nm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头隐痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tyt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头痛时作':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttsz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头痛无休止':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttwxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头目胀痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tmzt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头脑空痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tnkt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头跳痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头痛如蒙':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttrm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头刺痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tct = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头项强痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_txqt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            # 巅顶头痛 ？
            # 额头痛 ？
            # 偏头痛 ？
        if orgin[12] == '伴随症状_心胸背胁症状:':
            if orgin[14] == '胸痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸骨压痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xgyt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸闷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '憋气':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_bq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '气短':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_qd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸部膨满':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xbpm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心胸气逆':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxqn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '气上冲心':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_qscx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心悸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心慌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心律不齐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xlbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心跳加快':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xtjk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胁痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xiet = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胁胀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸胁痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸胁胀痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxzt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸胁窜痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxct = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '背痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胸背痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_呼吸症状:':
            if orgin[14] == '咳嗽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_ks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '晨起咳嗽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_cqks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '夜间咳嗽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_yjks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '干咳':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_gk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '呛咳':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咳声嘶哑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kssy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咳声重浊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kszz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咳嗽声低':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kssd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喉中痰鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_hztm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '气喘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咳喘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '气短':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '太息':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_tx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '气粗而喘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qcec = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '呼多吸少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_hdxs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肩息':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_jx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '哮鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_xm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咳血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咯血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kax = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_咳痰症状:':
            if orgin[14] == '咳痰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_kt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_td = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰难咯':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tnk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_ts = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '无痰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_wt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰色白':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tsb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰色黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tsh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰清稀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tqx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰质粘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tzn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '吐涎沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_txm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰中带血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tzdx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰带泡沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tdpm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咳吐脓痰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_ktnt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_腹部症状:':
            if orgin[14] == '脘痞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_wp = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '恶心':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ex = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '呕吐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ot = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '吞酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ts = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '嗳气':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_aq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '泛酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '吐酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_tus = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '干呕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_go = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '吐血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_tx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '呃逆':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_en = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '哕逆':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_yn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '嗳腐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_af = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '嘈杂':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_cz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '反胃':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胃空感':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_wkg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胃脘拒按':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_wwja = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '胃脘痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_wwt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腹痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ft = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腹胀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腹气下坠':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fqxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '烧心':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_sx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_肢体症状:':
            if orgin[14] == '肢体震颤':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_ztzc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肢体刺痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_ztct = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肢体酸痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_ztst = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '四肢疼痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_sztt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肩痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_jt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '臂痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '掌中热痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zzrt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肢端冷痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zdlt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腿痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_tt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '下肢灼痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_xzzt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '足跟痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zgt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '足痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_情志症状:':
            # 不安 ？
            if orgin[14] == '胆怯':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_dq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '烦躁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_fz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '恍惚心乱':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_hhxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '焦虑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '紧张':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '惊恐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '精神萎靡':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jswm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心烦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_xf = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '心急':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_xj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '夜惊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_yj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '怔忡':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_zc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_麻木症状:':
            if orgin[14] == '麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_mm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '头皮麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_tpmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '面部麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_mbmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '口不仁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_kbr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '舌麻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_sm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肌肤麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_jfmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肌肉麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_jrmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '少腹不仁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_sfbr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '肢体麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_ztmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '四肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_szmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '半身麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_bsmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '上肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_shazmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '下肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_xzmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '手足麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_shozmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '手麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_smm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '足麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_zmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '右上肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_yszmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '左上肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_zszmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_浮肿症状:':
            if orgin[14] == '全身浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_qsfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '身体肿重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_stzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '身微肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_swz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '颜面浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_ymfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '手足浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_shzfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '四肢浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_sizfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '下肢浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_xzfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腰以下肿甚':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_yyxzs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        if orgin[12] == '伴随症状_其他不适:':
            if orgin[14] == '感觉异常':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_gjyc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '喉中异物':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_hzyw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咽喉痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_yht = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '咽痒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_yy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '易感冒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_ygm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '痰核':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_th = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '气坠':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_qz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '水肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_sz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '乏力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_fl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '倦怠懒言':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_jdly = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '健忘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_jw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '身重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_shenz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '周身痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_zst = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '身热疼重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_srtz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '脐上悸动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_jsjd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '腰酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_ys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '膝软':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_xr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
        # 其他
        if orgin[12] == 'NT-proBNP:':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ntprobnp = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break
        # BNP ？
        if orgin[12] == '超敏C反应蛋白（hs-CRP）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET hscrp = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break
        # C反应蛋白（CRP）: ？
        if orgin[12] == '同型半胱氨酸（Hcy）:':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET hcy = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break
        # 冠心病
        # 心绞痛发作频率_心绞痛发作频率： ？
        if orgin[12] == '心肌梗死病史_最后一次发病累及部位：':
            if orgin[14] == '前壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsqb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '前间壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsqjb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '下壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsxb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '侧壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgscb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '高侧壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsgcb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '后壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgshb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break
            if orgin[14] == '右室':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsys = %s WHERE ID = %s;', (1, table_gxb_id))
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
