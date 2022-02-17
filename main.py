from parser.database import Database
from parser.channel import Channel
from parser.parser import Parser
from parser.video import Video
from pick import pick
import sys,os

INDICATOR = "->"

parser = Parser()

def pick_watching_type():
    option, index = pick(['Video and audio', 'Video only', 'Audio only'], 'Pick wathcing type: ', indicator=INDICATOR)
    return option

def show_videos(channel):
    title = f'{channel.name} videos: '
    options = channel.get_video_names()

    for i in range(len(options)):
        if channel.videos[i].isNew:
            options[i] = '[!] ' + options[i]
        if channel.videos[i].isWatched:
            options[i] = '[+] ' + options[i]

    options.insert(0, "..")

    channel.set_all_videos_old()
    option, index = pick(options, title, indicator=INDICATOR)

    if index == 0 and option == "..":
        show_channels()

    video = channel.videos[index-1]
    parser.add_video_in_history(video)

    watching_type = pick_watching_type()
    video.play(watching_type)

    show_videos(channel)

def show_channels():
    title = 'Your subscriptions: '
    options = parser.get_channel_names()

    for i in range(len(options)):
        chan = parser.channels[i]
        analog = chan.find_analog_in_list(parser.databaseChannels)
        
        if analog == None:
            continue

        hasNewVideos = chan.has_new_videos(analog)

        if hasNewVideos:
            options[i] = '[!] ' + options[i]

    options.insert(0, "..")

    option, index = pick(options, title, indicator=INDICATOR)
    
    if option == ".." and index == 0:
        exit()

    channel = parser.channels[index-1]
    show_videos(channel)
    
def ask_database_reload():
    title = 'Reload channels database? '
    options = ['No', 'Yes']

    option, index = pick(options, title, indicator=INDICATOR)
    
    if option == 'Yes' and index == 1:
        os.system('rm channels.db')
        parser.database = Database()
        parser.load_channels()
    
    show_channels()

def main():
    if parser.load_channels_from_database():
        ask_database_reload()          
    else:
        show_channels()
    
if __name__ == "__main__":
    main()
