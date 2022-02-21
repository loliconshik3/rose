from src.channels_list import ChannelsList
from src.database import Database
from src.channel import Channel
from src.history import History
from src.parser import Parser
from src.video import Video
from ui.picker import pick
import sys,os
import json

class MainWindow:

    def __init__(self):
        self.parser = Parser()
        self.database = Database()
        self.channels = ChannelsList([])
        self.history = History([])

        self.indicator = "->"

    def load_channels(self):
        self.parser.load_channels(self.channels, self.history)
        self.save_channels_into_database()

    def load_history_from_database(self):
        videos = self.database.load_history()

        for vid in videos:
            video = Video(name=vid[1], nmLink=vid[0])
            self.history.append(video, None)

    def load_channels_from_database(self):
        chans = self.database.load_channels()

        result = False
        self.channels.clear()
        for chan in chans:
            ch = json.loads(chan[1].replace("'", '"').replace("\\", "\\\\"))
            vd = json.loads(chan[2].replace("'", '"').replace("\\", "\\\\"))

            channel = Channel()
            channel.dictToChannel(ch, vd, self.history.videos)
            
            self.channels.append(channel)

        if self.channels.get_list() == []:
            self.load_channels()
            result = False
        else:
            self.parser.databaseChannels = self.channels.get_list().copy()
            result = True

        return result

    def show_videos(self, channel, search_dict={}):
        title = f'{channel.name} videos: '
        
        options = [video for video in channel.videos]

        for i in range(len(options)):
            if self.history.is_video_in_history(channel.videos[i]):
                channel.videos[i].isWatched = True

        options.insert(0, "..")
        channel.set_all_videos_old()
        
        channel_dict, videos_dict = channel.toDict()
        self.database.rewrite_channel_videos(channel_dict, videos_dict)
        
        option, index = pick(title, options, indicator=self.indicator)

        if index == 0 and option == "..":
            if search_dict != {}:
                self.show_search_query(search_dict['query'], search_dict['list'])
            else:
                self.show_channels()

        video = channel.videos[index-1]

        self.history.append(video.copy(), self.database)
        video.play()
        
        self.show_videos(channel, search_dict)

    def show_channels(self):
        title = 'Your subscriptions: '
        options = [chan for chan in self.channels.get_list()]

        channels = self.channels.get_list()
        for i in range(len(options)):
            chan = channels[i]

            analog = chan.find_analog_in_list(self.parser.databaseChannels)
            
            if analog == None:
                continue

            for vid in chan.videos:
                if self.history.is_video_in_history(vid):
                    vid.isWatched = True

            hasNewVideos = chan.has_new_videos(analog)

            if hasNewVideos:
                channel_dict, videos_dict = chan.toDict()
                self.database.rewrite_channel_videos(channel_dict, videos_dict)
                #options[i] = '[!] ' + options[i]


        options.insert(0, "..")
        option, index = pick(title, options, indicator=self.indicator)
        
        if option == ".." and index == 0:
            return self.show_menu()

        channel = self.channels.get_list()[index-1]

        analog = channel.find_analog_in_list(self.parser.databaseChannels)
        if not analog == None:
            analog.videos = channel.videos

        self.show_videos(channel)
   
    def show_search_query(self, query, search_list):
        title = f'Result of {query}:'

        options = []
        for index, item in enumerate(search_list):
            if type(item) == Video:
                if self.history.is_video_in_history(item):
                    item.isWatched = True
            options.append(item)

        options.insert(0, "..")
        option, index = pick(title, options, indicator=self.indicator)

        if option == '..' and index == 0:
            return self.show_menu()
            
        item = search_list[index-1]
        if type(item) == Channel:
            self.show_videos(item, search_dict={'query': query, 'list': search_list})
        else:
            self.history.append(item, self.database)

            item.play()

            self.show_search_query(query, search_list)

    def ask_search_query(self):
        query = input('Input your search query: ')

        search_list = self.parser.load_search_query(query, self.history)

        self.show_search_query(query, search_list)

    def save_channels_into_database(self):
        for channel in self.channels.get_list():
            channel_dict, videos_dict = channel.toDict()
            self.database.insert_channel(channel_dict, videos_dict)

    def ask_database_reload(self):
        title = 'Reload channels database? '
        options = ['No', 'Yes']

        option, index = pick(title, options, indicator=self.indicator)
        
        if option == 'Yes' and index == 1:
            os.system('rm channels.db')
            self.database = Database()
            self.load_channels()

        self.show_channels()

    def show_history(self):
        title = 'History: '

        options = []
        videos = self.history.videos
        for video in videos:
            options.append(video.name)

        options.reverse()
        options.insert(0, '..')
        option, index = pick(title, options, indicator=self.indicator)

        if option == '..' and index == 0:
            self.show_menu()

        video = videos[index-1]
        video.play()

        self.show_history()

    def show_menu(self):
        title = 'Menu: '
        options = ['..', 'Subscribes', 'Search', 'History']

        option, index = pick(title, options, indicator=self.indicator)
        
        if option == '..':
            exit()
        elif option == 'Subscribes':
            if self.channels.get_list() != []:
                self.ask_database_reload()
            else:
                self.load_channels_from_database()
                self.show_channels()
        elif option == 'Search':
            self.ask_search_query()
        elif option == 'History':
            self.show_history()

def main():
    window = MainWindow()

    window.load_history_from_database()
    window.show_menu()
    
if __name__ == "__main__":
    main()
