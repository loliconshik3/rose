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
        
        self.history_base = sqlite3.connect('history.db', check_same_thread=False)
        self.history_cursor = self.history_base.cursor()

        self.history_cursor.execute("""CREATE TABLE IF NOT EXISTS history (
            id TEXT,
            name TEXT
        )""")
        self.history_base.commit()

    def insert_channel(self, channel_dict, videos_dict):
        link = channel_dict['link']
        channel_dict = str(channel_dict)
        chan_list = (str(link), str(channel_dict), videos_dict)
        self.cursor.execute("INSERT INTO channels VALUES (?, ?, ?)", chan_list)
        self.base.commit()

    def rewrite_channel_videos(self, channel_dict, videos_dict):
        link = channel_dict['link']
        self.cursor.execute("UPDATE channels SET videos = ? WHERE link = ?", [videos_dict, link])
        self.base.commit()

    def insert_video_in_history(self, video):
        video_list = (str(video.nmLink), str(video.name))
        self.history_cursor.execute("INSERT INTO history VALUES (?, ?)", video_list)
        self.history_base.commit()

    def load_channels(self):
        return self.cursor.execute("SELECT * FROM channels")

    def load_history(self):
        return self.history_cursor.execute("SELECT * FROM history")
