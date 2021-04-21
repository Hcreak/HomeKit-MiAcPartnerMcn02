# coding=utf-8

DB_URL = "sqlite:///data.db?check_same_thread=False"

from sqlalchemy import Column,Integer,Float,DECIMAL, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import time
from decimal import Decimal

import warnings
warnings.filterwarnings("ignore")

Base = declarative_base()

class Each(Base):
    __tablename__ = 'each'

    timestamp = Column(Integer, nullable=False, primary_key=True)
    load_power = Column(Float, nullable=False)

class Day(Base):
    __tablename__ = 'day'

    day = Column(Integer, nullable=False, primary_key=True)
    energy_count = Column(DECIMAL(7,5), nullable=False)

class Month(Base):
    __tablename__ = 'month'

    month = Column(Integer, nullable=False, primary_key=True)
    energy_count = Column(DECIMAL(8,5), nullable=False)

engine = create_engine(DB_URL)
Base.metadata.create_all(engine, checkfirst=True)
DBSession = sessionmaker(bind=engine)

def unix_timestamp():
    return int(time.time())

def output_day():
    return int(time.strftime("%y%m%d", time.localtime()))

def output_month():
    return int(time.strftime("%y%m", time.localtime()))

def try_commit(dataObj):
    try:
        # 创建Session对象
        session = DBSession()
        # 添加到session
        session.add(dataObj)
        # 提交
        session.commit()
        # 关闭session
        session.close()
    except Exception as e:
        ## 异常回滚
        session.rollback()
        print(e)
        return False
    return True

def compute_energy(load_power):
    # print(load_power/1000/60)
    return Decimal(load_power/1000/60).quantize(Decimal("0.00000"))

def put_load_power(load_power):
    new_each = Each(timestamp=unix_timestamp(), load_power=load_power)
    try_commit(new_each)

def put_energy_count_day(energy):
    session = DBSession()
    int_day = output_day()
    queryresult = session.query(Day).filter(Day.day==int_day).all()
    if len(queryresult) == 0:
        new_day = Day(day=int_day, energy_count=energy)
        try_commit(new_day)
    else:
        queryresult[0].energy_count += energy
        session.commit()
    session.close()

def put_energy_count_month(energy):
    session = DBSession()
    int_month = output_month()
    queryresult = session.query(Month).filter(Month.month==int_month).all()
    if len(queryresult) == 0:
        new_month = Month(month=int_month, energy_count=energy)
        try_commit(new_month)
    else:
        queryresult[0].energy_count += energy
        session.commit()
    session.close()

def transform_dict(sqlalchemyListObj):
    transform_result = []
    for i in sqlalchemyListObj:
        item = i.__dict__
        del item['_sa_instance_state']
        transform_result.append(item)
    return transform_result

def transform_timestamp(int_day):
    struct_time = time.strptime(str(int_day), "%y%m%d")
    start_timestamp = time.mktime(struct_time)
    end_timestamp = start_timestamp + 86400
    return start_timestamp, end_timestamp

def get_energy_count_month():
    session = DBSession()
    queryresult = session.query(Month).all()
    session.close()
    return transform_dict(queryresult)

def get_energy_count_day(month):
    session = DBSession()
    queryresult = session.query(Day).filter(Day.day.like('{}%'.format(month))).all()
    session.close()
    return transform_dict(queryresult)

def get_load_power(day):
    start, end = transform_timestamp(day)
    session = DBSession()
    queryresult = session.query(Each).filter(Each.timestamp.between(start, end)).all()
    session.close()
    return transform_dict(queryresult)