from flask import Flask, request, jsonify, make_response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
# from database import *
import jwt
import datetime
from  flaskext.mysql import MySQL
from  functools import wraps

app = Flask(__name__)

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'walter'
app.config['MYSQL_DATABASE_PASSWORD'] = 'walter'
app.config['MYSQL_DATABASE_DB'] = 'flask_apis'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config["SECRET_KEY"] = "super_secret_key"

mysql.init_app(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print(token)
        if not token:
            return jsonify({'message': 'Token is missing!!!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE public_id=%s", (data['public_id'],))
            user = cursor.fetchone()
        except:
            return jsonify({'message': 'Invalid token!!!'}), 401
        return f(user, *args, **kwargs)

    return decorated


# prettyprinted.com
@app.route('/user', methods=["GET"])
@token_required
def get_all_users(user):
    if user[1] != 1:
        return jsonify({'message': 'You are not allowed to perform this action'})

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    user_data = []
    for user in data:
        person = {}
        person["public_id"] = user[1]
        person["names"] = user[0]
        person["admin"] = user[2]
        person["password"] = user[3]
        user_data.append(person)
    return jsonify({"users": user_data})


@app.route('/user/<user_id>', methods=["GET"])
@token_required
def get_one_user(user, user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE public_id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": "User Not Found"})
    person = {}
    print(user)
    person["public_id"] = user[1]
    person["names"] = user[2]
    person["admin"] = user[4]
    person["password"] = user[3]
    return jsonify(person)


@app.route('/user', methods=["POST"])
@token_required
def create_user(user):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    public_id = str(uuid.uuid4())
    names = data["names"]
    admin = False
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO `users`(`public_id`, `names`, `password`, `admin`) VALUES (%s,%s,%s,%s)",
                   (public_id, names, hashed_password, admin))
    conn.commit()
    return jsonify({'message': 'New User created!'})


@app.route('/user/<user_id>', methods=["PUT"])
@token_required
def promote_user(user, user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("update users set admin=1 where public_id=%s", (user_id,))
    conn.commit()
    return jsonify({'message': 'user updated'})


@app.route('/user/<user_id>', methods=["DELETE"])
@token_required
def delete_user(user, user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("delete from users where public_id=%s", (user_id,))
    conn.commit()
    return jsonify({'message': 'user deleted'})


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!!!'})
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE names=%s", (auth.username,))
    user = cursor.fetchone()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!!!'})

    if check_password_hash(user[3], auth.password):
        token = jwt.encode({'public_id': user[1], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required!!!'})


@app.route('/todos', methods=['GET'])
@token_required
def get_all_todos(user):
    user_id = user[0]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('select * from tasks where user_id=%s', (user_id,))
    todos = cursor.fetchall()
    all_todos = []
    for item in todos:
        one = {}
        one['id'] = item[0]
        one['title'] = item[1]
        one['complete'] = item[2]
        all_todos.append(one)
    return jsonify({'todos': all_todos})


@app.route('/todos/<todo_id>', methods=['GET'])
@token_required
def get_one_todos(user, todo_id):
    user_id = user[0]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('select * from tasks where user_id=%s AND id=%s', (user_id, todo_id))
    todos = cursor.fetchone()
    if not todos:
        return jsonify({'message': 'No Todo found with your given info'})
    item = {'id': todos[0], 'title': todos[1], 'complete': todos[2]}
    return jsonify({'todo': item})


@app.route('/todos', methods=['POST'])
@token_required
def create_todo(user):
    user_id = user[0]
    data = request.get_json()
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('insert into tasks(title, complete, user_id) VALUES (%s,%s,%s)', (data["title"], 0, user_id))
    conn.commit()
    return jsonify({'status': 'created'})


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(user, todo_id):
    user_id = user[0]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('delete from tasks where id=%s and user_id=%s', (todo_id, user_id))
    conn.commit()
    return jsonify({'status': 'deleted'})


@app.route('/todos/<todo_id>', methods=['PUT'])
@token_required
def update_todo(user, todo_id):
    user_id = user[0]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('update tasks set complete=1 where id=%s and user_id=%s', (todo_id, user_id))
    conn.commit()
    return jsonify({'status': 'Updated'})

if __name__ == '__main__':
    app.run(debug=True)
