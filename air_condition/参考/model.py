from extension import db
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
import threading
from datetime import datetime
from flask import jsonify, make_response
from sqlalchemy import and_, or_
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
    def compute_fee(self,mode):
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
    WQ=waiting_queue()#等待队列
    SQ=servering_queue()#服务队列
    rooms=[]#5个房间
    def init_temp(self,room_id,init_temp):#设置房间初始温度
        for room in self.rooms:
            if room.room_id==room_id:
                room.init_temp=init_temp
        return True
    def power(self):#开机，初始化room队列
        db.session.query(ROOM).delete()
        db.session.commit()
        self.state='setmode'
        if self.default_target_temp==22:
            self.SQ.compute_fee(1)    
        else:
            self.SQ.compute_fee(2)
        self.schedule()
        self.check()
        self.SQ.update_serve_time()
        self.WQ.update_wait_time()
        return self.state
    
    def request_on(self,room_id,current_temp_room):
        # 调用调度算法
        # 开始计费和计温
        request_room=ROOM(request_id=self.request_id)
        flag=1
        for room in self.rooms:
            if room.room_id==room_id:
                room.current_temp=current_temp_room
                flag=0
                if self.SQ.server_number<3:
                    self.SQ.insert(room) 
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

    def init (self,start_time,room_id,target_temp,fee,fee_rate,fan_speed):
        self.state='WORKING'
        self.start_time=start_time
        self.serve_time=0
        self.room_id=room_id
        self.target_temp=target_temp
        self.fee=fee
        self.fee_rate=fee_rate
        self.fan_speed=fan_speed
        result=[self.state,self.target_temp,self.fee]
        return result
    def change_temp(self, target_temp):
        self.target_temp = target_temp
        return True
    def change_fan_speed(self, fan_speed):
        self.fan_speed = fan_speed
        return True
    def delete_server(self):
        self.room_id = 0  # 将服务对象设置为空闲
        self.state = 'FREE'  # 状态为FREE
        return self.fee
    def set_serve_time(self):
        self.serve_time = datetime.now() - self.start_time
    def set_fee(self, fee):
        self.fee = fee

