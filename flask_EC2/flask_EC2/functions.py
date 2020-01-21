import requests
from konlpy.tag import Mecab
import pymysql
from DBUtils.SteadyDB import connect 

end_str = 'subwayinfo.cylwhwhcjyca.ap-northeast-2.rds.amazonaws.com'
# conn = pymysql.connect(host=end_str, user='user1234', password='user1234',
                    #    db='subwayinfo', charset='utf8')
conn = connect(
    creator=pymysql, 
    host=end_str, 
    user='user1234', 
    password='user1234', 
    database='subwayinfo',
    charset='utf8'
)

def move_conn(): 
    return conn
curs = conn.cursor()


mecab = Mecab()

num_list = list( map(str, range(1, 10)) )
num_to_korean_Dict = {
    '1':'일',
    '2':'이',
    '3':'삼',
    '4':'사',
    '5':'오',
    '6':'육',
    '7':'칠',
    '8':'팔',
    '9':'구',
}

def replace_num_eng_to_korean(word):
    for i in range(len(word)):
        char = word[i]
        if char in num_list: word = word.replace(char, num_to_korean_Dict[char])
    if 'J' in word: word = word.replace('J', '제이')
    return word    

# TODO 임시: 역 이름을 추출해야 하는데 그냥 명사만 추출하고 있음.
def extract_station_name(txt):
    morp = mecab.pos(txt)
    words = ""
    for m in morp:
        if 'NN' in m[1]: words += m[0]
        elif m[1] == 'UNKNOWN': words += m[0] 
    words = replace_num_eng_to_korean(words)
    return words

def extract_start_end(received_message):

    words_list = received_message.split(" ")
    len_words = len(words_list)
    morp_words = list() 

    for word in words_list:
        morp_words += mecab.pos(word)
        morp_words.append(0)
    
    start_point, end_point = '', ''
    morp_length = len(morp_words)

    # JKB(부사격조사)가 있는 문장일 경우. 
    # ex) "~에서" + "~(으)로"
    for i in range(1, morp_length):
        if morp_words[i] == 0: continue
        
        if morp_words[i][1] == 'JKB':
            current_idx = i-1
            each_str = list() 
            while current_idx >= 0:
                prev_morp = morp_words[current_idx]
                if prev_morp == 0: break
                if 'NN' in prev_morp[1]:
                    each_str.append(prev_morp[0])
                elif prev_morp[1] == 'JKB': break
                current_idx -= 1

            if len(start_point) == 0:
                while len(each_str) != 0: start_point += each_str.pop()
            else:
                if len(end_point) == 0:
                    while len(each_str) != 0: end_point += each_str.pop()

    if len(start_point) and len(end_point): pass 
    else:
        check = True if len(start_point) else False 
        check2 = False 
        for i in range(morp_length):
            if morp_words[i] == 0: continue
            word, morp = morp_words[i]
            if 'NN' in morp and word != '역': 
                if not check: 
                    start_point = word 
                    check = True 
                    check2 = True  
                else: 
                    if check2: 
                        end_point = word 
                        break 
                    else: check2 = True  
            

    start_point = replace_num_eng_to_korean(start_point)
    end_point = replace_num_eng_to_korean(end_point)

    return start_point, end_point

# JKB(부사격조사)가 없는 경우 ex) "명지대역 증산역"
def alter_extract_start_end(received_message): 

    words_list = received_message.split(" ") 
    start_point, end_point = '', '' 
    for word in words_list: 
        if word[-1] == '역': 
            if len(start_point) == 0: start_point = word 
            else: end_point = word 
    
    if len(start_point) and len(end_point): pass   
    else: 
        morps_list = mecab.pos(received_message)      
        check = True if len(start_point) else False 
        check2 = False 
        for word, morp in morps_list: 
            if 'NN' in morp and word != '역':
                if not check: 
                    start_point = word 
                    check = True 
                    check2 = True  
                else: 
                    if check2: 
                        end_point = word 
                        break
                    else: check = True 

    start_point = replace_num_eng_to_korean(start_point) 
    end_point = replace_num_eng_to_korean(end_point) 
    return start_point, end_point


def from_name_to_code(start_point, end_point):

    SID, EID = -1, -1

    if len(start_point) == 0 or len(end_point) == 0: return SID, EID

    # TO DO: Connect DB and find which number match with the station's name
    if start_point[-1] == '역' and not start_point == "서울역": start_point = start_point[:-1]

    sql_query = 'SELECT * FROM InfoSubway WHERE name=%s'
    curs.execute(sql_query, start_point)
    row = curs.fetchone()

    # DB table Schema: ["_id, name, line, code, isintoilet"]
    if row: SID = row[3]
    else: return -1, -1

    if end_point[-1] == '역' and not end_point == "서울역": end_point = end_point[:-1]
        
    sql_query = 'SELECT * FROM InfoSubway WHERE name=%s'
    curs.execute(sql_query, end_point)
    row = curs.fetchone()
    if row: EID = row[3]
    else: return -1, -1
    return SID, EID

