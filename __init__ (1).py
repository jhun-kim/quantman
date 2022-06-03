from PyQt5.QtWidgets import *
import sys,pickle
from PyQt5 import uic, QtWidgets ,QtCore, QtGui
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QAxContainer import * #키움 api를 실행해서 제어할려면 pyqt를 사용해야 한다. 
from PyQt5.QtCore import * #이벤트 루프를 사용하기 위한(동시성 처리를 위해)
# from config.errorCode import *
# from config.kiwoomtype import *
# from config.log_class import *
import pandas as pd
import time
from sqlalchemy import create_engine
import pymysql
import sys
import os
import math
from time import sleep

from data_visualise import data_
# import requests

###############################################################################################################




class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi('mainwindow.ui' , self)

        global data__
        data__ = data_()

        self.show()


        # Base
        self.columns = self.findChild(QListWidget, "column_list")
        self.list_account=self.findChild(QListWidget,"list_account")
        self.list_signal=self.findChild(QListWidget,"list_signal")
        self.list_ready=self.findChild(QListWidget,"list_ready")
        self.list_own=self.findChild(QListWidget,"list_own")
        self.list_sell=self.findChild(QListWidget,"list_sell")

        self.list_account_()

##############################################################################################

    def list_account_(self):
        self.columns.clear()       
        self.columns_list = []
        self.columns_list.append(f'예수금 : {int(deposit)}')
        self.columns_list.append(f'출금가능 금액 : {int(ok_deposit)}')
        self.columns_list.append(f'주문가능금액 : {int(available_deposit)}')
        self.columns_list.append(f'총매입금액 : {total_buy_money_result}')
        self.columns_list.append(f'총평가금액 : {total_value_money_result}')
        self.columns_list.append(f'총수익률(%) : {total_profit_loss_rate_result}')
        # print(self.columns_list)

        for i, j in enumerate(self.columns_list):
            # print(i, j)
            self.columns.insertItem(i, j)

        self.list_account__()

    def list_account__(self):
        self.list_account.clear()
        self.list_account.addItems(self.columns_list)

        self.list_signal_()

##############################################################################################

    def list_signal_(self):

        sleep(1)

        self.columns.clear()       
        self.columns_list = []
        
        for i in range(len(data_s)):
            self.columns_list.append(f'{data_s[i]}')
        # print(self.columns_list)

        for i, j in enumerate(self.columns_list):
            # print(i, j)
            self.columns.insertItem(i, j)
        
        self.list_signal__()

    def list_signal__(self):

        self.list_signal.clear()
        self.list_signal.addItems(self.columns_list)
        
       

        self.list_ready_()

##############################################################################################

    def list_ready_(self):

        sleep(1)

        # for i, j in enumerate(_list_signal_):
            # print(i, j)

        self.columns.clear()       
        self.columns_list = []

        for i in range(len(data_s)):    
            if float(data_s[i][4]) >= 10 and float(data_s[i][4]) < 15:
                self.columns_list.append(f'{data_s[i][1]} // {data_s[i][4]}')

        for i, j in enumerate(self.columns_list):
            # print(i, j)
            self.columns.insertItem(i, j)
 
        self.list_ready__()

    def list_ready__(self):
    
        self.list_ready.clear()
        self.list_ready.addItems(self.columns_list)


        self.list_own_()
        

##############################################################################################
        
    def list_own_(self):
        self.columns.clear()       
        self.columns_list = []

        sleep(1)

        for i in range(len(data_o)):
            self.columns_list.append(f'{data_o[i]}')
        # print(self.columns_list)

        for i, j in enumerate(self.columns_list):
            # print(i, j)
            self.columns.insertItem(i, j)

        self.list_own__()

    def list_own__(self):
        self.list_own.clear()
        self.list_own.addItems(self.columns_list)

        # self.list_sell_()
        # delay_time = 5
        # time.sleep(delay_time) 


