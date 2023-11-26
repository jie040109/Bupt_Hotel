from extension import db
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
import threading
from datetime import datetime
class ROOM(db.Model):
    __tablename__='room'
    request_id = Column(Integer, primary_key=True,info={'verbose_name':'请求号'})
    request_time = Column(DateTime, default=datetime.utcnow,info={'identity':'请求时间'})
    room_id = Column(Integer, default=0,info={'identity':'房间号'})
    current_temp = Column(Float, default=0.0,info={'identity':'当前温度'})
    init_temp = Column(Float, default=0.0,info={'identity':'初始温度'})
    target_temp = Column(Float, default=25.0,info={'identity':'目标温度'})
    fan_speed = Column(Enum('LOW', 'MIDDLE', 'HIGH'), default='MIDDLE',info={'identity':'风速'})
    state = Column(Enum('SERVING', 'WAITING', 'SHUTDOWN', 'SLEEPING'), default='SHUTDOWN',info={'identity':'状态'})
    fee_rate = Column(Float, default=0.8,info={'identity':'费率'})
    fee = Column(Float, default=0.0,info={'identity':'费用'})
    serve_time = Column(Integer, default=0,info={'identity':'服务时间'})
    wait_time = Column(Integer, default=0,info={'identity':'等待时间'})
    operation = Column(Enum('开机', '关机', '调节风速', '调节温度'), default='关机',info={'identity':'操作类型'})
    scheduling_num = Column(Integer, default=0,info={'identity':'调度次数'})

    def init (self,room_id,init_temperature,current_temperature,target_temperature,wind_speed,state,fee,serve_time,wait_time,operation,request_time,request_id):
        self.room_id=room_id
        self.init_temperature=init_temperature
        self.current_temperature=current_temperature
        self.target_temperature=target_temperature
        self.wind_speed=wind_speed
        self.state=state
        self.fee=fee
        self.serve_time=serve_time
        self.wait_time=wait_time
        self.operation=operation
        self.request_time=request_time
        self.request_id=request_id 
#服务队列
class servering_queue(db.Model):
    __tablename__='servering_queue'
    id=db.Column(db.Integer,primary_key=True,info={'identity':'ID'})
    server_number=db.Column(db.Integer,default=0,info={'identity':'服务对象数'})
    def __init__(self):
        self.server_number=0
    room_list=[]#房间列表
    def insert(self,room):#插入服务队列
        room.state='SERVING'
        room.schedule_num+=1
        self.room_list.append(room)
        self.room_list.sort(key=lambda x:(x.fan_speed))
        self.server_number+=1
        return True
    def set_temp(self,room_id,target_temp):#设置目标温度
        for room in self.room_list:
            if room.room_id==room_id:
                room.target_temp=target_temp
                break
        return True
    def set_fan_speed(self,room_id,fan_speed,fee_rate):#设置风速
        for room in self.room_list:
            if room.room_id==room_id:
                room.fan_speed=fan_speed
                room.fee_rate=fee_rate
                self.room_list.sort(key=lambda x:(x.fan_speed))
                break
        return True
    def delete_room(self,room):
        self.room_list.remove(room)
        self.server_number-=1
        return True
    def update_serve_time(self):
        if self.server_number!=0:
            for room in self.room_list:
                room.serve_time+=1
        timer=threading.Timer(60,self.update_serve_time)
        timer.start()
    def auto_fee_temp(self,mode):
        # 回温和计费函数，设定风速
        # H:1元/min,即0.016元/s,回温2℃/min，即0.03℃/s
        # M:0.5元/min,即0.008元/s,回温1.5℃/min，即0.025℃/s
        # L:0.3元/min,即0.005元/s,回温1℃/min，即0.016℃/s
        # mode=1,制热
        # mode=2,制冷
        if mode ==1:
            for room in self.room_list:
                if room.fan_speed=='HIGH':
                    room.fee+=0.016
                    room.current_temp+=0.03
                elif room.fan_speed=='MIDDLE':
                    room.current_temp+=0.025
                    room.fee+=0.008
                else:
                    room.current_temp+=0.016
                    room.fee+=0.005
                if room.current_temp>room.target_temp:
                    room.current_temp=room.target_temp
            timer=threading.Timer(1,self.auto_fee_temp,[1])
            timer.start()
        else:
            for room in self.room_list:
                if room.fan_speed=='HIGH':
                    room.fee+=0.016
                    room.current_temp-=0.03
                elif room.fan_speed=='MIDDLE':
                    room.current_temp-=0.025
                    room.fee+=0.008
                else:
                    room.current_temp-=0.016
                    room.fee+=0.005
                if room.current_temp<room.target_temp:
                    room.current_temp=room.target_temp
            timer=threading.Timer(1,self.auto_fee_temp,[2])
            timer.start()


    

