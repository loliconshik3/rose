from src.channels_list import ChannelsList
from src.database import Database
from src.channel import Channel
from src.mirror import Mirror
from src.video import Video
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup as bs
from os.path import exists
import requests
import json

class Parser:

    def __init__(self):
        self.SUBS_LIST = [i.strip('\n').split(',')[0] for i in open('subscribes.txt')]
        self.MIRRORS = [i.strip('\n').split(',')[0] for i in open('mirrors')]
        self.databaseChannels = []
        self.mirrors = []
        
        self.channels = ChannelsList([])

        self.HISTORY = []
        if exists('history.txt'):
            self.HISTORY = [i.strip('\n').split(',')[0] for i in open('history.txt')]

        self.database = Database()

    def add_video_in_history(self, video):
        self.HISTORY.append(video.nmLink)

        with open('history.txt', 'a') as file:
            file.write(video.nmLink + '\n')
            file.close()

    def send_request(self, link):
        resp = requests.get(link)
        resp.encoding = 'utf-8'

        if resp.status_code == 200:
            return resp
        else:
            print("Request error!")
            return None

    def is_mirror_work(self, link):
        resp = self.send_request(link)

        if resp == None:
            return False
        
        return True

    def load_mirrors(self):
        for mir in self.MIRRORS:
            is_work = self.is_mirror_work(mir)

            mirror = Mirror(mir, is_work)
            self.mirrors.append(mirror)

            if is_work:
                return

    def get_working_mirror(self):
        if self.mirrors == []:
            self.load_mirrors()

        for mirror in self.mirrors:
            if mirror.is_work:
                return mirror

        return None

    def is_link_to_channel(self, link):
        return '/channel/' in link

    def load_search_query(self, query):
        mirror = self.get_working_mirror()

        format_query = query.replace(" ", "+")
        resp = self.send_request(mirror.link + '/search?q=' + format_query)
        soup = bs(resp.text, 'html.parser')

        items = []
        for item_box in soup.find_all("div", {"class": "pure-u-1 pure-u-md-1-4"}):
            nmLink = item_box.find("a", href=True)['href']
            link = mirror.link + nmLink

            if not self.is_link_to_channel(nmLink):
                name = item_box.find_all("p")[1].text
                preview = item_box.find("img")['src']

                isWatched = nmLink in self.HISTORY

                video = Video(name, link, preview, nmLink, isWatched)
                items.append(video)
            else:
                item_name = item_box.select('p')[0]
                channel_name = item_name.text

                videos = []
                channel = Channel(channel_name, link, videos)

                self.load_channel_videos(channel)
                items.append(channel)
        
        return items

    def load_channel_videos(self, channel):
        mirror = self.get_working_mirror()
        html = self.send_request(mirror.link + '/channel/' + channel.link)

        soup = bs(html.text, 'html.parser')

        for video_box in soup.find_all("div", {"class": "pure-u-1 pure-u-md-1-4"}):
            nmLink = video_box.find("a", href = True)['href']
            link = mirror.link + nmLink
            name = video_box.find_all("p")[1].text
            preview = video_box.find("img")['src']

            isWatched = nmLink in self.HISTORY

            video = Video(name, link, preview, nmLink, isWatched)

            channel.videos.append(video)

    def load_channel(self, channel_id):
        if channel_id == "":
            return

        mirror = self.get_working_mirror()

        link = mirror.link + '/channel/' + channel_id

        html = self.send_request(link)
        if html == None:
            return

        parsed_html = bs(html.text, 'html.parser')
        html_name = parsed_html.select('span')[1]
        channel_name = html_name.text

        videos = []
        channel = Channel(channel_name, channel_id, videos)
        self.load_channel_videos(channel)
        self.channels.append(channel)

    def load_channels(self):
        if self.mirrors == []:
            self.load_mirrors()

        mirror = self.get_working_mirror()

        self.channels.clear()

        print(f"Loading {len(self.SUBS_LIST)} channels")

        pool = ThreadPool(processes=len(self.SUBS_LIST))
        pool.map(self.load_channel, self.SUBS_LIST)

        self.channels.sort_channels_by_link_list(self.SUBS_LIST)
        channels = self.channels.get_list()
        for channel in channels:
            channel_dict, videos_dict = channel.toDict()
            self.database.insert_channel(channel_dict, videos_dict)

        print("Complete!")

    def load_channels_from_database(self):
        chans = self.database.load_channels()

        self.channels.clear()
        for chan in chans:
            ch = json.loads(chan[1].replace("'", '"').replace("\\", "\\\\"))
            vd = json.loads(chan[2].replace("'", '"').replace("\\", "\\\\"))

            channel = Channel()
            channel.dictToChannel(ch, vd, self.HISTORY)
            
            self.channels.append(channel)
            
        if self.channels == []:
            self.load_channels()
            return False
        else:
            self.databaseChannels = self.channels.get_list()
            return True

    def print_mirrors(self):
        for mirror in self.mirrors:
            print(f"{mirror.link} | {mirror.is_work}")
