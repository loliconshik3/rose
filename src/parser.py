from src.channels_list import ChannelsList
from src.mirrors_list import MirrorsList
from src.database import Database
from src.channel import Channel
from src.history import History
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
        self.databaseChannels = []
        self.mirrors = MirrorsList()
        self.channels = None
        self.history = None
        
    def send_request(self, link):
        resp = requests.get(link)
        resp.encoding = 'utf-8'

        if resp.status_code == 200:
            return resp
        else:
            print("Request error!")
            return None

    def is_link_to_channel(self, link):
        return '/channel/' in link

    def load_search_query(self, query, history):
        mirror = self.mirrors.get_working_mirror()

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

                data_boxes = item_box.find_all("div", {"class": "video-card-row flexible"})

                channel_data = data_boxes[0].select('p')[0]
                author = channel_data.text

                video_data = data_boxes[1].select('p')

                if len(video_data) == 2:
                    shared = video_data[0].text.replace('Shared ', '')
                    views = video_data[1].text.replace(' views', '')
                else:
                    shared = 'None'
                    views = video_data[0].text.replace(' views', '')

                video = Video(name, link, preview, nmLink, False, shared, views, author)
                video.isWatched = history.is_video_in_history(video)

                items.append(video)
            else:
                item_name = item_box.select('p')[0]
                channel_name = item_name.text

                item_subs = item_box.select('p')[1]
                subs = item_subs.text.replace(' subscribers', '')

                videos = []
                channel_id = nmLink.replace('/channel/', '')
                channel = Channel(channel_name, channel_id, videos, subs)

                self.load_channel_videos(channel, history)
                items.append(channel)
        
        return items

    def load_channel_videos(self, channel, history):
        mirror = self.mirrors.get_working_mirror()
        html = self.send_request(mirror.link + '/channel/' + channel.link)

        soup = bs(html.text, 'html.parser')

        for video_box in soup.find_all("div", {"class": "pure-u-1 pure-u-md-1-4"}):
            nmLink = video_box.find("a", href = True)['href']
            link = mirror.link + nmLink
            name = video_box.find_all("p")[1].text
            preview = video_box.find("img")['src']

            data_boxes = video_box.find_all("div", {"class": "video-card-row flexible"})

            channel_data = data_boxes[0].select('p')[0]
            author = channel_data.text

            video_data = data_boxes[1].select('p')

            if len(video_data) == 2:
                shared = video_data[0].text.replace('Shared ', '')
                views = video_data[1].text.replace(' views', '')
            else:
                shared = 'None'
                views = video_data[0].text.replace(' views', '')

            video = Video(name, link, preview, nmLink, False, shared, views, author)
            video.isWatched = history.is_video_in_history(video)

            channel.videos.append(video)

    def load_channel(self, channel_id):
        if channel_id == "":
            return

        mirror = self.mirrors.get_working_mirror()

        link = mirror.link + '/channel/' + channel_id

        html = self.send_request(link)
        if html == None:
            return

        parsed_html = bs(html.text, 'html.parser')
        html_name = parsed_html.select('span')[1]
        channel_name = html_name.text

        html_subs = parsed_html.find('a', id='subscribe').select('b')[0]
        subs = html_subs.text.replace('Subscribe | ', '')

        videos = []
        channel = Channel(channel_name, channel_id, videos, subs)
        self.load_channel_videos(channel, self.history)
        self.channels.append(channel)

    def load_channels(self, channels, history):
        if self.mirrors.get_list() == []:
            self.mirrors.load_mirrors()

        mirror = self.mirrors.get_working_mirror()

        channels.clear()
        self.channels = channels
        self.history = history

        print(f"Loading {len(self.SUBS_LIST)} channels")

        pool = ThreadPool(processes=len(self.SUBS_LIST))
        pool.map(self.load_channel, self.SUBS_LIST)

        channels.sort_channels_by_link_list(self.SUBS_LIST)

        print("Complete!")