##############################################################################################
        
    # def list_sell_(self):
    #     self.columns.clear()       
    #     self.columns_list = []

    #     sleep(1)

    #     for i in range(len(data_o)):
    #         self.columns_list.append(f'{sell_success}')
    #     # print(self.columns_list)

    #     for i, j in enumerate(self.columns_list):
    #         # print(i, j)
    #         self.columns.insertItem(i, j)

    #     self.list_sell__()

    # def list_sell__(self):
    #     self.list_sell.clear()
    #     self.list_sell.addItems(self.columns_list)

    #     self.list_account_()



###############################################################################################################
# SQL

# engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
#                 .format(host="ls-a20f4420f7aa9967e25c1e0aecf4d8b641af5f13.cgtgapkuvqbt.ap-northeast-2.rds.amazonaws.com",
#                         user="dbmasteruser",
#                         pw="r,3Ipn|O7mL2vL4S)9Q~;7QVdHMV6R9j",
#                         db='upper_signal'))

###############################################################################################################
TR_REQ_TIME_INTERVAL = 0.5


# exit_flag = False
class Kiwoom(QAxWidget):   # OpenAPI+가 제공하는 메서드를 호출하려면 QAxWidget 클래스의 인스턴스가 필요
    def __init__(self):
        super().__init__()
        
        
        
        self.detail_account_info_event_loop = QEventLoop()
        self.login_event_loop = QEventLoop()
        self.buy_event_loop = QEventLoop()
        self.sell_event_loop = QEventLoop()
    
        self.screen_my_info = '2000'
        self.account_stock_dict = {}
        
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConnect()
        
        
        
        # self.reach_to_high()
        # self.bring_me_up()
        # self.real_event_slots()
        
        # self.request_sector_index()
        # self.stock_basic()
        self.get_account_info()
        self.detail_account_info()
        self.detail_account_mystock()  

        self.bring_me_up()
          
        # mytoken = "xoxb-3162802854482-3186677393312-9bBUtFVVEeTjjBye4CQxoZ07"
            
        # self.post_message('xoxb-3162802854482-3186677393312-9bBUtFVVEeTjjBye4CQxoZ07',"#stock", f"나의 보유잔고: {self.get_account_info}")
        # self.post_message('xoxb-3162802854482-3186677393312-9bBUtFVVEeTjjBye4CQxoZ07',"#stock", f"나의 보유잔고: {self.get_account_info}")

           
        
        
        
        ######################################################################
            
        # self.buy_order() 
        # self.sell_order()                               
                
                
    # def post_message(token, channel, text):
    #     response = requests.post("https://slack.com/api/chat.postMessage",
    #     headers={"Authorization": "Bearer "+token},
    #     data={"channel": channel,"text": text}
    #     )
    #     print(response)

       
    # def dbgout(message):
    #     """인자로 받은 문자열을 파이썬 셸과 슬랙으로 동시에 출력한다."""
    # print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    # strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    # post_message(mytoken,"#stock", strbuf)
    
    # def printlog(message, *args):
    #     """인자로 받은 문자열을 파이썬 셸에 출력한다."""
    # print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)
    
    
    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        
        
        
    def event_slots(self): #로그인 함수
        self.OnEventConnect.connect(self.login_slot) #로그인에 대한 이벤트, 결과값이 스롯으로 출력
        self.OnReceiveTrData.connect(self.trdata_slot) 
    
    def real_event_slots(self):
        self.OnReceiveRealData.connect(self.handler_real_data)            
        
        
    def signal_login_commConnect(self): #
        self.dynamicCall("CommConnect()")         
        self.login_event_loop.exec_()
        
        
    
    
    
    
    def login_slot(self, erroCode):
        # print(errors(erroCode))
        if erroCode == 0:
            print("0")
        
        self.login_event_loop.exit()
    
    
    
    
    
    def get_account_info(self): #계좌번호
        account_list  = self.dynamicCall('GetLogininfo(QString)', 'ACCNO')
        self.account_num = account_list.split(";")[0]
        print('나의 보유 계좌번호 %s' %self.account_num)
        asdd = self.account_num
        
        return asdd
    

    
    
    
    
    

       
    def bring_me_up(self):
        print('상하한가요청') #요청만     
        
        self.dynamicCall('SetInputValue(String, String)', '시장구분', "000")
        self.dynamicCall('SetInputValue(String, String)', '상하한구분', '2')
        self.dynamicCall('SetInputValue(String, String)', '정렬구분', '3')
        self.dynamicCall('SetInputValue(String, String)', '종목조건', '1')
        self.dynamicCall('SetInputValue(String, String)', '거래량구분', '00300')
        self.dynamicCall('SetInputValue(String, String)', '신용조건', '0')
        self.dynamicCall('SetInputValue(String, String)', '매매금구분', '0')
        self.dynamicCall('CommRqData(String, String, Int, String)', '상하한가요청', 'opt10017', "0", self.screen_my_info)


        self.login_event_loop.exit()
        # self.detail_account_info_event_loop.exec_()
        
        
    def reach_to_high(self):
        print('고가근접요청') #요청만     
        
        self.dynamicCall('SetInputValue(String, String)', '고저구분', "1")
        self.dynamicCall('SetInputValue(String, String)', '근접율', '15')
        self.dynamicCall('SetInputValue(String, String)', '시장구분', '000')
        self.dynamicCall('SetInputValue(String, String)', '거래량구분', '00000')
        self.dynamicCall('SetInputValue(String, String)', '종목조건', '0')
        self.dynamicCall('SetInputValue(String, String)', '신용조건', '0')
        
        self.dynamicCall('CommRqData(String, String, Int, String)', '고저가근접요청', 'OPT10018', "0", self.screen_my_info)
        
        # QEventLoop().exec_()
        
    
    
    
        
        
        
    def detail_account_info(self):
        # print('예수금 요청하는 부분') #요청만     
        
       
        self.dynamicCall('SetInputValue(String, String)', '계좌번호', self.account_num)
        self.dynamicCall('SetInputValue(String, String)', '비밀번호', '0000')
        self.dynamicCall('SetInputValue(String, String)', '비밀번호 입력매체 구분', '00')
        self.dynamicCall('SetInputValue(String, String)', '조회구분', '2')
        self.dynamicCall('CommRqData(String, String, Int, String)', '예수금상세현황요청', 'opw00001', "0", self.screen_my_info)
        
        self.login_event_loop.exec_()
        
        
        
    def detail_account_mystock(self, sPrevNext = '0'):
        print('계좌평가잔고내역요청')
        self.dynamicCall('SetInputValue(String, String)', '계좌번호', self.account_num)
        self.dynamicCall('SetInputValue(String, String)', '비밀번호', '0000')
        self.dynamicCall('SetInputValue(String, String)', '비밀번호 입력매체 구분', '00')
        self.dynamicCall('SetInputValue(String, String)', '조회구분', '2')
        self.dynamicCall('CommRqData(String, String, Int, String)', '계좌평가잔고내역요청', 'opw00018', sPrevNext, self.screen_my_info)
                
        self.detail_account_info_event_loop.exec_()
        
    # def request_sector_index(self, sPrevNext = '0'):
    #     print('업종현재가요청')
    #     self.dynamicCall('SetInputValue(String, String)', "시장구분", "1")
    #     self.dynamicCall('SetInputValue(String, String)', "업종코드", "201")             
    #     self.dynamicCall("CommRqData(QString, QString, int, QString)", '업종현재가요청', 'opt20001', sPrevNext, self.screen_my_info)
    
    #     self.detail_account_info_event_loop.exec_()
        
    def handler_real_data(self, code, REALTYPE, real_data):
        if REALTYPE == "주식체결":
            code = self.GetCommRealData(code, 567) 
            # open = self.GetCommRealData(code, 16) 
            # high = self.GetCommRealData(code, 17) 
            # low  = self.GetCommRealData(code, 18) 
            # close= self.GetCommRealData(code, 10)
            print(code)
            
    def GetCommRealData(self, code, fid):
        data = self.dynamicCall("GetCommRealData(QString, int)", code, fid)
        print(data)
        return data
                                        
                
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        
        global deposit, ok_deposit, available_deposit, total_buy_money_result, total_value_money_result, total_profit_loss_rate_result, data_s, data_o, use_money, cnt

        if sRQName == '예수금상세현황요청' :
            deposit = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '예수금')
            print(f'예수금 : {int(deposit)}')
            
            # self.use_money = int(deposit) * self.use_money_percent
            # self.use_money = self.use_money / 4 #한종목 살때 

            use_money = int(deposit) 
            #* 0.5
            # use_money = use_money / 10
            
            
            
            ok_deposit = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '출금가능금액')
            print(f'출금가능 금액 : {int(ok_deposit)}')
            
            available_deposit = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '주문가능금액')
            print(f'주문가능금액 : {int(available_deposit)}')
            
            self.login_event_loop.exit()



        if sRQName == '상하한가요청' :
            rows = self.dynamicCall('GetRepeatCnt(QString, QString)', sTrCode, sRQName)     
            print(rows)

            data_s =[]
            for i in range(rows):
                code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목코드')
                code_name = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목명')
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                fluctuation_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "등락률")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")

                singal_ = code.strip(), code_name.strip(), stock_quantity.strip(), current_price.strip(), fluctuation_rate.strip(), learn_rate.strip()
                                                 
                data_s.append(singal_)
            print(f'{data_s}')
            delay_time = 3
            time.sleep(delay_time)

            # 발표1
            self.buy_order_()

            self.login_event_loop.exec_()
                      
        if sRQName == '계좌평가잔고내역요청':
                
            total_buy_money = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '총매입금액')
            total_buy_money_result = int(total_buy_money)
            
            print(f'총매입금액 : {total_buy_money_result}')
            
            total_value_money = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '총평가금액')
            total_value_money_result = int(total_value_money)
            
            print(f'총평가금액 : {total_value_money_result}')
            
            total_profit_loss_rate = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '총수익률(%)')
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            
            print(f'총수익률(%) : {total_profit_loss_rate_result}')
            
            rows = self.dynamicCall('GetRepeatCnt(QString, QString)', sTrCode, sRQName) #보유종목 카운트, 멀티데이터의 정보를 받아 온다.
            #최대 20개 밖에 카운트 못함, 20개 넘어가면 sPrevNext = 2 요청
            cnt = 0
            data =[]
            for i in range(rows): #계좌평가 잔고 내역
                code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목번호')
                code = code.strip()[1:]
                
                
                # code_name = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목명')
                # stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")  # 보유수량 : 000000000000010
                # buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")  # 매입가 : 000000000054100
                # learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")  # 수익률 : -000000001.94
                # current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 현재가 : 000000003450
                # total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                # possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")
                
                
                # if code in self.account_stock_dict:
                #     pass
                # else:
                #     self.account_stock_dict.update({code:{}})
                cnt += 1
                  

                
                
                
                
                # code_name = code_name.strip()
                # stock_quantity = int(stock_quantity.strip())
                # buy_price = int(buy_price.strip())
                # learn_rate = float(learn_rate.strip())
                # current_price = int(current_price.strip())
                # total_chegual_price = int(total_chegual_price.strip())
                # possible_quantity = int(possible_quantity.strip())
                
                
                
                data.append(code)
                # data.append(code_name)
                # data.append(stock_quantity)
                # data.append(buy_price)
                # data.append(learn_rate)
                # data.append(current_price)
                # data.append(total_chegual_price)
                # data.append(possible_quantity)
                
                
            print(f'계좌에 있는 종목 : {data}')    
            print(f'계좌에 가지고 있는 종목 : {cnt}')     
                
                
                
                # self.account_stock_dict[code].update({'종목명' : code_name})
                # self.account_stock_dict[code].update({'보유수량' : stock_quantity})
                # self.account_stock_dict[code].update({'매입가' : buy_price})
                # self.account_stock_dict[code].update({'수익률(%)' : learn_rate})
                # self.account_stock_dict[code].update({'현재가' : current_price})
                # self.account_stock_dict[code].update({'매입금액' : total_chegual_price})
                # self.account_stock_dict[code].update({'매매가능수량' : possible_quantity})
                
            data_o =[]
            for i in range(rows):   
                code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목번호')
                code_name = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목명')
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                fluctuation_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "등락률")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                

                own_ = code.strip()[1:], code_name.strip(), int(stock_quantity), int(current_price), fluctuation_rate.strip(), float(learn_rate)
                                                 
                data_o.append(own_)
            print(f'data_o : {data_o}')

            # 발표2
            # self.sell_order_()   
                   
            
            if sPrevNext == '2': # 계좌평가 잔고 내역에서 갯수가 20개 넘어가면 다음 장으로 넘기기 위함, 다음이 없으면 0으로 출력
                self.detail_account_mystock(sPrevNext='2')
            else:
                self.detail_account_info_event_loop.exit()
            
            self.detail_account_info_event_loop.exit()
                    
            
        
        
        
        
