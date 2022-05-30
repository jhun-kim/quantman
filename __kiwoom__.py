from PyQt5.QAxContainer import * #키움 api를 실행해서 제어할려면 pyqt를 사용해야 한다. 
from PyQt5.QtCore import *
from matplotlib.style import available #이벤트 루프를 사용하기 위한(동시성 처리를 위해)
from config.errorCode import *
from config.kiwoomtype import *
from config.log_class import *
import pandas as pd
import time
import pymysql
from sqlalchemy import create_engine
import pandas as pd





TR_REQ_TIME_INTERVAL = 0.5


class KiwoomAPI(QAxWidget):   # OpenAPI+가 제공하는 메서드를 호출하려면 QAxWidget 클래스의 인스턴스가 필요
    def __init__(self):
        super().__init__()
        
        
        self._create_kiwoom_instance()
        self._set_signal_slots()
        self.comm_connect()
        
        # 이 두함수는 클라스가 실행되면 무조건 먼저 실행되야 하는 함수 
        
        
        
        self.on_receive_opw00001()
        # self.get_account_info()
        
        
        
    def _create_kiwoom_instance(self):
        '''#이건 키움 레지스트 폴더에 있는 키움 API 연결 파일
        #여기서 부터 시작 되어야 하기 때문에 생성자 영역에 들어가 있음'''
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        
        
        
        
    def _set_signal_slots(self):
        '''이 함수는 키움에서 접속을 원하는 함수 메개변수값으로 또 다른 함수를 받는데 이건 바래 아래에 나올 
        접속 확인, 에러코드 출력용 함수'''
        self.OnEventConnect.connect(self._on_event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        # 이 코드는 TR데이터 조회 연결 함수, 매개 변수 값으로 또 다른 함수를 연결
        
    
    
    
   
    def _on_event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()
        
    
    
    
    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
    
        if rqname == "opw00001_req":
            self.on_receive_opw00001(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass    
    
            
     
        
########################################################################################################################]
# 이 아래 부터는 이제 앞으로 필요한 키움 API 개발자 함수들을 함수화 시키는 영역



    def comm_connect(self):
        """Login 요청 후 서버가 이벤트 발생시킬 때까지 대기하는 메소드"""
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()
        
        
        
  
      
       
        
    def set_input_value(self, id, value):
        """
        CommRqData 함수를 통해 서버에 조회 요청 시,
        요청 이전에 SetInputValue 함수를 수차례 호출하여 해당 요청에 필요한
        INPUT 을 넘겨줘야 한다.
        """
        self.dynamicCall("SetInputValue(QString, QString)", id, value)   
        
        
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        # 이전에 내가 작업했을 때는 CommRqData 개발자 함수를 조회용 함수안에 INPUT값들과 같이 만들어 놨다. 
        # 함수의 매개변수들의 갯수와 CommRqData를 DYNAMICCALL로 부를 때 넣는 매개변수를 동일하게 해준다.
        # 같이 받아서 함수가 작동하게 할것이고, 이게 이 매개 변수를 받는 인자를 나중에 함수화 시키면 된다. 
        """
        서버에 조회 요청을 하는 메소드
        이 메소드 호출 이전에 set_input_value 메소드를 수차례 호출하여 INPUT을 설정해야 함
        """
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

        # 키움 Open API는 시간당 request 제한이 있기 때문에 딜레이를 줌
        time.sleep(TR_REQ_TIME_INTERVAL)    
        
        
    def detail_account_info(self):
        # print('예수금 요청하는 부분') #요청만     
        
       
        self.set_input_value("계좌번호", self.account_num)
        self.set_input_value("비밀번호", "0000")
        self.set_input_value("비밀번호 입력매체 구분", "00")
        self.set_input_value("조회구분", "2")
        self.comm_rq_data("opw00001_req", "opw00001", 0, "0101")
        
        self.login_event_loop.exec_()    
            
      
            
            
            
    
        
        
        
        
        
    def get_comm_data(self, trcode, rqname, next, real_name):
        ret = self.dynamicCall("GetCommData(QString, QString, QString, int, QString)", trcode, rqname,
                               next, real_name)
        return ret.strip()
        # 이 함수는 조회한 걸 요청할때 쓰는 함수 요청하면 값을 받을수 있는 함수 
        # 개발자 함수에는 trcode, trname, prenext, screennumber 만 있으면 된다.
        # 요구되는 매개변수, 인자 4개
        
        
    def get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret
    
    
    def on_receive_opw00001(self, rqname, trcode):
        '''주식 예수금상세현황요청 '''
        if rqname == 'opw00001_req' :
        
        
            deposit = self.get_comm_data(trcode, rqname, 0, '예수금')
            # deposit = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '예수금')
            # print(f'예수금 : {deposit.strip()}')
            print("예수금: " + int(deposit))
            
            ok_deposit = self.get_comm_data(trcode, rqname, 0, '출금가능금액' )
            # ok_deposit = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '출금가능금액')
            #     print(f'출금가능 금액 : {int(ok_deposit)}')
            # print(f'출금가능 금액 : {int(ok_deposit)}')
            
            available_deposit = self.get_comm_data(trcode, rqname, 0, '주문가능금액')
            # print(f'출금가능 금액 : {int(available_deposit)}')
        
        
        
    def get_account_info(self): #계좌번호
        account_list  = self.dynamicCall('GetLogininfo(QString)', 'ACCNO')
        self.account_num = account_list.split(";")[0]
        print('나의 보유 계좌번호 %s' %self.account_num)
        # asdd = self.account_num
        
        # return asdd
    
    
############################################################################################################################################################################        
# 이하 매수 매도     
        
        
        
        
    def buy_order(self):        
        
        buy_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                               ["신규매수", self.screen_my_info, self.account_num, 1, "047810", 10000, 0, "03", ""])
                               
        print(f'신규매수: {buy_success}')
        
        self.login_event_loop.exec_()
        
        

    # def sell_order(self):
    #     sell_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", 
    #                                      ["신규매도", self.screen_my_info, self.account_num, 2, "047810", 10, 0, "03", ""])
                                         
    #     print(f'신규매도: {sell_success}')
        
    #     self.login_event_loop.exec_()    
        
    
            
        
        
        
        
        
       
       
       
       
       
       
       
        
       
        

from copy import copy
# from kiwoom.Kiwoom import *                      #키움 모듈을 불러옴
import sys
from PyQt5.QtWidgets import *





class Ui_class():
    def __init__(self):
        print('UI 클래스입니다.')
        super().__init__()
        
        self.app = QApplication(sys.argv)
        self.kw = KiwoomAPI() #키움 클래스를 불러옴
        self.app.exec_()
        
        
        
        
        
        
        
    
        

# from ui.ui  import * #ui 모듈을 불러옴





class Main(): #메인 클래스
    def __init__(self):
        print('실행할 메인 클래스')
        
        
        Ui_class()  #UI클래스를 불러옴
        
    
    
    
if __name__ == "__main__":
   Main()
        

   
    
    
    