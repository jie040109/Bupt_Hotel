#客户模块
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sql_app import models
from sql_app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/user", tags=["user"])
 
# 客户登录
@router.post("/login")
def user_login(room_id:int,identity_card: str, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=400, detail="房间不存在")
    if db_room.identity_card != identity_card:
        raise HTTPException(status_code=400, detail="密码错误")
    return {"msg": "登录成功"}

#显示当前房间温度，风速，花费
@router.get("/show/{room_id}")
def show(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=400, detail="房间不存在")
    return {"current_temperature": db_room.current_temperature,'fan_speed':db_room.fan_speed,'total_cost':db_room.total_cost}

