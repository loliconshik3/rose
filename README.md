# Rose

# Archived on github. Updates available on: ```notabug.org/loliconshik3/rose```

Simple terminal-ui (TUI) youtube client.

## Feauters

* Simple subscribes

* Search videos and channels

* Watched videos history

* Youtube-like boxes interface

* Not use youtube for video parsing, only in youtube-dl

## How it works

### Subscribes
Rose parse your `subscribes.txt` file, then check `invidious` mirrors from `mirror` file, get first working mirror then parse channels and they videos. After that you can easy choice your favorite channel, video and play it with mpv.

## Dependencies

* Mpv video player

* youtube-dl (maybe, idk)

### On Arch Linux:
`sudo pacman -S mpv youtube-dl`

## Run
`python main.py` or `python3 main.py`
