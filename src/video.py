import sys, os

class Video:

    def __init__(self, name="", link="", preview="", nmLink="", isWatched=False, shared="", views="", author="", length=""):
        self.name = name
        self.link = link
        self.nmLink = nmLink
        self.preview = preview
        self.isWatched = isWatched
        self.shared = shared
        self.views = views
        self.author = author
        self.length = length

        self.isNew = False

        self.picker = None

    def toDict(self):
        video_dict = {
            "name" : self.name.replace('"', "").replace("'", ""),
            "link" : self.link,
            "nmLink" : self.nmLink,
            "preview" : self.preview,
            "isNew" : str(self.isNew),
            "isWatched" : str(self.isWatched),
            "shared" : self.shared,
            "views" : self.views,
            "author" : self.author,
            "length" : self.length
        }

        return video_dict

    def str_to_bool(self, arg):
        return True if arg == 'True' else False

    def dictToVideo(self, video_dict):
        self.name = video_dict['name']
        self.link = video_dict['link']
        self.nmLink = video_dict['nmLink']
        self.preview = video_dict['preview']
        self.shared = video_dict['shared']
        self.views = video_dict['views']
        self.author = video_dict['author']
        self.length = video_dict['length']

        self.isNew = self.str_to_bool(video_dict['isNew'])
        self.isWatched = self.str_to_bool(video_dict['isWatched'])

    def pick_watching_type(self):
        self.picker.set_title('Pick watching type: ')
        self.picker.set_items(['Video and audio', 'Video only', 'Audio only'])
        option, index = self.picker.start()
        return option

    def play(self):
        self.isWatched = True
        
        watching_type = self.pick_watching_type()

        mpv_command = "mpv "
        link = " https://youtube.com" + self.nmLink

        if watching_type == "Video only":
            mpv_command += "--aid=0"
        elif watching_type == "Audio only":
            mpv_command += "--vid=0"

        print(f'Watching: {self.name} | {link[1:]}')
        os.system(mpv_command + link)

    def copy(self):
        return Video(self.name, self.link, self.preview, self.nmLink, self.isWatched)
