from src.mirror import Mirror
import requests

requests.packages.urllib3.util.connection.HAS_IPV6 = False

class MirrorsList:

    def __init__(self):
        self.links = [i.strip('\n').split(',')[0] for i in open('mirrors')]
        self.mirrors = []

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
        for mir in self.links:
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

    def get_list(self):
        return self.mirrors
