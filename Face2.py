from tkinter import font
from tkinter.constants import TRUE
from typing import Text
import face_recognition
from cv2 import cv2
import numpy as np
import os
import mttkinter as tkinter
from telegram import update
import bot2
import sqlcode
import tkinter as tk
from PIL import Image,ImageTk
import time, requests
import threading as td
from _thread import start_new_thread
from datetime import datetime
from tkinter import messagebox
import setting
from ws4py.client.threadedclient import WebSocketClient
import logging



class DummyClient(WebSocketClient):
    def opened(self):
        None
    def closed(self, code, reason=None):
        print("NodeMCU Disconnected")

    def received_message(self, m):
        global tmr
       # global ws
        if(str(m)=="unlocked"):
            addlog("Door is successfully open for 10 second")
        elif(str(m) =="locked"):
            addlog("Door is successfully closed")
            if(setting.frisenable == 0):
                ws.send("lcd2/Face Detection/     Disabled")
            if(setting.frisenable == 2):
                setting.frisenable = 1
                ws.send("lcd2/Face Detection/    Ready")
        elif(str(m) =="stoptimer"):
            tmr.cancel()
            print("Timer is cancel")
           # ws.close()
#    def se

class PeriodicThread(object):
    """
    Python periodic Thread using Timer with instant cancellation
    """

    def __init__(self, callback=None, period=1, name=None, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.period = period
        self.stop = False
        self.current_timer = None
        self.schedule_lock = td.Lock()

    def start(self):
        """
        Mimics Thread standard start method
        """
        self.schedule_timer()

    def run(self):
        """
        By default run callback. Override it if you want to use inheritance
        """
        if self.callback is not None:
            self.callback()

    def _run(self):
        """
        Run desired callback and then reschedule Timer (if thread is not stopped)
        """
        try:
            self.run()
        except Exception:
            logging.exception("Exception in running periodic thread")
        finally:
            with self.schedule_lock:
                if not self.stop:
                    self.schedule_timer()

    def schedule_timer(self):
        """
        Schedules next Timer run
        """
        self.current_timer = td.Timer(self.period, self._run, *self.args, **self.kwargs)
        if self.name:
            self.current_timer.name = self.name
        self.current_timer.start()

    def cancel(self):
        """
        Mimics Timer standard cancel method
        """
        with self.schedule_lock:
            self.stop = True
            if self.current_timer is not None:
                self.current_timer.cancel()

    def join(self):
        """
        Mimics Thread standard join method
        """
        self.current_timer.join()



video_capture = cv2.VideoCapture("rtsp:///stream2")
esp8266host = "ws://doorlock.local:31725/"
ws = DummyClient(esp8266host)
t = td.Timer


    # Initialize some variables
options = ["STAFF","ADMIN"]
tempID = 0
def setenable1():
    userimage = []
    global known_face_names
    global known_face_encodings
    global process_this_frame
    global face_locations
    global face_encodings
    global face_names
    known_face_encodings = []
    known_face_names = []
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    os.chdir('FYP\picture')
    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)
    for getuserimage in files:
        userimage.append(face_recognition.load_image_file(getuserimage))
        known_face_names.append(getuserimage.split(".")[0])
    for userimg in userimage:
        known_face_encodings.append(face_recognition.face_encodings(userimg)[0])
    btn_enable.configure(state="disabled")
    btn_disable.configure(state="normal")
    btn_newuser.configure(state="disabled")
    btn_unlock.configure(state="disabled")
    setting.frisenable = 1
    ws.send("lcd2/Face Detection/    Ready")
    os.chdir('../../')
    addlog("Face Detection Enabled")
    

def setdisable1():
    setting.frisenable = 0
    btn_enable.configure(state="normal")
    btn_disable.configure(state="disabled")
    btn_newuser.configure(state="normal")
    btn_unlock.configure(state="normal")
    ws.send("lcd2/Face Detection/     Disabled")
    addlog("Face Detection Disabled")
    
def addnewuser():
    os.chdir('FYP\picture')
    ID = ID_box.get()
    name = username_box.get()
    upass = password_box.get()
    priv = clicked.get()
    data = [int(ID),name,upass,priv]
    check = sqlcode.insertnewuser(data)
    if(check == 1):
        ret, img = video_capture.read()
        cv2.imwrite(ID+".png", img)
        addlog(ID+" "+name+" have sucessfully added to the system")
    else:
        addlog(ID+" "+name+" Error adding new user")
    os.chdir('../../')

