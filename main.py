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


def transplant():
    error_stop = False

    mode = 1

    conn = get_conn()
    cur = conn.cursor()

    cur.execute('SELECT * FROM origin_data;')
    orgin_data = cur.fetchall()
    # print(type(results))  # 返回<class 'tuple'> tuple元组类型

    for orgin in orgin_data:
        logging.info('————————————————————————————————————————————————————')
        logging.info('[获取到数据]' + str(orgin))

        # 获取表/新建表：受试者基本信息
        patient_id = orgin[0]
        logging.info('[原始数据受试者编号]' + str(patient_id))
        hzbh = 102000000 + patient_id
        logging.info('[iHealth受试者编号]' + str(hzbh))
        cur.execute('SELECT ID FROM patient where hzbh = %s;', hzbh)
        table_patient_id = cur.fetchone()
        if table_patient_id is None:
            hzbh = 102000000 + patient_id
            xb = 1 if orgin[2] == '男' else 2
            try:
                cur.execute(
                    'INSERT INTO patient(ID, csrq, xb, gzgzh, bdgzh, hzbh, CREATE_TIME, UPDATE_TIME)'
                    'VALUES(%s,%s,%s,%s,%s,%s,%s,%s);',
                    (None, orgin[4], xb, 0, 0, hzbh, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
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
        if orgin[16] is not None:
            create_time = datetime.datetime.strptime(str(orgin[16]), "%Y-%m-%d %H:%M:%S")
        else:
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if orgin[17] is not None:
            record_date = datetime.datetime.strptime(str(orgin[17]), "%Y-%m-%d")
        else:
            record_date = time.strftime("%Y-%m-%d", time.localtime())
        logging.info('[电子病历创建日期]' + str(create_time))
        logging.info('[病史采集日期]' + str(record_date))
        if mode == 1:
            cur.execute('SELECT ID FROM record_common2 where PATIENT_ID = %s;', table_patient_id)
        elif mode == 2:
            cur.execute('SELECT ID FROM record_common2 where PATIENT_ID = %s and CREATE_TIME = %s;',
                        (table_patient_id, create_time))
        elif mode == 3:
            cur.execute('SELECT ID FROM record_common2 where PATIENT_ID = %s and bscjrq = %s;',
                        (table_patient_id, record_date))
        else:
            break
        table_common_id = cur.fetchone()
        if table_common_id is None:
            try:
                cur.execute(
                    'INSERT INTO record_common2(ID, BLLX, SUBJECT_ID, yljg_bh, yljg_mc, bscjrq, USER_ID, ORG_ID, CREATE_TIME,'
                    ' UPDATE_TIME, STATUS, PATIENT_ID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                    , (None, 0, 102, 191, '西苑医院心医云', record_date, 'gxb_lrm', 191, create_time, create_time, 0,
                       table_patient_id))
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
                    'INSERT INTO record_gxb2(ID, COMMON_ID, CREATE_TIME, UPDATE_TIME, STATUS) VALUES(%s,%s,%s,%s,%s);'
                    , (None, table_common_id, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 0))
                logging.debug("[最新ID]" + str(cur.lastrowid))
                logging.debug("[插入数据的ID]" + str(conn.insert_id()))
                table_gxb_id = conn.insert_id()
                conn.commit()
            except Exception as ex:
                logging.error('[插入异常]' + str(ex))
                conn.rollback()
                break

        # 转译数据
        # logging.info('[patient表主键]' + str(table_patient_id[0]))
        # logging.info('[common表主键]' + str(table_common_id[0]))
        # logging.info('[gxb表主键]' + str(table_gxb_id[0]))
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
                    if error_stop:
                        break
            if orgin[14] == '室上性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_ssxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '室性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_sxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '室性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_sxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心房扑动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_xfpd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心房颤动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_xfcd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '房室交界性逸搏心律':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_fsjjxybxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == 'Ⅱ度Ⅰ型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_2d1xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'Ⅱ度Ⅱ型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_2d2xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'Ⅲ度房室传导阻滞:':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_3dfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '房室交界性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_fsjjxqqss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '室性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_sxqqass = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # if orgin[12] == '平均心率：':
        #     try:
        #         cur.execute(
        #             'UPDATE record_common2 SET xl = %s WHERE ID = %s;', (orgin[14], table_common_id))
        #         conn.commit()
        #     except Exception as ex:
        #         logging.error('[更新异常]' + str(ex))
        #         conn.rollback()
        #         break
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
                    if error_stop:
                        break
            if orgin[14] == '恶寒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_eh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '恶风':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_ef = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '寒战':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_hz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '发冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_fl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '四肢不温':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_sizbw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '身大寒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_sdh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_tl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '背冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_bl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心中寒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_xzh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腹冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_ful = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胃中寒冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_wzhl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胃怕凉':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_wpl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腰冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_yl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腰膝酸冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_yxsl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腰以下发凉':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_yyxfl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '形寒肢冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_xhzl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '骨节寒冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_gjhl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '喜温':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wh_xw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '恶热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_er = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_fr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '五心烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_wxfr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '手足心热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_szxr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_cr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '骨蒸潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_gzcr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '午后夜间潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_whyjcr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '壮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_zr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '日脯潮热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_rfcr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '身热夜甚':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_srys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_tr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头面热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_tmr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸中烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_xiozfr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心中烦热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_xinzfr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸中有热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_xzyr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '背热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_br = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胃中有热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_wzyr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '手背热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_sbr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '夜热早凉':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wr_yrzl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '盗汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_daoh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_dah = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '多汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_duh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '汗少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '汗闭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '汗臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '冷汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_lh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '热汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_rh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黄汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '油汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_yh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '汗沾衣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hzy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '绝汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_jh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '战汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_zh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '食已汗出':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_sjhc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '醒后汗出':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_xhhc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '额汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_eh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_th = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_xh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '身汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_sh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '手足心汗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_szxh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '烘热汗出':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET weh_hrhc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '烦渴':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_fk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口渴欲饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kkyy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '渴喜热饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kxry = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口渴多饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kkdy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '渴喜冷饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kxly = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口不渴饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kbky = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '渴不欲饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kbyy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '渴不多饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_kbdy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '不欲饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_byy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '饮水多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_ysd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '饮水则呛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_yszq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '引入即吐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_yrjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '喜冷饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_xly = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '喜热饮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ky_xry = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '厌食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '饥不欲食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_jbzs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '食少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '饮食过度':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ysgd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '消谷善饥':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_xgsj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '恶闻食臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_ewsc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '夜食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnsnzz_yes = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '口甜':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口黏腻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_knn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_ks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口苦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口涩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kse = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口咸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kxian = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口香':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kxiang = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口辛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kxin = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '有尿味':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_ynw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口气浊臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wnkwzz_kqzc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '偏嗜辛辣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_psxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '偏食生冷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_pssl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '喜热食':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_xrs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '喜食异物':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ysps_xsyw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '不寐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_bm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '不能卧':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_bnw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眠而不寐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_mebm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '多梦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_dm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '易醒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_yx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '醒后不能再寐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_xhbnzm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '时寐时醒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_smsx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '夜卧不安':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_ywba = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '嗜睡':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_ss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '食后困顿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_shkd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '鼾眠':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_hm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '睡眠倒错':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_smdc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '梦言症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_myz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '梦游':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sm_my = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '泄泻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bc_xx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '上吐下泻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bc_stxx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '五更泻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bc_wgx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '溏结不调':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_tjbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '便溏':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便不实':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbbs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便变形':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbbx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便质粘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbzn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便质硬':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbzy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便水样':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbsy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便腥臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbxc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便臭秽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbch = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '便血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_bx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便夹泡沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_dbjpm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '粪便食物残渣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_fbswcz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '脓血便':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bz_nxb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '里急后重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_ljhz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '排便不爽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_pbbs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '便意频频':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_bypp = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便不通':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '泻下不爽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_xxbs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '排便无力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_pbwl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '泻下如注':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_xxrz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便失禁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbsj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '大便滑脱':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bg_dbht = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '少尿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nl_sn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '无尿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nl_wn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '夜尿多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nc_ynd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '遗尿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nc_yn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿潴留':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nc_nzl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '小便灼热':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbzr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便不利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbbl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便不通':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便无力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbwl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便失禁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbsj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便先少后多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbxshd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便中断':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_xbzd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿急':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_nj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿涩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_ns = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_nt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿后余沥':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ng_nhyl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '小便短少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbds = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便清':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便清长':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbqc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便有泡沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbypm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便夹精':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbjj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '小便浑浊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_xbhz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿臭':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_nc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿中砂石':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_nzss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尿血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET nz_nx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '善悲':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '善惊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '善恐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '善疑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '善忧思':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_sys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '自卑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_zb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '抑郁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx_yy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '情志':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_qt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '劳力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_ll = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '劳神':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_ls = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '食积':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_sj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '饮酒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET yfys_yj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主症_主症：':
            if orgin[14] == '气短':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_qd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_xt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头晕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_ty = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_tt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸闷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_xm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心悸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_xj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_fz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '乏力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_fl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眩晕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_xy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_tz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '背痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '喘促':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zyzz_cc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '耳鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_em = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '听力减退':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_tljt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '流涎':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_lx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '鼻衄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_bn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '流涕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目痒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_my = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目涩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_ms = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '少泪':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_sl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_mg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_mt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '舌干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_sg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '唇干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_cg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口唇焦裂':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_kcjl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口唇脱屑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_kctx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '齿衄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_cn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '舌衄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_sn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '牙痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET wgzz_yt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '头项僵':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_txj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眩晕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_xy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头昏':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_th = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头紧':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头胀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头身困重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tskz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tzho = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头重脚轻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tzjq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头重如裹':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tzrg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '脑鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_nm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头隐痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tyt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头痛时作':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttsz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头痛无休止':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttwxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头目胀痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tmzt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头脑空痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tnkt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头跳痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头痛如蒙':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_ttrm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头刺痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_tct = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '头项强痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tbzz_txqt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '胸骨压痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xgyt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸闷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '憋气':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_bq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '气短':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_qd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸部膨满':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xbpm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心胸气逆':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxqn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '气上冲心':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_qscx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心悸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心慌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心律不齐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xlbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心跳加快':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xtjk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胁痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xiet = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胁胀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸胁痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸胁胀痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxzt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸胁窜痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xxct = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '背痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胸背痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xxbxzz_xbt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '晨起咳嗽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_cqks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '夜间咳嗽':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_yjks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '干咳':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_gk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '呛咳':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咳声嘶哑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kssy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咳声重浊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kszz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咳嗽声低':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kssd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '喉中痰鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_hztm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '气喘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咳喘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '气短':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '太息':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_tx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '气粗而喘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_qcec = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '呼多吸少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_hdxs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肩息':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_jx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '哮鸣':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_xm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咳血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咯血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET hxzz_kax = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '痰多':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_td = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰难咯':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tnk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰少':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_ts = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '无痰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_wt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰色白':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tsb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰色黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tsh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰清稀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tqx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰质粘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tzn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '吐涎沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_txm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰中带血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tzdx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰带泡沫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_tdpm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咳吐脓痰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ktzz_ktnt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '恶心':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ex = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '呕吐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ot = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '吞酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ts = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '嗳气':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_aq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '泛酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '吐酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_tus = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '干呕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_go = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '吐血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_tx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '呃逆':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_en = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '哕逆':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_yn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '嗳腐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_af = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '嘈杂':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_cz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '反胃':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胃空感':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_wkg = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胃脘拒按':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_wwja = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胃脘痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_wwt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腹痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_ft = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腹胀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腹气下坠':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_fqxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '烧心':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fbzz_sx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '肢体刺痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_ztct = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肢体酸痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_ztst = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '四肢疼痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_sztt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肩痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_jt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '臂痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_bt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '掌中热痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zzrt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肢端冷痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zdlt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腿痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_tt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '下肢灼痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_xzzt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '足跟痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zgt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '足痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ztzz_zt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '烦躁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_fz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '恍惚心乱':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_hhxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '焦虑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '紧张':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '惊恐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jk = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '精神萎靡':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_jswm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心烦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_xf = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心急':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_xj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '夜惊':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_yj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '怔忡':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qzzz_zc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '头皮麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_tpmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '面部麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_mbmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口不仁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_kbr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '舌麻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_sm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肌肤麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_jfmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肌肉麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_jrmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '少腹不仁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_sfbr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肢体麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_ztmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '四肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_szmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '半身麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_bsmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '上肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_shazmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '下肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_xzmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '手足麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_shozmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '手麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_smm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '足麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_zmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '右上肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_yszmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '左上肢麻木':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET mmzz_zszmm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '身体肿重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_stzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '身微肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_swz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '颜面浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_ymfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '手足浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_shzfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '四肢浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_sizfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '下肢浮肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_xzfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腰以下肿甚':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET fzzz_yyxzs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '喉中异物':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_hzyw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咽喉痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_yht = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '咽痒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_yy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '易感冒':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_ygm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '痰核':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_th = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '气坠':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_qz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '水肿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_sz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '乏力':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_fl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '倦怠懒言':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_jdly = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '健忘':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_jw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '身重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_shenz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '周身痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_zst = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '身热疼重':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_srtz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '脐上悸动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_jsjd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腰酸':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_ys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '膝软':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtbs_xr = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
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
                if error_stop:
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
                if error_stop:
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
                if error_stop:
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
                    if error_stop:
                        break
            if orgin[14] == '前间壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsqjb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '下壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsxb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '侧壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgscb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '高侧壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsgcb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '后壁':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgshb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '右室':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # 心肌梗死 ？
        # 末次心肌梗死发生于： ？
        if orgin[12] == '心肌梗死病史_心肌梗死类型：':
            if orgin[14] == 'ST段抬高型心肌梗死':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_stemi = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '非ST段抬高型心肌梗死':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_nstemi = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # 手术次数 ？
        # 最近的一次手术日期 ？
        # 凝血 ？
        # 动态血压 ？
        # 心电图
        if orgin[12] == '心电图_心律:':
            if orgin[14] == '窦性心律':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_dxxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '室上性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_ssxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '室性心动过速':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_sxxdgs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心房扑动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_xfpd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心房颤动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_xfcd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '房室交界性逸搏心律':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xl_fsjjxybxl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '心电图_传导阻滞：':
            if orgin[14] == 'Ⅰ度房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_1dfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'Ⅱ度Ⅰ型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_2d1xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'Ⅱ度Ⅱ型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_2d2xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'Ⅲ度房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtcdzz_3dfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '心电图_期前收缩:':
            if orgin[14] == '房性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_fxqqss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '房室交界性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_fsjjxqqss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '室性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xdtqqss_sxqqass = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '心率：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET xl = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == 'QTc间期：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET qtcjq = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 心肌酶
        if orgin[12] == '超敏肌钙蛋白T（hs-TnT）':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET hstnt = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 心肌酶-超敏肌钙蛋白I（hs-TnI） ？
        if orgin[12] == '肌酸激酶同工酶（CKMB）:':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ckmb = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '肌红蛋白（MYO）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET myo = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 月经史 ？
        # 望五官
        if orgin[12] == '五官_白睛所见:':
            if orgin[14] == '目赤':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgbj_mc = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目黄':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgbj_mh = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '白睛肿胀':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgbj_bjzz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '白睛微肿':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgbj_bjwz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '白睛结节':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgbj_bjjj = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目珠俱青':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgbj_mzjq = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '五官_黑睛所见:':
            if orgin[14] == '黑镜浑浊':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wghj_hjhz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黑睛粗糙':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wghj_hjcc = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黑睛生翳':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wghj_hjsy = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黑睛色白':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wghj_hjsb = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黑睛色红':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wghj_hjsh = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '五官_目眦所见:':
            if orgin[14] == '目眦淡白':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgmz_mzdb = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目眦红肿':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgmz_mzhz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目眦溃烂':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgmz_mzkl = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '五官_眼脸所见:':
            if orgin[14] == '眼脸充血':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_yjcx = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眼睑浮肿':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_yjfz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眼睑色淡':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_yjsd = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眼睑下垂':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_yjxc = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胞睑红肿':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_bjhz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胞睑溃破':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_bjkp = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胞睑丘疹':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_bjqz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '睑缘湿烂':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgyj_jysl = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '五官_口唇所见:':
            if orgin[14] == '牙龈紫暗':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_yyza = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口唇色暗':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kcsa = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口唇赤烂':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kccl = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口唇红肿':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kchz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口唇淡白':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kcdb = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            # 口唇苍白 ？
            if orgin[14] == '口唇颤动':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kccd = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '唇舌青紫':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_csqz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '唇舌色暗':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_cssa = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口中生疮':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kzsc = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口腔赤烂':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kqcl = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口角皲裂':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kjjl = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口角红肿':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kjhz = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '口眼㖞斜':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET wgkc_kywx = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # 望面色
        if orgin[12] == '面色_赤色':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_cs = %s WHERE ID = %s;', (0, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '满面通红':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_cs = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '面红如妆':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_cs = %s WHERE ID = %s;', (2, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '午后两颧潮红':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_cs = %s WHERE ID = %s;', (3, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '目赤':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_cs = %s WHERE ID = %s;', (4, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '面色_白色:':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_bs = %s WHERE ID = %s;', (0, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '淡白':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_bs = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '晄白':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_bs = %s WHERE ID = %s;', (2, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '苍白':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_bs = %s WHERE ID = %s;', (3, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '面色_黄色:':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hus = %s WHERE ID = %s;', (0, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '萎黄':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hus = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黄胖':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hus = %s WHERE ID = %s;', (2, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黄疸':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hus = %s WHERE ID = %s;', (3, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '面色_青色:':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_qs = %s WHERE ID = %s;', (0, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '淡青或青黑':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_qs = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '青黄':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_qs = %s WHERE ID = %s;', (2, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '面色口唇青紫':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_qs = %s WHERE ID = %s;', (3, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眉间鼻柱唇周发青':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_qs = %s WHERE ID = %s;', (4, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '面色_黑色:':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hes = %s WHERE ID = %s;', (0, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '面黑暗淡':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hes = %s WHERE ID = %s;', (1, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '面黑焦干':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hes = %s WHERE ID = %s;', (2, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '眼眶发黑':
                try:
                    cur.execute(
                        'UPDATE record_common2 SET ms_hes = %s WHERE ID = %s;', (3, table_common_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # 现服西药
        if orgin[12] == '抗血小板药物_抗血小板药物：':
            if orgin[14] == '阿司匹林':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET kxxbyw_aspl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '氯吡格雷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET kxxbyw_lbgl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '普拉格雷':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET kxxbyw_plgl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '替格瑞洛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET kxxbyw_tgrl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '他汀类药物_他汀类药物：':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '氟伐他汀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '洛伐他汀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '辛伐他汀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '血脂康':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '阿托伐他汀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '瑞舒伐他汀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (6, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '匹伐他汀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (7, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '普伐他汀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ttlyw = %s WHERE ID = %s;', (8, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '血管紧张转换酶抑制剂（ACEI）_血管紧张转换酶抑制剂（ACEI）：':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '卡托普利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '贝那普利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '福辛普利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '依那普利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '培哚普利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '雷米普利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (6, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '来诺普利':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET acei = %s WHERE ID = %s;', (7, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '血管紧张素Ⅱ受体阻滞剂（ARB）_血管紧张素Ⅱ受体阻滞剂（ARB）：':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET arb = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '奥美沙坦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET arb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '厄贝沙坦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET arb = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '坎地沙坦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET arb = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '氯沙坦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET arb = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '替米沙坦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET arb = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '缬沙坦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET arb = %s WHERE ID = %s;', (6, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'β受体阻滞剂_β受体阻滞剂：':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bstzzj = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '琥珀酸美托洛尔':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bstzzj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '酒石酸美托洛尔':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bstzzj = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '比索洛尔':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bstzzj = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '卡维地洛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bstzzj = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '阿替洛尔':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET bstzzj = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '钙离子通道阻滞剂（CCB）_钙离子通道阻滞剂（CCB）：':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ccb = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '硝苯地平':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ccb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '氨氯地平':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ccb = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '地尔硫卓':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ccb = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '维拉帕米':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ccb = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '非洛地平':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ccb = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '贝尼地平':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ccb = %s WHERE ID = %s;', (6, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '硝酸酯类药物_硝酸酯类药物：':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xszlyw = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '硝酸异山梨酯':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xszlyw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '单硝酸异山梨酯':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xszlyw = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '利尿剂_利尿剂:':
            if orgin[14] == '呋塞米':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_fsm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '布美他尼':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_bmtn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '托拉塞米':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_tlsm = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '苄氟噻嗪':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_bfsq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '氯噻酮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_lst = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '吲达帕胺':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_ydpa = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '美托拉宗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_mtlz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '氨苯蝶啶':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_abdd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '托伐普坦':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_tfpt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '氢氯噻嗪':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET lnj_qlsq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '醛固酮受体拮抗剂_醛固酮受体拮抗剂:':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qgtstjkj = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '螺内酯':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qgtstjkj = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '依普利酮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qgtstjkj = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '其他抗心肌缺血药物_其他抗心肌缺血药物:':
            if orgin[14] == '曲美他嗪':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtkxjqxyw_qmtq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '尼可地尔':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtkxjqxyw_nkde = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '抗凝药物_抗凝药物:':
            if orgin[14] == '无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET knyw = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '华法林':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET knyw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '达比加群':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET knyw = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '利伐沙班':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET knyw = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '其他药物_其他药物:':
            if orgin[14] == '地高辛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtyw_dgx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '伊伐布雷定':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qtyw_yfbld = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            # 依折麦布 沙库巴曲缬沙坦钠 ？
        # 生命体征
        if orgin[12] == '身高：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET sg = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '体重:':
            try:
                cur.execute(
                    'UPDATE record_common2 SET tz = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 腰围 ？
        # 血压 ？
        if orgin[12] == '收缩压：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET ssy = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 呼吸 ？
        if orgin[12] == '心率：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET xl = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 甲功
        if orgin[12] == '游离三碘甲状腺原氨酸（FT3）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ft3 = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '游离甲状腺素（FT4）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ft4 = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '促甲状腺素（TSH）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET tsh = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 肝功能
        if orgin[12] == '谷丙转氨酶（ALT）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET alt = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '谷草转氨酶（AST）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ast = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '总胆红素（TBil）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET tbil = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 直接胆红素（DBil） ？
        # γ-谷氨酰转肽酶（γ-GT） ？
        # 碱性磷酸酶（ALP） ？
        # 肾功能
        if orgin[12] == '血肌酐（Cr）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET cr = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '尿酸（UA）：':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ua = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '尿素氮（BUN）:':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET bun = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 舌诊脉象
        if orgin[12] == '舌质_舌色：':
            if orgin[14] == '淡红':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_dh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '淡白':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_db = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '红舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_hos = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '绛舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_js = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '淡紫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_dz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '紫红':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_zh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '边尖红':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_bjh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '暗红':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_ah = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '绛紫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_jz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '青紫':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_qz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '紫暗':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_za = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '暗舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_as = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黑舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_hes = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '枯白':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_kb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '瘀斑瘀点':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_ybyd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '青舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_qs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '灰舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ss_hus = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '舌质_舌形：':
            if orgin[14] == '正常':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '胖大':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_pd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '边有齿痕':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_bych = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '苍老':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_cl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '娇嫩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_jn = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '瘦薄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_sb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '点刺':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_dc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '裂纹':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_lw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '舌疮':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_sc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肿胀':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_zz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '枯舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_ks = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '干舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_gs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '凸凹舌':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_ats = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '舌下瘀血':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_sxyx = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '舌下赘生物':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_sxzsw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '舌下痰包':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET sx_sxtb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '舌苔_苔色：':
            if orgin[14] == '白':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_b = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_hua = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '白黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_bh = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '淡黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_dh = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '焦黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_jh = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '深黄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_sh = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '灰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_hui = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '黑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_he = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '灰黑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_hh = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '绿':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET ts_l = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '舌苔_苔质：':
            if orgin[14] == '薄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_b = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '厚':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_ho = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '滑':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_hu = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '燥':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_z = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '糙':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_c = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_n = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '腐':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_f = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '剥脱':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_bt = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '润':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_r = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '少干':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_sg = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '少苔':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_st = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '燥裂':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_zl = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '燥腻':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_zn = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '无苔':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tz_wt = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # 血常规
        # 淋巴细胞百分比 ？
        if orgin[12] == '中性粒细胞百分比':
            try:
                cur.execute(
                    'UPDATE record_common2 SET zxlxb_bfb = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '红细胞计数（RBC）':
            try:
                cur.execute(
                    'UPDATE record_common2 SET hxb_js = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '白细胞计数（WBC）:':
            try:
                cur.execute(
                    'UPDATE record_common2 SET bxb_js = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '血红蛋白（Hb）：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET xhdb_hl = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 血小板计数（PLT）： ？
        # 血糖
        if orgin[12] == '空腹血糖（GLU）：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET kfxt = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '餐后2小时血糖':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ch2xxxthl = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '糖化血红蛋白（HAb1c）:':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET thxhdb = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 血脂
        if orgin[12] == '总胆固醇（TC）：':
            try:
                cur.execute(
                    'UPDATE record_common2 SET zdgc = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '甘油三酯（TG）:':
            try:
                cur.execute(
                    'UPDATE record_common2 SET gysz = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '高密度脂蛋白胆固醇（HDL-C）:':
            try:
                cur.execute(
                    'UPDATE record_common2 SET gmdzdbc = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '低密度脂蛋白胆固醇（LDL-C）:':
            try:
                cur.execute(
                    'UPDATE record_common2 SET dmdzdbc = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == '脂蛋白a（Lp（a））':
            try:
                cur.execute(
                    'UPDATE record_common2 SET zzdba = %s WHERE ID = %s;', (orgin[14], table_common_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        # 西医诊断
        if orgin[12] == '主要诊断_主要诊断_冠心病_亚诊断':
            if orgin[14] == '稳定性心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_wdxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '缺血性心肌病':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_qxxxjb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '不稳定性心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_bwdxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '初发劳力型心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cfllxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '恶化劳力型心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_ehllxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '自发型心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_zfxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '变异型心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_byxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '卧位型心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_wwxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '其他型心绞痛':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_qtxxjt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'CCS I级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_ccs1j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'CCS  II级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_ccs2j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'CCS  III级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_ccs3j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'CCS IV级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_ccs4j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'PCI术后':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_pcish = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'CABG术后':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cabgsh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（未知部位）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgswzbw = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（前壁）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsqb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（前间壁）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsqjb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（下壁）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsxb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（后壁）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgshb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（侧壁）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgscb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（高侧壁）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsgcb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '陈旧性心肌梗死（右室）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_cjxxjgsys = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'STEMI':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_stemi = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'NSTEMI':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_nstemi = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '室壁瘤':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_sbl = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '附壁血栓':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxb_jxxjgshxsfbxsxc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_心功能不全_亚诊断':
            if orgin[14] == 'NYHA  I级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_nyha1j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'NYHA  II级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_nyha2j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'NYHA  III级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_nyha3j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'NYHA  IV 级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_nyha4j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '左心衰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_zxs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '右心衰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_yxs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '全心衰':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_qxs = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'HFrEF':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_hfref = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'HFmrEF':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_hfmref = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'HFpEF':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xgnbq_hfpef = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_心律失常_亚诊断':
            if orgin[14] == '室性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_sxqqss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '房性期前收缩':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_fxqqss = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心房颤动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_xfcd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心房扑动':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_xfpd = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'II度I型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_2d1xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'II度II型房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_2d2xfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'III度房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_3dfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '安装心脏起搏器状态':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_azxzqbqzt = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '预激综合征':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_yjzhz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '窦性心动过缓':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_dxxdgh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '病窦综合征':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_bdzhz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'I度房室传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_1dfscdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '左束支传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_zszcdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '右束支传导阻滞':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_yszcdzz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '快慢综合征':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xlsc_kmzhz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_高血压_亚诊断':
            if orgin[14] == '高血压  1级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxyb_gxy1j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '高血压 2级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxyb_gxy2j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '高血压3级':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxyb_gxy3j = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '原发性高血压':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxyb_yfxgxy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '继发性高血压':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxyb_jfxgxy = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_高脂血症_亚诊断':
            if orgin[14] == '高甘油三酯血症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxzz_ggyszxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '高胆固醇血症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxzz_gdgcxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '低高密度脂蛋白血症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxzz_dgmdzdbxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '混合型高脂血症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gxzz_hhxgzxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断':
            if orgin[14] == '2型糖尿病':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET extnb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_糖尿病前期_亚诊断':
            if orgin[14] == '空腹血糖异常':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tnbqq_kfxtyc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '糖耐量异常':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tnbqq_tnlyc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_糖尿病并发症_亚诊断':
            if orgin[14] == '糖尿病肾病':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tnbbfz_tnbsb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '糖尿病眼部并发症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tnbbfz_tnbybbfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '糖尿病足':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tnbbfz_tnbz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '糖尿病大血管并发症':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tnbbfz_tnbdxgbfz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '糖尿病周围血管病变':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET tnbbfz_tnbzwxgbb = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # if orgin[12] == '主要诊断_主要诊断_慢性肾功能不全_亚诊断':
        if orgin[12] == '主要诊断_主要诊断_周围血管病_亚诊断':
            if orgin[14] == '颈动脉粥样硬化':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_jdmzyyh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '下肢动脉粥样硬化':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_xzdmzyyh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '主动脉粥样硬化':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_zdmzyyh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '脑动脉粥样硬化':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_ndmzyyh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '锁骨下动脉粥样硬化':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_sgxdmzyyh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肾动脉粥样硬化':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_sdmzyyh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '深静脉血栓形成':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_sjmxsxc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '下肢静脉曲张':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET zwxgb_xzjmqz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_扩张性心肌病_亚诊断':
            if orgin[14] == '二尖瓣关闭不全':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_ejbgbbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '三尖瓣关闭不全':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_sjbgbbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == '主要诊断_主要诊断_心脏瓣膜病_亚诊断':
            if orgin[14] == '主动脉瓣狭窄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_zdmbxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '主动脉瓣关闭不全':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_zdmbgbbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '二尖瓣狭窄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_ejbxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '二尖瓣关闭不全':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_fdmbgbbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '二尖瓣脱垂':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_ejbtc = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '三尖瓣关闭不全':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_sjbgbbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肺动脉瓣狭窄':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_fdmbxz = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '肺动脉瓣关闭不全':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_fdmbgbbq = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == '心脏瓣膜置换术后':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET xzbmb_xzbmzhsh = %s WHERE ID = %s;', (1, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        # 冠脉CTA
        if orgin[12] == '冠脉钙化计分:':
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET gmghjf = %s WHERE ID = %s;', (orgin[14], table_gxb_id))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                if error_stop:
                    break
        if orgin[12] == 'LM:_头部:':
            if orgin[14] == 'LM:_头部:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmtb = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_头部:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmtb = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_头部:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmtb = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_头部:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmtb = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_头部:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmtb = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'LM:_尾部:':
            if orgin[14] == 'LM:_尾部:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmwb = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_尾部:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmwb = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_尾部:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmwb = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_尾部:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmwb = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LM:_尾部:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lmwb = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'LAD:_近段:':
            if orgin[14] == 'LAD:_近段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladjd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_近段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladjd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_近段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladjd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_近段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladjd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_近段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladjd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'LAD:_中段:':
            if orgin[14] == 'LAD:_中段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladzd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_中段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladzd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_中段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladzd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_中段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladzd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_中段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladzd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'LAD:_远段:':
            if orgin[14] == 'LAD:_远段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladyd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_远段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladyd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_远段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladyd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_远段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladyd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LAD:_远段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_ladyd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'LCX_近段:':
            if orgin[14] == 'LCX_近段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxjd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_近段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxjd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_近段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxjd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_近段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxjd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_近段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxjd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'LCX_中段:':
            if orgin[14] == 'LCX_中段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxzd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_中段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxzd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_中段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxzd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_中段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxzd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_中段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxzd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'LCX_远段:':
            if orgin[14] == 'LCX_远段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxyd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_远段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxyd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_远段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxyd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_远段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxyd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'LCX_远段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_lcxyd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'RCA:_近段:':
            if orgin[14] == 'RCA:_近段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcajd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_近段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcajd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_近段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcajd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_近段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcajd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_近段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcajd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'RCA:_中段:':
            if orgin[14] == 'RCA:_中段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcazd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_中段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcazd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_中段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcazd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_中段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcazd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_中段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcazd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'RCA:_远段:':
            if orgin[14] == 'RCA:_远段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcayd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_远段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcayd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_远段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcayd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_远段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcayd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'RCA:_远段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_rcayd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
        if orgin[12] == 'D1:_近段:':
            if orgin[14] == 'D1:_近段:无':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_d1hzzzjd = %s WHERE ID = %s;', (0, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'D1:_近段:轻度狭窄（<50%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_d1hzzzjd = %s WHERE ID = %s;', (2, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'D1:_近段:中度狭窄（50%-75%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_d1hzzzjd = %s WHERE ID = %s;', (3, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'D1:_近段:重度狭窄（76%-99%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_d1hzzzjd = %s WHERE ID = %s;', (4, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break
            if orgin[14] == 'D1:_近段:重度狭窄（100%）':
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET gmcta_d1hzzzjd = %s WHERE ID = %s;', (5, table_gxb_id))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    if error_stop:
                        break

    cur.close()
    conn.close()


def clean_common():
    conn = get_conn()
    cur = conn.cursor()

    # shent神态是否异常
    cur.execute('SELECT ID, st_fz, st_hh, st_ss, st_hm, st_zw, st_dm FROM record_common2;')
    shent_data = cur.fetchall()
    for shent in shent_data:
        if 1 in shent:
            try:
                cur.execute(
                    'UPDATE record_common2 SET shent = %s WHERE ID = %s;', (1, shent[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # qx情绪是否异常
    cur.execute('SELECT ID, qx_jz, qx_yn, qx_xf, qx_dsdl FROM record_common2;')
    qx_data = cur.fetchall()
    for qx in qx_data:
        if 1 in qx:
            try:
                cur.execute(
                    'UPDATE record_common2 SET qx = %s WHERE ID = %s;', (1, qx[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # sm睡眠是否异常
    cur.execute('SELECT ID, sm_rskn, sm_yx, sm_dm, sm_ss, sm_hz FROM record_common2;')
    sm_data = cur.fetchall()
    for sm in sm_data:
        if 1 in sm:
            try:
                cur.execute(
                    'UPDATE record_common2 SET sm = %s WHERE ID = %s;', (1, sm[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # xb小便是否异常
    cur.execute('SELECT ID, xb_cs, xb_ys, xb_dx, xb_tt FROM record_common2;')
    xb_data = cur.fetchall()
    for xb in xb_data:
        if 1 in xb:
            try:
                cur.execute(
                    'UPDATE record_common2 SET xb = %s WHERE ID = %s;', (1, xb[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # db大便是否异常
    cur.execute(
        'SELECT ID, db_ys, db_zdgy, db_zdxsy, db_zdzrbcx, db_zdnnbs, db_zdwgbh, db_zdtjbt, db_zdjyny, db_bggmzr, '
        'db_bgljhz, db_bgpbbs, db_bgjpyb FROM record_common2;')
    db_data = cur.fetchall()
    for db in db_data:
        if 1 in db:
            try:
                cur.execute(
                    'UPDATE record_common2 SET db = %s WHERE ID = %s;', (1, db[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # sx舌形是否异常
    cur.execute('SELECT ID, sx_ls, sx_ns, sx_pds, sx_sxs, sx_dcs, sx_lws, sx_chs FROM record_common2;')
    sx_data = cur.fetchall()
    for sx in sx_data:
        if 1 in sx:
            try:
                cur.execute(
                    'UPDATE record_common2 SET sx = %s WHERE ID = %s;', (1, sx[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # ms面色是否异常
    cur.execute('SELECT ID, ms_cs, ms_bs, ms_hus, ms_qs, ms_hes FROM record_common2;')
    ms_data = cur.fetchall()
    for ms in ms_data:
        if 1 in ms:
            try:
                cur.execute(
                    'UPDATE record_common2 SET ms = %s WHERE ID = %s;', (1, ms[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wgbj五官白睛是否异常
    cur.execute('SELECT ID, wgbj_mc, wgbj_mh, wgbj_bjzz, wgbj_bjwz, wgbj_bjjj, wgbj_mzjq FROM record_common2;')
    wgbj_data = cur.fetchall()
    for wgbj in wgbj_data:
        if 1 in wgbj:
            try:
                cur.execute(
                    'UPDATE record_common2 SET wgbj = %s WHERE ID = %s;', (1, wgbj[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wghj五官黑睛是否异常
    cur.execute('SELECT ID, wghj_hjhz, wghj_hjcc, wghj_hjsy, wghj_hjsb, wghj_hjsh FROM record_common2;')
    wghj_data = cur.fetchall()
    for wghj in wghj_data:
        if 1 in wghj:
            try:
                cur.execute(
                    'UPDATE record_common2 SET wghj = %s WHERE ID = %s;', (1, wghj[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wgmz五官目眦是否异常
    cur.execute('SELECT ID, wgmz_mzdb, wgmz_mzhz, wgmz_mzkl FROM record_common2;')
    wgmz_data = cur.fetchall()
    for wgmz in wgmz_data:
        if 1 in wgmz:
            try:
                cur.execute(
                    'UPDATE record_common2 SET wgmz = %s WHERE ID = %s;', (1, wgmz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wgyj五官眼睑是否异常
    cur.execute('SELECT ID, wgyj_yjcx, wgyj_yjfz, wgyj_yjsd, wgyj_yjxc, wgyj_bjhz, wgyj_bjkp, wgyj_bjqz, wgyj_jysl '
                'FROM record_common2;')
    wgyj_data = cur.fetchall()
    for wgyj in wgyj_data:
        if 1 in wgyj:
            try:
                cur.execute(
                    'UPDATE record_common2 SET wgyj = %s WHERE ID = %s;', (1, wgyj[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wgkc五官口唇是否异常
    cur.execute('SELECT ID, wgkc_yyza, wgkc_kcsa, wgkc_kccl, wgkc_kchz, wgkc_kcdb, wgkc_kccd, wgkc_csqz, wgkc_cssa,  '
                'wgkc_kzsc, wgkc_kqcl, wgkc_kjjl, wgkc_kjhz, wgkc_kywx FROM record_common2;')
    wgkc_data = cur.fetchall()
    for wgkc in wgkc_data:
        if 1 in wgkc:
            try:
                cur.execute(
                    'UPDATE record_common2 SET wgkc = %s WHERE ID = %s;', (1, wgkc[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    cur.close()
    conn.close()


def clean_gxb():
    conn = get_conn()
    cur = conn.cursor()

    # wh问寒是否异常
    cur.execute(
        'SELECT ID, wh_wh, wh_eh, wh_ef, wh_hz, wh_fl, wh_szbw, wh_sizbw, wh_sdh, wh_tl, wh_bl, wh_xzh, wh_ful, '
        'wh_wzhl, wh_yxsl, wh_wpl, wh_yl, wh_yyxfl, wh_xhzl, wh_gjhl, wh_xw FROM record_gxb2;')
    wh_data = cur.fetchall()
    for wh in wh_data:
        if 1 in wh:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET wh = %s WHERE ID = %s;', (1, wh[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wr问热是否异常
    cur.execute(
        'SELECT ID, wr_wr, wr_er, wr_fr, wr_wxfr, wr_szxr, wr_cr, wr_gzcr, wr_whyjcr, wr_zr, wr_rfcr, wr_srys, wr_tr, '
        'wr_tmr, wr_xiozfr, wr_xinzfr, wr_xzyr, wr_br, wr_wzyr, wr_sbr, wr_yrzl FROM record_gxb2;')
    wr_data = cur.fetchall()
    for wr in wr_data:
        if 1 in wr:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET wr = %s WHERE ID = %s;', (1, wr[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # weh问汗是否异常
    cur.execute(
        'SELECT ID, weh_zih, weh_daoh, weh_dah, weh_duh, weh_hs, weh_hb, weh_hc, weh_lh, weh_rh, weh_hh, weh_yh, '
        'weh_hzy, weh_jh, weh_zh, weh_sjhc, weh_xhhc, weh_eh, weh_th, weh_xh, weh_sh, weh_szxh, weh_hrhc'
        ' FROM record_gxb2;')
    weh_data = cur.fetchall()
    for weh in weh_data:
        if 1 in weh:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET weh = %s WHERE ID = %s;', (1, weh[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # ky渴饮是否异常
    cur.execute(
        'SELECT ID, ky_kg, ky_fk, ky_kkyy, ky_kxry, ky_kkdy, ky_kxly, ky_kbky, ky_kbyy, ky_kbdy, ky_byy, ky_ysd, '
        'ky_yszq, ky_yrjt, ky_xly, ky_xry'
        ' FROM record_gxb2;')
    ky_data = cur.fetchall()
    for ky in ky_data:
        if 1 in ky:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ky = %s WHERE ID = %s;', (1, ky[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wnsnzz是否有胃纳食纳症状
    cur.execute(
        'SELECT ID, wnsnzz_syjt, wnsnzz_ys, wnsnzz_jbzs, wnsnzz_ss, wnsnzz_ysgd, wnsnzz_xgsj, wnsnzz_ewsc, wnsnzz_yes '
        'FROM record_gxb2;')
    wnsnzz_data = cur.fetchall()
    for wnsnzz in wnsnzz_data:
        if 1 in wnsnzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET wnsnzz = %s WHERE ID = %s;', (1, wnsnzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wnkwzz是否有胃纳口味症状
    cur.execute(
        'SELECT ID, wnkwzz_kd, wnkwzz_kt, wnkwzz_knn, wnkwzz_ks, wnkwzz_kk, wnkwzz_kse, wnkwzz_kxian, wnkwzz_kxiang, '
        'wnkwzz_kxin, wnkwzz_ynw, wnkwzz_kqzc FROM record_gxb2;')
    wnkwzz_data = cur.fetchall()
    for wnkwzz in wnkwzz_data:
        if 1 in wnkwzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET wnkwzz = %s WHERE ID = %s;', (1, wnkwzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # yfys是否有诱发因素
    cur.execute(
        'SELECT ID, yfys_yl, yfys_qt, yfys_ll, yfys_ls, yfys_sj, yfys_yj FROM record_gxb2;')
    yfys_data = cur.fetchall()
    for yfys in yfys_data:
        if 1 in yfys:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET yfys = %s WHERE ID = %s;', (1, yfys[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # ysps是否有饮食偏奢
    cur.execute(
        'SELECT ID, ysps_psfg, ysps_psxl, ysps_pssl, ysps_xrs, ysps_xsyw FROM record_gxb2;')
    ysps_data = cur.fetchall()
    for ysps in ysps_data:
        if 1 in ysps:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ysps = %s WHERE ID = %s;', (1, ysps[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # zyzz主要症状是否有明显不适
    cur.execute(
        'SELECT ID, zyzz_xm, zyzz_xt, zyzz_ty, zyzz_tt, zyzz_xj, zyzz_qd, zyzz_fz, zyzz_fl, zyzz_xy, zyzz_tz, zyzz_bt, '
        'zyzz_cc FROM record_gxb2;')
    zyzz_data = cur.fetchall()
    for zyzz in zyzz_data:
        if 1 in zyzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET zyzz = %s WHERE ID = %s;', (1, zyzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # wgzz是否有五官症状
    cur.execute(
        'SELECT ID, wgzz_el, wgzz_em, wgzz_tljt, wgzz_lx, wgzz_bn, wgzz_bt, wgzz_my, wgzz_ms, wgzz_th, wgzz_sl, wgzz_mg, '
        'wgzz_mt, wgzz_sg, wgzz_cg, wgzz_kcjl, wgzz_kctx, wgzz_cn, wgzz_sn, wgzz_yt FROM record_gxb2;')
    wgzz_data = cur.fetchall()
    for wgzz in wgzz_data:
        if 1 in wgzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET wgzz = %s WHERE ID = %s;', (1, wgzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # tbzz是否有头部症状
    cur.execute(
        'SELECT ID, tbzz_ty, tbzz_txj, tbzz_xy, tbzz_th, tbzz_tj, tbzz_tz, tbzz_tskz, tbzz_tzho, tbzz_tzjq, tbzz_tzrg, '
        'tbzz_nm, tbzz_tt, tbzz_tyt, tbzz_ttsz, tbzz_ttwxz, tbzz_tmzt, tbzz_tnkt, tbzz_ttt, tbzz_ttrm, tbzz_tct, '
        'tbzz_txqt FROM record_gxb2;')
    tbzz_data = cur.fetchall()
    for tbzz in tbzz_data:
        if 1 in tbzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET tbzz = %s WHERE ID = %s;', (1, tbzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # xxbxzz是否有心胸背胁症状
    cur.execute(
        'SELECT ID, xxbxzz_xt, xxbxzz_xgyt, xxbxzz_xm, xxbxzz_bq, xxbxzz_qd, xxbxzz_xbpm, xxbxzz_qscx, xxbxzz_xxqn, '
        'xxbxzz_xj, xxbxzz_xh, xxbxzz_xlbq, xxbxzz_xtjk, xxbxzz_xiet, xxbxzz_xz, xxbxzz_xxt, xxbxzz_xxzt, xxbxzz_xxct, '
        'xxbxzz_bt, xxbxzz_xbt FROM record_gxb2;')
    xxbxzz_data = cur.fetchall()
    for xxbxzz in xxbxzz_data:
        if 1 in xxbxzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET xxbxzz = %s WHERE ID = %s;', (1, xxbxzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # hxzz是否有呼吸症状
    cur.execute(
        'SELECT ID, hxzz_ks, hxzz_cqks, hxzz_yjks, hxzz_gk, hxzz_qk, hxzz_kssy, hxzz_kszz, hxzz_kssd, hxzz_hztm, '
        'hxzz_qc, hxzz_kc, hxzz_qd, hxzz_tx, hxzz_qcec, hxzz_hdxs, hxzz_jx, hxzz_xm, hxzz_kx, hxzz_kax FROM record_gxb2;')
    hxzz_data = cur.fetchall()
    for hxzz in hxzz_data:
        if 1 in hxzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET hxzz = %s WHERE ID = %s;', (1, hxzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # ktzz是否有咳痰症状
    cur.execute(
        'SELECT ID, ktzz_kt, ktzz_td, ktzz_tnk, ktzz_ts, ktzz_wt, ktzz_tsb, ktzz_tsh, ktzz_tqx, ktzz_tzn, ktzz_txm, '
        'ktzz_tzdx, ktzz_tdpm, ktzz_ktnt FROM record_gxb2;')
    ktzz_data = cur.fetchall()
    for ktzz in ktzz_data:
        if 1 in ktzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ktzz = %s WHERE ID = %s;', (1, ktzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # fbzz是否有腹部症状
    cur.execute(
        'SELECT ID, fbzz_wp, fbzz_ex, fbzz_ot, fbzz_ts, fbzz_aq, fbzz_fs, fbzz_tus, fbzz_go, fbzz_tx, fbzz_en, '
        'fbzz_yn, fbzz_af, fbzz_cz, fbzz_fw, fbzz_wkg, fbzz_wwja, fbzz_wwt, fbzz_ft, fbzz_fz, fbzz_fqxz, fbzz_sx '
        'FROM record_gxb2;')
    fbzz_data = cur.fetchall()
    for fbzz in fbzz_data:
        if 1 in fbzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET fbzz = %s WHERE ID = %s;', (1, fbzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # ztzz是否有肢体症状
    cur.execute(
        'SELECT ID, ztzz_ztzc, ztzz_ztct, ztzz_ztst, ztzz_sztt, ztzz_jt, ztzz_bt, ztzz_zzrt, ztzz_zdlt, ztzz_tt, '
        'ztzz_xzzt, ztzz_zgt, ztzz_zt FROM record_gxb2;')
    ztzz_data = cur.fetchall()
    for ztzz in ztzz_data:
        if 1 in ztzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET ztzz = %s WHERE ID = %s;', (1, ztzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # qzzz是否有情志症状
    cur.execute(
        'SELECT ID, qzzz_dq, qzzz_fz, qzzz_hhxl, qzzz_jl, qzzz_jz, qzzz_jk, qzzz_jswm, qzzz_xf, qzzz_xj, qzzz_yj, '
        'qzzz_zc FROM record_gxb2;')
    qzzz_data = cur.fetchall()
    for qzzz in qzzz_data:
        if 1 in qzzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET qzzz = %s WHERE ID = %s;', (1, qzzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # mmzz是否有麻木症状
    cur.execute(
        'SELECT ID, mmzz_mm, mmzz_tpmm, mmzz_mbmm, mmzz_kbr, mmzz_sm, mmzz_jfmm, mmzz_jrmm, mmzz_sfbr, mmzz_ztmm, '
        'mmzz_szmm, mmzz_bsmm, mmzz_shazmm, mmzz_xzmm, mmzz_shozmm, mmzz_smm, mmzz_zmm, mmzz_yszmm, mmzz_zszmm '
        'FROM record_gxb2;')
    mmzz_data = cur.fetchall()
    for mmzz in mmzz_data:
        if 1 in mmzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET mmzz = %s WHERE ID = %s;', (1, mmzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # fzzz是否有浮肿症状
    cur.execute(
        'SELECT ID, fzzz_qsfz, fzzz_stzz, fzzz_swz, fzzz_ymfz, fzzz_shzfz, fzzz_sizfz, fzzz_xzfz, fzzz_yyxzs '
        'FROM record_gxb2;')
    fzzz_data = cur.fetchall()
    for fzzz in fzzz_data:
        if 1 in fzzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET fzzz = %s WHERE ID = %s;', (1, fzzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # qtbs是否有其他不适
    cur.execute(
        'SELECT ID, qtbs_gjyc, qtbs_hzyw, qtbs_yht, qtbs_yy, qtbs_ygm, qtbs_th, qtbs_qz, qtbs_sz, qtbs_fl, qtbs_jdly, '
        'qtbs_jw, qtbs_shenz, qtbs_zst, qtbs_srtz, qtbs_jsjd, qtbs_ys, qtbs_xr FROM record_gxb2;')
    qtbs_data = cur.fetchall()
    for qtbs in qtbs_data:
        if 1 in qtbs:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET qtbs = %s WHERE ID = %s;', (1, qtbs[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # lnj是否有利尿剂
    cur.execute(
        'SELECT ID, lnj_fsm, lnj_bmtn, lnj_tlsm, lnj_bfsq, lnj_lst, lnj_ydpa, lnj_mtlz, lnj_abdd, lnj_tfpt, lnj_qlsq '
        'FROM record_gxb2;')
    lnj_data = cur.fetchall()
    for lnj in lnj_data:
        if 1 in lnj:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET lnj = %s WHERE ID = %s;', (1, lnj[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # xl心律是否异常
    cur.execute(
        'SELECT ID, xl_dxxl, xl_ssxxdgs, xl_xfpd, xl_fsjjxybxl, xl_xfcd, xl_sxxdgs FROM record_gxb2;')
    xl_data = cur.fetchall()
    for xl in xl_data:
        if 1 in xl:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET xl = %s WHERE ID = %s;', (1, xl[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # xdtqqss心电图期前收缩是否异常
    cur.execute(
        'SELECT ID, xdtqqss_fxqqss, xdtqqss_fsjjxqqss, xdtqqss_sxqqass FROM record_gxb2;')
    xdtqqss_data = cur.fetchall()
    for xdtqqss in xdtqqss_data:
        if 1 in xdtqqss:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET xdtqqss = %s WHERE ID = %s;', (1, xdtqqss[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # gxb是否有冠心病异常
    cur.execute(
        'SELECT ID, gxb_wdxxjt, gxb_qxxxjb, gxb_bwdxxjt, gxb_cfllxxjt, gxb_ehllxxjt, gxb_zfxxjt, gxb_byxxjt, gxb_wwxxjt, '
        'gxb_wwxxjt, gxb_qtxxjt, gxb_ccs1j, gxb_ccs2j, gxb_ccs3j, gxb_ccs4j, gxb_pcish, gxb_cabgsh, gxb_cjxxjgswzbw, '
        'gxb_cjxxjgsqb, gxb_cjxxjgsqjb, gxb_cjxxjgsxb, gxb_cjxxjgshb, gxb_cjxxjgscb, gxb_cjxxjgsgcb, gxb_cjxxjgsys, '
        'gxb_nstemi, gxb_stemi, gxb_sbl, gxb_jxxjgshxsfbxsxc FROM record_gxb2;')
    gxb_data = cur.fetchall()
    for gxb in gxb_data:
        if 1 in gxb:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET gxb = %s WHERE ID = %s;', (1, gxb[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # xgnbq是否有心功能不全
    cur.execute(
        'SELECT ID, xgnbq_nyha1j, xgnbq_nyha2j, xgnbq_nyha3j, xgnbq_nyha4j, xgnbq_zxs, xgnbq_yxs, xgnbq_qxs, xgnbq_hfref, '
        'xgnbq_hfmref, xgnbq_hfpef FROM record_gxb2;')
    xgnbq_data = cur.fetchall()
    for xgnbq in xgnbq_data:
        if 1 in xgnbq:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET xgnbq = %s WHERE ID = %s;', (1, xgnbq[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # xlsc是否有心律失常
    cur.execute(
        'SELECT ID, xlsc_sxqqss, xlsc_fxqqss, xlsc_xfcd, xlsc_xfpd, xlsc_1dfscdzz, xlsc_2d1xfscdzz, xlsc_2d2xfscdzz, '
        'xlsc_3dfscdzz, xlsc_azxzqbqzt, xlsc_yjzhz, xlsc_dxxdgh, xlsc_bdzhz, xlsc_zszcdzz, xlsc_yszcdzz, xlsc_kmzhz, '
        'xlsc_spxrsh FROM record_gxb2;')
    xlsc_data = cur.fetchall()
    for xlsc in xlsc_data:
        if 1 in xlsc:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET xlsc = %s WHERE ID = %s;', (1, xlsc[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # gxyb是否有高血压病
    cur.execute(
        'SELECT ID, gxyb_gxy1j, gxyb_gxy2j, gxyb_gxy3j, gxyb_yfxgxy, gxyb_jfxgxy FROM record_gxb2;')
    gxyb_data = cur.fetchall()
    for gxyb in gxyb_data:
        if 1 in gxyb:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET gxyb = %s WHERE ID = %s;', (1, gxyb[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # gxzz是否有高血脂症
    cur.execute(
        'SELECT ID, gxzz_ggyszxz, gxzz_gdgcxz, gxzz_dgmdzdbxz, gxzz_hhxgzxz FROM record_gxb2;')
    gxzz_data = cur.fetchall()
    for gxzz in gxzz_data:
        if 1 in gxzz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET gxzz = %s WHERE ID = %s;', (1, gxzz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # tnbbfz是否有糖尿病并发症
    cur.execute(
        'SELECT ID, tnbbfz_tnbsb, tnbbfz_tnbybbfz, tnbbfz_tnbz, tnbbfz_tnbdxgbfz, tnbbfz_tnbzwxgbb FROM record_gxb2;')
    tnbbfz_data = cur.fetchall()
    for tnbbfz in tnbbfz_data:
        if 1 in tnbbfz:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET tnbbfz = %s WHERE ID = %s;', (1, tnbbfz[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # zwxgb是否有周围血管病异常
    cur.execute(
        'SELECT ID, zwxgb_jdmzyyh, zwxgb_xzdmzyyh, zwxgb_zdmzyyh, zwxgb_ndmzyyh, zwxgb_sgxdmzyyh, zwxgb_sdmzyyh, '
        'zwxgb_sjmxsxc, zwxgb_xzjmqz FROM record_gxb2;')
    zwxgb_data = cur.fetchall()
    for zwxgb in zwxgb_data:
        if 1 in zwxgb:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET zwxgb = %s WHERE ID = %s;', (1, zwxgb[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

    # xzbmb是否有心脏瓣膜病异常
    cur.execute(
        'SELECT ID, xzbmb_ejbgbbq, xzbmb_sjbgbbq, xzbmb_zdmbxz, xzbmb_zdmbgbbq, xzbmb_ejbxz, xzbmb_ejbtc, xzbmb_fdmbxz, '
        'xzbmb_fdmbgbbq, xzbmb_xzbmzhsh FROM record_gxb2;')
    xzbmb_data = cur.fetchall()
    for xzbmb in xzbmb_data:
        if 1 in xzbmb:
            try:
                cur.execute(
                    'UPDATE record_gxb2 SET xzbmb = %s WHERE ID = %s;', (1, xzbmb[0]))
                conn.commit()
            except Exception as ex:
                logging.error('[更新异常]' + str(ex))
                conn.rollback()
                break

        # qx情绪是否异常
        cur.execute(
            'SELECT ID, qx_jzyn, qx_sb, qx_sj, qx_sk, qx_sy, qx_sys, qx_zb, '
            'qx_yy FROM record_gxb2;')
        qx_data = cur.fetchall()
        for qx in qx_data:
            if 1 in qx:
                try:
                    cur.execute(
                        'UPDATE record_gxb2 SET qx = %s WHERE ID = %s;', (1, qx[0]))
                    conn.commit()
                except Exception as ex:
                    logging.error('[更新异常]' + str(ex))
                    conn.rollback()
                    break

    cur.close()
    conn.close()


# def update_gxb():
#     update_args = ['wh_wh', 'wh_eh', 'wh_ef', 'wh_hz', 'wh_fl', 'wh_szbw', 'wh_sizbw', 'wh_sdh', 'wh_tl', 'wh_bl',
#                    'wh_xzh', 'wh_ful', 'wh_wzhl', 'wh_yxsl', 'wh_wpl', 'wh_yl', 'wh_yyxfl', 'wh_xhzl', 'wh_gjhl',
#                    'wh_xw', 'wr_wr', 'wr_er', 'wr_fr', 'wr_wxfr', 'wr_szxr', 'wr_cr', 'wr_gzcr', 'wr_whyjcr', 'wr_zr',
#                    'wr_rfcr', 'wr_srys', 'wr_tr', 'wr_tmr', 'wr_xiozfr', 'wr_xinzfr', 'wr_xzyr', 'wr_br', 'wr_wzyr',
#                    'wr_sbr', 'wr_yrzl', 'weh_zih', 'weh_daoh', 'weh_dah', 'weh_duh', 'weh_hs', 'weh_hb', 'weh_hc',
#                    'weh_lh', 'weh_rh', 'weh_hh', 'weh_yh', 'weh_hzy', 'weh_jh', 'weh_zh', 'weh_sjhc', 'weh_xhhc',
#                    'weh_eh', 'weh_th', 'weh_xh', 'weh_sh', 'weh_szxh', 'weh_hrhc', 'ky_kg', 'ky_fk', 'ky_kkyy',
#                    'ky_kxry', 'ky_kkdy', 'ky_kxly', 'ky_kbky', 'ky_kbyy', 'ky_kbdy', 'ky_byy', 'ky_ysd', 'ky_yszq',
#                    'ky_yrjt', 'ky_xly', 'ky_xry', 'wnsnzz_syjt', 'wnsnzz_ys', 'wnsnzz_jbzs', 'wnsnzz_ss',
#                    'wnsnzz_ysgd', 'wnsnzz_xgsj', 'wnsnzz_ewsc', 'wnsnzz_yes', 'wnkwzz_kd', 'wnkwzz_kt', 'wnkwzz_knn',
#                    'wnkwzz_ks', 'wnkwzz_kk', 'wnkwzz_kse', 'wnkwzz_kxian', 'wnkwzz_kxiang', 'wnkwzz_kxin', 'wnkwzz_ynw',
#                    'wnkwzz_kqzc', 'yfys', 'yfys_yl', 'yfys_qt', 'yfys_ll', 'yfys_ls', 'yfys_sj', 'yfys_yj',
#                    'ysps_psfg', 'ysps_psxl', 'ysps_pssl', 'ysps_xrs', 'ysps_xsyw', 'xl_dxxl', 'xl_ssxxdgs', 'xl_xfpd',
#                    'xl_fsjjxybxl', 'xl_xfcd', 'xl_sxxdgs', 'xdtqqss_fxqqss', 'xdtqqss_fsjjxqqss', 'xdtqqss_sxqqass',
#                    'xdtcdzz_1dfscdzz', 'xdtcdzz_2d1xfscdzz', 'xdtcdzz_2d2xfscdzz', 'xdtcdzz_3dfscdzz', 'kxxbyw_aspl',
#                    'kxxbyw_lbgl', 'kxxbyw_plgl', 'kxxbyw_tgrl', 'ttlyw', 'acei', 'arb', 'bstzzj', 'ccb', 'xszlyw',
#                    'lnj', 'lnj_fsm', 'lnj_bmtn', 'lnj_tlsm', 'lnj_bfsq', 'lnj_lst', 'lnj_ydpa', 'lnj_mtlz', 'lnj_abdd',
#                    'lnj_tfpt', 'lnj_qlsq', 'qgtstjkj', 'qtkxjqxyw_qmtq', 'qtkxjqxyw_nkde', 'knyw', 'sm', 'sm_byrm',
#                    'sm_bm', 'sm_bnw', 'sm_mebm', 'sm_dm', 'sm_yx', 'sm_xhbnzm', 'sm_smsx', 'sm_ywba', 'sm_ss',
#                    'sm_shkd', 'sm_hm', 'sm_smdc', 'sm_myz', 'sm_my', 'nl_dn', 'nl_sn', 'nl_wn', 'nc_np', 'nc_ynd',
#                    'nc_yn', 'nc_nzl', 'ng_xbct', 'ng_xbzr', 'ng_xbbl', 'ng_xbbt', 'ng_xbwl', 'ng_xbsj', 'ng_xbxshd',
#                    'ng_xbzd', 'ng_nj', 'ng_ns', 'ng_nt', 'ng_nhyl', 'nz_xbdh', 'nz_xbds', 'nz_xbq', 'nz_xbqc',
#                    'nz_xbypm', 'nz_xbjj', 'nz_xbhz', 'nz_nc', 'nz_nzss', 'nz_nx', 'bc_bm', 'bc_xx', 'bc_stxx', 'bc_wgx',
#                    'bz_wgbh', 'bz_tjbt', 'bz_bt', 'bz_dbbs', 'bz_dbbx', 'bz_dbzn', 'bz_dbzy', 'bz_dbsy', 'bz_dbxc',
#                    'bz_dbch', 'bz_bx', 'bz_dbjpm', 'bz_fbswcz', 'bz_nxb', 'bg_gmzr', 'bg_ljhz', 'bg_pbbs', 'bg_bypp',
#                    'bg_dbg', 'bg_dbbt', 'bg_xxbs', 'bg_pbwl', 'bg_xxrz', 'bg_dbsj', 'bg_dbht', 'xl_dxxl', 'xl_ssxxdgs',
#                    'xl_xfpd', 'xl_fsjjxybxl', 'xl_xfcd', 'xl_sxxdgs', 'xdtqqss_fxqqss', 'xdtqqss_fsjjxqqss',
#                    'xdtqqss_sxqqass', 'xdtcdzz_1dfscdzz', 'xdtcdzz_2d1xfscdzz', 'xdtcdzz_2d2xfscdzz',
#                    'xdtcdzz_3dfscdzz', 'wgzz_el', 'wgzz_em', 'wgzz_tljt', 'wgzz_lx', 'wgzz_bn', 'wgzz_bt', 'wgzz_my',
#                    'wgzz_ms', 'wgzz_th', 'wgzz_sl', 'wgzz_mg', 'wgzz_mt', 'wgzz_sg', 'wgzz_cg', 'wgzz_kcjl',
#                    'wgzz_kctx', 'wgzz_cn', 'wgzz_sn', 'wgzz_yt', 'tbzz_ty', 'tbzz_txj', 'tbzz_xy', 'tbzz_th',
#                    'tbzz_tj', 'tbzz_tz', 'tbzz_tskz', 'tbzz_tzho', 'tbzz_tzjq', 'tbzz_tzrg', 'tbzz_nm', 'tbzz_tt',
#                    'tbzz_tyt', 'tbzz_ttsz', 'tbzz_ttwxz', 'tbzz_tmzt', 'tbzz_tnkt', 'tbzz_ttt', 'tbzz_ttrm', 'tbzz_tct',
#                    'tbzz_txqt', 'xxbxzz_xt', 'xxbxzz_xgyt', 'xxbxzz_xm', 'xxbxzz_bq', 'xxbxzz_qd', 'xxbxzz_xbpm',
#                    'xxbxzz_qscx', 'xxbxzz_xxqn', 'xxbxzz_xj', 'xxbxzz_xh', 'xxbxzz_xlbq', 'xxbxzz_xtjk', 'xxbxzz_xiet',
#                    'xxbxzz_xz', 'xxbxzz_xxt', 'xxbxzz_xxzt', 'xxbxzz_xxct', 'xxbxzz_bt', 'xxbxzz_xbt', 'hxzz_ks',
#                    'hxzz_cqks', 'hxzz_yjks', 'hxzz_gk', 'hxzz_qk', 'hxzz_kssy', 'hxzz_kszz', 'hxzz_kssd', 'hxzz_hztm',
#                    'hxzz_qc', 'hxzz_kc', 'hxzz_qd', 'hxzz_tx', 'hxzz_qcec', 'hxzz_hdxs', 'hxzz_jx', 'hxzz_xm',
#                    'hxzz_kx', 'hxzz_kax', 'ktzz_kt', 'ktzz_td', 'ktzz_tnk', 'ktzz_ts', 'ktzz_wt', 'ktzz_tsb',
#                    'ktzz_tsh', 'ktzz_tqx', 'ktzz_tzn', 'ktzz_txm', 'ktzz_tzdx', 'ktzz_tdpm', 'ktzz_ktnt', 'fbzz_wp',
#                    'fbzz_ex', 'fbzz_ot', 'fbzz_ts', 'fbzz_aq', 'fbzz_fs', 'fbzz_tus', 'fbzz_go', 'fbzz_tx', 'fbzz_en',
#                    'fbzz_yn', 'fbzz_af', 'fbzz_cz', 'fbzz_fw', 'fbzz_wkg', 'fbzz_wwja', 'fbzz_wwt', 'fbzz_ft',
#                    'fbzz_fz', 'fbzz_fqxz', 'fbzz_sx', 'ztzz_ztzc', 'ztzz_ztct', 'ztzz_ztst', 'ztzz_sztt', 'ztzz_jt',
#                    'ztzz_bt', 'ztzz_zzrt', 'ztzz_zdlt', 'ztzz_tt', 'ztzz_xzzt', 'ztzz_zgt', 'ztzz_zt', 'qzzz_dq',
#                    'qzzz_fz', 'qzzz_hhxl', 'qzzz_jl', 'qzzz_jz', 'qzzz_jk', 'qzzz_jswm', 'qzzz_xf', 'qzzz_xj',
#                    'qzzz_yj', 'qzzz_zc', 'mmzz_mm', 'mmzz_tpmm', 'mmzz_mbmm', 'mmzz_kbr', 'mmzz_sm', 'mmzz_jfmm',
#                    'mmzz_jrmm', 'mmzz_sfbr', 'mmzz_ztmm', 'mmzz_szmm', 'mmzz_bsmm', 'mmzz_shazmm', 'mmzz_xzmm',
#                    'mmzz_shozmm', 'mmzz_smm', 'mmzz_zmm', 'mmzz_yszmm', 'mmzz_zszmm', 'fzzz_qsfz', 'fzzz_stzz',
#                    'fzzz_swz', 'fzzz_ymfz', 'fzzz_shzfz', 'fzzz_sizfz', 'fzzz_xzfz', 'fzzz_yyxzs', 'qtbs_gjyc',
#                    'qtbs_hzyw', 'qtbs_yht', 'qtbs_yy', 'qtbs_ygm', 'qtbs_th', 'qtbs_qz', 'qtbs_sz', 'qtbs_fl',
#                    'qtbs_jdly', 'qtbs_jw', 'qtbs_shenz', 'qtbs_zst', 'qtbs_srtz', 'qtbs_jsjd', 'qtbs_ys', 'qtbs_xr',
#                    'gmcta_lmtb', 'gmcta_lmwb', 'gmcta_ladjd', 'gmcta_ladzd', 'gmcta_ladyd', 'gmcta_lcxjd',
#                    'gmcta_lcxyd', 'gmcta_rcajd', 'gmcta_rcazd', 'gmcta_rcayd', 'gmcta_d1hzzzjd', 'gmcta_d1hzzzyd',
#                    'gmcta_qtfzzzxzwz', 'gmzy_lmzjs', 'gmzy_lmzjnzxz', 'gmzy_ladzjs', 'gmzy_ladzjnzxz', 'gmzy_lcxzjs',
#                    'gmzy_lcxzjnzxz', 'gmzy_rcazjs', 'gmzy_rcazjnzxz', 'gmzy_d1zjs', 'gmzy_d1hzjzjnzxz',
#                    'gmzy_qtfzzzxzwz', 'gmzy_qtfzxzzjsl', 'jdmcszc_jzdm', 'jdmcszc_jndm', 'jdmcszc_zdm',
#                    'jdmcsyc_jzdm', 'jdmcsyc_jndm', 'jdmcsyc_zdm', 'ss_dh', 'ss_db', 'ss_hos', 'ss_js', 'ss_dz',
#                    'ss_zh', 'ss_bjh', 'ss_ah', 'ss_jz', 'ss_qz', 'ss_za', 'ss_as', 'ss_hes', 'ss_kb', 'ss_ybyd',
#                    'ss_qs', 'ss_hus', 'sx', 'sx_pd', 'sx_bych', 'sx_cl', 'sx_jn', 'sx_sb', 'sx_dc', 'sx_lw', 'sx_sc',
#                    'sx_zz', 'sx_ks', 'sx_gs', 'sx_ats', 'sx_sxyx', 'sx_sxzsw', 'sx_sxtb', 'ts_b', 'ts_hua', 'ts_bh',
#                    'ts_dh', 'ts_jh', 'ts_sh', 'ts_hui', 'ts_he', 'ts_hh', 'ts_l', 'tz_b', 'tz_ho', 'tz_hu', 'tz_z',
#                    'tz_c', 'tz_n', 'tz_f', 'tz_bt', 'tz_r', 'tz_sg', 'tz_st', 'tz_zl', 'tz_zn', 'tz_wt', 'gxb_wdxxjt',
#                    'gxb_qxxxjb', 'gxb_bwdxxjt', 'gxb_cfllxxjt', 'gxb_ehllxxjt', 'gxb_zfxxjt', 'gxb_byxxjt',
#                    'gxb_wwxxjt', 'gxb_qtxxjt', 'gxb_ccs1j', 'gxb_ccs2j', 'gxb_ccs3j', 'gxb_ccs4j', 'gxb_pcish',
#                    'gxb_cabgsh', 'gxb_cjxxjgswzbw', 'gxb_cjxxjgsqb', 'gxb_cjxxjgsqjb', 'gxb_cjxxjgsxb', 'gxb_cjxxjgshb',
#                    'gxb_cjxxjgscb', 'gxb_cjxxjgsgcb', 'gxb_cjxxjgsys', 'gxb_nstemi', 'gxb_stemi', 'gxb_sbl',
#                    'gxb_jxxjgshxsfbxsxc', 'xgnbq_nyha1j', 'xgnbq_nyha2j', 'xgnbq_nyha3j', 'xgnbq_nyha4j', 'xgnbq_zxs',
#                    'xgnbq_yxs', 'xgnbq_qxs', 'xgnbq_hfref', 'xgnbq_hfmref', 'xgnbq_hfpef', 'xlsc_sxqqss', 'xlsc_fxqqss',
#                    'xlsc_xfcd', 'xlsc_xfpd', 'xlsc_1dfscdzz', 'xlsc_2d1xfscdzz', 'xlsc_2d2xfscdzz', 'xlsc_3dfscdzz',
#                    'xlsc_azxzqbqzt', 'xlsc_yjzhz', 'xlsc_dxxdgh', 'xlsc_bdzhz', 'xlsc_zszcdzz', 'xlsc_yszcdzz',
#                    'xlsc_kmzhz', 'xlsc_spxrsh', 'gxyb_gxy1j', 'gxyb_gxy2j', 'gxyb_gxy3j', 'gxyb_yfxgxy', 'gxyb_jfxgxy',
#                    'gxzz_ggyszxz', 'gxzz_gdgcxz', 'gxzz_dgmdzdbxz', 'gxzz_hhxgzxz', 'extnb', 'tnbqq_kfxtyc',
#                    'tnbqq_tnlyc', 'tnbbfz_tnbsb', 'tnbbfz_tnbybbfz', 'tnbbfz_tnbz', 'tnbbfz_tnbdxgbfz',
#                    'tnbbfz_tnbzwxgbb', 'mxsgnbq_ckd1q', 'mxsgnbq_ckd2q', 'mxsgnbq_ckd3q', 'mxsgnbq_ckd4q',
#                    'mxsgnbq_ckd5q', 'zwxgb_jdmzyyh', 'zwxgb_xzdmzyyh', 'zwxgb_zdmzyyh', 'zwxgb_ndmzyyh',
#                    'zwxgb_sgxdmzyyh', 'zwxgb_sdmzyyh', 'zwxgb_sjmxsxc', ' zwxgb_xzjmqz', 'nxgb_ngshyz', 'nxgb_dzxnqxfz',
#                    'nxgb_ncxhyz', 'xzbmb_ejbgbbq', 'xzbmb_sjbgbbq', 'xzbmb_zdmbxz', 'xzbmb_zdmbgbbq', 'xzbmb_ejbxz',
#                    'xzbmb_ejbtc', 'xzbmb_fdmbxz', 'xzbmb_fdmbgbbq', 'xzbmb_xzbmzhsh']
#
#     conn = get_conn()
#     cur = conn.cursor()
#
#     for arg in update_args:
#         sql = "update record_gxb2 set " + arg + " = 0 where " + arg + " is null"
#         try:
#             cur.execute(sql)
#             conn.commit()
#         except Exception as ex:
#             logging.error('字段：' + arg + '[更新异常]' + str(ex))
#             conn.rollback()
#
#     cur.close()
#     conn.close()


if __name__ == '__main__':
    # 数据移植
    print('------------------------ 1.数据移植 ----------------------------------')
    transplant()
    # common表数据清洗
    print('--------------------- 2.common表数据清洗 ------------------------------')
    clean_common()
    # gxy表数据清洗
    print('---------------------- 3.gxy表数据清洗 --------------------------------')
    clean_gxb()
    # gxy表数据清洗
    # print('---------------------- 4.gxy表数据补全 --------------------------------')
    # update_gxb()
