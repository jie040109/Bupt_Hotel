from fastapi import FastAPI
from routers import (
   admin,user,schedule
)

app = FastAPI()

app.include_router(admin.router)
app.include_router(user.router)
app.include_router(schedule.router)

    

