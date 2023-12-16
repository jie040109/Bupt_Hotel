from sqlalchemy import Boolean, Column, ForeignKey, Integer,Float, String, Enum, DateTime
from datetime import datetime
from .database import Base, engine

class Room(Base):
    __tablename__ = 'rooms'

    room_id = Column(Integer, primary_key=True, unique=True,index=True)
    record_id = Column(Integer, ForeignKey('service_records.record_id'),nullable=True,index=True)
    identity_card = Column(String)
    initial_temperature = Column(Float)
    current_temperature = Column(Float)
    target_temperature = Column(Float,default=25.0)
    fan_speed = Column(Enum('high','medium','low'),default='medium')
    status = Column(Enum('SERVING', 'WAITING', 'SHUTDOWN', 'SLEEPING'),default='SHUTDOWN')
    server_time = Column(Integer,default=0)
    total_cost = Column(Float,default=0.0)

'''
Room（房间信息）表格
room_id (主键，整数)：房间号
record_id (外键，整数)：详单记录号关联ServiceRecord表
identity_card (字符串)：身份证号(密码)
initial_temperature (浮点数)：房间初始温度
current_temperature (浮点数)：当前温度
target_temperature (浮点数)：目标温度
fan_speed (字符串)：风速（高/中/低）
status (字符串)：状态（服务中/等待中/关机/休眠）
server_time (整数)：服务时间（以秒为单位）
total_cost (实数)：总费用
'''

class ServiceRecord(Base):
    __tablename__ = 'service_records'

    record_id = Column(Integer, primary_key=True, unique=True,index=True,autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.room_id'),nullable=False,index=True)
    request_time = Column(DateTime,default=datetime.now())
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)
    fan_speed = Column(Enum('high','medium','low'),default='medium')
    current_cost = Column(Float)
    rate = Column(Integer,default=1)

'''
ServiceRecord（服务详单）表格
record_id (主键，整数)：详单记录号
room_id (外键，整数)：房间号关联Room表
request_time (日期时间)：请求时间
start_time (日期时间)：服务开始时间
end_time (日期时间)：服务结束时间
duration (整数)：服务时长（以秒为单位）
fan_speed (字符串)：风速（高/中/低）
current_cost (实数)：当前费用
rate (实数)：费率
'''

class Bill(Base):
    __tablename__ = 'bills'

    bill_id = Column(Integer, primary_key=True,unique=True,index=True,autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.room_id'),nullable=False,index=True)
    checkin_time = Column(DateTime)
    checkout_time = Column(DateTime)
    total_cost = Column(Float)

'''
Bill（账单）表格
bill_id (主键，整数)：账单号
room_id (外键，整数)：房间号关联Room表
checkin_time (日期时间)：入住时间
checkout_time (日期时间)：离开时间
total_cost (实数)：空调总费用
'''

Base.metadata.create_all(bind=engine)