# 이상 조회        
############################################################################################################################################################################        
# 이하 매수 매도     
        
        
    # def buy_order(self):        
        
    #     buy_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
    #                            ["신규매수", self.screen_my_info, self.account_num, 1, "047810", 10000, 0, "03", ""])
                               
    #     print(f'신규매수: {buy_success}')
        
    #     self.login_event_loop.exec_()
        
        

    # def sell_order(self):
    #     sell_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", 
    #                                      ["신규매도", self.screen_my_info, self.account_num, 2, "047810", 10, 0, "03", ""])
                                         
    #     print(f'신규매도: {sell_success}')
        
    #     self.login_event_loop.exec_()



############################################################################################################################################################################
        
# 매수        

    def buy_order_(self):

        global buy_code, buy_q


        if int(available_deposit) > 0:
            for i in range(len(data_s)):
                if float(data_s[i][4]) >= 10 and float(data_s[i][4]) < 15:
                    buy_code = data_s[i][0]
                    buy_code = buy_code.strip()
                    buy_q = math.floor(int(use_money)/int(data_s[i][3]))

                    buy_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                ["신규매수", self.screen_my_info, self.account_num, 1, buy_code , buy_q, 0, "03", ""])

                    delay_time = 3
                    time.sleep(delay_time)
                    print(f'{data_s[i][1]} 매수 완료!')
            print(f'신규매수: {buy_success}')

        self.buy_event_loop.exec_()
    

