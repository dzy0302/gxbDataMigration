#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import time
import logging
import configparser
import datetime

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # Log等级总开关

# 第二步，创建一个handler，用于写入日志文件
logfile = 'logs/logs_update.txt'
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


def update():

    update_args = ['wh_wh', 'wh_eh', 'wh_ef', 'wh_hz', 'wh_fl', 'wh_szbw', 'wh_sizbw', 'wh_sdh', 'wh_tl', 'wh_bl',
                   'wh_xzh',  'wh_ful', 'wh_wzhl', 'wh_yxsl', 'wh_wpl', 'wh_yl', 'wh_yyxfl', 'wh_xhzl', 'wh_gjhl',
                   'wh_xw', 'wr_wr', 'wr_er', 'wr_fr', 'wr_wxfr', 'wr_szxr', 'wr_cr', 'wr_gzcr', 'wr_whyjcr', 'wr_zr',
                   'wr_rfcr', 'wr_srys', 'wr_tr', 'wr_tmr', 'wr_xiozfr', 'wr_xinzfr', 'wr_xzyr', 'wr_br', 'wr_wzyr',
                   'wr_sbr', 'wr_yrzl', 'weh_zih', 'weh_daoh', 'weh_dah', 'weh_duh', 'weh_hs',	'weh_hb', 'weh_hc',
                   'weh_lh',	'weh_rh', 'weh_hh', 'weh_yh', 'weh_hzy', 'weh_jh', 'weh_zh', 'weh_sjhc', 'weh_xhhc',
                   'weh_eh', 'weh_th',	 'weh_xh',	 'weh_sh', 'weh_szxh', 'weh_hrhc', 'ky_kg',	 'ky_fk', 'ky_kkyy',
                   'ky_kxry', 'ky_kkdy', 'ky_kxly',	'ky_kbky',	'ky_kbyy',	'ky_kbdy',	'ky_byy', 'ky_ysd', 'ky_yszq',
                   'ky_yrjt', 'ky_xly', 'ky_xry',	 'wnsnzz_syjt', 'wnsnzz_ys', 'wnsnzz_jbzs', 'wnsnzz_ss',
                   'wnsnzz_ysgd', 'wnsnzz_xgsj', 'wnsnzz_ewsc', 'wnsnzz_yes', 'wnkwzz_kd', 'wnkwzz_kt', 'wnkwzz_knn',
                   'wnkwzz_ks', 'wnkwzz_kk', 'wnkwzz_kse', 'wnkwzz_kxian', 'wnkwzz_kxiang', 'wnkwzz_kxin', 'wnkwzz_ynw',
                   'wnkwzz_kqzc', 'yfys', 'yfys_yl',	'yfys_qt', 'yfys_ll', 'yfys_ls', 'yfys_sj',	'yfys_yj',
                   'ysps_psfg', 'ysps_psxl'	, 'ysps_pssl', 'ysps_xrs', 'ysps_xsyw', 'xl_dxxl', 'xl_ssxxdgs', 'xl_xfpd',
                   'xl_fsjjxybxl', 'xl_xfcd', 'xl_sxxdgs', 'xdtqqss_fxqqss', 'xdtqqss_fsjjxqqss', 'xdtqqss_sxqqass',
                   'xdtcdzz_1dfscdzz', 'xdtcdzz_2d1xfscdzz', 'xdtcdzz_2d2xfscdzz', 'xdtcdzz_3dfscdzz', 'kxxbyw_aspl',
                   'kxxbyw_lbgl', 'kxxbyw_plgl', 'kxxbyw_tgrl', 'ttlyw', 'acei', 'arb',  'bstzzj', 'ccb', 'xszlyw',
                   'lnj', 'lnj_fsm', 'lnj_bmtn', 'lnj_tlsm', 'lnj_bfsq', 'lnj_lst', 'lnj_ydpa', 'lnj_mtlz', 'lnj_abdd',
                   'lnj_tfpt', 'lnj_qlsq', 'qgtstjkj', 'qtkxjqxyw_qmtq', 'qtkxjqxyw_nkde', 'knyw', 'sm', 'sm_byrm',
                   'sm_bm', 'sm_bnw', 'sm_mebm', 'sm_dm', 'sm_yx', 'sm_xhbnzm', 'sm_smsx', 'sm_ywba', 'sm_ss',
                   'sm_shkd', 'sm_hm', 'sm_smdc', 'sm_myz',	'sm_my', 'nl_dn', 'nl_sn', 'nl_wn', 'nc_np', 'nc_ynd',
                   'nc_yn', 'nc_nzl', 'ng_xbct', 'ng_xbzr', 'ng_xbbl', 'ng_xbbt', 'ng_xbwl', 'ng_xbsj', 'ng_xbxshd',
                   'ng_xbzd', 'ng_nj', 'ng_ns', 'ng_nt', 'ng_nhyl', 'nz_xbdh', 'nz_xbds', 'nz_xbq', 'nz_xbqc',
                   'nz_xbypm', 'nz_xbjj', 'nz_xbhz', 'nz_nc', 'nz_nzss', 'nz_nx', 'bc_bm', 'bc_xx', 'bc_stxx', 'bc_wgx',
                   'bz_wgbh', 'bz_tjbt', 'bz_bt', 'bz_dbbs', 'bz_dbbx', 'bz_dbzn', 'bz_dbzy', 'bz_dbsy', 'bz_dbxc',
                   'bz_dbch', 'bz_bx', 'bz_dbjpm', 'bz_fbswcz', 'bz_nxb', 'bg_gmzr', 'bg_ljhz', 'bg_pbbs', 'bg_bypp',
                   'bg_dbg', 'bg_dbbt', 'bg_xxbs', 'bg_pbwl', 'bg_xxrz', 'bg_dbsj', 'bg_dbht', 'xl_dxxl', 'xl_ssxxdgs',
                   'xl_xfpd', 'xl_fsjjxybxl', 'xl_xfcd', 'xl_sxxdgs', 'xdtqqss_fxqqss', 'xdtqqss_fsjjxqqss',
                   'xdtqqss_sxqqass', 'xdtcdzz_1dfscdzz', 'xdtcdzz_2d1xfscdzz', 'xdtcdzz_2d2xfscdzz',
                   'xdtcdzz_3dfscdzz', 'wgzz_el', 'wgzz_em', 'wgzz_tljt', 'wgzz_lx', 'wgzz_bn', 'wgzz_bt', 'wgzz_my',
                   'wgzz_ms', 'wgzz_th', 'wgzz_sl', 'wgzz_mg', 'wgzz_mt', 'wgzz_sg', 'wgzz_cg', 'wgzz_kcjl',
                   'wgzz_kctx', 'wgzz_cn', 'wgzz_sn', 'wgzz_yt', 'tbzz_ty', 'tbzz_txj', 'tbzz_xy', 'tbzz_th',
                   'tbzz_tj', 'tbzz_tz', 'tbzz_tskz', 'tbzz_tzho', 'tbzz_tzjq', 'tbzz_tzrg', 'tbzz_nm', 'tbzz_tt',
                   'tbzz_tyt', 'tbzz_ttsz', 'tbzz_ttwxz', 'tbzz_tmzt', 'tbzz_tnkt', 'tbzz_ttt', 'tbzz_ttrm', 'tbzz_tct',
                   'tbzz_txqt', 'xxbxzz_xt', 'xxbxzz_xgyt', 'xxbxzz_xm', 'xxbxzz_bq', 'xxbxzz_qd', 'xxbxzz_xbpm',
                   'xxbxzz_qscx', 'xxbxzz_xxqn', 'xxbxzz_xj', 'xxbxzz_xh', 'xxbxzz_xlbq', 'xxbxzz_xtjk', 'xxbxzz_xiet',
                   'xxbxzz_xz', 'xxbxzz_xxt', 'xxbxzz_xxzt', 'xxbxzz_xxct', 'xxbxzz_bt', 'xxbxzz_xbt', 'hxzz_ks',
                   'hxzz_cqks', 'hxzz_yjks', 'hxzz_gk', 'hxzz_qk', 'hxzz_kssy', 'hxzz_kszz', 'hxzz_kssd', 'hxzz_hztm',
                   'hxzz_qc', 'hxzz_kc', 'hxzz_qd', 'hxzz_tx', 'hxzz_qcec', 'hxzz_hdxs', 'hxzz_jx', 'hxzz_xm',
                   'hxzz_kx', 'hxzz_kax', 'ktzz_kt', 'ktzz_td', 'ktzz_tnk', 'ktzz_ts', 'ktzz_wt', 'ktzz_tsb',
                   'ktzz_tsh', 'ktzz_tqx', 'ktzz_tzn', 'ktzz_txm', 'ktzz_tzdx', 'ktzz_tdpm', 'ktzz_ktnt', 'fbzz_wp',
                   'fbzz_ex', 'fbzz_ot', 'fbzz_ts', 'fbzz_aq', 'fbzz_fs', 'fbzz_tus', 'fbzz_go', 'fbzz_tx', 'fbzz_en',
                   'fbzz_yn', 'fbzz_af', 'fbzz_cz', 'fbzz_fw', 'fbzz_wkg', 'fbzz_wwja', 'fbzz_wwt', 'fbzz_ft',
                   'fbzz_fz', 'fbzz_fqxz', 'fbzz_sx', 'ztzz_ztzc', 'ztzz_ztct', 'ztzz_ztst', 'ztzz_sztt', 'ztzz_jt',
                   'ztzz_bt', 'ztzz_zzrt', 'ztzz_zdlt', 'ztzz_tt', 'ztzz_xzzt', 'ztzz_zgt', 'ztzz_zt', 'qzzz_dq',
                   'qzzz_fz', 'qzzz_hhxl', 'qzzz_jl', 'qzzz_jz', 'qzzz_jk', 'qzzz_jswm', 'qzzz_xf', 'qzzz_xj',
                   'qzzz_yj', 'qzzz_zc', 'mmzz_mm', 'mmzz_tpmm', 'mmzz_mbmm', 'mmzz_kbr', 'mmzz_sm', 'mmzz_jfmm',
                   'mmzz_jrmm', 'mmzz_sfbr', 'mmzz_ztmm', 'mmzz_szmm', 'mmzz_bsmm', 'mmzz_shazmm', 'mmzz_xzmm',
                   'mmzz_shozmm', 'mmzz_smm', 'mmzz_zmm', 'mmzz_yszmm', 'mmzz_zszmm', 'fzzz_qsfz', 'fzzz_stzz',
                   'fzzz_swz', 'fzzz_ymfz', 'fzzz_shzfz', 'fzzz_sizfz', 'fzzz_xzfz', 'fzzz_yyxzs', 'qtbs_gjyc',
                   'qtbs_hzyw', 'qtbs_yht', 'qtbs_yy', 'qtbs_ygm', 'qtbs_th', 'qtbs_qz', 'qtbs_sz', 'qtbs_fl',
                   'qtbs_jdly', 'qtbs_jw', 'qtbs_shenz', 'qtbs_zst', 'qtbs_srtz', 'qtbs_jsjd', 'qtbs_ys', 'qtbs_xr',
                   'gmcta_lmtb', 'gmcta_lmwb', 'gmcta_ladjd', 'gmcta_ladzd', 'gmcta_ladyd', 'gmcta_lcxjd',
                   'gmcta_lcxyd', 'gmcta_rcajd', 'gmcta_rcazd', 'gmcta_rcayd', 'gmcta_d1hzzzjd', 'gmcta_d1hzzzyd',
                   'gmcta_qtfzzzxzwz', 'gmzy_lmzjs', 'gmzy_lmzjnzxz', 'gmzy_ladzjs', 'gmzy_ladzjnzxz', 'gmzy_lcxzjs',
                   'gmzy_lcxzjnzxz', 'gmzy_rcazjs', 'gmzy_rcazjnzxz', 'gmzy_d1zjs', 'gmzy_d1hzjzjnzxz',
                   'gmzy_qtfzzzxzwz', 'gmzy_qtfzxzzjsl', 'jdmcszc_jzdm', 'jdmcszc_jndm', 'jdmcszc_zdm',
                   'jdmcsyc_jzdm', 'jdmcsyc_jndm', 'jdmcsyc_zdm', 'ss_dh', 'ss_db', 'ss_hos', 'ss_js', 'ss_dz',
                   'ss_zh', 'ss_bjh', 'ss_ah', 'ss_jz', 'ss_qz', 'ss_za', 'ss_as', 'ss_hes', 'ss_kb', 'ss_ybyd',
                   'ss_qs', 'ss_hus', 'sx', 'sx_pd', 'sx_bych', 'sx_cl', 'sx_jn', 'sx_sb', 'sx_dc', 'sx_lw', 'sx_sc',
                   'sx_zz', 'sx_ks', 'sx_gs', 'sx_ats', 'sx_sxyx', 'sx_sxzsw', 'sx_sxtb', 'ts_b', 'ts_hua', 'ts_bh',
                   'ts_dh', 'ts_jh', 'ts_sh', 'ts_hui', 'ts_he', 'ts_hh', 'ts_l', 'tz_b', 'tz_ho', 'tz_hu', 'tz_z',
                   'tz_c', 'tz_n', 'tz_f', 'tz_bt', 'tz_r', 'tz_sg', 'tz_st', 'tz_zl', 'tz_zn', 'tz_wt', 'gxb_wdxxjt',
                   'gxb_qxxxjb', 'gxb_bwdxxjt', 'gxb_cfllxxjt', 'gxb_ehllxxjt', 'gxb_zfxxjt', 'gxb_byxxjt',
                   'gxb_wwxxjt', 'gxb_qtxxjt', 'gxb_ccs1j', 'gxb_ccs2j', 'gxb_ccs3j', 'gxb_ccs4j', 'gxb_pcish',
                   'gxb_cabgsh', 'gxb_cjxxjgswzbw', 'gxb_cjxxjgsqb', 'gxb_cjxxjgsqjb', 'gxb_cjxxjgsxb', 'gxb_cjxxjgshb',
                   'gxb_cjxxjgscb', 'gxb_cjxxjgsgcb', 'gxb_cjxxjgsys', 'gxb_nstemi', 'gxb_stemi', 'gxb_sbl',
                   'gxb_jxxjgshxsfbxsxc', 'xgnbq_nyha1j', 'xgnbq_nyha2j', 'xgnbq_nyha3j', 'xgnbq_nyha4j', 'xgnbq_zxs',
                   'xgnbq_yxs', 'xgnbq_qxs', 'xgnbq_hfref', 'xgnbq_hfmref', 'xgnbq_hfpef', 'xlsc_sxqqss', 'xlsc_fxqqss',
                   'xlsc_xfcd', 'xlsc_xfpd', 'xlsc_1dfscdzz', 'xlsc_2d1xfscdzz', 'xlsc_2d2xfscdzz', 'xlsc_3dfscdzz',
                   'xlsc_azxzqbqzt', 'xlsc_yjzhz', 'xlsc_dxxdgh', 'xlsc_bdzhz', 'xlsc_zszcdzz', 'xlsc_yszcdzz',
                   'xlsc_kmzhz', 'xlsc_spxrsh', 'gxyb_gxy1j', 'gxyb_gxy2j', 'gxyb_gxy3j', 'gxyb_yfxgxy', 'gxyb_jfxgxy',
                   'gxzz_ggyszxz', 'gxzz_gdgcxz', 'gxzz_dgmdzdbxz', 'gxzz_hhxgzxz', 'extnb', 'tnbqq_kfxtyc',
                   'tnbqq_tnlyc', 'tnbbfz_tnbsb', 'tnbbfz_tnbybbfz', 'tnbbfz_tnbz', 'tnbbfz_tnbdxgbfz',
                   'tnbbfz_tnbzwxgbb', 'mxsgnbq_ckd1q', 'mxsgnbq_ckd2q', 'mxsgnbq_ckd3q', 'mxsgnbq_ckd4q',
                   'mxsgnbq_ckd5q', 'zwxgb_jdmzyyh', 'zwxgb_xzdmzyyh', 'zwxgb_zdmzyyh', 'zwxgb_ndmzyyh',
                   'zwxgb_sgxdmzyyh', 'zwxgb_sdmzyyh', 'zwxgb_sjmxsxc', ' zwxgb_xzjmqz', 'nxgb_ngshyz', 'nxgb_dzxnqxfz',
                   'nxgb_ncxhyz', 'xzbmb_ejbgbbq', 'xzbmb_sjbgbbq', 'xzbmb_zdmbxz', 'xzbmb_zdmbgbbq', 'xzbmb_ejbxz',
                   'xzbmb_ejbtc', 'xzbmb_fdmbxz', 'xzbmb_fdmbgbbq', 'xzbmb_xzbmzhsh', 'wh', 'wr', 'weh', 'ky', 'wnsnzz',
                   'wnkwzz', 'ysps', 'wgzz', 'tbzz', 'xxbxzz', 'hxzz', 'ktzz',  'fbzz', 'ztzz', 'qzzz', 'mmzz', 'fzzz',
                   'qtbs', 'xl', 'xdtqqss', 'gxb', 'xgnbq', 'xlsc', 'gxyb', 'gxzz', 'tnbbfz', 'mxsgnbq', 'zwxgb',
                   'xzbmb', 'qx', 'qx_jzyn', 'qx_sb', 'qx_sj', 'qx_sk', 'qx_sy', 'qx_sys', 'qx_zb', 'qx_yy']

    conn = get_conn()
    cur = conn.cursor()

    for arg in update_args:
        sql = "update record_gxb2 set " + arg + " = 0 where " + arg + " is null"
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as ex:
            logging.error('字段：' + arg + '[更新异常]' + str(ex))
            conn.rollback()

    cur.close()
    conn.close()



if __name__ == '__main__':
    update()
