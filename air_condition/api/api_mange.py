# 管理员模块
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sql_app import models
from sql_app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])

admin_password = "admin"

# 管理员登录
@router.post("/login")
def admin_login(password: str):
    if password == admin_password:
        return {"msg": "登录成功"}
    else:
        raise HTTPException(status_code=400, detail="密码错误")
    
# 管理员获取所有房间信息
@router.get("/rooms")
def get_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).all()

# 管理员获取特定房间信息
@router.get("/rooms/")
def get_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=400, detail="房间不存在")
    return [db_room]

# 管理员修改房间信息(房间目标温度、风速、状态)
@router.post("/modify")
def update_room(room_id: int, target_temperatuer:float,fan_speed:str,status:str, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=400, detail="房间不存在")
    db_room.target_temperature = target_temperatuer
    db_room.fan_speed = fan_speed
    db_room.status = status
    db.commit()
    return {"msg": "修改成功"}

# 管理员获取特定房间的所有详单
@router.get("/records/{room_id}")
def get_records(room_id: int, db: Session = Depends(get_db)):
    return db.query(models.ServiceRecord).filter(models.ServiceRecord.room_id == room_id).all()

# 管理员获取特定房间的账单
@router.get("/bills/{room_id}")
def get_bills(room_id: int, db: Session = Depends(get_db)):
    return db.query(models.Bill).filter(models.Bill.room_id == room_id).order_by(models.Bill.bill_id.desc()).first()

# 管理员创建房间(房间号、身份证号、初始温度)，同时创建账单
@router.post("/create")
def create_room(room_id: int, identity_card: str, initial_temperature: float, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is not None:
        raise HTTPException(status_code=400, detail="房间已存在")
    db_room = models.Room(room_id=room_id, identity_card=identity_card, initial_temperature=initial_temperature)
    db.add(db_room)
    db_bill = models.Bill(room_id=room_id,checkin_time=datetime.now(),total_cost=db_room.total_cost)
    db.add(db_bill)
    db_room.current_temperature = initial_temperature
    db.commit()
    return {"msg": "创建成功"}

# 管理员删除房间,同时修改账单
@router.delete("/delete")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=400, detail="房间不存在")
    db.delete(db_room)
    # 返回最后一个账单
    db_bill = db.query(models.Bill).filter(models.Bill.room_id == room_id).order_by(models.Bill.bill_id.desc()).first()
    db_bill.checkout_time = datetime.now()
    db_bill.total_cost = db_room.total_cost
    db.commit()
    return {"msg": "删除成功"}


