#--*-- coding=utf-8 --*--



"""
中间是注释部分
测试git

"""

import time  #涉及到时间日期的操作
import uuid  #uuid是一种唯一标示 在许多领域作为标识用途 1 :uuid1 从硬件地址和时间生成 2 uuid3 从md5算法生成 3 uudi4 随机生成 4 uudi5 从SHA-1算法生成
import functools
import threading
import logging

#定义了一个全局变量 数据引擎
engine=None

def next_id(t=None):
    """
    生成一个唯一id
    :param t:
    :return:14761966601561ab8b6fc755e4ecd8a2587befff83c74
    """
    if t is None:
        t=time.time()
    return '%015d%s000' %(int(t*1000),uuid.uuid4().hex)
def _profiling(start,sql=''):
    t=time.time()-start
    if t>0.1:
        logging.warning('[PROFILING][DB] %s:%s' %(t,sql))
    else:
        logging.info('[PROFILING][DB] %s:%s' %(t,sql))


if __name__ == '__main__':
    def create_engine(user,password,database,host='127.0.0.1',port=3306,**kw):
        import MySQLdb
        global engine
        if engine is not None:
            raise DBError('Engine is already initialized.')
        params=dict(user=user,password=password,database=database,host=host,port=port)
        defaults=dict(use_unicode=True,charset='utf8',collation='utf8_general_ci',autocommit=False)
        for k,v in defaults.iteritems():
            params[k]=kw.pop(k,v)
        params.update(kw)
        params['buffered']=True
        engine=_Engine(lambda:MySQLdb.connect(**params))
        #检测连接是否正常..
        logging.info('init mysql engine <%> ok.' %hex(id(engine)))

    def connection():



class DBError(Exception):
    pass
class _Engine(object):
    def __init__(self,connect):
        self.__connect=connect


