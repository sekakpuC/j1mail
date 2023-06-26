import datetime
import json
import sqlite3

class UserSessionStore:
    def __init__(self, store_type):
        if store_type == "jsonl":
            self.store = UserSessionStoreJSONL()
        elif store_type == "sqlite3":
            self.store = UserSessionStoreSQLite3()

    def create(self, user_session_id, data):
        return self.store.create(user_session_id, data)

    def add_usersession(self, usersession):
        return self.store.add_usersession(usersession)

    def saveAll(self, userSessions):
        return self.store.saveAll(userSessions)

    def read(self, user_session_id):
        return self.store.read(user_session_id)

    def readAll(self):
        return self.store.readAll()

    def update(self, user_session_id, data):
        return self.store.update(user_session_id, data)

    def delete(self, user_session_id):
        return self.store.delete(user_session_id)

class UserSessionStoreJSONL:
    def __init__(self):
        self.file = open("usersessions.jsonl", "w")
        self.filename = "usersessions.jsonl"

    def create(self, userSession):
        sessions = self.readAll()
        sessions.append(userSession)
        with open(self.filename, 'a') as f:
            json.dump(sessions, f)

    def add_usersession(self, usersession):
        with open(self.filename, 'a') as f:
            json.dump(usersession, f)

    def saveAll(self, sessions):
        f = self.file
        with open(self.filename, 'w') as f:
            for item in sessions:
                f.write(json.dumps(item) + '\n')

    def read(self, user_session_id):
        with open(self.filename, 'r') as f:
            for line in f:
                data = json.loads(line)
                if data["user_session_id"] == user_session_id:
                    return data
        return None

    def readAll(self):
        data = []
        try:
            with open(self.filename, 'r') as f:
                for line in f:
                    data.append(json.loads(line))
        except:
            pass
        return data

    def update(self, user_session_id, data):
        for i, line in enumerate(self.file):
            data_old = json.loads(line)
            if data_old["user_session_id"] == user_session_id:
                self.file.seek(i)
                self.file.write(json.dumps({"user_session_id": user_session_id, "data": data}) + "\n")
                return

    def delete(self, user_session_id):
        for i, line in enumerate(self.file):
            data_old = json.loads(line)
            if data_old["user_session_id"] == user_session_id:
                self.file.seek(i)
                self.file.truncate()
                return

class UserSessionStoreSQLite3:
    def __init__(self):
        self.conn = sqlite3.connect("j1mailv2.db")
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS usersessions (user_session_id TEXT PRIMARY KEY, username TEXT, login_time TEXT)")

    def create(self, usersession):
        conn = sqlite3.connect('j1mailv2.db')
        cur = conn.cursor()
        session_id = usersession["user_session_id"]
        username = usersession["username"]
        session_time = datetime.datetime.utcnow()
        cur.execute("INSERT INTO usersessions VALUES (?, ?, ?)", (session_id, username, session_time))
        conn.commit()

    def add_usersession(self, usersession):
        return self.create(usersession)

    # TODO
    def saveAll(self, sessions):
        raise Exception("NotImplemented")

    def read(self, user_session_id):
        self.cur.execute("SELECT data FROM usersessions WHERE user_session_id = ?", (user_session_id,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0]
        return None

    def readAll(self):
        self.cur.execute("SELECT data FROM usersessions")
        data = self.cur.fetchall()
        return data

    def update(self, user_session_id, data):
        self.cur.execute("UPDATE usersessions SET data = ? WHERE user_session_id = ?", (data, user_session_id))
        self.conn.commit()

    def delete(self, user_session_id):
        self.cur.execute("DELETE FROM usersessions WHERE user_session_id = ?", (user_session_id,))
        self.conn.commit()

def main():
    store = UserSessionStore("jsonl")
    user_session_id = "1234567890"
    data = {"username": "bardo", "email": "bardo@example.com"}
    store.create(user_session_id, data)
    data_read = store.read(user_session_id)
    assert data_read == data
    store.update(user_session_id, {"username": "bard"})
    data_read = store.read(user_session_id)
    assert data_read["username"] == "bard"
    store.delete(user_session_id)
    data_read = store.read(user_session_id)
    assert data_read is None

if __name__ == "__main__":
    main()