# 매도

    def sell_order_(self):

        sleep(2)

        global sell_success, sell_code, sell_q

    
        for i in range(cnt):
            if float(data_o[i][5]) > 7 or float(data_o[i][5]) <= -3:

                sell_code = data_o[i][0]
                sell_code = sell_code.strip()
                # print(sell_code)
                sell_q = int(data_o[i][2])
                # print(sell_q)
                sell_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", 
                        ["신규매도", self.screen_my_info, self.account_num, 2, sell_code, sell_q, 0, "03", ""])

                delay_time = 0.5
                time.sleep(delay_time)
                print(f'{data_o[i][1]} 매도 완료!')                          
                # print(f'신규매도: {sell_success}')



        self.sell_event_loop.exec_()

#######################################################################
   

        
                        
                        
                        

  
        
       
        




from copy import copy


import sys
from PyQt5.QtWidgets import *

class Ui_class():
    def __init__(self):
        print('UI 클래스입니다.')
        
        
        self.app = QApplication(sys.argv)   
        
        self.kiwoom = Kiwoom()                  #키움 클래스를 불러옴  
        
        window=UI()
        window.show() 

        self.app.exec_()                         #종료 되지 않게 함









class Main(): #메인 클래스
    def __init__(self):
        print('실행할 메인 클래스')
        
        
        Ui_class()  #UI클래스를 불러옴
        
        
if __name__ =="__main__":
    Main()
    
    
    
    #1. 클래스 하나로 합치기
    #2. 모든 환경에 sql 활용 (보내는 것도, 받는 것도)
        #2-1 상한가 포착후 sql 보내기[[조회 당시의 종목코드]]
        #2-2 구매신호 sql 받아온 후 해당종목 구매[[받아온 종목코드와 1]]
        # 