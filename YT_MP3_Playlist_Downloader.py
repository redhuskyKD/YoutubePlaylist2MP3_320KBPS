import PySimpleGUI as sg
from sys import exit
from enum import Enum
from termcolor import colored
import os
import youtube_dl
import yt_dlp


class YtdlImpl(Enum):
    yt_dl = 1
    yt_dlp = 2


class MyLogger(object):
    @staticmethod
    def debug(msg):
        pass

    @staticmethod
    def warning(msg):
        print(msg)

    @staticmethod
    def error(msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ... \n\n')
    if d['status'] == 'downloading':
        progress_counter = int(float(d['_percent_str'][:-1]) / 5)
        print(colored('[' + u"\u2588" * progress_counter + '-' * (20 - progress_counter) + ']', 'red'), d['filename'],
              d['_percent_str'], d['_eta_str'])


def download_mp3_playlist(playlist_url, destination_path, youtube_dl_impl):
    ydl_opts = {
        'ignoreerrors': True,
        'WriteThumbnail': True,
        'download_archive': destination_path + '/already_downloaded_tracks.txt',
        'format': 'bestaudio/best',
        'outtmpl': destination_path + '/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        },
            {'key': 'FFmpegMetadata'},
        ],
        'logger': MyLogger(),
        'progress_hooks': [my_hook]
    }

    if youtube_dl_impl == YtdlImpl.yt_dlp:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
    elif youtube_dl_impl == YtdlImpl.yt_dl:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])


def load_path():
    file_path = sg.filedialog.askdirectory()
    return file_path


def cancel():
    exit()


def open_and_exit(url_destination):
    os.system('start ' + url_destination)
    exit()


def main():
    while True:
        sg.theme('LightGreen6')

        key_yt_url = 'yt_url'
        key_path = 'path'
        key_start_button = 'key_start_button'
        key_is_yt_dl = 'youtube-dl'
        key_is_yt_dlp = 'youtube-dlp (faster)'

        layout = [
            [sg.Text('Enter link of Youtube playlist:')],
            [sg.Input(key=key_yt_url, size=(100, 1), enable_events=True)],
            [sg.Text('')],
            [sg.Text('Choose folder to save files:')],
            [sg.Input(key=key_path, size=(100, 1), disabled=True, disabled_readonly_background_color='PaleGreen4',
                      enable_events=True), sg.Button(button_text="...")],
            [sg.Text('')],
            [sg.Text('Please select a youtube-dl implementation (DO NOT CHANGE UNLESS ERRORS POP-UP):')],
            [sg.Radio(key_is_yt_dl, "RADIO1", default=False, key=key_is_yt_dl, enable_events=True)],
            [sg.Radio(key_is_yt_dlp, "RADIO1", default=True, key=key_is_yt_dlp, enable_events=True)],
            [sg.Text('')],
            [sg.Button('Start', disabled=True, key=key_start_button, enable_events=True),
             sg.Button('Cancel')]
        ]
        window = sg.Window('Youtube MP3 Playlist Downloader', layout)

        def check_if_button_should_be_enabled():
            if window.Element(key_path).get() and window.Element(key_yt_url).get():
                return True
            else:
                return False

        while True:
            event, values = window.read()

            yt_url = window.Element(key_yt_url).get()
            path = window.Element(key_path).get()
            use_yt_dl_over_dlp = window.Element(key_is_yt_dl).get()

            if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                cancel()
            elif event == key_yt_url:
                window.Element(key_start_button).update(disabled=not check_if_button_should_be_enabled())
            elif event == '...':
                window.Element(key_path).update(load_path())
                window.Element(key_start_button).update(disabled=not check_if_button_should_be_enabled())
            elif event == key_start_button:
                window.close()
                break

        if use_yt_dl_over_dlp:
            download_mp3_playlist(yt_url, path, YtdlImpl.yt_dl)
        else:
            download_mp3_playlist(yt_url, path, YtdlImpl.yt_dlp)

        layout_2 = [
            [sg.Text('MP3 files exported successfuly.')],
            [sg.Button('Close'), sg.Button('Close and open folder'), sg.Button('Return')]
        ]

        window = sg.Window("Download finished!", layout_2)

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'Exit', 'Close'):
                cancel()
            elif event == 'Close and open folder':
                open_and_exit(path)
            elif event == 'Return':
                break

        continue


if __name__ == '__main__':
    main()
