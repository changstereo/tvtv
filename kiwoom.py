import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import time
from pandas import Series, DataFrame

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.OnEventConnect.connect(self.event_connect)
        self.OnReceiveTrData.connect(self.receive_tr_data)
        self.OnReceiveChejanData.connect(self.receive_order_data)
        self.OnReceiveMsg.connect(self.receive_msg)

    def receive_msg(self, scr_no, rq_name, tr_code, msg):
        print(scr_no, rq_name, tr_code, msg)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_loop = QEventLoop()
        self.login_loop.exec_()

    def event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("not connected")

        self.login_loop.exit()

    def get_codelist_by_market(self, market):
        func = 'GetCodeListByMarket("%s")' % market
        codes = self.dynamicCall(func)
        return codes.split(';')

    def get_master_code_name(self, code):
        func = 'GetMasterCodeName("%s")' % code
        name = self.dynamicCall(func)
        return name

    def get_login_info(self, tag):
        func ='GetLoginInfo("%s")' % tag
        ret = self.dynamicCall(func)
        return ret

    def get_chejan_data(self, fid):
        cmd = 'GetChejanData("%s")' % fid
        ret = self.dynamicCall(cmd)
        return ret

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, code, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, code, next, screen_no)
        self.tr_rq_loop = QEventLoop()
        self.tr_rq_loop.exec_()

    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga_type, org_order_no):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                          [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga_type, org_order_no])
        self.order_rq_loop = QEventLoop()
        self.order_rq_loop.exec_()

    def comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code, real_type,
                               field_name, index, item_name)
        return ret.strip()

    def receive_order_data(self, gubun, item, fid_list):
        print("called")
        print(self.get_chejan_data(9203))
        print(self.get_chejan_data(302))
        print(self.get_chejan_data(900))
        print(self.get_chejan_data(901))
        self.order_rq_loop.exit()

    def receive_tr_data(self, scrno, rqname, trcode, record_name, next, unused0, unused1, unused2, unused3):
        print("tr called")
        self.remained_data = next

        if rqname == "opt10081_req":
            cnt = self.get_repeat_cnt(trcode, rqname)

            for i in range(cnt):
                date    = self.comm_get_data(trcode, "", rqname, i, "일자")
                open    = self.comm_get_data(trcode, "", rqname, i, "시가")
                high    = self.comm_get_data(trcode, "", rqname, i, "고가")
                low     = self.comm_get_data(trcode, "", rqname, i, "저가")
                close   = self.comm_get_data(trcode, "", rqname, i, "현재가")
                volume  = self.comm_get_data(trcode, "", rqname, i, "거래량")

                if date >= self.start:
                    self.ohlcv['date'].append(date)
                    self.ohlcv['open'].append(int(open))
                    self.ohlcv['high'].append(int(high))
                    self.ohlcv['low'].append(int(low))
                    self.ohlcv['close'].append(int(close))
                    self.ohlcv['volume'].append(int(volume))

        elif rqname == "opt10001_req":
            self.pbr = self.comm_get_data(trcode, "", rqname, 0, "PBR")

        try:
            self.tr_rq_loop.exit()
        except:
            pass

    def get_repeat_cnt(self, code, record_name):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", code, record_name)
        return ret

    def get_daily_data(self, code, start, end):
        self.start = start
        self.ohlcv = {'date': [], 'open': [], 'high':[], 'low': [], 'close': [], 'volume': []}

        self.set_input_value("종목코드", code)
        self.set_input_value("기준일자", end)
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

        while self.remained_data == '2':
            time.sleep(0.2)
            self.set_input_value("종목코드", code)
            self.set_input_value("기준일자", end)
            self.set_input_value("수정주가구분", 1)
            self.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

        df = DataFrame(self.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'], index=self.ohlcv['date'])
        return df

    def get_pbr(self, code):
        self.set_input_value("종목코드", code)
        self.comm_rq_data("opt10001_req", "opt10001", 0, "0101")
        return self.pbr

    def buy(self, account, code, quantity, price, hoga_type):
        self.send_order("send_order_req", "0101", account, 1, code, quantity, price, hoga_type, "")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Test Code
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    account = kiwoom.get_login_info("ACCNO")
    account = account[:-1]
    print(account)

    kiwoom.buy(account, "003540", 10, 30000, "03")