class Record(db.Model): 
    @staticmethod
    def create_rdr(room_id, begin_date, end_date):
        detail = []
        rdr = ROOM.query.filter_by(room_id=room_id).filter(ROOM.request_time.between(begin_date, end_date)).order_by(ROOM.request_time.desc()).all()
        for r in rdr:
            dic = {}
            dic.update(request_id=r.request_id,
                        request_time=r.request_time,
                        room_id=r.room_id,
                        operation=r.get_operation_display(),
                        current_temp=r.current_temp,
                        target_temp=r.target_temp,
                        fan_speed=r.get_fan_speed_display(),
                        fee=r.fee)
            detail.append(dic)

        for d in detail:
            print(d)
        return detail

    @staticmethod
    def print_rdr(room_id, begin_date, end_date):
        rdr = Record.create_rdr(room_id, begin_date, end_date)
        import csv
        # 文件头，一般就是数据名
        file_header = ["request_id",
                        "request_time",
                        "room_id",
                        "operation",
                        "current_temp",
                        "target_temp",
                        "fan_speed",
                        "fee"]

            # 写入数据
        with open("./result/detailed_list.csv", "w")as csvFile:
            writer = csv.DictWriter(csvFile, file_header)
            writer.writeheader()
            # 写入的内容都是以列表的形式传入函数
            for d in rdr:
                writer.writerow(d)
            csvFile.close()
            return True
        
    @staticmethod
    def create_bill(room_id, begin_date, end_date):
        bill = ROOM.query.filter_by(room_id=room_id).filter(ROOM.request_time.between(begin_date, end_date)).order_by(ROOM.request_time.desc()).first()
        print("fee=%f" % bill.fee)

    @staticmethod
    def print_bill(room_id, begin_date, end_date):
        fee = Record.create_bill(room_id, begin_date, end_date)
        import csv
        with open('./result/bill.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["room_id", "fee"])
            writer.writerow([room_id, fee])
        return fee

    @staticmethod
    def create_report(room_id, type_report, year=-1, month=-1, week=-1):
        global operations
        if type_report == '月报表':
            """经理选择打印月报"""
            operations = db.session.query(ROOM).filter(
            and_(ROOM.room_id == room_id, and_(db.extract('year', ROOM.request_time) == year, db.extract('month', ROOM.request_time) == month))
            ).order_by(ROOM.request_time.desc()).all()
        if not operations:
            return make_response(jsonify({'error': 'Object does not exist'}), 404)

        elif type_report == '周表':
            """打印周报"""
            operations = db.session.query(ROOM).filter(
            and_(ROOM.room_id == room_id, and_(db.extract('year', ROOM.request_time) == year, db.extract('week', ROOM.request_time) == week))
            ).order_by(ROOM.request_time.desc()).all()
        if not operations:
            return make_response(jsonify({'error': 'Object does not exist'}), 404)
        report = {}
        report.update(room_id=room_id)
        # 开关次数
        switch_times = operations.filter(or_(operation='开机') | or_(operation='关机')).count()
        report.update(switch_times=switch_times)
        # 详单条数
        detailed_num = len(operations)
        report.update(detailed_num=detailed_num)
        # 调温次数
        change_temp_times = operations.filter(operation='调温').count()
        report.update(change_temp_times=change_temp_times)
        # 调风次数
        change_fan_times = operations.filter(operation='调风').count()
        report.update(change_fan_times=change_fan_times)

        if len(operations) == 0:
            schedule_times = 0
            request_time = 0
            fee = 0
        else:
            # 调度次数
            schedule_times = operations[0].scheduling_num
            # 请求时长
            request_time = operations[0].serve_time
            # 总费用
            fee = operations[0].fee

        report.update(schedule_times=schedule_times)
        report.update(request_time=request_time)
        report.update(fee=fee)

        print(report)
        return report

    @staticmethod
    def print_report(room_id=-1, type_report=1, year=-1, month=-1, week=-1):
            import csv
            header = [
                'room_id', 'switch_times', 'detailed_num', 'change_temp_times', 'change_fan_times',
                'schedule_times', 'request_time', 'fee'
            ]
            with open('./result/report.csv', 'w') as csv_file:
                writer = csv.DictWriter(csv_file, header)

            writer.writeheader()

            # 如果没有输入房间号，默认输出所有的房间报表
            if room_id == -1:
                for i in range(1, 6):
                    report = Record.create_report(room_id, type_report, year, month, week)

                    writer.writerow(report)
            else:
                report = Record.create_report(room_id, type_report, year, month, week)

                writer.writerow(report)

            return True

    @staticmethod
    def draw_report(room_id=-1, type_report=1, year=-1, month=-1, week=-1):
        import matplotlib.pyplot as plt
        if room_id == -1:
            import numpy as np
            import pandas as pd
            data = []
            global report
            rows = []
            for i in range(1,6):
                report = Record.create_report(i, type_report, year, month, week)
                data.append(list(report.values())[1:-2])
                rows.append('room' + str(report['room_id']))
            columns = list(report.keys())[1:-2]
            rows = tuple(rows)
            df = pd.DataFrame(data, columns=columns,
                            index=rows)
            df.plot(kind='barh', grid=True, colormap='YlGnBu', stacked=True,figsize=(15,5))  # 创建堆叠图
            print(data)
            data.reverse()
            table = plt.table(cellText=data,
                            cellLoc='center',
                            cellColours=None,
                            rowLabels=rows,
                            rowColours=plt.cm.BuPu(np.linspace(0, 0.5, len(rows)))[::-1],  # BuPu可替换成其他colormap
                            colLabels=columns,
                            colColours=plt.cm.Reds(np.linspace(0, 0.5, len(columns)))[::-1],
                            rowLoc='right',
                            loc='bottom',
                            fontsize=10.0)
            table.auto_set_font_size(False)
            table.set_fontsize(7)
            table.scale(1, 1)
            plt.subplots_adjust(left=0.2, bottom=0.3)
            plt.xticks([]) 
            plt.savefig('./result/report.png', dpi=300)

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
    s=Record()
    db.session.add(s)
    db.session.commit()
if __name__=='__main__':
    init_db()


