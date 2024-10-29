import pydantic_core
import requests.cookies
from flask import *
import middleware.profanity_check as profanity_check
from middleware.profanity_check import ProfanityException
import logging
import middleware.date_converter as date_converter
from data.db import *
from werkzeug.security import generate_password_hash, check_password_hash
import xml.etree.ElementTree as ET

launcher = DatabaseLauncher()
db = DatabaseManager(launcher)
user_db = UserManager(launcher)
posts_db = PostManager(launcher)
comments_db = CommentManager(launcher)
app = Flask(__name__)
app.debug = True
app.secret_key = 'Secret_Kkey'

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@app.route('/', methods=['GET', 'POST'])
def main_menu():
    try:
        post_data = None
        if request.method == 'POST':
            if request.form.get('action') == 'logout':
                session.clear()
                response = make_response(redirect(url_for('main_menu')))
                response.delete_cookie('id')
                return response
            elif request.form.get('action') == 'analytics':
                response = make_response(redirect(url_for('analytics')))
                if request.cookies.get("logged") is False:
                    cookie_max_age = 60 * 2
                    response.set_cookie('id', f"{request.cookies.get('id')}", max_age=cookie_max_age)
                return response

        client_id = request.cookies.get('id')
        client_data = None
        logging.info(f'Cookies: {client_id}')
        if client_id:
            logging.info(f"Cookies: {request.cookies.get('id')}")
            user_check = user_db.EXECUTE(idc=client_id)
            if user_check['status_code'] == 200:
                client_data = user_check

        posts_res = posts_db.EXECUTE()
        # logging.info(f'Post data: {posts_res["result"][0]["user_id"]}')
        if 'result' in posts_res:
            # logging.info(f'User_id_data: {user_db.EXECUTE(idc=int(posts_res["result"][0]["user_id"]))}')
            post_data = [{
                "id": int(post['id']),
                "user_id": int(post["user_id"]),
                "title": post["title"],
                "username": user_db.EXECUTE(idc=int(post['user_id']))['result']['name'],
                "content": post['content'],
                "comment_qua": post["comment_qua"],
                "created_at": date_converter.convert(post["created_at"], True)
            } for post in posts_res['result']]

        post_with_most_comments = max(post_data, key=lambda x: x["comment_qua"], default=None) if post_data else None
        # logging.info(f"User: {username}")
        commentz = comments_db.EXECUTE()['result'] if 'result' in comments_db.EXECUTE() is not None else {}

        commentz = [{**comment, "user_name": comment.get("user_name", user_db.EXECUTE(idc=comment['user_id'])['result']['name'])} for comment in commentz]
        logging.info(f"Comments: {commentz if commentz else None}")
        return render_template("/home/home.html", posts=post_data if post_data else {},
                               user=client_data['result'] if client_data and 'result' in client_data else None,
                               comments=commentz if commentz else {}, top1post=post_with_most_comments if post_with_most_comments else None)

    except RuntimeError as ex:
        return render_template("/error/error_page.html", info=ex.__str__())


