from src.video import Video

class Channel:

    def __init__(self, name="", link="", videos=[], subscribes=""):
        self.name = name
        self.link = link
        self.videos = videos
        self.subscribes = subscribes

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
            "subscribes" : self.subscribes
        }

        return channel_dict, str(videos_list)

    def dictToChannel(self, channel_dict, videos_list, history):
        self.name = channel_dict['name']
        self.link = channel_dict['link']
        self.subscribes = channel_dict['subscribes']

        self.videos = []
        for video_dict in videos_list:
            video = Video()
            video.dictToVideo(video_dict)
            video.isWatched = video.nmLink in history
            self.videos.append(video)

    def set_all_videos_old(self):
        for video in self.videos:
            video.isNew = False

    def find_analog_in_list(self, channels_list):
        for channel in channels_list:
            if channel.link == self.link:
                return channel

    def get_count_of_watched_videos(self):
        count = 0
        for video in self.videos:
            if video.isWatched:
                count += 1
        return count

    def is_full_watched(self):
        for video in self.videos:
            if not video.isWatched:
                return False

        return True

    def has_new_videos(self, old_channel):
        result = False
        old_videos = []
        
        for video in old_channel.videos:
            old_videos.append(video.nmLink)

        for video in self.videos: 
            if not video.nmLink in old_videos or video.isNew == True:
                video.isNew = True
                result = True

        return result


