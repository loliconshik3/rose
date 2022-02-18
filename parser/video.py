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
            "nmLink" : self.nmLink,
            "isNew" : str(self.isNew)
        }

        return video_dict

    def str_to_bool(self, arg):
        return True if arg == 'True' else False

    def dictToVideo(self, video_dict):
        self.name = video_dict['name']
        self.link = video_dict['link']
        self.preview = video_dict['preview']
        self.nmLink = video_dict['nmLink']

        self.isNew = self.str_to_bool(video_dict['isNew'])

    def play(self, watching_type=""):
        self.isWatched = True
        
        mpv_command = "mpv "
        link = " https://youtube.com" + self.nmLink

        if watching_type == "Video only":
            mpv_command += "--aid=0"
        elif watching_type == "Audio only":
            mpv_command += "--vid=0"

        os.system(mpv_command + link)
