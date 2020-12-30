from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import * 



# 原生 Python 程式
import threading    as THREAD
import time         as TIME
import os           as OS
import sys          as SYSTEM
import datetime     as DATETIME

# 頭部旋轉判斷程式
import head_rotation_detect as HEAD

# 取得ui檔案路徑
path = OS.getcwd()
# 設計好的ui檔案路徑
qtCreatorFile = path + OS.sep + "ui" + OS.sep + "mainView.ui"  
# 讀入用Qt Designer設計的GUI layout
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)   


# Python的多重繼承 MainUi 繼承自兩個類別
class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):
   
    # =========================================================
    # ======================= UI 主程式 ========================
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # 取得內部物件
        self.label_imageView        = self.findChild(QLabel, name='imageView')   # 圖片顯示 Label
        self.label_fpsVal           = self.findChild(QLabel, name='labelShow_FPS_Rate')         # 顯示 FPS 的 Label
        self.label_horizonVal       = self.findChild(QLabel, name='labelShow_Angle_Horizon')    # 顯示水平數值的 Label
        self.label_verticleVal      = self.findChild(QLabel, name='labelShow_Angle_Verticle')   # 顯示垂直數值的 Label
        self.label_headDirection    = self.findChild(QLabel, name='labelShow_Head_Direction')   # 目前頭部的轉向 Label

        self.label_horizonThreshold = self.findChild(QLabel, name='labelText_Angle_Threshold_Horizon')  # 顯示垂直閥值的 Label
        self.label_verticleThreshold= self.findChild(QLabel, name='labelText_Angle_Threshold_Verticle') # 顯示垂直閥值的 Label
        self.scrollBar_horizon      = self.findChild(QSlider, name='sliderBar_Threshold_Horizon')    # 水平閥值
        self.scrollBar_verticle     = self.findChild(QSlider, name='sliderBar_Threshold_Verticle')   # 垂直閥值
        self.label_focusRate        = self.findChild(QLabel, name='labelShow_Focus_Rate')        # 專注度

        # 初始化影片顯示區域
        self.initVideoEvent()
        
        
        self.update_flag = True     # 是否要繼續更新旗標
        self.fps_rate = 0           # FPS
        self.pre_time = TIME.time() # 取得目前時間

        self.hRotation          = 0 # 水平轉向值
        self.vRotation          = 0 # 垂直轉向值
        self.focus_count        = 0
        self.focus_timer        = 0

        # 多執行續，用來更新圖片
        thread = THREAD.Thread(target = self.update_Image, args=( ))
        thread.setDaemon(True)
        thread.start()

    def initVideoEvent(self):
        pixmap = QPixmap('image.jpg')
        self.label_imageView.setPixmap(pixmap)


    def updateUI_second(self):

        avg_hRotation = round( self.hRotation / self.fps_rate, 2)
        avg_vRotation = round( self.vRotation / self.fps_rate, 2)
        # 更新頭部旋轉數值
        self.label_horizonVal.setText(  str( avg_hRotation ) )
        self.label_verticleVal.setText( str( avg_vRotation ) )

        # 取得目前 ScrollBar 的值
        hThreshold = self.scrollBar_horizon.value()
        vThreshold = self.scrollBar_verticle.value()
        
        # 取得目前頭部的轉向
        (head_rotation, head_rotation_str) = HEAD.judge_look(horizon_angle       =avg_hRotation, vertical_angle    =avg_vRotation, 
                                                             horizon_threshold   =hThreshold   , vertical_threshold=vThreshold)
        
        # ------------------------------------------------------------
        rotation_str = '目前頭部方向： ' + str(head_rotation_str)
        self.label_headDirection.setText( rotation_str )

        self.hRotation = 0
        self.vRotation = 0

        # ------------------------------------------------------------
        if head_rotation == HEAD.LEFT or head_rotation == HEAD.RIGHT or head_rotation == HEAD.GONE:
            self.focus_count += 1
        self.focus_timer += 1

        self.label_focusRate.setText( str( round( (1 - (self.focus_count / self.focus_timer)) * 100, 2)  ) + '%' )
    
    # 更新影像函式
    def update_Image(self):
        # 開始偵測
        while self.update_flag:
            QtWidgets.QApplication.instance().processEvents()
            # ------------------------------------------------------------
            # 偵測頭部旋轉，並取得數值
            (horizon_angle, vertical_angle, cvimg) = HEAD.detect()

            try:
                # 更新影像
                image = QtGui.QImage(cvimg.data, cvimg.shape[1], cvimg.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                image = QtGui.QPixmap.fromImage( image )
                self.label_imageView.setPixmap(image)
            except:
                pass

            self.hRotation += horizon_angle
            self.vRotation += vertical_angle

            # ------------------------------------------------------------
            # 取得目前 ScrollBar 的值
            hThreshold = self.scrollBar_horizon.value()
            vThreshold = self.scrollBar_verticle.value()
            self.label_horizonThreshold.setText('水平閥值：     ' + str(hThreshold) )
            self.label_verticleThreshold.setText('垂直閥值：     ' + str(vThreshold) )

 

            # ------------------------------------------------------------    
            # 計算 FPS
            self.fps_rate += 1
            now_time = TIME.time()
            if (now_time - self.pre_time) > 1:
                self.updateUI_second()

                self.label_fpsVal.setText( str( self.fps_rate ) )
                self.fps_rate = 0
                self.pre_time = now_time

            



# =========================================================
# ======================= 啟動程式 ========================
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication( SYSTEM.argv )
        window = MainUi()
        window.show()
        app.exec_()

    run_app()