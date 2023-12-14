from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sql_app import models
from sql_app.database import get_db, SessionLocal
from datetime import datetime
import threading

class RoomData:
    def __init__(self, db_room):
        self.room_id = db_room.room_id
        self.record_id = db_room.record_id
        self.identity_card = db_room.identity_card
        self.initial_temperature = db_room.initial_temperature
        self.current_temperature = db_room.current_temperature
        self.target_temperature = db_room.target_temperature
        self.fan_speed = db_room.fan_speed
        self.status = db_room.status
        self.server_time = db_room.server_time
        self.total_cost = db_room.total_cost

db = SessionLocal()

router = APIRouter(prefix="/schedule", tags=["schedule"])

# 服务队列
service_queue = []

# 等待队列
waiting_queue = []

# 房间队列
room_queue = []

'''
优先级调度	以高中低为三级进行优先级判断，高速风优先级最高，中速风次之，低速风优先级最低																			
时间片调度	等待队列中的对象被分配2mins时长，服务队列服务时长最长的一旦到达2mins将被调度到等待队列																			
房间温度算法	每分钟变化0.5度，只有目标温度到达时以及房间关机时才会启动该算法。																			
房间关机的回温	假定，房间关机，房间温度每分钟变化0.5度，直到房间的初始化温度，比如房间2只下降到22度
'''

# 优先级调度
def priority_scheduling(db):
    # 优先级调度
    # 以高中低为三级进行优先级判断，高速风优先级最高，中速风次之，低速风优先级最低
    # 服务队列中的对象按照优先级从高到低排序
    # 等待队列中的对象按照优先级从高到低排序

    # 定义一个字典，将风扇速度的字符串映射为相应的整数值
    speed_mapping = {'high': 3, 'medium': 2, 'low': 1}

    room_queue.sort(key=lambda x: speed_mapping[x.fan_speed], reverse=True)

    service_queue.sort(key=lambda x: speed_mapping[x.fan_speed])

    if(len(service_queue)<3 and len(waiting_queue)!=0):
        for room in waiting_queue:
            if(len(service_queue)<3):
                temp=room
                waiting_queue.remove(temp)
                service_queue.append(temp)
                temp.status='SERVING'
                db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
                db_room.status='SERVING'
                db.commit()
            else:
                break

    for room in room_queue:
        for service in service_queue:
            if(room.status=='WAITING'and speed_mapping[room.fan_speed] > speed_mapping[service.fan_speed]):
                temp=service
                service_queue.remove(temp)
                waiting_queue.append(temp)
                temp.status='WAITING'
                db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
                db_room.status='WAITING'
                
                temp = room
                waiting_queue.remove(temp)
                service_queue.append(temp)
                temp.status='SERVING'
                db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
                db_room.status='SERVING'
                db.commit()
                break

def time_slicing(db):
    # 服务队列：先按风速排序，风速相同的情况先入先出
    # 等待队列：先入先出的时间片调度 20s
    # 定义一个字典，将风扇速度的字符串映射为相应的整数值
    speed_mapping = {'high': 3, 'medium': 2, 'low': 1}

    if(len(service_queue)==3):
        for room in service_queue:
            for wait in waiting_queue:
                if room.server_time>=20 and speed_mapping[room.fan_speed] == speed_mapping[wait.fan_speed]:
                    temp=room
                    service_queue.remove(temp)
                    waiting_queue.append(temp)
                    temp.status='WAITING'
                    db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
                    db_room.status='WAITING'

                    temp = wait
                    waiting_queue.remove(temp)
                    service_queue.append(temp)
                    temp.status='SERVING'
                    db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
                    db_room.status='SERVING'
                    db.commit()
                    break

def schedule(db):
    # 服务队列：先按风速排序，风速相同的情况先入先出
    # 等待队列：先入先出的时间片调度

    temp_queue=service_queue.copy()

    priority_scheduling(db)
    time_slicing(db)
    priority_scheduling(db)

    for temp in temp_queue:
        if temp.status=='WAITING':
            # 结束一个详单
            db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == temp.record_id).first()
            db_record.end_time=datetime.now()
            db_record.duration=(datetime.now()-db_record.start_time).seconds
            db_record.current_cost=temp.total_cost-db_record.current_cost
            db.commit()
            # 新建一个详单
            db_record = models.ServiceRecord(room_id=temp.room_id, request_time=datetime.now(), fan_speed=temp.fan_speed,current_cost=temp.total_cost)
            db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
            db_room.server_time=0;
            temp.server_time=0;
            db.add(db_record)
            db.commit()
            db_room.record_id=db_record.record_id
            temp.record_id=db_record.record_id
            db.commit()
    for service in service_queue:
        service.server_time+=10
        db_room = db.query(models.Room).filter(models.Room.room_id == service.room_id).first()
        db_room.server_time+=10
        db.commit()
        if service not in temp_queue:
            # 更新一个详单
            db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == service.record_id).first()
            db_record.start_time=datetime.now()
            db.commit()

    timer = threading.Timer(10, schedule,args=(db,))  # 每10s执行一次调度函数
    timer.start()

