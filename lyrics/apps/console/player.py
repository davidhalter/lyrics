""" taken from pyradio """

import subprocess
import thread
import os


class Player(object):
    """ Media player class. Playing is handled by mplayer """
    process = None

    def __init__(self, outputStream):
        self.outputStream = outputStream

    def __del__(self):
        self.close()

    def updateStatus(self):
        try:
            user_input = self.process.stdout.readline()
            while(user_input != ''):
                self.outputStream.write(user_input)
                user_input = self.process.stdout.readline()
        except:
            pass

    def is_playing(self):
        return bool(self.process)

    def play(self, uri):
        """ use mplayer to play a stream """
        self.close()
        file_name = uri.split("?")[0] if uri.starts_with('http://') else uri

        is_play_list = file_name[-4:] in ('.m3u', '.pls')

        opts = ["mplayer", "-quiet", uri]
        if is_play_list:
            opts.insert(2, '-playlist')

        self.process = subprocess.Popen(opts, shell=False,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
        thread.start_new_thread(self.updateStatus, ())

    def sendCommand(self, command):
        """ send keystroke command to mplayer """
        if(self.process is not None):
            try:
                self.process.stdin.write(command)
            except:
                pass

    def mute(self):
        """ mute mplayer """
        self.sendCommand("m")

    def pause(self):
        """ pause streaming (if possible) """
        self.sendCommand("p")

    def close(self):
        """ exit pyradio (and kill mplayer instance) """
        self.sendCommand("q")
        if self.process is not None:
            os.kill(self.process.pid, 15)
            self.process.wait()
        self.process = None

    def volumeUp(self):
        """ increase mplayer's volume """
        self.sendCommand("*")

    def volumeDown(self):
        """ decrease mplayer's volume """
        self.sendCommand("/")
