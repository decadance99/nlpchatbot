from flask_EC2.functions import move_conn 
import pymysql
# end_str = 'subwayinfo.cylwhwhcjyca.ap-northeast-2.rds.amazonaws.com'
# conn = pymysql.connect(host=end_str, user='user1234', password='user1234',
                    #    db='subwayinfo', charset='utf8')
# curs = conn.cursor()

conn = move_conn()
curs = conn.cursor() 

def check_user(uid):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row: stage = row[2]
    else:
        stage = 0
        q = 'INSERT INTO InfoUser(uid, stage) VALUES(%s, %s)'
        curs.execute(q, (uid, stage))
        conn.commit()
    return stage

def set_stage(uid, stage_num): 
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row:
        q = 'UPDATE InfoUser set stage = %s where uid=%s'
        curs.execute(q, (stage_num, uid))
        conn.commit()
    return stage_num

def initialize(uid):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row:
        stage = 0
        start = ""
        end = ""
        last = 0
        # modified area 
        curs.execute('UPDATE InfoUser set stage = %s where uid=%s', (stage, uid))
        curs.execute('UPDATE InfoUser set start = %s where uid=%s', (start, uid))
        curs.execute('UPDATE InfoUser set end = %s where uid=%s', (end, uid))
        curs.execute('UPDATE InfoUser set last = %s where uid=%s', (last, uid))
        conn.commit()

    return stage

def set_last(uid, last):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row:
        q = 'UPDATE InfoUser set last = %s where uid=%s'
        curs.execute(q, (last, uid))
        conn.commit()

def get_last(uid):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row: return row[5]