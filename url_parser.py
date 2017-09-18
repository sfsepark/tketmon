#-*-coding:utf-8-*-

#-------------------------------------------
# tketmon chatbot - URL Parsing modules
# 
# sfsepark@gmail.com
#
# last change : 2017. 05. 08
#-------------------------------------------

import threading
import urllib.request
import queue
import json

class Chatter_Parser(threading.Thread):

    viewers = []

    def __init__(self, thread_queue, channel) :
        super(Chatter_Parser,self).__init__()
        self.channel = channel
        self.thread_queue = thread_queue

    def run(self) :

        self.thread_queue.put(self)

        req = urllib.request.Request("https://tmi.twitch.tv/group/user/" \
             + self.channel + "/chatters")
        data = urllib.request.urlopen(req).read()
    
        jsondata = json.loads(data.decode("utf-8"))

        self.chatterdata = jsondata["chatters"]
        self.viewers = self.chatterdata["moderators"]
        self.viewers = self.viewers + self.chatterdata["staff"] 
        self.viewers = self.viewers + self.chatterdata["admins"]
        self.viewers = self.viewers + self.chatterdata["global_mods"]
        self.viewers = self.viewers + self.chatterdata["viewers"]
