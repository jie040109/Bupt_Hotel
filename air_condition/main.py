from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import (
   api_mange,api_user,api_air
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

app.include_router(api_mange.router)
app.include_router(api_air.router)
app.include_router(api_user.router)

    

