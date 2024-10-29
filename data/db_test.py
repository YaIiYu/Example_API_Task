import sqlite3
import datetime
import logging
import json
import os
import time

import pytz
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    logged = Column(Boolean, default=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String)
    hashtags = Column(String, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class DatabaseLauncher():

    def __init__(self):
        logging.info(f"DB Path... {os.path.join('A://PythonBots//Projects//STR_JUN_Task//', 'data//database.db')}")
        self.path = Path(os.path.join('A://PythonBots//Projects//STR_JUN_Task//', 'data//database.db'))
        print(os.path.join(os.getcwd(), 'data'))
        self.engine = create_engine(f"sqlite:///{self.path}", connect_args={"check_same_thread": False})
        if not self.path.exists():
            self.CREATE_TABLE()

    def CREATE_TABLE(self):
        logging.info("Creating database...")
        Base.metadata.create_all(bind=self.engine)


class DatabaseManager():
    def __init__(self, manager: DatabaseLauncher):
        self.__path = Path(manager.path)
        self.engine = manager.engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def format_datetime(self, dt):
        local_tz = pytz.timezone('Europe/Kyiv')
        local_dt = dt.astimezone(local_tz)
        return local_dt.strftime("%Y-%m-%d %H:%M")

    def EXECUTE(self, method="GET", values: dict = {}, user_id=None, values_for_return=[]):
        session = self.SessionLocal()
        status_code = 200
        res = {}
        if method == "GET":
            status_code, res = self.GET(session, user_id, values, status_code, values_for_return)
        elif method == "POST":
            status_code = self.ADD(session, values, status_code)
        elif method == "PUT":
            res = self.UPDATE(session, values, user_id)
        elif method == "PATCH":
            res = self.PATCH(session, user_id)
        elif method == "DELETE":
            res = self.DELETE(session, user_id)

        else:
            status_code = 400

        logging.info("Session close...")
        session.close()

        result = {"status_code": status_code}
        if res:
            result["result"] = res
        return result

    def GET(self, session, user_id, values, status_code, values_for_return):
        logging.info("SESSION: GET")
        return status_code, None

    def ADD(self, session, values, status_code):
        logging.info("SESSION: POST")

    def UPDATE(self, session, values, user_id):
        logging.info("SESSION: UPDATE")

    def PATCH(self, session, user_id):
        logging.info("SESSION: PATCH")

    def DELETE(self, session, user_id):
        logging.info("SESSION: DELETE")


class UserManager(DatabaseManager):

    def __init__(self, manager: DatabaseLauncher):
        super().__init__(manager)

    def GET(self, session, user_id, values, status_code):
        super().GET(session, user_id, values, status_code)
        res = {}
        status_code = 200
        if user_id:
            user = session.query(Users).filter(Users.id == user_id).first()
            if user:
                res = {  # json.dumps({
                    "id": user.id,
                    "name": user.name,
                    "created_at": self.format_datetime(user.created_at),
                }  # , indent=4)
            else:
                status_code = 404

        elif values:
            user = session.query(Users).filter_by(**values).first()
            if user:
                res = {  # json.dumps({
                    "id": user.id,
                    "name": user.name,
                    "created_at": self.format_datetime(user.created_at),
                }  # , indent=4)
            elif len(values) > 1 and 'email' in values:
                user = session.query(Users).filter(Users.email == values['email']).first()
                if user:
                    status_code = 402
                else:
                    status_code = 404
            else:
                status_code = 404
        else:
            users = session.query(Users).all()
            res = [{  # json.dumps([{
                "id": user.id,
                "name": user.name,
                "created_at": self.format_datetime(user.created_at),
            } for user in users]  # , indent=4)

        return status_code, res

    def ADD(self, session, values, status_code):
        super().ADD(session, values, status_code)
        new_task = Users(**values)
        session.add(new_task)
        session.commit()
        return status_code

    def UPDATE(self, session, values, user_id):
        super().UPDATE(session, values, user_id)
        task = session.query(Posts).filter(Posts.id == user_id).first()
        if task:
            for key, value in values.items():
                setattr(task, key, value)
            task.updated_at = datetime.datetime.utcnow()
        session.commit()

    def PATCH(self, session, user_id):
        super().PATCH(session, user_id)
        task = session.query(Posts).filter(Posts.id == user_id).first()
        if task:
            task.completed = 1
            task.updated_at = datetime.datetime.utcnow()
        session.commit()

    def DELETE(self, session, user_id):
        super().DELETE(session, user_id)
        task = session.query(Posts).filter(Posts.id == user_id).first()
        if task:
            session.delete(task)
            session.commit()
            # res = json.dumps({"message": f"Task with id {task_id} deleted."}, indent=4)


class PostManager(DatabaseManager):
    def __init__(self, manager: DatabaseLauncher):
        super().__init__(manager)

    def GET(self, session, post_id, values, status_code, values_for_return: tuple):
        super().GET(session, post_id, values, status_code)
        res = {}
        status_code = 200
        if post_id:
            post = session.query(Posts).filter(Posts.id == post_id).first()
            if post:
                res = {  # json.dumps({
                    "user_id": post.user_id,
                    "title": post.title,
                    "content": post.content,
                    "created_at": self.format_datetime(post.created_at),
                }  # , indent=4)

            else:
                status_code = 404

        elif values:
            post = session.query(Posts).filter_by(**values).first()
            if post:
                res = {  # json.dumps({
                    "user_id": post.user_id,
                    "title": post.title,
                    "content": post.content,
                    "created_at": self.format_datetime(post.created_at),
                }  # , indent=4)

                if post:
                    status_code = 402
                else:
                    status_code = 404
            else:
                status_code = 404
        else:
            posts = session.query(Posts).all()
            res = [{  # json.dumps({
                "user_id": post.user_id,
                "title": post.title,
                "content": post.content,
                "created_at": self.format_datetime(post.created_at),
            } for post in posts]  # , indent=4)


        return status_code, res

    def ADD(self, session, values, status_code):
        super().ADD(session, values, status_code)
        new_task = Posts(**values)
        session.add(new_task)
        session.commit()
        return status_code

    def UPDATE(self, session, values, user_id):
        super().UPDATE(session, values, user_id)
        task = session.query(Posts).filter(Posts.id == user_id).first()
        if task:
            for key, value in values.items():
                setattr(task, key, value)
            task.updated_at = datetime.datetime.utcnow()
        session.commit()

    def PATCH(self, session, user_id):
        super().PATCH(session, user_id)
        task = session.query(Posts).filter(Posts.id == user_id).first()
        if task:
            task.completed = 1
            task.updated_at = datetime.datetime.utcnow()
        session.commit()

    def DELETE(self, session, user_id):
        super().DELETE(session, user_id)
        task = session.query(Posts).filter(Posts.id == user_id).first()
        if task:
            session.delete(task)
            session.commit()
            # res = json.dumps({"message": f"Task with id {task_id} deleted."}, indent=4)




if __name__ == "__main__":
    launcher = DatabaseLauncher()
    db = DatabaseManager(launcher)
    user_db = UserManager(launcher)
    posts_db = PostManager(launcher)
    data = {
        "user_id": 2,
        "title": "What is Lorem Ipsum?",
        "content": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
    }
    result = posts_db.EXECUTE("POST", values=data)
    print(posts_db.EXECUTE())