def get_odsay_API(lang=0, CID=1000, SID=201, EID=222, Sopt=1):
    
    API_KEY = 'aOL47WqSS5JZuMY8n7TXU0vvvYRMh5XjleXt7IXEClI'
    openApiURL = 'https://api.odsay.com/v1/api/subwayPath?lang={lang}&CID={CID}&SID={SID}&EID={EID}&Sopt={Sopt}&apiKey={API_KEY}'.format(
        lang=lang, 
        CID=CID,
        SID=SID,
        EID=EID,
        Sopt=Sopt,
        API_KEY=API_KEY
        )

    openApiURL = openApiURL.encode(encoding='UTF-8')
    response = requests.get(openApiURL)
    rsp_json = response.json()
    return rsp_json

# extract ID of station in route
def extract_routine_ID(data):
    start_point = data['result']['globalStartName']
    station_route = data['result']['stationSet']['stations']
    route_name = list() 
    for elem in station_route: route_name.append(elem['endSID'])
    return route_name

# extract totalTime
def extract_total_time(data):
    return str(data['result']["globalTravelTime"])

# extract exchangeInfo
def extract_exchange_info(data):
    if not "exChangeInfoSet" in data['result']:
        return list()
    exchange_list = list()
    infoSet = data['result']['driveInfoSet']['driveInfo']
    for elem in infoSet: exchange_list.append(( elem['startName'], elem['laneName']))
    return exchange_list

def extract_exact_start_code(data): 
    start_info = data['result']['stationSet']['stations'][0]
    return start_info["startID"] 


def extract_show_routine(data):
    start_point = data['result']['globalStartName']
    station_route = data['result']['stationSet']['stations']
    route_name = list() 
    route_name.append(start_point)
    for elem in station_route: route_name.append(elem['endName'])
    return route_name
    
def set_start_point(uid, start):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row:
        q = 'UPDATE InfoUser set start = %s where uid=%s'
        curs.execute(q, (start, uid))
        conn.commit()
    return start

def set_end_point(uid, end):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row:
        q = 'UPDATE InfoUser set end = %s where uid=%s'
        curs.execute(q, (end, uid))
        conn.commit()
    return end

# 동사 존재 여부 확인
def is_vv(txt):
    morp = mecab.pos(txt)
    cnt = 0 
    for m in morp:
        if 'VV' in m[1]: return True
        elif m[1] == 'JKB': cnt += 1
    if cnt >= 2: return True 
    return False

# check if toilet is in route_stations
def check_isintoilet_by_code(elem_id):
    # DB table Schema: ["_id, name, line, code, isintoilet"]
    sql_query = 'SELECT * FROM InfoSubway WHERE code=%s'
    curs.execute(sql_query, elem_id)
    row = curs.fetchone()

    if row[4] == 1:
        if row[6] is None or len(row[6]) == 0: return [ row[3], row[2] ]
        return [ row[3], row[6] ]
    else: return False

# 하나의 역에 대해 화장실 위치 확인, 있으면 해당 코드 return
def check_one_isintoilet(station):
    if ("역" in station) and (station != "서울역"):
        station = station[:-1]
    sql_query = 'SELECT * FROM InfoSubway WHERE name=%s'
    curs.execute(sql_query, station)
    row = curs.fetchone()
    if row:
        if row[4] == 1:
            if row[6] is None or len(row[6]) == 0: return [ row[3], row[2] ]
            return [ row[3], row[6] ]
    return False

# 역 이름을 DB에서 불러옴
def get_start_point(uid):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row: return row[3]
    else: return ""

def get_end_point(uid):
    sql_query = 'SELECT * FROM InfoUser WHERE uid=%s'
    curs.execute(sql_query, uid)
    row = curs.fetchone()
    if row: return row[4]
    else: return ""

def get_official_name(name):
    sql_query = 'SELECT name2 FROM InfoSubway WHERE name=%s'
    curs.execute(sql_query, name)
    row = curs.fetchone()
    return row[0]

def get_line_name(code_id):
    sql_query = 'SELECT line FROM InfoSubway WHERE code=%s'
    curs.execute(sql_query, code_id)
    row = curs.fetchone()
    return row[0]