# 遍历所有房间，计算费用
def calculate_cost(db):
    for room in room_queue:
        db_room = db.query(models.Room).filter(models.Room.room_id == room.room_id).first()
        if room.status=='SERVING':
            if room.fan_speed=='high':
                room.total_cost+=0.1
                room.current_temperature-=0.1
                db_room.current_temperature-=0.1
                db_room.total_cost+=0.1
            elif room.fan_speed=='medium':
                room.total_cost+=0.05
                room.current_temperature-=0.05
                db_room.current_temperature-=0.05
                db_room.total_cost+=0.05
            else:
                room.total_cost+=1/30
                room.current_temperature-=1/30
                db_room.current_temperature-=1/30
                db_room.total_cost+=1/30
            if room.current_temperature<=room.target_temperature:
                room.current_temperature=room.target_temperature
                room.total_cost-=room.target_temperature-room.current_temperature
                room.status='SLEEPING'
                db_room.status='SLEEPING'
                db_room.total_cost-=room.target_temperature-room.current_temperature
                db_room.current_temperature=room.target_temperature
            
                service_queue.remove(room)
                # 结束一个详单
                db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == room.record_id).first()
                db_record.end_time=datetime.now()
                db_record.duration=(datetime.now()-db_record.start_time).seconds
                db_record.current_cost=room.total_cost-db_record.current_cost
            db.commit()
        elif room.status=='SLEEPING':
            if room.current_temperature<room.target_temperature+1:
                room.current_temperature+=0.05
                db_room.current_temperature+=0.05
                db.commit()
            elif room.current_temperature>=room.target_temperature+1:
                if len(service_queue)<3:
                    service_queue.append(room)
                    room.status='SERVING'
                    db_room.status='SERVING'
                    # 新建一个详单
                    db_record = models.ServiceRecord(room_id=room.room_id, request_time=datetime.now(),start_time=datetime.now(),fan_speed=room.fan_speed,current_cost=room.total_cost)
                    #写入数据库
                    db.add(db_record)
                    db.commit()
                    db_room.record_id=db_record.record_id
                    room.record_id=db_record.record_id
                    db.commit()
                else:
                    waiting_queue.append(room)
                    room.status='WAITING'
                    db_room.status='WAITING'
                    # 新建一个详单
                    db_record = models.ServiceRecord(room_id=room.room_id, request_time=datetime.now(), fan_speed=room.fan_speed,current_cost=room.total_cost)
                    #写入数据库
                    db.add(db_record)
                    db.commit()
                    db_room.record_id=db_record.record_id
                    room.record_id=db_record.record_id
                    db.commit()
            elif room.status=='SHUTDOWN':
                if(room.current_temperature>room.initial_temperature):
                    room.current_temperature-=0.05
                    db_room.current_temperature-=0.05
                    if(room.current_temperature<room.initial_temperature):
                        room.current_temperature=room.initial_temperature
                        db_room.current_temperature=room.initial_temperature
                db.commit()
    timer=threading.Timer(1,calculate_cost,args=(db,))
    timer.start()

@router.get("/poweron")
def poweron(db: Session = Depends(get_db)):
    schedule(db)
    calculate_cost(db)
    return {"msg": "开机成功"}


# 开机请求
@router.post("/request_on")
def request_on(room_id: int,db: Session = Depends(get_db)):
    flag=1
    for room in room_queue:
        if room.room_id==room_id:
            # 新建一个详单
            db_record = models.ServiceRecord(room_id=room_id, request_time=datetime.now(), fan_speed=room.fan_speed,current_cost=room.total_cost)
            db_room=db.query(models.Room).filter(models.Room.room_id == room_id).first()
            flag=0
            if len(service_queue)<3:
                service_queue.append(room)
                room.status='SERVING'
                db_room.status='SERVING'
                db_record.start_time=datetime.now()
            else:
                waiting_queue.append(room)
                room.status='WAITING'
                db_room.status='WAITING'
            #写入数据库
            db.add(db_record)
            db.commit()
            db_room.record_id=db_record.record_id
            room.record_id=db_record.record_id
            db.commit()
    if flag==1:
        db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
        room_data=RoomData(db_room)
        room_queue.append(room_data)
        # 新建一个详单
        db_record = models.ServiceRecord(room_id=room_id, request_time=datetime.now(), fan_speed=db_room.fan_speed,current_cost=db_room.total_cost)
        if len(service_queue)<3:
            service_queue.append(room_data)
            db_room.status='SERVING'
            room_data.status='SERVING'
            db_record.start_time=datetime.now()
        else:
            waiting_queue.append(room_data)
            db_room.status='WAITING'
            room_data.status='WAITING'
        #写入数据库
        db.add(db_record)
        db.commit()
        db_room.record_id=db_record.record_id
        room_data.record_id=db_record.record_id
        db.commit()
    return {"msg": "开机成功"}
        
