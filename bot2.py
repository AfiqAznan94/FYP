##!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.


from numpy import empty, split
import mttkinter as tkinter
import logging
from threading import Timer
from datetime import datetime
from typing import Text
from telegram import Update, ForceReply, chat, forcereply, message, update
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import sqlcode
import setting


# Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )

# logger = logging.getLogger(__name__)
updater = Updater("")
dispatcher = updater.dispatcher



def echo(update: Update, _: CallbackContext) -> None:
    global ws
    global ID
    if(ID == str(update.message.chat_id)):
        if(update.message.text == retpass[0]):
            setting.inside.append(ID)
            dispatcher.bot.send_message(chat_id=ID,text="Welcome "+retpass[1]+" Door will be unlocked, you have 10 second to enter")
            ws.send("lcd2/Door Sucessfully/      Unlocked")
            ws.send("success/br")
            setting.status = "success"
            setting.frisenable = 2
            time.sleep(2)
            dispatcher.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
            ID = 0
            #updater.stop()
        else:
            dispatcher.bot.send_message(chat_id=ID,text="Incorrect Password, please try again")
            time.sleep(2)
            dispatcher.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
            ID = 0
    

def unlock(update: Update, _: CallbackContext) -> None:
    for name in setting.inside:
        if(name ==  str(update.message.chat_id)):
            update.message.reply_text("Door will be unlock for 10 second")
            ws.send("lcd2/Door Sucessfully/      Unlocked")
            ws.send("success/br")
            setting.inside.remove(name)

def msguser(IDs,newws):
    global ws
    global ID
    global name1
    global retpass
    ID = IDs
    ws = newws
    dispatcher.bot.send_message(chat_id=ID,text="You have 30 second to Insert your password to unlock the door")
    retpass = sqlcode.fetchpass(ID)
    name1 = str(retpass[1]).split(" ")
    ws.send("lcd2/"+name1[0]+"/"+name1[1])
    #startbot()



# def startbot():
#     dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
#     updater.start_polling(drop_pending_updates=True)
#     return


