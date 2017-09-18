#-*-coding:utf-8-*-

#-------------------------------------------------
# tketmon chatbot - chatbot module
# 
# sfsepark@gmail.com
#
# last change : 2017.05.08
#-------------------------------------------------

import socket, string,time
import threading
import urllib.request
import pymysql
import queue

#packages
import command
import url_parser

def init_sql_conn():
    return pymysql.connect(host='localhost', user='tket_admin', password='3141592q', db='tket',charset='utf8')

def send_str(soc, string):
    soc.send(string.encode())

def recv_str(soc, buff_size):
    return soc.recv(buff_size).decode()

class Tket_chatbot:

    channel = ""
    
    CONN = init_sql_conn()
    CUR = CONN.cursor(pymysql.cursors.DictCursor)

    HOST = 'irc.chat.twitch.tv'
    PORT = 6667
    PASS = "oauth:6lyjpoevf55bxc8bvn317nwfqrl1jh"
    NICK = "tketmon"
 
    NOR_LIMIT_SIZE = 17
    MOD_LIMIT_SIZE = 97
    message_limit_queue = queue.Queue()
    message_limit = {'front':0, 'queue':message_limit_queue}

    URL_PARSE_INTERVAL = 20

    readbuffer = ""

    soc = socket.socket()

    def __init__(self, channel_str):
        self.channel = channel_str
        self.thread_queue = queue.Queue()
        self.chatter_parser = url_parser.Chatter_Parser(self.thread_queue,channel_str)

    def send_message(self, message, moderator = False) :

        #IRC message limit : moderator - 100 message per 30sec | not - 20 message per 30sec
        #moderator 가 아닐 때 message limit 을 넘으면 30분 타임 아웃.
        #따라서 message limit 을 넘으면 ignore (ignore 될 일이 많이 없도록 설계하는 것이 우선)

        LIMIT_SIZE = -1

        if(moderator == False) :
            LIMIT_SIZE = self.NOR_LIMIT_SIZE
        else :
            LIMIT_SIZE = self.MODE_LIMIT_SIZE

        if(self.message_limit['queue'].qsize() >= LIMIT_SIZE):
            if(self.message_limit['front'] == 0) :
                self.message_limit['front'] = self.message_limit['queue'].get()

        if(self.message_limit['front'] + 31 > time.time()) :
            return False

        if(self.message_limit['front'] != 0) :
            self.message_limit['front'] = 0
        self.message_limit['queue'].put(time.time())

        send_str(self.soc,"PRIVMSG #" + self.channel + " :" + message + "\r\n")
        return True


    def start(self):
    

        self.soc.connect((self.HOST, self.PORT))
        send_str(self.soc,"PASS " + self.PASS + "\r\n")
        send_str(self.soc,"NICK " + self.NICK + "\r\n")
        send_str(self.soc,"JOIN #"+ self.channel + " \r\n")

        #---parser_manage thread---
        #url을 파싱하여 필요한 정보를 따옴. 정보는 각 parser 오브젝트의 멤버에 저장
        def parser_manage(PARSE_INTERVAL) :
            
            while True :
                #URL_PARSE_INTERVAL 마다 필요한 URL 정보를 추출(스레딩)
                self.chatter_parser.run()
                           
                time.sleep(PARSE_INTERVAL)
         
                #url parser thread 종료 체크
                while(self.thread_queue.empty() == False) :
                    tmp_thread = self.thread_queue.get()
                    if(tmp_thread.is_alive() == True) :
                        tmp_thread.join()

        threading.Thread(target = parser_manage,args =(self.URL_PARSE_INTERVAL,)).start()


        #IRC 스트림에서 채팅 처리
        while True:
            self.readbuffer = self.readbuffer + recv_str(self.soc,1024)
            temp = str.split(self.readbuffer, "\n")
            self.readbuffer = temp.pop()

            for line in temp :
                if (line[0] == "PING"):
                    send_str(soc,"PONG %s\r\n" % line[1])
                else :
                    parts = str.split(line, ":")
                    if ("PRIVMSG" in parts[1]) :

                        #커맨드 체크
                        if (parts[2][0] == '!') :
                            command_token = command.parse(parts[2])
                        

                            #!트켓몬 XX

                            if(len(command_token) >= 2 and command_token[0] == '트켓몬') :
                                username = str.split(parts[1],"!")
                                USER = username[0]
                                STREAMER = self.channel
                                TKET_NAME = command_token[1]

                                command.appear_tketmon(self, USER, STREAMER, TKET_NAME)
