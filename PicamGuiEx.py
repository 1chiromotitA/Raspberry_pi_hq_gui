import io
import math
import sys
import time
import tkinter
import tkinter as tk
import warnings
from datetime import datetime
from re import sub
from time import sleep
from tkinter import N, filedialog, messagebox, ttk

#warnings.filterwarnings('error', category=DeprecationWarning)
import cv2
import numpy as np
from picamera import PiCamera
from PIL import Image, ImageOps, ImageTk

# from tkinter import *
# from tkinter import ttk
#import tkinter as tk

WIDTH=832
HEIGHT=624 #1280*720,1920*1080,832*464,832*624,4056*3040
FPS=15 #Hqcamera limit
SUB=320
ZOOM=4
RECORD_RESOLUTION=(960,540) #録画フォーマットに合わせた解像度が必要　H264
log=0

#camera = PiCamera()

class GuiCamera(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        tk.Frame.__init__(self,master)
        master.title("CAMERA")
        master.attributes('-zoomed',True)#ウィンドウ幅に合わせて拡大

        self.master = master
        self.pack()
        self.update_idletasks()#ウィンドウを設置する前に.update_idletasks()を実行しておくことで事前にウインドウの情報を知ることができる

        w_width=self.get_winfo()[0]
        w_height=self.get_winfo()[1]
        self.canvas = tk.Canvas(self.master, width=WIDTH, height=HEIGHT)#解像度決め打ちなので必要なら変える
        self.canvas.bind('<Button-1>', self.mouse_canvas)
        
        self.WIDE_HEIGHT=int(WIDTH//16*9-WIDTH//16*9%16)#元解像度から録画中の高さを生成する　１６の倍数である必要がある
        self.canvas.clicked=(WIDTH//2,HEIGHT//2)#デフォルトでのマウス位置を設定
        
        self.canvas.place(x=0,y=0)
        self.sub_canvas = tk.Canvas(self.master, width=SUB, height=SUB)
        self.sub_canvas.place(x=850,y=150)#サブ画面

        self.buttun_frame = tk.Frame(self.master,width=SUB,height=100)        
        self.buttun_frame.pack_propagate(0)#ボタンの位置、幅を固定
        
        self.label_indicator=tk.Label(self.master,text="PINT_INDICATOR")
        self.indicator=tk.Canvas(self.master, width=SUB, height=40)
        self.indicator.place(x=850,y=520)#ピント合わせ用のゲージを設置する
        
        self.btn = tk.Button(self.master, text="start camera",command=self.canvas_start)
        self.btn.place(x=self.get_winfo()[0]/2-100,y=self.get_winfo()[1]/2-75,\
                       width=200,height=150)#スプラッシュ画面的なものとして設定　カメラの有無などを取得したいができなかった

        self.camera=PiCamera()
        self.camera.resolution=(WIDTH,HEIGHT)
        self.record_now=False#録画中かどうかによって若干画面レイアウトが変わるのでクラスインスタンスとして設定
     
        #self.canvas.bind('<Button-1>', self.canvas_click)

        #path="./"+datetime.now().strftime("%Y%m%d_%H%M%S")+".H264"
        self.rec_b=tk.Button(self.buttun_frame, text="@REC",command=self.rec_start)
        self.cap_b=tk.Button(self.buttun_frame, text="CAP",command=self.cap_image)
        self.close_b=tk.Button(self.buttun_frame, text="CLOSE",command=self.close_w)#ボタン類配置
    
    def mouse_canvas(self, event):#クリックされた位置を返す
        if self.record_now:
            self.canvas.clicked=None#録画中はリソース節約のために反応しない
        else:
            if event.x>SUB//2\
                and event.x <=WIDTH-SUB//2\
                and event.y >SUB//2\
                and event.y <=HEIGHT-SUB//2:
                self.canvas.clicked=(event.x,event.y)#描画領域がはみ出る場合は位置を変更しない
            else:
                return
        
    def get_path(self):#日時～秒までをパスとして生成する
        path="./"+datetime.now().strftime("%Y%m%d_%H%M%S")
        return(path)
       
    def get_winfo(self):#ウィンドウの大きさを取得
        #print(self.master.winfo_width(),",",self.master.winfo_height())
        return(self.master.winfo_width(),self.master.winfo_height())
    
    def main_camera(self):#カメラ画像を表示する　ピント合わせ用にクリックした点をズームして表示するサブ画面もつける
        global main#画面更新の際に画像のデータがgrobalでないと失敗するので用意
        global sub
        global forcus
        global log
        
        if self.record_now:
            output = np.empty(((self.WIDE_HEIGHT), (WIDTH),3), dtype=np.uint8)#画像格納用のndarrayを用意　幅が32高さが16の倍数である必要がある
            self.camera.capture(output, 'rgb',use_video_port=True,#usb_video_portをTrueにすることでリソースを節約する
                                resize=(WIDTH,self.WIDE_HEIGHT))
            height=self.WIDE_HEIGHT           
        else:
            output = np.empty(((HEIGHT), (WIDTH),3), dtype=np.uint8)#832,624
            self.camera.capture(output, 'rgb',use_video_port=True)
            height=HEIGHT
        output_p=Image.fromarray(output)#ndarrayに格納した画像をPILで使えるようにする

        #マウス位置に合わせてサブ画面を切り抜き
        if self.canvas.clicked is None:
            #forcus=output[(HEIGHT-SUB//2)//2:(HEIGHT+SUB//2)//2,\
            #       (WIDTH-SUB//2)//2:(WIDTH+SUB//2)//2]
            sub_p=output_p.crop(((WIDTH-SUB//2)//2,(height-SUB//2)//2,\
                  (WIDTH+SUB//2)//2,(height+SUB//2)//2))#録画中はリソース節約のためにマウス位置がデフォルトに設定されている
        else:
            forcus=output[self.canvas.clicked[1]-SUB//2:\
                          self.canvas.clicked[1]+SUB//2,\
                          self.canvas.clicked[0]-SUB//2:\
                          self.canvas.clicked[0]+SUB//2]#cv2で処理するために画像化せずに処理
            sub_p=output_p.crop((self.canvas.clicked[0]-SUB//ZOOM,\
                                self.canvas.clicked[1]-SUB//ZOOM,\
                                self.canvas.clicked[0]+SUB//ZOOM,\
                                self.canvas.clicked[1]+SUB//ZOOM,))#切り抜きの倍率はZOOMの値で管理される
         
        if self.record_now:#録画中はリソース節約
            pass
        else:
            gray = cv2.cvtColor(forcus, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)#グレースケール化
            log=log*0.6+0.4*math.log(laplacian.var(),4)#特徴量を取得し対数で管理 
            if log<0 or log>SUB:
                pass
            else:
                self.indicator.create_rectangle(0,0,SUB,40,
                                        width=10,fill="black")#バーグラフの背景
                self.indicator.create_rectangle(0,0,SUB*log//6,40,
                                        width=10,fill="blue")#特徴量の増減でバーが伸び縮みする
        
        main=ImageTk.PhotoImage(image=output_p)#メイン画像
        sub=ImageTk.PhotoImage(image=sub_p.resize((SUB,SUB)))#サブ画像
        if self.record_now:#録画中はプレビュー画面の縦幅が変わるので位置も調整する
            self.canvas.create_image(0,(HEIGHT-self.WIDE_HEIGHT)//2
                                     ,image=main ,anchor = tk.NW)         
        else:
            self.canvas.create_image(0,0,image=main ,anchor = tk.NW)         
        self.sub_canvas.create_image(0,0,image=sub ,anchor = tk.NW)

        #self.canvas.pack()
        self.after(3,self.main_camera)#画面更新
        
    def canvas_start(self):#各種ウィジェット配置
        sleep(2) 
        self.btn.place_forget()
        self.place_button()
        self.label_indicator.place(x=850,y=500)
        self.main_camera()
    
    def place_button(self):
        cell_x=self.get_winfo()[0]/10
        cell_y=self.get_winfo()[1]/10
        if self.record_now==False:
            self.rec_b=tk.Button(self.buttun_frame, text="REC",command=self.rec_start)
            self.rec_b.pack(expand=True,fill=tk.X,side=tk.LEFT)
        else:
            self.rec_b=tk.Button(self.buttun_frame, text="STOP",command=self.rec_stop)
            self.rec_b.pack(expand=True,fill=tk.X,side=tk.LEFT)
        self.cap_b.pack(expand=True,fill=tk.X,side=tk.LEFT)
        self.close_b.pack(expand=True,fill=tk.X,side=tk.LEFT)
        self.buttun_frame.pack(anchor=tk.E)
        
    def replace_button(self):
        self.rec_b.pack_forget()
        self.cap_b.pack_forget()
        self.close_b.pack_forget()
        self.place_button()
        
    def rec_start(self):
        self.camera.resolution=RECORD_RESOLUTION
        self.camera.start_recording(self.get_path()+".H264" ,quality=13)
        self.record_now=True
        self.canvas.clicked=None
        self.replace_button()

    def rec_stop(self):
        self.camera.stop_recording()
        self.camera.resolution=(WIDTH,HEIGHT)
        self.record_now=False
        self.replace_button()
        
    def cap_image(self):
        if self.record_now==False:
            self.camera.resolution=(4056,3040)
            self.camera.capture(self.get_path()+".jpeg")
            self.camera.resolution=(WIDTH,HEIGHT)
        else:
            self.camera.capture(self.get_path()+".jpeg",use_video_port=True)#録画中は録画の１フレームを切り抜く
    def close_w(self):
        if self.record_now==False:
            self.quit()
        else:
            self.rec_stop()#録画中なら停止して終了
            sleep(2)
            self.quit()

root=tk.Tk()
app=GuiCamera(master=root)
app.mainloop()

