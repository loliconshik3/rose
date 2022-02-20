from src.database import Database
from src.channel import Channel
from src.parser import Parser
from src.video import Video
from pick import pick
import sys,os

INDICATOR = "->"

parser = Parser()

def pick_watching_type():
    option, index = pick(['Video and audio', 'Video only', 'Audio only'], 'Pick wathcing type: ', indicator=INDICATOR)
    return option

def show_videos(channel, search_dict={}):
    title = f'{channel.name} videos: '
    options = channel.get_video_names()

    for i in range(len(options)):
        if channel.videos[i].isNew:
            options[i] = '[!] ' + options[i]
        if channel.videos[i].isWatched:
            options[i] = '[+] ' + options[i]

    options.insert(0, "..")

    channel.set_all_videos_old()
    
    channel_dict, videos_dict = channel.toDict()
    parser.database.rewrite_channel_videos(channel_dict, videos_dict)
    
    option, index = pick(options, title, indicator=INDICATOR)

    if index == 0 and option == "..":
        if search_dict != {}:
            show_search_query(search_dict['query'], search_dict['list'])
        else:
            show_channels()

    video = channel.videos[index-1]
    parser.add_video_in_history(video)

    watching_type = pick_watching_type()
    video.play(watching_type)
    
    show_videos(channel, search_dict)

def show_channels():
    title = 'Your subscriptions: '
    options = parser.channels.get_channel_names()

    channels = parser.channels.get_list()
    for i in range(len(options)):
        chan = channels[i]
        analog = chan.find_analog_in_list(parser.databaseChannels)
        
        if analog == None:
            continue

        hasNewVideos = chan.has_new_videos(analog)

        if hasNewVideos:
            channel_dict, videos_dict = chan.toDict()
            parser.database.rewrite_channel_videos(channel_dict, videos_dict)
            options[i] = '[!] ' + options[i]

        if chan.is_full_watched():
            options[i] = '[+] ' + options[i]

    options.insert(0, "..")
    option, index = pick(options, title, indicator=INDICATOR)
    
    if option == ".." and index == 0:
        return show_menu()

    channel = channels[index-1]
    
    analog = channel.find_analog_in_list(parser.databaseChannels)
    if not analog == None:
        analog.videos = channel.videos

    show_videos(channel)
   
def show_search_query(query, search_list):
    title = f'Result of {query}:'

    options = []
    for index, item in enumerate(search_list):
        name = item.name
        if type(item) == Channel:
            name = "[" + name + "]"
        options.append(name)

    options.insert(0, "..")
    option, index = pick(options, title, indicator=INDICATOR)

    if option == '..' and index == 0:
        return show_menu()
        
    item = search_list[index-1]
    if type(item) == Channel:
        show_videos(item, search_dict={'query': query, 'list': search_list})
    else:
        parser.add_video_in_history(item)

        watching_type = pick_watching_type()
        item.play(watching_type)

        show_search_query(query, search_list)

def ask_search_query():
    query = input('Input your search query: ')

    search_list = parser.load_search_query(query)

    show_search_query(query, search_list)

def ask_database_reload():
    title = 'Reload channels database? '
    options = ['No', 'Yes']

    option, index = pick(options, title, indicator=INDICATOR)
    
    if option == 'Yes' and index == 1:
        os.system('rm channels.db')
        parser.database = Database()
        parser.load_channels()
    
    show_menu()

def show_menu():
    title = 'Menu: '
    options =['..', 'Subscribes', 'Search']

    option, index = pick(options, title, indicator=INDICATOR)
    
    if option == '..':
        exit()
    elif option == 'Subscribes':
        show_channels()
    elif option == 'Search':
        ask_search_query()

def main():
    if parser.load_channels_from_database():
        ask_database_reload()          
    else:
        show_menu()
    
if __name__ == "__main__":
    main()
