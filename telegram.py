import tkinter as tk
from tkinter import messagebox
import pandas as pd
from telethon import TelegramClient, events
from multi_rake import Rake
import stanza
import datetime
import asyncio
from telethon.tl.types import ReactionCustomEmoji, ReactionEmoji, ReactionPaid
import re
import emoji

class MyRequests:
    def __init__(self):
        stanza.download(lang="multilingual")

        self.api_id=0
        self.api_hash=""
        self.channel_url=""
        today=datetime.datetime.today().strftime('%Y-%m-%d')
        self.filename = "telegram_messages_"+today
        self.nlpBasic=stanza.Pipeline(lang="multilingual",proccesor='langid',langid_clean_text=True)

        self.client=None
        self.data=[]
        self.listening=False
         
    def save_to_database(self,message):
        text=message.text
        if not text:
            return False
        doc=self.nlpBasic(text)
        text=doc.text
        text=self.clean_telegram_text(text)
        lang=doc.lang
        kw=Rake(language_code=lang)        
        keywords=kw.apply(text)        
        
        date=message.date
        nlp = stanza.Pipeline(lang=lang,  processors='tokenize,mwt,pos,lemma,ner',download_method=False)
        reaction=None
        if message.reactions:
            for react in message.reactions.results:
                if isinstance(react.reaction,ReactionPaid):
                    continue
                elif isinstance(react.reaction,ReactionEmoji):
                    reaction=react.reaction.emoticon
                    break
                elif isinstance(react.reaction,ReactionCustomEmoji):
                    reaction=react.reaction.document_id

        keys=[]
        res=[]
        print(keywords)
        for k in keywords:
            if k[1]>3:
                keys.append(k[0])
        doc=nlp(''.join(keys))
        
        ents={}
        doc=nlp(text)
        for sent in doc.sentences:
            words=[]
            for word in sent.words:
                if  word.upos in {"NOUN", "PROPN", "ADJ"}:
                    words.append(f"{word.lemma} ") 
            res.append(f"{words};")
        for ent in doc.ents:
            
                ents[ent.type]+=f"{ent.text} "
                ents[ent.type]+=";"

        
        dict={"message":text,"keywords":res,"date":date,"reaction":reaction,"language":lang}
        dict.update(ents)

        self.data.append(dict)

        

    def write_to_csv(self,lastdate):
        df=pd.DataFrame(self.data)
        lastdate=lastdate.strftime(' %d-%m-%Y')
        df.to_csv(self.filename+self.channel_url+lastdate+".csv",encoding='utf-8')
        self.data=[]
    def read_from_database(self,file):
        df=pd.read_csv(file,encoding='utf-8')
        print(df.head)
        return df

    def start_monitoring(self):
        
        if not self.client:
             messagebox.showerror("Error", "No connection set, set credentials and press 'Start'")
        else:
            check=messagebox.askokcancel("Warning",f"start read  message of channel {self.channel_url}")
            if check:
            
                if not self.listening:
            
                    self.running=True
                    loop=asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    asyncio.run_coroutine_threadsafe(self.monitor_telegram_channel(), loop)
                else:
                    asyncio.run_coroutine_threadsafe(self.client.disconnect(), asyncio.get_event_loop())

    async def monitor_telegram_channel(self):
        await self.client.run_until_disconnected()
        @self.client.on(events.NewMessage(chats=(self.channel_url)))
        async def my_event_handler(event):
            if self.listening:
                message = event.message
                self.save_to_database(message)
                self.write_to_csv()
                messagebox.showinfo("Info","get mesage:"+message.text)

    def connect_to_telegram(self):

        try:
            self.client= TelegramClient('session_name', self.api_id, self.api_hash)
            self.client.start()


        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

        messagebox.showinfo("Info","everything connect")    

    def create_credentiol(self,api_id_entry,api_hash_entry,channel_url_entry):
        try:
            api_id = int(api_id_entry.get())
            api_hash = api_hash_entry.get()
            channel_url = channel_url_entry.get()
            if api_id == 0 or api_hash == "" or channel_url == "":
                messagebox.showerror("Error", "Please fill in all the fields.")
                return
            self.api_id=api_id
            self.api_hash=api_hash
            self.channel_url=channel_url   
        except  Exception:
            messagebox.showerror("Error"," Bad id,hash or group id, check again" ) 
        self.connect_to_telegram()
    
    def loop_get_messages(self,date):
        if not date:
            messagebox.ERROR("ERROR","No date select")
            return False
        check=messagebox.askokcancel("Warning",f"start read  message of channel {self.channel_url} from {date}")
        if check:
            date= datetime.datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=datetime.timezone.utc)
            self.client.loop.run_until_complete(self.get_messages_at_date(date))
            self.write_to_csv(date)
            messagebox.showinfo("INFO","everything done, your file save as:"+self.filename)

    async def get_messages_at_date(self,date):


        async for msg in self.client.iter_messages( self.channel_url, offset_date=date,reverse=True):
            self.save_to_database(msg)
        messagebox.showinfo("Info","Everything save")
        return True

                

    
    def display_messages(self,message_text,filename):
        messages = self.read_from_database(filename)
        message_text.delete('1.0', tk.END)
        headers = "\t".join(messages.columns) + "\n"
        message_text.insert(tk.END, headers)
        for _, row in messages.iterrows():
            row_text = "\t".join(str(value) for value in row) + "\n"
            message_text.insert(tk.END, row_text)

    def clean_telegram_text(self,text):
    # Remove markdown bold and italics (e.g. **text**, *text*)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)

        # Remove inline links but keep visible text: [text](url) -> text
        text = re.sub(r'\[(.*?)\]\((?:http.*?)\)', r'\1', text)

        # Remove invisible Unicode characters (e.g. zero-width space)
        text = re.sub(r'[\u200b\u200c\u200d\ufeff\ue000-\uf8ff]', '', text)

        # Remove empty links or decorative characters like "[ㅤ ]"
        text = re.sub(r'\[\s*ㅤ\s*\]', '', text)

        # Replace multiple newlines with one
        text = re.sub(r'\n{2,}', '\n\n', text)
        
        text = emoji.replace_emoji(text, replace='')

        # Strip leading/trailing whitespace
        text = text.strip()

        return text