def addlog(log):
    logbox.configure(state="normal")
    logbox.insert(tk.END,"\n")
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logbox.insert(tk.END,dt_string + " : " + log, 'green')
    logbox.see('end')
    logbox.configure(state="disabled")

def delaydetect(tx):
    ws.send("lcd2/Unrecognized/     face")
    time.sleep(tx)
    ws.send("lcd2/Face Detection/    Ready")
    setting.frisenable = 1
    return

def timesup():
    global tmr
    global tempID
    if(setting.status != "success"):
        bot2.dispatcher.bot.send_message(chat_id=tempID,text="Times is up, Thank you")
        setting.status = "fail"
        setting.frisenable = 1
        tmr.cancel()
        ws.send("lcd2/Face Detection/    Ready")
        return

def settimer():
    #global tmr
    x=datetime.today()
    if(x.second+30 > 59 ):
        getsecond = x.second+30 - 59
        getminute = x.minute+1
        gethour = x.hour
        getday = x.day
        if(getminute > 59):
            gethour = x.hour+1
            getminute = 0
            if(gethour > 23):
                getday = x.day+1
                gethour = 0
            else:
                getday = x.day
        else:
            gethour = x.hour
    else:
        getsecond = x.second+30
        getminute = x.minute
        gethour = x.hour
        getday = x.day
    y=x.replace(day=getday, hour=gethour, minute=getminute, second=getsecond, microsecond=x.microsecond)
    delta_t=y-x
    secs = delta_t.seconds+1
    t = td.Timer(secs, timesup)
    t.start()


def createpiclog(pic):
    now = datetime.now()
    #dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dt_string = now.strftime("%d_%m_%Y")
    tm_string = now.strftime("%H_%M_%S")
    try:
        dir = 'FYP/Pictureslog/'+dt_string
        os.chdir(dir)
    except:
        dir = 'FYP/Pictureslog/'+dt_string
        os.mkdir(dir)
        os.chdir(dir)
    cv2.imwrite(tm_string+".png", pic)
    os.chdir('../../../')
    
    

def enablefr(frame):
    global tempID
    global tmr
    global process_this_frame
    #global ws
    #ws = DummyClient(esp8266host)
    # Enable facial recognition


    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                getnamesql = sqlcode.fetchname(name)
                createpiclog(frame)
                addlog("Sending Message to " + getnamesql[0])
                setting.frisenable = 0
                setting.status = ""
                bot2.msguser(name,ws)
                tmr.start()
                tempID = name
               # ws.connect()
                break

            #face_names.append(name)
            addlog(name + " Face")
            setting.frisenable = 0
            start_new_thread(delaydetect, (5,))
            break

    process_this_frame = not process_this_frame

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        ws.send("lcd2/Face Detection/    Disabled")
        ws.close()
        video_capture.release()
        cv2.destroyAllWindows()
        window.destroy()

def unlockdoor():
   # global ws
  #  ws = DummyClient(esp8266host)
   # ws.connect()
    ws.send("lcd2/Door Sucessfully/      Unlocked")
    ws.send("success")
    



