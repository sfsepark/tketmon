#-*-coding:utf-8-*-

#-----------------------------------------
# tketmont chatbot - command module
# 
# sfsepark@gmail.com
#
# last change : 2017.05.14
#----------------------------------------

import re,time
import urllib.request
import chatbot
import pymysql

#sql injection 방지와 str.split 함수의 유니코드 깨짐 현상 개선
def parse(command) :
    p = re.compile('[_a-zA-Z0-9\uAC00-\uD7AF]+')
    return p.findall(command)

def message_to_channel(t_chatbot,row) :
    appeared_msg = ("앗! 야생의 " + row['tket_kor'] + 
         " 을(를) 발견했다!  " + row['tket_kor'][0] + " - 하!")
    t_chatbot.send_message(appeared_msg)

def give_tketmon_to_user(t_chatbot,row) :
    print("give_test")

def appear_tketmon(t_chatbot, user,streamer, tket_name) :
    
    query = ("SELECT * from tket_table where tket_kor = '" + tket_name + 
        "' or tket_eng = '" +tket_name + "'or tket_kor_ab = '" + tket_name + "'")
 
    t_chatbot.CUR.execute(query)
    rows = t_chatbot.CUR.fetchall()
    
    for row in rows:
        if(streamer != row['tket_eng']) :

            #방에 존재하는 트켓몬인지 체크
            print(t_chatbot.chatter_parser.viewers)
            for viewer in t_chatbot.chatter_parser.viewers :
                if( row['tket_eng'] == viewer) :
                    message_to_channel(t_chatbot,row)
                    give_tketmon_to_user(t_chatbot,row)
                    break;

