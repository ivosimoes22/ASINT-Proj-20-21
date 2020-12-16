import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

import datetime
from sqlalchemy.orm import sessionmaker
from os import path

from flask import Flask
from flask import jsonify
from flask import request


app = Flask(__name__)


#SLQ access layer initialization
DATABASE_FILE = "db_users.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    id = Column(String, primary_key=True)
    name = Column(String)
    views = Column(Integer, default=0)

    def __repr__(self):
        return "<User (id=%s, name=%s>, views=%d)" % (self.id, self.name, self.views)

    def to_dict(self):
        return {"user_id": self.id, "name": self.name, 'views': self.views}


Base.metadata.create_all(engine) #Create tables for the data models
db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)
#session = Session()

#Functions related with the db
def listUsers():
    return db_session.query(User).all()

def listUsersDict():
    users = []
    userList = listUsers()
    for user in userList:
        u = user.to_dict()
        users.append(u)
    return users

def getUserDB(user_id):
    user = db_session.query(User).filter(User.id==user_id).first()
    return user.to_dict()


def addNewUserDB(user_id, name):
    newUser = User(id=user_id,name=name)
    try:
        db_session.add(newUser)
        db_session.commit()
        #db_session.close()
        return newUser.id
    except:
        db_session.rollback()
        return None

def newView(id):
    v = db_session.query(User).filter(User.id==id).first()
    v.views +=1
    n_view = v.views
    db_session.commit()
    db_session.close()
    print(listUsers())
    return n_view

@app.route('/user/add', methods=['POST'] )
def addNewUser():
    try:
        if addNewUserDB(request.form["id"], request.form["name"]) is not None:
            print("New User added to the Database")
        else:
            print("User Already in")
            print(listUsersDict())
    except:
        print("Error adding to user DB")
    return jsonify()       

@app.route('/user/get/', methods=["GET"])
def getUser():
    user = {}
    try:
        user_id = request.args.get('id')
        print(user_id)
        user = getUserDB(user_id)
    except:
        print("Error accessing the DB")
    return jsonify(user)
    

@app.route('/user/view/add/', methods=["PUT"])
def addNewView():
    user_id = request.args.get('id')
    
    try:
        return {"views": newView(user_id)}
    except:
        print("Error")
        return jsonify()


if __name__ == '__main__':
    app.run(debug=True, port=4700)