@app.route('/sign_up', methods=['GET', 'POST'])  # POST-запит на створення нового юзера
def sign_up():
    status_code = 400
    resp = render_template("/auth/sign_up.html")
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            if request.form.get('remember_me') is None:
                raise KeyError()
            logged = request.form.get('remember_me').lower() == 'true'
            existing_user = user_db.EXECUTE(values={"name": name})
            data = {"name": name, "email": email, "password": password, "logged": logged}

            logging.info(f"Data: {data}")
            if 'result' in existing_user:
                flash('User with this name already exists.', 'error')
                return redirect(url_for('sign_up'))

            if {key: value for key, value in data.items() if value is None}:
                flash('One or few values was empty.', 'error')
                return redirect(url_for('sign_up'))

            result = user_db.EXECUTE("POST", values=data)

            if result['status_code'] == 200:
                session['user_name'] = name
                logging.info(f"{name} - Adding to DB")
                usr_id = user_db.EXECUTE(values={"name": name})['result']['id']
                resp = redirect(url_for('main_menu'))
                cookie_max_age = 60 * 60 * 24 * 365 * 2
                if logged is False:
                    cookie_max_age = 60 * 2
                resp.set_cookie('id', f"{usr_id}", max_age=cookie_max_age)
                resp.set_cookie('logged', str(logged), max_age=60 * 60 * 24 * 365 * 2)
                return resp
            else:
                flash('Registration failed. Please try again.', 'error')
                return redirect(url_for('sign_up')), 200
        except pydantic_core.ValidationError as ex:
            status_code = 400
            resp = render_template("/error/error_page.html", exception=status_code, info=ex.__str__().replace(
                "For further information visit https://errors.pydantic.dev/2.9/v/string_type", ""))
        except KeyError:
            status_code = 400
            resp = render_template("/error/error_page.html", exception=status_code,
                                   info=f"KeyError - 'argument missed or used wrong'")
        except AttributeError as ex:
            status_code = 400
            resp = render_template("/error/error_page.html", exception=status_code, info=f"Argument error - {ex.name}")
    return resp, status_code


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    resp = render_template("/auth/log_in.html")
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        logged = request.form.get('remember_me').lower() == 'true'
        existing_user = user_db.EXECUTE(values={"email": email, "password": password})

        if 'result' not in existing_user:
            if existing_user['status_code'] == 402:
                flash('Wrong password', 'error')
                return redirect(url_for('log_in'))
            else:
                flash('There is no user with that email', 'error')
                return redirect(url_for('log_in'))
        else:
            if existing_user['status_code'] == 200:
                resp = redirect(url_for('main_menu'))
                cookie_max_age = 60 * 60 * 24 * 365 * 2
                if logged is False:
                    cookie_max_age = 60 * 2
                # resp.set_cookie('session', session.sid)
                resp.headers.set("auth", f"Bearer {existing_user['result']['id']}")
                resp.set_cookie('id', f"{existing_user['result']['id']}", max_age=cookie_max_age)
                resp.set_cookie('logged', str(logged), max_age=60 * 60 * 24 * 365 * 2)
                return resp
    return resp

@app.route('/analytics', methods=['GET'])
def analytics():
    post_data = []
    client_data = None
    client_cookie = request.cookies.get('id')
    posts_res = posts_db.EXECUTE(values={"user_id": int(client_cookie)})
    if 'result' in posts_res:
        posts_res = [post for post in posts_res['result'] if post["user_id"] == int(client_cookie)]
    logging.info(f"posts_res: {posts_res if 'result' not in posts_res and posts_res else None}")
    # logging.info(f'Post data: {posts_res["result"][0]["user_id"]}')
    if client_cookie:
        logging.info(f"Cookies: {request.cookies.get('id')}")
        user_check = user_db.EXECUTE(idc=client_cookie)
        if user_check['status_code'] == 200:
            client_data = user_check

    # logging.info(f"User: {username}")
    commentz = comments_db.EXECUTE()['result'] if 'result' in comments_db.EXECUTE() is not None else {}

    commentz = [
        {**comment, "user_name": comment.get("user_name", user_db.EXECUTE(idc=comment['user_id'])['result']['name'])}
        for comment in commentz]

    return render_template("/home/analytics.html", posts=posts_res if 'result' not in posts_res and posts_res else {}, comments=commentz if commentz else {}, user=client_data['result'] if client_data and 'result' in client_data else None)



#БАЗОВІ API

