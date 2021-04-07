from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget)
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import * 


# 原生 Python 程式
import threading    as THREAD
import os           as OS
import sys          as SYSTEM


# Zip File
import zipfile as ZIP

from NetCrawlerService  import NetCrawlerService
from obj.FlowLayout     import FlowLayout
from obj.ImageWidget    import ImageWidget


# 取得ui檔案路徑
path = OS.getcwd()
# 設計好的ui檔案路徑
qtCreatorFile = path + OS.sep + "ui" + OS.sep + "mainwindow.ui"  
# 讀入用Qt Designer設計的GUI layout
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)   


# Python的多重繼承 MainUi 繼承自兩個類別
class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):
            

    # =========================================================
    # ==================== UI main program ====================
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # 取得內部物件
        self.searchButton        = self.findChild(QPushButton, name='searchButton')    # 搜尋按鈕
        self.searchEditText      = self.findChild(QLineEdit, name='searchTextEdit')     # search text
        self.centerWidget        = self.findChild(QWidget, name='centerScrollAreaWidgetContents')   # image widget


        self.initialEvent()

    # 初始化影片顯示區域
    def pressSearch(self):
        # # downloading image
        # downloadUrl = 'https://www.mymypic.net/data/attachment/album/202103/30/134312jgtytf14jscepftu.gif'
        # data2 = URL_REQUEST.urlopen( downloadUrl ).read()
        # filePath = OS.getcwd() + OS.sep + "testImage.gif"
        # with open( filePath, 'wb' ) as localFile:
        #     localFile.write( data2 )


        # # Zip file
        # imageDataList = [ data1, data2 ]

        # zipPath = OS.path.join( OS.getcwd(), "test.zip")
        # with ZIP.ZipFile( zipPath, 'w' ) as zipFile1:
        #     zipFile1.writestr( 'image1.jpg', data1 )
        #     zipFile1.writestr( 'image2.gif', data2 )
        searchUrl = self.searchEditText.text()

        # check the url is legal
        if( searchUrl == "" ):
            return

        netImageList = NetCrawlerService().getData( searchUrl, [1, 2] )
        
        
        flowLayout = FlowLayout()
        # create center image
        for netImage in netImageList:
            flowLayout.addWidget( ImageWidget( netImage ) )
       

        self.centerWidget.setLayout( flowLayout )
     

    # inital all the event
    def initialEvent(self):
        self.searchButton.clicked.connect( self.pressSearch )




            


# =========================================================
# ======================= 啟動程式 ========================
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication( SYSTEM.argv )
        window = MainUi()
        window.show()
        app.exec_()

    run_app()