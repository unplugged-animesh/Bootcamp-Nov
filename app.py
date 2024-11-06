from sqlalchemy import or_
from flask import Flask
from Models.model import *


app=Flask(__name__)
app.config['SECRET_KEY']='East'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///gs_store.sqlite3'
app.config['SQLALCHMEY_TRACK_MODIFICATIONS']=False

db.init_app(app)


#before_first_request:
#db.create_all()

with app.app_context():
    db.create_all()