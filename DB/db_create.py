import pymysql
from sqlalchemy import create_engine

# Connect RDS(AWS) ======================================
init_str = 'mysql+pymysql://'
end_str = 'user1234:user1234@subwayinfo.cylwhwhcjyca.ap-northeast-2.rds.amazonaws.com/subwayinfo'
fin_str = init_str + end_str
engine = create_engine(fin_str)
engine.connect()
# =======================================================


# CREATE TABLE ==========================================
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence
Base = declarative_base()
class InfoSubway(Base):
    __tablename__ = 'InfoSubway'
    
    id = Column(Integer, Sequence('info_subway_id_seq'), primary_key=True)
    name = Column(String(50))
    line = Column(String(50))
    code = Column(String(10))
    inToilet = Column(Integer)
    name2 = Column(String(50))
    detailed = Column(String(200))
    
    def __init__(self, name, line, code, inToilet, name2, detailed=""):
        self.name = name
        self.line = line
        self.code = code
        self.inToilet = inToilet
        self.name2 = name2
        self.detailed = detailed
        
    def __repr__(self):
        id = ""
        if self.id is not None:
            id = str(self.id)
        else:
            id = "None"
        
        return "<InfoSubway('%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
                id, self.name, self.line, self.code, self.inToilet, self.name2, self.detailed)
    
class InfoUser(Base):
    __tablename__ = 'InfoUser'
    
    id = Column(Integer, Sequence('info_user_id_seq'), primary_key=True)
    uid = Column(String(50))
    stage = Column(Integer)
    start = Column(String(50))
    end = Column(String(50))
    last = Column(String(50))
    
    def __init__(self, uid, stage):
        self.uid = uid
        self.stage = stage
        
    def __repr__(self):
        id = ""
        if self.id is not None:
            id = str(self.id)
        else:
            id = "None"
        
        return "<InfoSubway('%s', '%s', '%s')>" % (
                id, self.uid, self.stage)


Base.metadata.create_all(engine)
# =======================================================


# Read CSV(Information of subway station in round Seoul)
import csv

f = open("./subwayInfo.csv", 'r', encoding='utf-8')
data = csv.reader(f)
# =======================================================


# Information about exist of toilet in station ==========
from info_intoilet import return_toilet_dict
from copy import deepcopy
toilet_dict = return_toilet_dict()
# =======================================================

# Add session(INSERT session) ===========================
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

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
num_list = list( map(str, range(1, 10)) )

for elem in data:

    name, line, code = elem
    if name in toilet_dict[line]:
        inToilet = 1
    else:
        inToilet = 0
    name2 = deepcopy(name)
    for i in range(len(name)):
        char = name[i]
        if char in num_list:
            name = name.replace(char, num_to_korean_Dict[char])

    column = InfoSubway(name, line, code, inToilet, name2)
    session.add(column)
# =======================================================


# Commit Session ========================================
session.commit()
# =======================================================


# SELECT * FROM SubwayInfo  =============================
print( session.query(InfoSubway).all() )
# =======================================================