#等待队列
class waiting_queue(db.Model):
    __tablename__='waiting_queue'
    id=db.Column(db.Integer,primary_key=True,info={'identity':'ID'})
    waiting_number=db.Column(db.Integer,default=0,info={'identity':'等待对象数'})
    def init(self):
        self.waiting_number=0
    room_list=[]#房间列表
    def set_temp(self,room_id,target_temp):#设置目标温度
        for room in self.room_list:
            if room.room_id==room_id:
                room.target_temp=target_temp
                break
        return True
    def set_fan_speed(self,room_id,fan_speed,fee_rate):#设置风速
        for room in self.room_list:
            if room.room_id==room_id:
                room.fan_speed=fan_speed
                room.fee_rate=fee_rate
                break
        return True
    def delete(self,room):
        self.room_list.remove(room)
        self.waiting_number-=1
        return True
    def insert(self,room):
        room.state='WAITING'
        room.schedule_num+=1
        self.room_list.append(room)
        self.waiting_number+=1
        return True
    def update_wait_time(self):
        if self.waiting_number!=0:
            for room in self.room_list:
                room.wait_time+=1
        timer=threading.Timer(60,self.update_wait_time)
        timer.start()
   
#调度器
class scheduler(db.Model):
    __tablename__='scheduler'
    id = db.Column(db.Integer, primary_key=True,info={'identity':'ID'})
    state = db.Column(Enum('working','shoutdown','setmode','ready'), default='关机', nullable=False, info={'identity':'调度器状态'})
    temp_high_limit = db.Column(db.Integer, default=32, nullable=False,info={'identity':'温度上限'})
    temp_low_limit = db.Column(db.Integer, default=16, nullable=False,info={'identity':'温度下限'})
    default_target_temp = db.Column(Enum('22','26'), default='22', nullable=False,info={'identity':'默认目标温度'})
    fee_rate_h = db.Column(db.Float, default=1.0, nullable=False,info={'identity':'高风速费率'})
    fee_rate_l = db.Column(db.Float, default=0.5, nullable=False,info={'identity':'低风速费率'})
    fee_rate_m = db.Column(db.Float, default=0.8, nullable=False,info={'identity':'中风速费率'})

    def __init__ (self,state,temp_high_limit,temp_low_limit,default_target_temp,fee_rate_h,fee_rate_l,fee_rate_m):
        self.state=state
        self.temp_high_limit=temp_high_limit
        self.temp_low_limit=temp_low_limit
        self.default_target_temp=default_target_temp
        self.fee_rate_h=fee_rate_h
        self.fee_rate_l=fee_rate_l
        self.fee_rate_m=fee_rate_m
    request_num=0#发出开机请求的房间数
    request_id=0#请求号
    temchoice=[(22,'制热'),(26,'制冷')]
    wq=waiting_queue()#等待队列
    sq=servering_queue()#服务队列
    rooms=[]#5个房间
    
    def power(self):#开机，初始化room队列
        ROOM.objects.all().delete()
        self.state='setmode'
        if self.default_target_temp==22:
            self.SQ.auto_fee_temp(1)    
        else:
            self.SQ.auto_fee_temp(2)
        self.schedule()
        self.check()
        self.SQ.update_serve_time()
        self.WQ.update_wait_time()
        return self.state
    def init_temp(self,room_id,init_temp):#设置房间初始温度
        for room in self.rooms:
            if room.room_id==room_id:
                room.init_temp=init_temp
        return True
    def request_on(self,room_id,current_temp_room):#开机请求
        # 调用调度算法
        # 开始计费和计温
        request_room=ROOM(request_id=self.request_id)
        flag=1
        for room in self.rooms:
            if room.room_id==room_id:
                room.current_temp=current_temp_room
                flag=0
                if self.SQ.server_number<3:
                    self.WQ.insert(room)
                else:
                    self.WQ.insert(room)
                request_room=room
                room.request_time=datetime.now()
                room.request_id=self.request_id
                self.request_id+=1
                room.operation='开机'
                #写入数据库
                db.session.add(room)
                db.session.commit()
        if flag==1:
            temp_room=request_room
            self.request_num+=1
            if self.request_num>5:
                return False
            temp_room.room_id=room_id
            temp_room.current_temp=current_temp_room
            self.rooms.append(temp_room)
            if self.SQ.server_number<3:
                self.SQ.insert(temp_room)
            else:
                self.WQ.insert(temp_room)
            request_room=temp_room
            temp_room.request_time=datetime.now()
            self.request_id+=1
            temp_room.operation='开机'
            #写入数据库
            db.session.add(temp_room)
            db.session.commit()
            return request_room
        
    
    def request_off(self,room_id):#关机请求
        for room in self.rooms:
            if room.room_id==room_id:
                room.current_temp=room.init_temp
                if room.state=='SERVING':
                    room.state='SHUTDOWN'
                    self.SQ.delete_room(room)
                elif room.state=='WAITING':
                    self.WQ.delete_room(room)
                    room.state='SHUTDOWN'
                else:
                    room.state='SHUTDOWN'
                room.request_id=self.request_id
                self.request_id+=1
                room.operation='关机'
                room.request_time=datetime.now()
                #写入数据库
                db.session.add(room)
                db.session.commit()
                

    def back_temp(self, room, mode):  # 回温函数
        if room.state == 'SLEEPING':
            if mode == 1:
                room.current_temp -= 0.008
                if abs(room.target_temp - room.current_temp) > 1:
                    if self.SQ.serving_num < 3: 
                        self.SQ.insert(room)
                    else:
                        self.WQ.insert(room)
                timer = threading.Timer(1, self.back_temp, [room, 1])  
                timer.start()
            else:
                room.current_temp += 0.008
                if abs(room.target_temp - room.current_temp) > 1 and room.current_temp > room.target_temp:
                    if self.SQ.serving_num < 3: 
                        self.SQ.insert(room)
                    else:
                        self.WQ.insert(room)
                timer = threading.Timer(1, self.back_temp, [room, 2]) 
                timer.start()

    def change_temp(self,room_id,target_temp):#调节温度
        if target_temp<18:
            target_temp=18
        if target_temp>28:
            target_temp=28
        for room in self.rooms:
            if room.room_id==room_id:
                if room.state=='SERVING':
                    self.SQ.set_temp(room_id,target_temp)
                elif room.state=='WAITING':
                    self.WQ.set_temp(room_id,target_temp)
                else:
                    room.target_temp=target_temp
                room.request_id=self.request_id
                self.request_id+=1
                room.operation='调节温度'
                room.request_time=datetime.now()
                #写入数据库
                db.session.add(room)
                db.session.commit()
                return room
    def change_fan_speed(self,room_id,fan_speed):#调节风速
        if fan_speed=='HIGH':
            fee_rate=self.fee_rate_h
        elif fan_speed=='MIDDLE':
            fee_rate=self.fee_rate_m
        else:
            fee_rate=self.fee_rate_l
        for room in self.rooms:
            if room.room_id==room_id:
                if room.state=='SERVING':
                    self.SQ.set_fan_speed(room_id,fan_speed,fee_rate)
                elif room.state=='WAITING':
                    self.WQ.set_fan_speed(room_id,fan_speed,fee_rate)
                else:
                    room.fan_speed=fan_speed
                    room.fee_rate=fee_rate
                room.request_id=self.request_id
                self.request_id+=1
                room.operation='调节风速'
                room.request_time=datetime.now()
                #写入数据库
                db.session.add(room)
                db.session.commit()
                return room
    def update_room(self,room_id):#每分钟查看房间状态
        for room in self.rooms:
            if room.room_id==room_id:
                return room
    def set_parameter(self, temp_high_limit, temp_low_limit, default_target_temp, fee_rate_h, fee_rate_l, fee_rate_m):
        self.temp_high_limit = temp_high_limit
        self.temp_low_limit = temp_low_limit
        self.default_target_temp = default_target_temp
        self.fee_rate_h = fee_rate_h
        self.fee_rate_l = fee_rate_l
        self.fee_rate_m = fee_rate_m
        return True
    def start(self):
        self.state='ready'
        return self.state
    def check_target(self):#遍历服务队列的房间，达到温度的房间移出服务队列 ,并且回温
        if self.SQ.server_number!=0:
            for room in self.SQ.room_list:
                if abs(room.current_temp-room.target_temp)<0.1:
                    room.state='SLEEPING'
                    self.SQ.delete_room(room)
                    if self.default_target_temp==22:
                        self.back_temp(room,1)
                    else:
                        self.back_temp(room,2)
        if self.WQ.waiting_number!=0:
            for room in self.WQ.room_list:
                if abs(room.current_temp-room.target_temp)<0.1:
                    room.state='SLEEPING'
                    self.WQ.delete_room(room)
                    if self.default_target_temp==22:
                        self.back_temp(room,1)
                    else:
                        self.back_temp(room,2)
        timer=threading.Timer(1,self.check_target)
        timer.start()
    def schedule(self):
        #时间片调度算法
        # 服务队列：先按风速排序，风速相同的情况先入先出
        # 等待队列：先入先出的时间片调度
        # 把SQ的第一个加入WQ，WQ的第一个放入SQ末尾
        if self.WQ.waiting_num != 0 and self.SQ.serving_num == 3:
            temp = self.SQ.room_list[0]
            self.SQ.delete_room(temp)
            self.WQ.insert(temp)
            temp = self.WQ.room_list[0]
            self.WQ.delete_room(temp)
            self.SQ.insert(temp)

        elif self.WQ.waiting_num != 0 and self.SQ.serving_num == 2:
            temp = self.WQ.room_list[0]
            self.WQ.delete_room(temp)
            self.SQ.insert(temp)

        elif self.WQ.waiting_num != 0 and self.SQ.serving_num <= 1:
            i = 1
            for temp in self.WQ.room_list:
                if i <= 2:
                    self.WQ.delete_room(temp)
                    self.SQ.insert(temp)
                i += 1

        elif self.WQ.waiting_num != 0 and self.SQ.serving_num <= 0:
            i = 1
            for temp in self.WQ.room_list:
                if i <= 3:
                    self.WQ.delete_room(temp)
                    self.SQ.insert(temp)
                i += 1
        timer = threading.Timer(120, self.schedule)  # 每2min执行一次调度函数
        timer.start()








    

