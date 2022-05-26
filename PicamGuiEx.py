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
RECORD_RESOLUTION=(960,540) #�^��t�H�[�}�b�g�ɍ��킹���𑜓x���K�v�@H264
log=0

#camera = PiCamera()

class GuiCamera(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        tk.Frame.__init__(self,master)
        master.title("CAMERA")
        master.attributes('-zoomed',True)#�E�B���h�E���ɍ��킹�Ċg��

        self.master = master
        self.pack()
        self.update_idletasks()#�E�B���h�E��ݒu����O��.update_idletasks()�����s���Ă������ƂŎ��O�ɃE�C���h�E�̏���m�邱�Ƃ��ł���

        w_width=self.get_winfo()[0]
        w_height=self.get_winfo()[1]
        self.canvas = tk.Canvas(self.master, width=WIDTH, height=HEIGHT)#�𑜓x���ߑł��Ȃ̂ŕK�v�Ȃ�ς���
        self.canvas.bind('<Button-1>', self.mouse_canvas)
        
        self.WIDE_HEIGHT=int(WIDTH//16*9-WIDTH//16*9%16)#���𑜓x����^�撆�̍����𐶐�����@�P�U�̔{���ł���K�v������
        self.canvas.clicked=(WIDTH//2,HEIGHT//2)#�f�t�H���g�ł̃}�E�X�ʒu��ݒ�
        
        self.canvas.place(x=0,y=0)
        self.sub_canvas = tk.Canvas(self.master, width=SUB, height=SUB)
        self.sub_canvas.place(x=850,y=150)#�T�u���

        self.buttun_frame = tk.Frame(self.master,width=SUB,height=100)        
        self.buttun_frame.pack_propagate(0)#�{�^���̈ʒu�A�����Œ�
        
        self.label_indicator=tk.Label(self.master,text="PINT_INDICATOR")
        self.indicator=tk.Canvas(self.master, width=SUB, height=40)
        self.indicator.place(x=850,y=520)#�s���g���킹�p�̃Q�[�W��ݒu����
        
        self.btn = tk.Button(self.master, text="start camera",command=self.canvas_start)
        self.btn.place(x=self.get_winfo()[0]/2-100,y=self.get_winfo()[1]/2-75,\
                       width=200,height=150)#�X�v���b�V����ʓI�Ȃ��̂Ƃ��Đݒ�@�J�����̗L���Ȃǂ��擾���������ł��Ȃ�����

        self.camera=PiCamera()
        self.camera.resolution=(WIDTH,HEIGHT)
        self.record_now=False#�^�撆���ǂ����ɂ���Ď኱��ʃ��C�A�E�g���ς��̂ŃN���X�C���X�^���X�Ƃ��Đݒ�
     
        #self.canvas.bind('<Button-1>', self.canvas_click)

        #path="./"+datetime.now().strftime("%Y%m%d_%H%M%S")+".H264"
        self.rec_b=tk.Button(self.buttun_frame, text="@REC",command=self.rec_start)
        self.cap_b=tk.Button(self.buttun_frame, text="CAP",command=self.cap_image)
        self.close_b=tk.Button(self.buttun_frame, text="CLOSE",command=self.close_w)#�{�^���ޔz�u
    
    def mouse_canvas(self, event):#�N���b�N���ꂽ�ʒu��Ԃ�
        if self.record_now:
            self.canvas.clicked=None#�^�撆�̓��\�[�X�ߖ�̂��߂ɔ������Ȃ�
        else:
            if event.x>SUB//2\
                and event.x <=WIDTH-SUB//2\
                and event.y >SUB//2\
                and event.y <=HEIGHT-SUB//2:
                self.canvas.clicked=(event.x,event.y)#�`��̈悪�͂ݏo��ꍇ�͈ʒu��ύX���Ȃ�
            else:
                return
        
    def get_path(self):#�����`�b�܂ł��p�X�Ƃ��Đ�������
        path="./"+datetime.now().strftime("%Y%m%d_%H%M%S")
        return(path)
       
    def get_winfo(self):#�E�B���h�E�̑傫�����擾
        #print(self.master.winfo_width(),",",self.master.winfo_height())
        return(self.master.winfo_width(),self.master.winfo_height())
    
    def main_camera(self):#�J�����摜��\������@�s���g���킹�p�ɃN���b�N�����_���Y�[�����ĕ\������T�u��ʂ�����
        global main#��ʍX�V�̍ۂɉ摜�̃f�[�^��grobal�łȂ��Ǝ��s����̂ŗp��
        global sub
        global forcus
        global log
        
        if self.record_now:
            output = np.empty(((self.WIDE_HEIGHT), (WIDTH),3), dtype=np.uint8)#�摜�i�[�p��ndarray��p�Ӂ@����32������16�̔{���ł���K�v������
            self.camera.capture(output, 'rgb',use_video_port=True,#usb_video_port��True�ɂ��邱�ƂŃ��\�[�X��ߖ񂷂�
                                resize=(WIDTH,self.WIDE_HEIGHT))
            height=self.WIDE_HEIGHT           
        else:
            output = np.empty(((HEIGHT), (WIDTH),3), dtype=np.uint8)#832,624
            self.camera.capture(output, 'rgb',use_video_port=True)
            height=HEIGHT
        output_p=Image.fromarray(output)#ndarray�Ɋi�[�����摜��PIL�Ŏg����悤�ɂ���

        #�}�E�X�ʒu�ɍ��킹�ăT�u��ʂ�؂蔲��
        if self.canvas.clicked is None:
            #forcus=output[(HEIGHT-SUB//2)//2:(HEIGHT+SUB//2)//2,\
            #       (WIDTH-SUB//2)//2:(WIDTH+SUB//2)//2]
            sub_p=output_p.crop(((WIDTH-SUB//2)//2,(height-SUB//2)//2,\
                  (WIDTH+SUB//2)//2,(height+SUB//2)//2))#�^�撆�̓��\�[�X�ߖ�̂��߂Ƀ}�E�X�ʒu���f�t�H���g�ɐݒ肳��Ă���
        else:
            forcus=output[self.canvas.clicked[1]-SUB//2:\
                          self.canvas.clicked[1]+SUB//2,\
                          self.canvas.clicked[0]-SUB//2:\
                          self.canvas.clicked[0]+SUB//2]#cv2�ŏ������邽�߂ɉ摜�������ɏ���
            sub_p=output_p.crop((self.canvas.clicked[0]-SUB//ZOOM,\
                                self.canvas.clicked[1]-SUB//ZOOM,\
                                self.canvas.clicked[0]+SUB//ZOOM,\
                                self.canvas.clicked[1]+SUB//ZOOM,))#�؂蔲���̔{����ZOOM�̒l�ŊǗ������
         
        if self.record_now:#�^�撆�̓��\�[�X�ߖ�
            pass
        else:
            gray = cv2.cvtColor(forcus, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)#�O���[�X�P�[����
            log=log*0.6+0.4*math.log(laplacian.var(),4)#�����ʂ��擾���ΐ��ŊǗ� 
            if log<0 or log>SUB:
                pass
            else:
                self.indicator.create_rectangle(0,0,SUB,40,
                                        width=10,fill="black")#�o�[�O���t�̔w�i
                self.indicator.create_rectangle(0,0,SUB*log//6,40,
                                        width=10,fill="blue")#�����ʂ̑����Ńo�[���L�яk�݂���
        
        main=ImageTk.PhotoImage(image=output_p)#���C���摜
        sub=ImageTk.PhotoImage(image=sub_p.resize((SUB,SUB)))#�T�u�摜
        if self.record_now:#�^�撆�̓v���r���[��ʂ̏c�����ς��̂ňʒu����������
            self.canvas.create_image(0,(HEIGHT-self.WIDE_HEIGHT)//2
                                     ,image=main ,anchor = tk.NW)         
        else:
            self.canvas.create_image(0,0,image=main ,anchor = tk.NW)         
        self.sub_canvas.create_image(0,0,image=sub ,anchor = tk.NW)

        #self.canvas.pack()
        self.after(3,self.main_camera)#��ʍX�V
        
    def canvas_start(self):#�e��E�B�W�F�b�g�z�u
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
            self.camera.capture(self.get_path()+".jpeg",use_video_port=True)#�^�撆�͘^��̂P�t���[����؂蔲��
    def close_w(self):
        if self.record_now==False:
            self.quit()
        else:
            self.rec_stop()#�^�撆�Ȃ��~���ďI��
            sleep(2)
            self.quit()

root=tk.Tk()
app=GuiCamera(master=root)
app.mainloop()

