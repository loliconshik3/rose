from src.channel import Channel

class ChannelsList:

    def __init__(self, channels=[]):
        self.channels = channels

    def append(self, channel):
        self.channels.append(channel)

    def get_channel_names(self):
        names = []
        for channel in self.channels:
            names.append(channel.name)

        return names

    def get_channel_index(self, channel):
        for index, chan in enumerate(self.channels):
            if chan.link == channel.link:
                return index

    def get_channels_indexs_by_link_list(self, link_list):
        index_dict = {}

        for lindex, link in enumerate(link_list):
            for index, channel in enumerate(self.channels):
                if link in channel.link:
                    index_dict[lindex] = index
                    break

        return index_dict

    def sort_channels_by_link_list(self, link_list):
        index_dict = self.get_channels_indexs_by_link_list(link_list)

        sorted_channels = []
        for key, value in index_dict.items():
            sorted_channels.insert(key, self.channels[value])

        self.channels = sorted_channels

    def clear(self):
        self.channels.clear()

    def print_channels(self):
        for channel in self.channels:
            print(f"{channel.name} | {channel.link} | {len(channel.videos)}")

    def get_list(self):
        return self.channels
