from bs4 import BeautifulSoup as bs
from parser.database import Database
from parser.channel import Channel
from parser.mirror import Mirror
from parser.video import Video
import requests
import json

class Parser:

    def __init__(self):
        self.SUBS_LIST = [i.strip('\n').split(',')[0] for i in open('subscribes.txt')]
        self.MIRRORS = [i.strip('\n').split(',')[0] for i in open('mirrors')]
        self.channels = []
        self.mirrors = []

        self.database = Database()

    def send_request(self, link):
        resp = requests.get(link)

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
        for mirror in self.mirrors:
            if mirror.is_work:
                return mirror

        return ""

    def load_channel_videos(self, channel):
        html = self.send_request(channel.link)
        html.encoding = 'utf-8'

        mirror = self.get_working_mirror()

        soup = bs(html.text, 'html.parser')

        for video_box in soup.find_all("div", {"class": "pure-u-1 pure-u-md-1-4"}):
            nmLink = video_box.find("a", href = True)['href']
            link = mirror.link[:-1] + nmLink
            name = video_box.find_all("p")[1].text
            preview = video_box.find("img")['src']

            video = Video(name, link, preview, nmLink)

            channel.videos.append(video)

    def load_channels(self):
        if self.mirrors == []:
            self.load_mirrors()

        mirror = self.get_working_mirror()

        self.channels = []
        for channel_id in self.SUBS_LIST:
            if channel_id == "":
                continue

            link = mirror.link + channel_id

            html = self.send_request(link)
            if html == None:
                continue

            html.encoding = 'utf-8'
            parsed_html = bs(html.text, 'html.parser')
            html_name = parsed_html.select('span')[1]
            channel_name = html_name.text

            videos = []
            channel = Channel(channel_name, link, videos)
            self.load_channel_videos(channel)
            self.channels.append(channel)

            channel_dict, videos_dict = channel.toDict()
            self.database.insert_channel(channel_dict, videos_dict)

    def load_channels_from_database(self):
        chans = self.database.load_channels()

        self.channels = []
        for chan in chans:
            ch = json.loads(chan[0].replace("'", '"'))
            vd = json.loads(chan[1].replace("'", '"'))

            channel = Channel()
            channel.dictToChannel(ch, vd)
            
            self.channels.append(channel)
            
        if self.channels == []:
            self.load_channels()
            return False
        else:
            return True

    def get_channel_names(self):
        names = []
        for channel in self.channels:
            names.append(channel.name)
        
        return names

    def print_channels(self):
        for channel in self.channels:
            print(f"{channel.name} | {channel.link} | {len(channel.videos)}")

    def print_mirrors(self):
        for mirror in self.mirrors:
            print(f"{mirror.link} | {mirror.is_work}")
