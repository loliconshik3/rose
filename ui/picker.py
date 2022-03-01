import curses

import sys
sys.path.append("..")
from src.channel import Channel
from src.video import Video

KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_UP = (curses.KEY_UP, ord('k'))
KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
KEYS_LEFT = (curses.KEY_RIGHT, ord('h'))
KEYS_RIGHT = (curses.KEY_LEFT, ord('l'))
KEYS_BACKSPACE = (curses.KEY_BACKSPACE, )

class Picker:

    def __init__(self, title='', items=[], indicator='->'):
        self.title = title
        self.items = items
        self.indicator = indicator

        self.index = 0
        self.scroll_top = 0
        
        self.box_index = 0
        self.box_count_in_line = 4
        self.box_count_in_column = 4

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

    def is_items_contain_string(self):
        for item in self.items:
            if type(item) == str:
                return True

        return False

    def get_box_size(self, screen):
        max_y, max_x = screen.getmaxyx()
        return int(max_y / self.box_count_in_column), int(max_x / self.box_count_in_line)

    def get_line_index(self, index):
        return int((index-1) / self.box_count_in_line)

    def get_column_index(self, index):
        ind_x = index
        while ind_x > self.box_count_in_column:
            ind_x -= self.box_count_in_column
        return ind_x

    def get_box_start_location(self, screen, index):
        y, x = 1, 1
        max_y, max_x = screen.getmaxyx()
        box_height, box_width = self.get_box_size(screen)
        
        line_index = self.get_line_index(index)
        y = y + (box_height * line_index)

        column_index = self.get_column_index(index)-1
        x = x + (box_width * column_index) 
        
        if x <= 0: x = 1
        if y <= 0: y = 1

        return y, x

    def get_visible_box_list(self):
        grid_size = self.box_count_in_column * self.box_count_in_line
        grid_index = self.index
        while grid_index > grid_size-1:
            grid_index -= grid_size

        min_index = self.index - grid_index
        max_index = self.index + (grid_size - grid_index)
        items_length = len(self.items)
        
        if max_index > items_length:
            max_index -= max_index - items_length

        return self.items[min_index : max_index], grid_index

    def draw_channel(self, screen, item, grid_index):
        box_height, box_width = self.get_box_size(screen)
        start_y, start_x = self.get_box_start_location(screen, self.box_index)

        box = curses.newwin(box_height, box_width, start_y, start_x)
        
        if self.box_index-1 == grid_index:
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            box.bkgd(curses.color_pair(1))

        box.box()

        name = self.crop_line_to_limit(item.name, box_width-2)

        if item.isHasNewVideos: box.attron(curses.A_ITALIC)
        box.addstr(1, 1, name)
        if item.isHasNewVideos: box.attroff(curses.A_ITALIC)

        watched_string = f'Watched: {item.get_count_of_watched_videos()}/{len(item.videos)}'
        box.addstr(2, 3, watched_string)

        subs_string = self.crop_line_to_limit(f'Subscribes: {item.subscribes}', box_width-4)
        box.addstr(3, 3, subs_string)

        shared_str = self.crop_line_to_limit(f'Last video: {item.get_last_video_date()}', box_width-4)
        box.addstr(4, 3, shared_str)
        
        box.refresh()

    def draw_video(self, screen, item, grid_index):
        box_height, box_width = self.get_box_size(screen)
        start_y, start_x = self.get_box_start_location(screen, self.box_index)

        box = curses.newwin(box_height, box_width, start_y, start_x)
        
        if self.box_index-1 == grid_index:
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            box.bkgd(curses.color_pair(1))

        box.box()

        name = self.crop_line_to_limit(item.name, box_width-2)
        
        if not item.isWatched: box.attron(curses.A_BOLD) 
        if item.isNew: box.attron(curses.A_ITALIC)
        box.addstr(1, 1, name)
        if item.isNew: box.attroff(curses.A_ITALIC)
        if not item.isWatched: box.attroff(curses.A_BOLD)

        author_str = self.crop_line_to_limit(f'Author: {item.author}', box_width-4)
        box.addstr(2, 3, author_str)

        shared_string = self.crop_line_to_limit(f'Shared: {item.shared}', box_width-4)
        box.addstr(3, 3, shared_string)

        views_string = self.crop_line_to_limit(f'Views: {item.views}', box_width-4)
        box.addstr(4, 3, views_string)

        length_str = self.crop_line_to_limit(f'Length: {item.length}', box_width-4)
        box.addstr(5, 3, length_str)

        box.refresh()

    def draw(self, screen):
        # clear screen
        screen.erase()

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

        if self.is_items_contain_string():
            for line in lines_to_draw:
                line_name = str(line)
                max_line_length = middle_x - 2

                if len(line_name) > max_line_length:
                    line_name = line_name[:max_line_length-3] + '...'

                screen.addnstr(y, x, line_name, max_line_length)
                y += 1
        
            screen.refresh()
        else:
            screen.addnstr(0, middle_x - int(len(self.title)/2), self.title, max_x-2)
            screen.refresh()
            items, grid_index = self.get_visible_box_list()
            for item in items:
                self.box_index += 1
                if type(item) == Channel:
                    self.draw_channel(screen, item, grid_index)
                elif type(item) == Video:
                    self.draw_video(screen, item, grid_index)
            self.box_index = 0

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
            elif c in KEYS_BACKSPACE:
                return '..', -1

    def init_curses(self):
        # use the default colors of the terminal
        curses.use_default_colors()
        # hide the cursor
        curses.curs_set(0)

        curses.initscr()

    def _start(self, screen):
        self.init_curses()
        screen.idlok(False)
        screen.idcok(False)
        return self.run_loop(screen)

    def start(self):
        return curses.wrapper(self._start)

    def set_title(self, title):
        self.title = title
    
    def set_items(self, items):
        self.items = items

    def set_indicator(self, indicator):
        self.indicator = indicator

def pick(title='', items=[], indicator='->'):
    picker = Picker(title, items, indicator)
    
    return picker.start()
