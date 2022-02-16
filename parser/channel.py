from parser.video import Video

class Channel:

    def __init__(self, name="", link="", videos=[]):
        self.name = name
        self.link = link
        self.videos = videos

    def get_video_names(self):
        names = []
        for video in self.videos:
            names.append(video.name)

        return names

    def toDict(self):
        videos_list = [ video.toDict() for video in self.videos ]

        channel_dict = {
            "name" : self.name,
            "link" : self.link,
        }

        return channel_dict, str(videos_list)

    def dictToChannel(self, channel_dict, videos_list):
        self.name = channel_dict['name']
        self.link = channel_dict['link']

        self.videos = []
        for video_dict in videos_list:
            video = Video()
            video.dictToVideo(video_dict)
            self.videos.append(video)
