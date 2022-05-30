import sys
import datetime
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import time
import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QAxContainer import *
from PyQt5.QtTest import * #

from tqdm import tqdm




########################################################################################################################

#조회시간 정보 : https://kminito.tistory.com/35
TR_REQ_TIME_INTERVAL = 0.5

number = 72


class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        # Login 요청 후 서버가 발생시키는 이벤트의 핸들러 등록
        self.OnEventConnect.connect(self._on_event_connect)

        # 조회 요청 후 서버가 발생시키는 이벤트의 핸들러 등록
        self.OnReceiveTrData.connect(self._on_receive_tr_data)


    def _on_event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()


    def comm_connect(self):
        """Login 요청 후 서버가 이벤트 발생시킬 때까지 대기하는 메소드"""
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()


    def comm_rq_data(self, rqname, trcode, next, screen_no):
        """
        서버에 조회 요청을 하는 메소드
        이 메소드 호출 이전에 set_input_value 메소드를 수차례 호출하여 INPUT을 설정해야 함
        """
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

        # 키움 Open API는 시간당 request 제한이 있기 때문에 딜레이를 줌
        time.sleep(TR_REQ_TIME_INTERVAL)

    def comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def get_code_list_by_market(self, market):
        """market의 모든 종목코드를 서버로부터 가져와 반환하는 메소드"""
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        """종목코드를 받아 종목이름을 반환하는 메소드"""
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def get_connect_state(self):
        """서버와의 연결 상태를 반환하는 메소드"""
        ret = self.dynamicCall("GetConnectState()")
        return ret

    def set_input_value(self, input_dict):
        """
        CommRqData 함수를 통해 서버에 조회 요청 시,
        요청 이전에 SetInputValue 함수를 수차례 호출하여 해당 요청에 필요한
        INPUT 을 넘겨줘야 한다.
        """
        for key, val in input_dict.items():
            self.dynamicCall("SetInputValue(QString, QString)", key, val)

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def get_server_gubun(self):
        """
        실투자 환경인지 모의투자 환경인지 구분하는 메소드
        실투자, 모의투자에 따라 데이터 형식이 달라지는 경우가 있다. 대표적으로 opw00018 데이터의 소수점
        """
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

    def get_login_info(self, tag):
        """
        계좌 정보 및 로그인 사용자 정보를 얻어오는 메소드
        """
        ret = self.dynamicCall("GetLoginInfo(QString)", tag)
        return ret


    def on_receive_opt10080(kw: 'KiwoomAPI', rqname, trcode):
        """주식분봉차트조회요청 완료 후 서버에서 보내준 데이터를 받는 메소드"""

        data_cnt = kw.get_repeat_cnt(trcode, rqname)
        ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        for i in range(data_cnt):
            date = kw.comm_get_data(trcode, "", rqname, i, "체결시간")
            open = kw.comm_get_data(trcode, "", rqname, i, "시가")
            high = kw.comm_get_data(trcode, "", rqname, i, "고가")
            low = kw.comm_get_data(trcode, "", rqname, i, "저가")
            close = kw.comm_get_data(trcode, "", rqname, i, "현재가")
            volume = kw.comm_get_data(trcode, "", rqname, i, "거래량")

            ohlcv['date'].append(datetime.datetime.strptime(date, '%Y%m%d%H%M%S%f'))
            ohlcv['open'].append(abs(int(open)))
            ohlcv['high'].append(abs(int(high)))
            ohlcv['low'].append(abs(int(low)))
            ohlcv['close'].append(abs(int(close)))
            ohlcv['volume'].append(int(volume))

        return ohlcv

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next,
                            unused1, unused2, unused3, unused4):

        self.latest_tr_data = None

        if next == '2':
            self.is_tr_data_remained = True
        else:
            self.is_tr_data_remained = False

        if rqname == "opt10081_req": #일봉
            pass
            #self.latest_tr_data = KiwoomAPI.on_receive_opt10081(self, rqname, trcode)
        elif rqname == "opt10080_req": #분봉
            self.latest_tr_data = KiwoomAPI.on_receive_opt10080(self, rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

# C++과 python destructors 간의 충돌 방지를 위해 전역 설정
# garbage collect 순서를 맨 마지막으로 강제함
# 사실, 이 파일을 __main__으로 하지 않는경우에는 고려 안해도 무방
# app = None


# def main():
#     global app
#     app = QApplication(sys.argv)
#     kiwoom = KiwoomAPI()
#     kiwoom.comm_connect()
#     app.exec_()
    

# if __name__ == "__main__":
#     main()

##lineEdit는 코드인풋, lineEdit_2는 자동 이름변환

# form_class = uic.loadUiType("./Kiwoom_datareader-master/Kiwoom_datareader.ui")[0]


class MainWindow(QMainWindow): #, form_class
    def __init__(self):
        super().__init__()
        #self.setupUi(self)

        self.kw = KiwoomAPI()

        # login
        self.kw.comm_connect()

        # status bar 에 출력할 메세지를 저장하는 변수
        # 어떤 모듈의 실행 완료를 나타낼 때 쓰인다.
        # self.return_status_msg = ''

        # # timer 등록. tick per 1s
        # self.timer_1s = QTimer(self)
        # self.timer_1s.start(1000)
        # #self.timer_1s.timeout.connect(self.timeout_1s)

        # label '종목코드' 오른쪽 lineEdit 값이 변경 될 시 실행될 함수 연결
        #self.lineEdit.textChanged.connect(self.code_changed)

        # pushButton '실행'이 클릭될 시 실행될 함수 연결
        #self.pushButton.clicked.connect(self.fetch_chart_data)
        #클릭이 없으니 직접 입력함
        self.fetch_chart_data(number, final_list)

    # def timeout_1s(self):
    #     current_time = QTime.currentTime()

    #     text_time = current_time.toString("hh:mm:ss")
    #     time_msg = "현재시간: " + text_time

    #     state = self.kw.get_connect_state()
    #     if state == 1:
    #         state_msg = "서버 연결 중"
    #     else:
    #         state_msg = "서버 미 연결 중"

    #     if self.return_status_msg == '':
    #         statusbar_msg = state_msg + " | " + time_msg
    #     else:
    #         statusbar_msg = state_msg + " | " + time_msg + " | " + self.return_status_msg

    #     self.statusbar.showMessage(statusbar_msg)

    # label '종목' 우측의 lineEdit의 이벤트 핸들러
    def code_changed(self):
        code = self.lineEdit.text()
        name = self.kw.get_master_code_name(code)
        self.lineEdit_2.setText(name)


    def fetch_chart_data(self, number, final_list):
        for i in range(number-1, len(final_list)):        
            print(f'{i+1}번째 실행입니다!')
            lineEdit = final_list[i][1]
            exact_date = final_list[i][0]   
            # for i in tqdm(range(len(code_list)), desc='주식 출력 중:'):
            #시간측정
            start = time.time()

            code = lineEdit #self.lineEdit.text()
            name = self.kw.get_master_code_name(code)
            print(f'{name}_{code}_{exact_date}하는 중입니다...')
            tick_unit = '분봉' #일봉이냐 분봉이냐
            tick_range = 1 #분봉틱

            input_dict = {}
            ohlcv = None

            if tick_unit == '일봉':
                # 일봉 조회의 경우 현재 날짜부터 과거의 데이터를 조회함
                base_date = datetime.datetime.today().strftime('%Y%m%d')
                input_dict['종목코드'] = code
                input_dict['기준일자'] = base_date
                input_dict['수정주가구분'] = 1

                self.kw.set_input_value(input_dict)
                self.kw.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
                ohlcv = self.kw.latest_tr_data

                while self.kw.is_tr_data_remained == True:
                    self.kw.set_input_value(input_dict)
                    self.kw.comm_rq_data("opt10081_req", "opt10081", 2, "0101")
                    for key, val in self.kw.latest_tr_data.items():
                        ohlcv[key][-1:] = val

            elif tick_unit == '분봉':
                # 일봉 조회의 경우 현재 날짜부터 과거의 데이터를 조회함
                # 현 시점부터 과거로 약 160일(약 60000개)의 데이터까지만 제공된다. (2018-02-20)
                base_date = datetime.datetime.today().strftime('%Y%m%d')
                input_dict['종목코드'] = code
                input_dict['기준일자'] = exact_date
                input_dict['틱범위'] = tick_range
                input_dict['수정주가구분'] = 1

                self.kw.set_input_value(input_dict)
                self.kw.comm_rq_data("opt10080_req", "opt10080", 0, "0101")
                ohlcv = self.kw.latest_tr_data

                #기간내 인경우(True) 동안 일데이터 계속 append하기
                while self.kw.is_tr_data_remained == True:
                    self.kw.set_input_value(input_dict)
                    self.kw.comm_rq_data("opt10080_req", "opt10080", 2, "0101")
                    for key, val in self.kw.latest_tr_data.items():
                        ohlcv[key][-1:] = val
                        

            df = pd.DataFrame(ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df.date = pd.to_datetime(df.date,format='%Y-%m-%d %H:%M:%S')
            # df.set_index('date', drop=True,inplace = True)


            ##############################################################################
            #특정일 추출

            target_date = exact_date
            format = '%Y-%m-%d'
            dt_datetime = datetime.datetime.strptime(target_date,format)
            after_one_day = dt_datetime + datetime.timedelta(days=1)

            df_filered = df[df['date'].between(dt_datetime, after_one_day)]
            df_last = df_filered.set_index('date', drop=True)


            ##############################################################################
            #추출값 전처리 위해 분봉인덱싱 가져와서 해당일만 잘라내기

            _db = pymysql.connect(
                host=
                db=
                user = 
                password= 
                port = 3306)

            search_sql = "SELECT * From `min_index`"

            cursor = _db.cursor(pymysql.cursors.DictCursor)

            cursor.execute(search_sql)            
            result = cursor.fetchall() 

            min_table = pd.DataFrame(result)

            min_table_filered = min_table[min_table['date'].between(dt_datetime, after_one_day)]
            min_table_filered

            df_join = pd.merge(min_table_filered, df_last, how='left', on='date')
            df_join 
            df_join_2 = df_join.fillna(method='ffill')
            df_join_2

            ##############################################################################
            #

            from sqlalchemy import create_engine

            engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                            .format(host=,
                                    user=,
                                    pw=,
                                    db=))

            #if_exists: {'fail', 'replace', 'append'}
            df_join_2.to_sql(f'{lineEdit}_{exact_date}' , con = engine, if_exists = 'replace')

            print(f'{name} SQL로 보냈습니다...')
            print(f'{name} 소요 시간 : {(time.time() - start)}초')
            print("="*60)


###############################################################################################        
###############################################################################################      
###############################################################################################
# 기간별 상한가 간 종목 깍두기로 받아오기
import pymysql
import pandas as pd


table_name = '2022-01-01_2022-05-24'


_db = pymysql.connect(
    host=
    db=
    user = 
    password= 
    port = 3306)


search_sql = f"SELECT * From `{table_name}`"

cursor = _db.cursor(pymysql.cursors.DictCursor)

cursor.execute(search_sql)            
result = cursor.fetchall() 

data_table = pd.DataFrame(result)

def final_list_():
    #'=30'에서 notnull인 df만들기
    asd = data_table[data_table['=30'].notnull()]
    date_list = asd['date'].tolist()
    code_list = asd['code'].tolist()
    final_list = []
    for i in zip(date_list, code_list):
        final_list.append(i)
    return final_list

final_list = final_list_()

print("="*60)
print(f'총 {len(final_list)}개 입니다!')
print("="*60)

###############################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    

         
    mainWindow = MainWindow()
        #mainWindow.show()

    app.exec_()
    