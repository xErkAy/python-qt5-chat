import socket
import re
import time
import sqlite3
import hashlib
from threading import Thread

def getUsersOnline():
    result = "Users online:"
    for user in users_online:
        result += "|" + user
    return result

def getResult(text):
    return int(re.search(".(.*),", str(text)).group(1))

def nick_encrypt(text):
    return hashlib.sha224(hashlib.md5(hashlib.sha1(hashlib.sha384(hashlib.md5(hashlib.sha512(
        text.encode()).hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).
        hexdigest().encode()).hexdigest()

def pass_encrypt(text):
    return hashlib.md5(hashlib.sha224(hashlib.sha512(hashlib.sha1(hashlib.md5(text.encode()).
        hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).hexdigest()

def admin_encrypt(text):
    return hashlib.sha384(hashlib.sha1(hashlib.md5(hashlib.sha384(hashlib.md5(text.encode()).
        hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).hexdigest()

def banlist_encrypt(text):
    return hashlib.sha512(hashlib.sha1(hashlib.sha384(hashlib.sha384(hashlib.sha1(text.encode()).
        hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).hexdigest().encode()).hexdigest()

def addUser(username):
    with open("BanList.txt", "a") as file:
        file.write(username + "\n")

def deleteUser(username):
    text = open("BanList.txt").read()
    text = text.replace(username + "\n", "")
    with open("BanList.txt", "wt") as file:
        file.write(text)

def new_thread(new_connection):
    status = 0
    admin = 0
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    while True:
        try:
            data = new_connection.recv(1024)
            if "/adminlogin" in data.decode("utf-8"):
                if not re.search("/adminlogin (.*) (.*)", data.decode("utf-8")).group(1) == key:
                    new_connection.send(("/adminlogin 0").encode("utf-8"))
                    new_connection.close()
                    break
                else:
                    password = re.search("/adminlogin (.*) (.*)", data.decode("utf-8")).group(2)
                    cursor.execute("SELECT password FROM users WHERE password = '" + admin_encrypt(password) + "' AND nick_name = 'admin'")

                    if len(str(cursor.fetchall())) > 4:
                        new_connection.send(("/adminlogin 1").encode("utf-8"))
                        users.append(new_connection)
                        cursor.execute("SELECT id FROM users WHERE password = '" + admin_encrypt(password) + "' AND nick_name = 'admin'")
                        user_id.append(getResult(cursor.fetchall()[0]))
                        status = 1
                        admin = 1
                        break
                    else:
                        new_connection.send(("/adminlogin 0").encode("utf-8"))
                        new_connection.close()
                        break
            elif "/adminregister" in data.decode("utf-8"):
                if not re.search("/adminregister (.*) (.*)", data.decode("utf-8")).group(1) == key:
                    new_connection.send(("/adminregister 0").encode("utf-8"))
                    new_connection.close()
                    break
                else:
                    password = re.search("/adminregister (.*) (.*)", data.decode("utf-8")).group(2)
                    cursor.execute("SELECT nick_name FROM users WHERE nick_name = 'admin'")

                    if len(str(cursor.fetchall())) > 4:
                        new_connection.send(("/adminregister 0").encode("utf-8"))
                        new_connection.close()
                        break
                    else:
                        try:
                            cursor.execute("SELECT id FROM users ORDER BY ROWID DESC LIMIT 1")
                            cursor.execute("INSERT INTO users VALUES ('" + str(int(re.search(".(.*),", str(cursor.fetchall()[0])).group(1))+1) +
                                           "', 'admin', '" + admin_encrypt(password) + "')")
                        except:
                            cursor.execute("INSERT INTO users VALUES ('1', 'admin', '" + admin_encrypt(password) + "')")
                        conn.commit()
                        new_connection.send(("/adminregister 1").encode("utf-8"))
                        new_connection.close()
                        break
            elif "/auth" in data.decode("utf-8"):
                if not re.search("/auth (.*) (.*) (.*)", data.decode("utf-8")).group(1) == key:
                    new_connection.send(("/auth 0").encode("utf-8"))
                    new_connection.close()
                    break
                else:
                    nick = re.search("/auth (.*) (.*) (.*)", data.decode("utf-8")).group(2)
                    password = re.search("/auth (.*) (.*) (.*)", data.decode("utf-8")).group(3)
                    if banlist_encrypt(nick) in banlist:
                        new_connection.send(("/auth -1").encode("utf-8"))
                        new_connection.close()
                        break

                    cursor.execute("SELECT password FROM users WHERE password = '" + pass_encrypt(password) + "' AND nick_name = '" + nick_encrypt(nick) + "'")

                    if len(str(cursor.fetchall())) > 4:
                        new_connection.send(("/auth 1").encode("utf-8"))
                        users.append(new_connection)
                        cursor.execute("SELECT id FROM users WHERE password = '" + pass_encrypt(password) + "' AND nick_name = '" + nick_encrypt(nick) + "'")
                        user_id.append(getResult(cursor.fetchall()[0]))
                        status = 1
                        break
                    else:
                        new_connection.send(("/auth 0").encode("utf-8"))
                        new_connection.close()
                        break
            elif "/register" in data.decode("utf-8"):
                if not re.search("/register (.*) (.*) (.*)", data.decode("utf-8")).group(1) == key:
                    new_connection.send(("/register 0").encode("utf-8"))
                    new_connection.close()
                    break
                else:
                    nick = re.search("/register (.*) (.*) (.*)", data.decode("utf-8")).group(2)
                    password = re.search("/register (.*) (.*) (.*)", data.decode("utf-8")).group(3)
                    cursor.execute("SELECT nick_name FROM users WHERE nick_name = '" + nick_encrypt(nick) + "'")

                    if len(str(cursor.fetchall())) > 4:
                        new_connection.send(("/register 0").encode("utf-8"))
                        new_connection.close()
                        break
                    else:
                        try:
                            cursor.execute("SELECT id FROM users ORDER BY ROWID DESC LIMIT 1")
                            cursor.execute("INSERT INTO users VALUES ('" + str(int(re.search(".(.*),", str(cursor.fetchall()[0])).group(1))+1) +
                                           "', '" + nick_encrypt(nick) + "', '" + pass_encrypt(password) + "')")
                        except:
                            cursor.execute("INSERT INTO users VALUES ('1', '" + nick_encrypt(nick) + "', '" + pass_encrypt(password) + "')")
                        conn.commit()
                        new_connection.send(("/register 1").encode("utf-8"))
                        new_connection.close()
                        break
        except:
            continue

    if status:
        while True:
            try:
                data = new_connection.recv(32768)
                if admin:
                    if "/ban" in data.decode("utf-8"):
                        addUser(banlist_encrypt(re.search("/ban (.*)", data.decode("utf-8")).group(1)))
                        banlist.append(banlist_encrypt(re.search("/ban (.*)", data.decode("utf-8")).group(1)))
                        try:
                            cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/ban (.*)", data.decode("utf-8")).group(1)) + "'")
                            client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                            client.send(("/ban").encode("utf-8"))
                        except:
                            pass
                    elif "/unban" in data.decode("utf-8"):
                        try:
                            deleteUser(banlist_encrypt(re.search("/unban (.*)", data.decode("utf-8")).group(1)))
                            banlist.remove(banlist_encrypt(re.search("/unban (.*)", data.decode("utf-8")).group(1)))
                        except:
                            pass
                    elif "/kick" in data.decode("utf-8"):
                        try:
                            cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/kick (.*)", data.decode("utf-8")).group(1)) + "'")
                            client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                            client.send(("/kick").encode("utf-8"))
                        except:
                            pass
                    elif "/delete" in data.decode("utf-8"):
                        try:
                            try:
                                cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/kick (.*)", data.decode("utf-8")).group(1)) + "'")
                                client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                                client.send(("/kick").encode("utf-8"))
                            except:
                                pass
                            cursor.execute("UPDATE users SET password = '0' WHERE nick_name = '" + nick_encrypt(re.search("/delete (.*)", data.decode("utf-8")).group(1)) + "'")
                            conn.commit()
                            cursor.execute("UPDATE users SET nick_name = '0' WHERE nick_name = '" + nick_encrypt(re.search("/delete (.*)", data.decode("utf-8")).group(1)) + "'")
                            conn.commit()
                        except:
                            pass
                if "/myaudiomessage" in data.decode("utf-8") or "/privatemyaudiomessage" in data.decode("utf-8"):
                    new_connection.send(data)
                elif "/message" in data.decode("utf-8") or "/afterfilemessage" in data.decode("utf-8") or "/audiomessage" in data.decode("utf-8"):
                    for client in users:
                        if client != new_connection:
                            try:
                                client.send(data)
                            except:
                                user_id.remove(user_id[users.index(client)])
                                users_online.remove(users_online[users.index(client)])
                                users.remove(client)
                                client.close()
                elif "/privateaudiomessage" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/privateaudiomessage (.*) (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/privateaudiomessage " + re.search("/privateaudiomessage (.*) (.*) (.*)", data.decode("utf-8")).group(2) + " " + re.search("/privateaudiomessage (.*) (.*) (.*)", data.decode("utf-8")).group(3)).encode("utf-8"))
                    except:
                        pass
                elif "/privateafterfilemessage" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/privateafterfilemessage (.*) (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/privateafterfilemessage " + re.search("/privateafterfilemessage (.*) (.*) (.*)", data.decode("utf-8")).group(2) + " " + re.search("/privateafterfilemessage (.*) (.*) (.*)", data.decode("utf-8")).group(3)).encode("utf-8"))
                    except:
                        pass
                elif "/startfilesending" in data.decode("utf-8"):
                    for client in users:
                        if client != new_connection:
                            try:
                                client.send(data)
                            except:
                                user_id.remove(user_id[users.index(client)])
                                users_online.remove(users_online[users.index(client)])
                                users.remove(client)
                                client.close()
                    while True:
                        data = new_connection.recv(32768)
                        if data == b"/endfilesending":
                            for client in users:
                                if client != new_connection:
                                    try:
                                        client.send(b"/endfilesending")
                                    except:
                                        pass
                            break
                        for client in users:
                            if client != new_connection:
                                try:
                                    client.send(data)
                                except:
                                    pass
                elif "/privatestartfilesending" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/privatestartfilesending (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/privatestartfilesending " + re.search("/privatestartfilesending (.*) (.*)", data.decode("utf-8")).group(2)).encode("utf-8"))
                        while True:
                            data = new_connection.recv(32768)
                            if data == b"/endfilesending":
                                client.send(b"/endfilesending")
                                break
                            client.send(data)
                    except:
                        pass
                elif "connected to the server!" in data.decode("utf-8"):
                    print("[" + time.strftime("%H:%M:%S") + "] " + data.decode("utf-8"))
                    users_online.append(re.search("(.*) connected", data.decode("utf-8")).group(1))
                    for client in users:
                        try:
                            client.send(("/usersOnline " + getUsersOnline()).encode("utf-8"))
                        except:
                            user_id.remove(user_id[users.index(client)])
                            users_online.remove(users_online[users.index(client)])
                            users.remove(client)
                            client.close()
                elif "/changepassword" in data.decode("utf-8"):
                    if admin:
                        old_password = re.search("/changepassword (.*) (.*)", data.decode("utf-8")).group(1)
                        new_password = re.search("/changepassword (.*) (.*)", data.decode("utf-8")).group(2)
                        cursor.execute("SELECT password FROM users WHERE password = '" + admin_encrypt(old_password) + "' AND nick_name = 'admin'")
                    else:
                        nick = re.search("/changepassword (.*) (.*) (.*)", data.decode("utf-8")).group(1)
                        old_password = re.search("/changepassword (.*) (.*) (.*)", data.decode("utf-8")).group(2)
                        new_password = re.search("/changepassword (.*) (.*) (.*)", data.decode("utf-8")).group(3)
                        cursor.execute("SELECT password FROM users WHERE password = '" + pass_encrypt(old_password) + "' AND nick_name ="
                                                                                        "'" + nick_encrypt(nick) + "'")

                    if len(str(cursor.fetchall())) < 4:
                        new_connection.send(("/changepassword 0").encode("utf-8"))
                    else:
                        if admin:
                            cursor.execute("UPDATE users SET password = '" + admin_encrypt(new_password) + "' WHERE password = '" +
                                pass_encrypt(old_password) + "' AND nick_name = 'admin'")
                        else:
                            cursor.execute("UPDATE users SET password = '" + pass_encrypt(new_password) + "' WHERE password = '" +
                                       pass_encrypt(old_password) + "' AND nick_name = '" + nick_encrypt(nick) + "'")
                        conn.commit()
                        new_connection.send(("/changepassword 1").encode("utf-8"))
                elif "/pm" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/pm (.*) (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/pm " + re.search("/pm (.*) (.*) (.*)", data.decode("utf-8")).group(2) + " " + re.search("/pm (.*) (.*) (.*)", data.decode("utf-8")).group(3)).encode("utf-8"))
                    except:
                        pass
                elif "/startPM" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/startPM (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/startPM " + re.search("/startPM (.*) (.*)", data.decode("utf-8")).group(2)).encode("utf-8"))
                    except:
                        pass
                elif "/acceptPM" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/acceptPM (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/acceptPM " + re.search("/acceptPM (.*) (.*)", data.decode("utf-8")).group(2)).encode("utf-8"))
                    except:
                        pass
                elif "/endPM" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/endPM (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/endPM " + re.search("/endPM (.*) (.*)", data.decode("utf-8")).group(2)).encode("utf-8"))
                    except:
                        pass
                elif "/cancelPM" in data.decode("utf-8"):
                    try:
                        cursor.execute("SELECT id FROM users WHERE nick_name = '" + nick_encrypt(re.search("/cancelPM (.*) (.*)", data.decode("utf-8")).group(1)) + "'")
                        client = users[user_id.index(getResult(cursor.fetchall()[0]))]
                        client.send(("/cancelPM " + re.search("/cancelPM (.*) (.*)", data.decode("utf-8")).group(2)).encode("utf-8"))
                    except:
                        pass
                elif "disconnected from the server!" in data.decode("utf-8"):
                    print("[" + time.strftime("%H:%M:%S") + "] " + data.decode("utf-8"))
                    user_id.remove(user_id[users.index(new_connection)])
                    users_online.remove(users_online[users.index(new_connection)])
                    users.remove(new_connection)
                    for client in users:
                        try:
                            client.send(("/usersOnline " + getUsersOnline()).encode("utf-8"))
                        except:
                            user_id.remove(user_id[users.index(client)])
                            users_online.remove(users_online[users.index(client)])
                            users.remove(client)
                            client.close()
                    new_connection.close()
                    cursor.close()
                    conn.close()
                    break
            except:
                continue

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
key = "d58a506ee8cb983b6944e8372c8e72bc"

try:
    server.bind(("localhost", 1234))
    server.listen()
except:
    print("The connection has been failed. Try again.")
    time.sleep(2)
    exit(0)

users = []
user_id = []
users_online = []
file = open("BanList.txt", "rt")
banlist = [line.strip() for line in file]
file.close()
print("Server is running.")

while True:
    new_connection, address = server.accept()
    thread = Thread(target=new_thread, args=(new_connection,), daemon=True)
    thread.start()