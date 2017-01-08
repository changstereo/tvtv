
from PyQt5 import uic
from kiwoom import *

#main window by designer import
form_class = uic.loadUiType("tvtv_main_window.ui")[0]

#main window class inherited from designer
class MyWindow(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.kw = Kiwoom()
        self.setupUi(self)

        self.pushButton_login.clicked.connect(self.pushButton_login_clicked)
        self.pushButton_view_by_code.clicked.connect(self.pushButton_view_by_code_clicked)
        self.pushButton_conbuy.clicked.connect(self.pushButton_conbuy_clicked)
        self.pushButton_consell.clicked.connect(self.pushButton_consell_clicked)

    def pushButton_login_clicked(self):
        self.kw.comm_connect()


    def pushButton_view_by_code_clicked(self):
        pass

    def pushButton_conbuy_clicked(self):
        pass

    def pushButton_consell_clicked(self):
        pass

#    def setupUI(self):
 #       pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()


