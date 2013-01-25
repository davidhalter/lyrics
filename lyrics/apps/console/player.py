"""
taken from pyradio and modified
Playing is handled by mplayer
"""

import subprocess
import threading
import os


def popen_with_callback(on_exit=None, *args, **kwargs):
    """
    Normal suprocess.Popen that calls.
    """
    def run_in_thread(on_exit, *args, **kwargs):
        global process
        process = subprocess.Popen(*args, **kwargs)
        process.wait()
        process = None
        if on_exit is not None:
            return on_exit()

    thread = threading.Thread(target=run_in_thread, args=((on_exit,) + args),
                                                    kwargs=kwargs)
    thread.start()
    # returns immediately after the thread starts
    return thread


process = None
last_status = ''


def status():
    try:
        user_input = process.stdout.readline()
        while(user_input != ''):
            outputStream.write(user_input)
            user_input = process.stdout.readline()
    except:
        return None

def is_playing():
    return bool(process)

def play(uri, callback_on_finish):
    """ use mplayer to play a stream """
    global process
    close()
    file_name = uri.split("?")[0] if uri.startswith('http://') else uri

    is_play_list = file_name[-4:] in ('.m3u', '.pls')

    opts = ["mplayer", "-quiet", uri]
    if is_play_list:
        opts.insert(2, '-playlist')

    process = popen_with_callback(callback_on_finish, opts, shell=False,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
    #thread.start_new_thread(updateStatus, ())

def sendCommand(command):
    """ send keystroke command to mplayer """
    if(process is not None):
        try:
            process.stdin.write(command)
        except:
            pass

def mute():
    """ mute mplayer """
    sendCommand("m")

def pause():
    """ pause streaming (if possible) """
    sendCommand("p")

def close():
    """ exit pyradio (and kill mplayer instance) """
    global process
    sendCommand("q")
    if process is not None:
        os.kill(process.pid, 15)
        process.wait()
    process = None

def volumeUp():
    """ increase mplayer's volume """
    sendCommand("*")

def volumeDown():
    """ decrease mplayer's volume """
    sendCommand("/")
