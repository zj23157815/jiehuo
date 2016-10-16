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
    return _ConnectionCtx()

def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args,**kw):
        with _ConnectionCtx():
            return func(*args,**kw)
    return _wrapper

def transaction():
    return _TransactionCtx()



class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_close_conn=False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn=True
        _db_ctx.transactions+=1
        logging.info('begin transaction...' if _db_ctx.transactions==1 else 'join current transaction...')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_ctx
        _db_ctx.transactions-=1
        try:
            if _db_ctx.transactions==0:
                if exc_type is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()
    def commit(self):
        global _db_ctx
        logging.info('commit transaction...')
        try:
            _db_ctx.connection.commit()
            logging.info('commit ok')
        except:
            logging.warning('commit failed.try rollback...')
            _db_ctx.connection.rollback()
            logging.warning('rollback ok')
            raise
    def rollback(self):
        global _db_ctx
        logging.warning('rollback transaction...')
        _db_ctx.connection.rollback()
        logging.info('rollback ok.')


class _DbCtx(threading.local):
    def __init__(self):
        self.connection=None
        self.transactions=0
    def is_init(self):
        return self.connection is not None
    def init(self):
        logging.info('open lasy connection...')
        self.connection=_LasyConnection()
        self.transactions=0
    def cleanup(self):
        self.connection.cleanup()
        self.connection=None
    def cursor(self):
        return self.connection.cursor()


_db_ctx=_DbCtx()

class _LasyConnection(object):
    def __init__(self):
        self.connection=None
    def cursor(self):
        if self.connection is None:
            _connection=engine.connect()
            logging.info('[CONNECTION][OPEN] connection <%s>...' % hex(id(_connection)))
            self.connection=_connection
        return self.connection.cursor()
    def commit(self):
        self.connection.commit()
    def rollback(self):
        self.connection.rollback()
    def cleanup(self):
        if self.connection:
            _connection=self.connection
            self.connection=None
            logging.info('[CONNECTION][CLOSE] connection <%>...' %hex(id(connection)))
            _connection.close()
class _ConnectionCtx(object):
    def __enter__(self):
        global  _db_ctx
        self.should_cleanup=False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup=True
        return self
    def __exit__(self,exctype,excvalue,traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()

class DBError(Exception):
    pass
class _Engine(object):
    def __init__(self,connect):
        self.__connect=connect