@app.route('/posts', methods=['POST'])
def posts_ADD():
    try:
        result = None
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = int(request.form.get('user_id'))
        data = {
            "title": title,
            "user_id": user_id,
            "content": content,
        }

        if "title" in data:
            if profanity_check.check_profanity(content) and profanity_check.check_profanity(title):
                raise ProfanityException()
            result = posts_db.EXECUTE("POST", data)
            if result['status_code']== 200:
                resp = redirect(url_for('main_menu'))
                return resp
        return result

    except ProfanityException as ex:
        status_code = 400
        return render_template("/error/error_page.html", info=ex.__str__())
    except pydantic_core.ValidationError as ex:
        status_code = 400
        return render_template("/error/error_page.html", exception=status_code, info=ex.__str__().replace(
            "For further information visit https://errors.pydantic.dev/2.9/v/string_type", ""))

    except Exception as ex:
        return render_template("/error/error_page.html", info=ex)

@app.route('/posts', methods=['GET'])
def posts_GET():
    result = posts_db.EXECUTE()
    return result


@app.route('/posts/<post_id>', methods=['GET'])
def GET_POST_FROM_ID(post_id):
    result = posts_db.EXECUTE(idc=post_id)
    # print(f"Result is: {result}")
    # print(f"Result type: {type(result)}")
    return result


@app.route('/posts/<post_id>', methods=['PUT'])
def posts_UPDATE(post_id):
    result = posts_db.EXECUTE("UPDATE", values=request.json, idc=post_id)
    return result


@app.route('/posts/<post_id>', methods=['DELETE'])
def posts_DELETE(post_id):
    logging.info(f"Post_id is: {post_id}")
    post_comments = comments_db.EXECUTE()
    if post_comments['status_code'] == 200:
        for comment in post_comments['result']:
            if int(comment['post_id']) == int(post_id):
                comments_db.EXECUTE("DELETE", idc=comment['id'])
    result = posts_db.EXECUTE("DELETE", idc=post_id)

    return result


# COMMENTS

@app.route('/posts/<post_id>', methods=['POST'])
def comment_ADD(post_id):

    try:
        data = {
            "content": request.form.get('commentContent'),
            "user_id": int(request.form.get('user_id')),
            "post_id": int(post_id)
        }

        logging.info(f"COMMENT:DATA - {data}")
        result = None

        if "post_id" in data:
            if profanity_check.check_profanity(data["content"]):
                raise ProfanityException()
            result = comments_db.EXECUTE("POST", values=data)
            logging.info(f"COMMENT:POST - {result}")
            if result['status_code'] == 200:
                result2 = posts_db.EXECUTE(method="PUT", idc=post_id)
                logging.info(f"COMMENT:POST2 - {result2}")
                return redirect(url_for('main_menu'))
        return result

    except ProfanityException as ex:
        status_code = 400
        posts_db.EXECUTE(method="PATCH", idc=post_id)
        return render_template("/error/error_page.html", info=ex.__str__())

    except pydantic_core.ValidationError as ex:
        status_code = 400
        resp = render_template("/error/error_page.html", exception=status_code, info=ex.__str__().replace(
            "For further information visit https://errors.pydantic.dev/2.9/v/string_type", ""))

    except KeyError:
        status_code = 400
        resp = render_template("/error/error_page.html", exception=status_code,
                               info=f"KeyError - 'argument missed or used wrong'")

    except AttributeError as ex:
        status_code = 400
        resp = render_template("/error/error_page.html", exception=status_code, info=f"Argument error - {ex.name}")
    return resp

@app.route('/posts/<post_id>/comments', methods=['GET'])
def comments_GET(post_id):
    res = comments_db.EXECUTE(values={"post_id": post_id})
    logging.info(f"Result is: {res}")
    return res


@app.route('/posts/<post_id>/<comment_id>', methods=['GET'])
def GET_COMMENT_FROM_ID(post_id, comment_id):
    result = comments_db.EXECUTE(idc=comment_id, values={"post_id": post_id})
    logging.info(f"Result is: {result}")
    return result


@app.route('/admin/post/<post_id>', methods=['PUT'])
def UPDATE(post_id):
    result = db.EXECUTE("UPDATE", values=request.json, idc=post_id)
    return result


@app.route('/posts/<post_id>', methods=['DELETE'])
def DELETE(post_id):
    result = db.EXECUTE("DELETE", idc=post_id)
    return result
