import sqlite3
import datetime
import logging
import json
import os

import pydantic_core

from middleware.data_validator import *
import time
import pytz
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from middleware.data_validator import *
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
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String)
    comment_qua = Column(Integer, default=0)
    comments_blocked = Column(Integer, default=0)
    hashtags = Column(String, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
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
    def __init__(self, manager: DatabaseLauncher, pattern: BasePattern() = BasePattern):
        self.__path = Path(manager.path)
        self.engine = manager.engine
        self.pattern = pattern
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def format_datetime(self, dt):
        local_tz = pytz.timezone('Europe/Kyiv')
        local_dt = dt.astimezone(local_tz)
        return local_dt.strftime("%Y-%m-%d %H:%M")

    def EXECUTE(self, method="GET", values: dict = {}, idc=None, values_for_return=[]):
        session = self.SessionLocal()
        status_code = 200
        res = {}
        if method == "GET":
            status_code, res = self.GET(session, idc, values, status_code, values_for_return)
        elif method == "POST":
            status_code = self.ADD(session, values, status_code)
        elif method == "PUT":
            res = self.UPDATE(session, values, idc)
        elif method == "PATCH":
            res = self.PATCH(session, idc)
        elif method == "DELETE":
            res = self.DELETE(session, idc)

        else:
            status_code = 404

        logging.info("Session close...")
        session.close()

        result = {"status_code": status_code}
        if res:
            result["result"] = res
        return result

    def GET(self, session, idc, values, status_code, values_for_return):
        logging.info("SESSION: GET")
        return status_code, None

    def ADD(self, session, values, status_code):
        logging.info("SESSION: POST")

    def UPDATE(self, session, values, idc):
        logging.info("SESSION: UPDATE")

    def PATCH(self, session, idc):
        logging.info("SESSION: PATCH")

    def DELETE(self, session, idc):
        logging.info("SESSION: DELETE")


class UserManager(DatabaseManager):

    def __init__(self, manager: DatabaseLauncher):
        super().__init__(manager, pattern=UserV)

    def GET(self, session, user_id, values, status_code, values_for_return=[]):
        res = {}
        status_code = 200
        if user_id:
            user = session.query(Users).filter(Users.id == user_id).first()
            if user:
                res = {  # json.dumps({
                    "id": user.id,
                    "name": user.name,
                    ""
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
        try:
            self.pattern(name=values["name"], email=values["email"], password=values["password"])
            super().ADD(session, values, status_code)
            new_task = Users(**values)
            session.add(new_task)
            session.commit()
            return status_code
        except Exception as ex:
            raise pydantic_core.ValidationError

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
        super().GET(session, post_id, values, status_code, values_for_return)
        res = {}
        status_code = 200
        if post_id:
            posts = session.query(Posts).filter(Posts.id == post_id).all()
            if posts:
                res = [{  # json.dumps({
                    "id": post.id,
                    "user_id": post.user_id,
                    "title": post.title,
                    "content": post.content,
                    "comment_qua": post.comment_qua,
                    "comments_blocked": int(post.comments_blocked),
                    "created_at": self.format_datetime(post.created_at),
                } for post in posts]  # , indent=4)

            else:
                status_code = 404

        elif values:
            posts = session.query(Posts).filter_by(**values).all()
            if posts:
                res = [{  # json.dumps({
                "id": post.id,
                "user_id": post.user_id,
                "title": post.title,
                "content": post.content,
                "comment_qua": post.comment_qua,
                "comments_blocked": int(post.comments_blocked),
                "created_at": self.format_datetime(post.created_at),
            } for post in posts]  # , indent=4)

                if res:
                    status_code = 402
                else:
                    status_code = 404
            else:
                status_code = 404
        else:
            posts = session.query(Posts).all()
            res = [{  # json.dumps({
                "id": post.id,
                "user_id": post.user_id,
                "title": post.title,
                "content": post.content,
                "comment_qua": post.comment_qua,
                "comments_blocked": int(post.comments_blocked),
                "created_at": self.format_datetime(post.created_at),
            } for post in posts]  # , indent=4)

        return status_code, res

    def ADD(self, session, values, status_code):
        try:
            self.pattern(user_id=values["user_id"], content=values["content"], title=["title"])
            super().ADD(session, values, status_code)
            new_task = Posts(**values)
            session.add(new_task)
            session.commit()
            return status_code

        except pydantic_core.ValidationError:
            raise pydantic_core.ValidationError()

    def UPDATE(self, session, values, post_id):
        super().UPDATE(session, values, post_id)
        posts = session.query(Posts).filter(Posts.id == post_id).first()
        comments = session.query(Comments).filter(Comments.id == int(post_id)).all()
        if posts:
            for key, value in values.items():
                setattr(posts, key, value)
        posts.comment_qua = len(comments)
        logging.info(f"COMMENTS: {len(comments)}")
        session.commit()

    def PATCH(self, session, post_id):
        super().PATCH(session, post_id)
        posts = session.query(Posts).filter(Posts.id == post_id).first()
        if posts:
            posts.comments_blocked += 1
        session.commit()

    def DELETE(self, session, post_id):
        super().DELETE(session, post_id)
        task = session.query(Posts).filter(Posts.id == post_id).first()
        if task:
            session.delete(task)
            session.commit()
            # res = json.dumps({"message": f"Task with id {task_id} deleted."}, indent=4)


class CommentManager(DatabaseManager):
    def __init__(self, manager: DatabaseLauncher):
        super().__init__(manager)

    def GET(self, session, comment_id, values, status_code, values_for_return=None):
        super().GET(session, comment_id, values, status_code, values_for_return)
        res = {}
        status_code = 200
        if comment_id:
            comment = session.query(Comments).filter(Comments.id == comment_id).first()
            if comment:
                res = {  # json.dumps({
                    "user_id": comment.user_id,
                    "post_id": comment.post_id,
                    "content": comment.content,
                    "created_at": self.format_datetime(comment.created_at),
                }  # , indent=4)

            else:
                status_code = 404

        elif values:
            comment = session.query(Comments).filter_by(**values).first()
            if comment:
                res = {  # json.dumps({
                    "user_id": comment.user_id,
                    "post_id": comment.post_id,
                    "content": comment.content,
                    "created_at": self.format_datetime(comment.created_at),
                }  # , indent=4)

                if comment:
                    status_code = 402
                else:
                    status_code = 404
            else:
                status_code = 404
        else:
            comments = session.query(Comments).all()
            res = [{  # json.dumps({
                "id": comment.id,
                "user_id": comment.user_id,
                "post_id": comment.post_id,
                "content": comment.content,
                "created_at": self.format_datetime(comment.created_at),
            } for comment in comments]  # , indent=4)

        return status_code, res

    def ADD(self, session, values, status_code):
        super().ADD(session, values, status_code)

        self.pattern(user_id=values['user_id'], post_id=values['post_id'],
                     content=values['content'])

        new_comment = Comments(**values)
        session.add(new_comment)
        session.commit()
        return status_code

    def UPDATE(self, session, values, comment_id):
        super().UPDATE(session, values, comment_id)
        task = session.query(Comments).filter(Comments.id == comment_id).first()
        if task:
            for key, value in values.items():
                setattr(task, key, value)
            task.updated_at = datetime.datetime.utcnow()
        session.commit()

    def PATCH(self, session, comment_id):
        super().PATCH(session, comment_id)

    def DELETE(self, session, comment_id):
        logging.info(f"Comment ID: {comment_id}")
        super().DELETE(session, comment_id)
        comment = session.query(Comments).filter(Comments.id == comment_id).first()
        if comment:
            session.delete(comment)
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
    # result = posts_db.EXECUTE("POST", values=data)
    print(user_db.EXECUTE())
