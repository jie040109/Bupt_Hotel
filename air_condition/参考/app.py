from flask import Flask
from extension import db
from model import room,scheduler,server,servering_queue,waiting_queue,statistic_controller

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

if __name__=='__main__':
    app.run(debug=True)