class server(db.Model):
    __tablename__='server'
    id = db.Column(db.Integer, primary_key=True,info={'identity':'ID'})
    state = db.Column(Enum('WORKING','FREE'), default='FREE', nullable=False, info={'verbose_name': '服务状态'})
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, info={'verbose_name': '创建时间'})
    serve_time = db.Column(db.Float, nullable=False, info={'verbose_name': '服务时长'})
    room_id = db.Column(db.Integer, nullable=False, info={'verbose_name': '服务房间号'})
    target_temp = db.Column(db.Integer, nullable=False, info={'verbose_name': '目标温度'})
    fee = db.Column(db.Float, nullable=False, info={'verbose_name': '费用'})
    fee_rate = db.Column(db.Float, nullable=False, info={'verbose_name': '费率'})
    fan_speed = db.Column(db.Integer, default=2, info={'verbose_name': '风速'})

    def init (self,state,start_time,serve_time,room_id,target_temp,fee,fee_rate,fan_speed):
        self.state=state
        self.start_time=start_time
        self.serve_time=serve_time
        self.room_id=room_id
        self.target_temp=target_temp
        self.fee=fee
        self.fee_rate=fee_rate
        self.fan_speed=fan_speed

class statistic_controller(db.Model):
    __tablename__='statistic_controller'
    id=db.Column(db.Integer,primary_key=True,info={'identity':'ID'})

#初始化数据库
def init_db():
    # db.drop_all()
    db.create_all()
    for i in range(5):
        for j in range(50):
            r=ROOM(room_id=(i+1)*100+j,init_temp=25.0,current_temp=25.0,target_temp=25.0,fan_speed='MIDDLE',state='SHUTDOWN',fee=0.0,serve_time=0,wait_time=0,operation='关机',request_time='2018-01-01 00:00:00',request_id=0)
            db.session.add(r)
    s=scheduler(state=2,temp_high_limit=30,temp_low_limit=18,default_target_temp=25,fee_rate_h=1.0,fee_rate_l=0.5,fee_rate_m=0.8)
    db.session.add(s)
    for i in range(5):
        s=server(state='FREE',start_time='2018-01-01 00:00:00',serve_time=0,room_id=0,target_temp=25,fee=0.0,fee_rate=0.0,fan_speed=2)
        db.session.add(s)
    s=servering_queue(server_number=0)
    db.session.add(s)
    s=waiting_queue(waiting_number=0)
    db.session.add(s)
    s=statistic_controller()
    db.session.add(s)
    db.session.commit()
if __name__=='__main__':
    init_db()


