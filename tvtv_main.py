import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from kiwoom import *

###### import kiwoom
###### MyWindow의 생성자에 넣어서 사용하면 됨

form_class = uic.loadUiType("tvtv_main_window.ui")[0]



class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()

        kw = Kiwoom()

        kw.comm_connect()

        self.setupUi(self)



def setupUI(self):
    pass





if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()


