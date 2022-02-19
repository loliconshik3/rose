import sqlite3

class Database:

    def __init__(self):
        self.base = sqlite3.connect('channels.db', check_same_thread=False)
        self.cursor = self.base.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
            link TEXT,
            channel TEXT,
            videos TEXT
        )""")
        self.base.commit()

    def insert_channel(self, channel_dict, videos_dict):
        link = channel_dict['link']
        channel_dict = str(channel_dict)
        chan_list = (str(link), str(channel_dict), videos_dict)
        self.cursor.execute("INSERT INTO channels VALUES (?, ?, ?)", chan_list)
        self.base.commit()

    def rewrite_channel(self, channel_dict, videos_dict):
        link = channel_dict['link']
        chan_list = (str(link), str(channel_dict), videos_dict)
        self.cursor.execute("UPDATE channels SET channel = ? WHERE link = ?", [str(channel_dict), link])
        self.cursor.execute("UPDATE channels SET videos = ? WHERE link = ?", [videos_dict, link])
        self.base.commit()

    def load_channels(self):
        return self.cursor.execute("SELECT * FROM channels")

