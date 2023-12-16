from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
   admin,user,schedule
)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3100"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(user.router)
app.include_router(schedule.router)

    

