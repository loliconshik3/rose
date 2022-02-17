import os

class Video:

    def __init__(self, name="", link="", preview="", nmLink="", isWatched=False):
        self.name = name
        self.link = link
        self.preview = preview
        self.nmLink = nmLink
        self.isWatched = isWatched
        
        self.isNew = False

    def toDict(self):
        video_dict = {
            "name" : self.name.replace('"', "").replace("'", ""),
            "link" : self.link,
            "preview" : self.preview,
            "nmLink" : self.nmLink
        }

        return video_dict

    def dictToVideo(self, video_dict):
        self.name = video_dict['name']
        self.link = video_dict['link']
        self.preview = video_dict['preview']
        self.nmLink = video_dict['nmLink']

    def play(self):
        self.isWatched = True
        os.system("mpv " + "https://youtube.com" + self.nmLink)