# 关机请求
@router.post("/request_off")
def request_off(room_id: int,db: Session = Depends(get_db)):
    for room in room_queue:
        if room.room_id==room_id:
            db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()

            room.current_temperature=room.initial_temperature
            db_room.current_temperature=room.initial_temperature

            if room.status=='SERVING':
                room.status='SHUTDOWN'
                db_room.status='SHUTDOWN'
                service_queue.remove(room)
            elif room.status=='WAITING':
                room.status='SHUTDOWN'
                db_room.status='SHUTDOWN'
                waiting_queue.remove(room)
            else:
                room.status='SHUTDOWN'
                db_room.status='SHUTDOWN'
            
            # 结束一个详单
            db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == room.record_id).first()
            db_record.end_time=datetime.now()
            db_record.duration=(datetime.now()-db_record.start_time).seconds
            db_record.current_cost=room.total_cost-db_record.current_cost
            #写入数据库
            db.add(db_record)
            db.commit()
    return {"msg": "关机成功"}

# 调整温度请求
@router.post("/request_temp")
def request_temp(room_id: int, target_temperature: float,db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    db_room.target_temperature = target_temperature
    db.commit()
    for room in room_queue:
        if room.room_id==room_id:
            room.target_temperature=target_temperature
            break
    return {"msg": "修改成功"}

# 调整风速请求
@router.post("/request_speed")
def request_speed(room_id: int, fan_speed: str,db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    db_room.fan_speed = fan_speed
    db.commit()
    for room in room_queue:
        if room.room_id==room_id:
            room.fan_speed=fan_speed
            if room.status=='SERVING':
                # 结束一个详单
                db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == room.record_id).first()
                db_record.end_time=datetime.now()
                db_record.duration=(datetime.now()-db_record.start_time).seconds
                db_record.current_cost=room.total_cost-db_record.current_cost
                #写入数据库
                db.add(db_record)
                db.commit()
                # 新建一个详单
                db_record = models.ServiceRecord(room_id=room.room_id, request_time=datetime.now(),start_time=datetime.now(),fan_speed=room.fan_speed,current_cost=room.total_cost)
                #写入数据库
                db.add(db_record)
                db.commit()
                db_room.record_id=db_record.record_id
                room.record_id=db_record.record_id
                db.commit()
            if room.status=='WAITING':
                # 更新一个详单
                db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == room.record_id).first()
                db_record.fan_speed=fan_speed
                #写入数据库
                db.commit()
            break
    return {"msg": "修改成功"}

# 返回当前队列信息
@router.get("/show")
def show(db: Session = Depends(get_db)):
    # 返回房间id
    service_id_list=[]
    for room in service_queue:
        service_id_list.append(room.room_id)
    # 返回房间id
    waiting_id_list=[]
    for room in waiting_queue:
        waiting_id_list.append(room.room_id)
    
    return service_id_list,waiting_id_list

'''
def schedule(self,db: Session = Depends(get_db)):
    # 服务队列：先按风速排序，风速相同的情况先入先出
    # 等待队列：先入先出的时间片调度

    priority_scheduling()
    if len(waiting_queue) != 0 and len(service_queue) == 3:
        temp = service_queue[0]
        temp.status='WAITING'
        service_queue.remove(temp)
        waiting_queue.append(temp)

        # 结束一个详单
        db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == temp.record_id).first()
        db_record.end_time=datetime.now()
        db_record.duration=(db_record.end_time-db_record.start_time).seconds
        db_record.current_cost=temp.total_cost-db_record.current_cost
        db.commit()

        # 新建一个详单
        db_record = models.ServiceRecord(room_id=temp.room_id, request_time=datetime.now(), fan_speed=temp.fan_speed,current_cost=temp.total_cost)
        db_room=db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
        db_room.record_id=db_record.record_id
        temp.record_id=db_record.record_id
        db_room.status='WAITING'
        # 写入数据库
        db.add(db_record)
        db.commit()

        temp = waiting_queue[0]
        temp.status='SERVING'
        waiting_queue.remove(temp)
        service_queue.append(temp)

        db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
        db_room.status='SERVING'

        # 更新一个详单
        db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == temp.record_id).first()
        db_record.start_time=datetime.now()
        db.commit()

    elif len(waiting_queue) != 0 and len(service_queue) == 2:
        temp = waiting_queue[0]
        temp.status='SERVING'
        waiting_queue.remove(temp)
        service_queue.append(temp)
        # 更新一个详单
        db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == temp.record_id).first()
        db_record.start_time=datetime.now()
        db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
        db_room.status='SERVING'
        db.commit()

    elif len(waiting_queue) != 0 and len(service_queue) <= 1:
        for temp in waiting_queue:
                temp.status='SERVING'
                waiting_queue.remove(temp)
                service_queue.append(temp)
                # 更新一个详单
                db_record = db.query(models.ServiceRecord).filter(models.ServiceRecord.record_id == temp.record_id).first()
                db_record.start_time=datetime.now()
                db_room = db.query(models.Room).filter(models.Room.room_id == temp.room_id).first()
                db_room.status='SERVING'
                db.commit()
    
    priority_scheduling()
    timer = threading.Timer(20, self.schedule)  # 每20s执行一次调度函数
    timer.start()
'''