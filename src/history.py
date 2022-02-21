

class History:

    def __init__(self, videos):
        self.videos = videos

    def is_video_in_history(self, video):
        for vid in self.videos:
            if vid.nmLink == video.nmLink:
                return True

        return False

    def append(self, video, db):
        if not self.is_video_in_history(video):
            self.videos.append(video)
            
            if db != None:
                db.insert_video_in_history(video)