if __name__ == '__main__':
    global tmr
    setting.init()
    while True:
        try:
            ws.connect()
            if(ws.handshake_ok):
                break
        except Exception as e:
            print("Try to connect with doorlock")
            print(f"\n{e}")
        else:
            time.sleep(1)
    
    bot2.dispatcher.add_handler(bot2.MessageHandler(bot2.Filters.text & ~bot2.Filters.command, bot2.echo))
    start_handler = bot2.CommandHandler('unlock', bot2.unlock)
    bot2.dispatcher.add_handler(start_handler)
    bot2.updater.start_polling(drop_pending_updates=True)
    tmr = PeriodicThread(timesup,30)
    window = tk.Tk()
    window.title("UnimapLab Security System") #Name For GUI window title
    window.rowconfigure(0, minsize=300, weight=1) #set minimum size for row window
    window.columnconfigure(1, minsize=200, weight=1) # set minimum size for column window

    secondfr = tk.Frame(master=window, width=200)
    btn_enable = tk.Button(master=secondfr, text="Enable Face Detection", command=setenable1,background='green') #login button , will call login function on clicked
    btn_disable = tk.Button(master=secondfr, text="Disable Face Detection", command=setdisable1,background='red') #login button , will call login function on clicked
    btn_unlock = tk.Button(master=secondfr, text="Manual Unlock Door", command=unlockdoor,background='red') #login button , will call login function on clicked)

    #first column of grid GUI
    secondfr.grid(row=0, column=0, sticky="nwse")
    btn_enable.grid(row=0, column=0, columnspan=2 , pady=5, padx=10)
    btn_disable.grid(row=1, column=0, columnspan=2, pady=5, padx=10)
    btn_disable.configure(state="disabled")
    btn_unlock.grid(row=2, column=0,columnspan=2, pady=5, padx=10)


    #second column of grid gui
    firstfr = tk.Frame(master=window,height=700)
    firstfr.grid(row=0, column=1, sticky="nsw")
    btn_newuser = tk.Button(master=firstfr, text="Add New User", command=addnewuser,background='yellow') #login button , will call login function on clicked


    clicked = tk.StringVar()
    clicked.set(options[0])
    drop = tk.OptionMenu(firstfr, clicked, *options)
    label1 = tk.Label(master=firstfr,text="This Section is used to add new user to the system")
    label2 = tk.Label(master=firstfr,text="User can obtain Telegram ID by requesting at @IDBot")
    label3 = tk.Label(master=firstfr,text="Telegram Chat ID : ")
    ID_box = tk.Entry(master=firstfr)
    username_box = tk.Entry(master=firstfr)
    password_box = tk.Entry(master=firstfr)
    label4 = tk.Label(master=firstfr,text="Name : ")
    label5 = tk.Label(master=firstfr,text="Privilege : ")
    label6 = tk.Label(master=firstfr,text="Password : ")
    label1.grid(row=2, column=0 ,sticky="nw" , pady=5)
    label2.grid(row=3, column=0 ,sticky="nw", pady=5)
    label3.grid(row=4, column=0 ,sticky="nw", pady=5)
    label4.grid(row=5, column=0 ,sticky="nw", pady=5)
    label6.grid(row=5, column=0 ,sticky="nw", pady=5, padx=250)
    label5.grid(row=6, column=0 ,sticky="nw", pady=5)
    ID_box.grid(row=4, column=0,padx=110, sticky="nw" ,pady=5)
    username_box.grid(row=5, column=0,padx=110, sticky="nw", pady=5)
    password_box.grid(row=5, column=0,padx=320, sticky="nw", pady=5)
    btn_newuser.grid(row=6, column=0,padx=320, sticky="nw", pady=5)
    drop.grid(row=6, column=0, padx=60, sticky="nw")



    #third column of grid gui
    thirdfr = tk.Frame(master=window,width=300)
    thirdfr.grid(row=0, column=2, sticky="nse")

    logbox = tk.Text(master=thirdfr)
    logbox.tag_config("white", foreground="white")
    logbox.tag_config("red", foreground="red")
    logbox.tag_config("green", foreground="#FFD700", font=font.BOLD)
    logbox.insert(tk.END,Text.upper("  Welcome to UniMAP Lab Security System, System log will be display here"), 'white')
    logscrollbar = tk.Scrollbar(master=thirdfr,orient="vertical", command=logbox.yview, width=30)
    logbox.configure( background="gray", yscrollcommand=logscrollbar.set)
    logbox.grid(column="0",row="0",sticky="n")
    logscrollbar.grid(column="0",row="0",sticky="nse")

    while True:
        #print('number of current threads is ', td.active_count())
        # Grab a single frame of video
        ret, frame = video_capture.read()
        #try:
        if(ret):
            if(setting.frisenable == 1):
                enablefr(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = ImageTk.PhotoImage(Image.fromarray(frame))
            showvideo = tk.Label(image=frame,master=firstfr)
            showvideo.grid(row=0, column=0, sticky="nwse")
            window.protocol("WM_DELETE_WINDOW", on_closing)
            window.update()
        else:
            window.protocol("WM_DELETE_WINDOW", on_closing)
            window.update()
        #except RuntimeError:
           # print()
           # break
        
        
        # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


