
import tkinter as GUI

if __name__ == "__main__":

    # 建立主視窗和 Frame（把元件變成群組的容器）
    window = GUI.Tk()
    window.title('分心檢測視窗')
    window.geometry('800x600')
    window.configure( background='gray' )
    
    main_frame = GUI.Frame(window)

    # 將元件分為 top/bottom 兩群並加入主視窗
    main_frame.pack()
    bottom_frame = GUI.Frame(window)
    bottom_frame.pack( side = GUI.BOTTOM )

    # 建立事件處理函式（event handler），透過元件 command 參數存取
    def echo_hello():
        print('hello world :)')

    # 以下為 top 群組
    left_button = GUI.Button(main_frame, text='Red', fg='red')
    # 讓系統自動擺放元件，預設為由上而下（靠左）
    left_button.pack( side = GUI.LEFT )

    # 以下為 bottom 群組
    # bottom_button 綁定 echo_hello 事件處理，點擊該按鈕會印出 hello world :)
    bottom_button = GUI.Button(bottom_frame, text='Black', fg='black', command=echo_hello)
    # 讓系統自動擺放元件（靠下方）
    bottom_button.pack( side = GUI.BOTTOM )

    # 運行主程式
    window.mainloop()

    pass