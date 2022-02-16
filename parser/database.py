import sqlite3

class Database:

    def __init__(self):
        self.base = sqlite3.connect('channels.db')
        self.cursor = self.base.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
            channel TEXT,
            videos TEXT
        )""")
        self.base.commit()
    
    def insert_channel(self, channel_dict, videos_dict):
        channel_dict = str(channel_dict)
        chan_list = (str(channel_dict), videos_dict)
        self.cursor.execute("INSERT INTO channels VALUES (?, ?)", chan_list)
        self.base.commit()

    def load_channels(self):
        return self.cursor.execute("SELECT * FROM channels")

