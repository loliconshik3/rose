import curses

import sys
sys.path.append("..")
from src.channel import Channel
from src.video import Video

KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_UP = (curses.KEY_UP, ord('k'))
KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))

class Picker:

    def __init__(self, title='', items=[], indicator=''):
        self.title = title
        self.items = items
        self.indicator = indicator

        self.index = 0
        self.scroll_top = 0

    def move_up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.items) - 1

    def move_down(self):
        self.index += 1
        if self.index >= len(self.items):
            self.index = 0

    def get_selected(self):
        return self.items[self.index], self.index

    def get_item_lines(self):
        lines = []
        for index, item in enumerate(self.items):
            if index == self.index:
                prefix = self.indicator
            else:
                prefix = len(self.indicator) * ' '
            
            if type(item) == str:
                line = '{0} {1}'.format(prefix, item)
            else:
                name = item.name 
                
                if type(item) == Channel:
                    name = '[' + name + ']'
                    if item.is_full_watched():
                        name = '[+] ' + name
                elif type(item) == Video:
                    if item.isNew:
                        name = '[!] ' + name
                    if item.isWatched:
                        name = '[+] ' + name

                line = '{0} {1}'.format(prefix, name)

            lines.append(line)

        return lines

    def get_title_lines(self):
        if self.title:
            return self.title.split('\n') + ['']
        return []

    def get_lines(self):
        title_lines = self.get_title_lines()
        item_lines = self.get_item_lines()
        lines = title_lines + item_lines
        current_line = self.index + len(title_lines) + 1
        return lines, current_line

    def crop_line_to_limit(self, line, limit):            
        if len(line) > limit:
            line = line[:limit-3] + '...'
        return line

    def draw(self, screen):
        # clear screen
        screen.clear()

        y, x = 1, 1 # start point
        max_y, max_x = screen.getmaxyx()
        middle_y, middle_x = int(max_y/2), int(max_x/2)
        max_rows = max_y - y # max draws we can draw

        lines, current_line = self.get_lines()

        # calculate how many line we should scroll, relative to the top
        if current_line <= self.scroll_top:
            self.scroll_top = 0
        elif current_line - self.scroll_top > max_rows:
            self.scroll_top = current_line - max_rows

        lines_to_draw = lines[self.scroll_top : self.scroll_top + max_rows]

        for line in lines_to_draw:
            line_name = str(line)
            max_line_length = middle_x - 2
            
            if len(line_name) > max_line_length:
                line_name = line_name[:max_line_length-3] + '...'

            screen.addnstr(y, x, line_name, max_line_length)
            y += 1

        # item description
        y = 1
        item = self.items[self.index]
        if type(item) in [Channel, Video]:
            name = self.crop_line_to_limit(item.name, middle_x-2)
            if type(item) == Channel:
                watched_string = f' [{item.get_count_of_watched_videos()}/{len(item.videos)}]'
                screen.addnstr(y, middle_x, name + watched_string, max_x-2)
                y += 1

                subs_string = self.crop_line_to_limit(f'Subscribes: {item.subscribes}', middle_x-4)
                screen.addnstr(y, middle_x+2, subs_string, max_x-2)
            elif type(item) == Video:
                screen.addnstr(y, middle_x, name, max_x-2)
                y += 1

                author_str = self.crop_line_to_limit(f'Author: {item.author}', middle_x-4)
                screen.addnstr(y, middle_x+2, author_str, max_x-2)
                y += 1

                shared_string = self.crop_line_to_limit(f'Shared: {item.shared}', middle_x-4)
                screen.addnstr(y, middle_x+2, shared_string, max_x-2)
                y += 1

                views_string = self.crop_line_to_limit(f'Views: {item.views}', middle_x-4)
                screen.addnstr(y, middle_x+2, views_string, max_x-2)

        screen.refresh()

    def run_loop(self, screen):
        while True:
            self.draw(screen)
            
            # get pressed keys
            c = screen.getch()
            if c in KEYS_UP:
                self.move_up()
            elif c in KEYS_DOWN:
                self.move_down()
            elif c in KEYS_ENTER:
                return self.get_selected()

    def init_curses(self):
        # use the default colors of the terminal
        curses.use_default_colors()
        # hide the cursor
        curses.curs_set(0)

        curses.initscr()

    def _start(self, screen):
        self.init_curses()
        return self.run_loop(screen)

    def start(self):
        return curses.wrapper(self._start)

def pick(title='', items=[], indicator='->'):
    picker = Picker(title, items, indicator)
    
    return picker.start()

if __name__ == '__main__':
    pick('Test picker', [Channel('kisa'), 'Penis', Video('pisya')])
