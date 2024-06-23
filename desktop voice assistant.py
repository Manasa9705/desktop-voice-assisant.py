import random
import tkinter as tk
from tkinter import scrolledtext, Entry, Button
import openai
import speech_recognition as sr
import win32com.client
import threading
import os
import webbrowser
import datetime
import json
from config import apikey

openai.api_key = apikey

class ChatbotApp:
    def _init_(self, root,conversations):
        self.root = root
        self.root.title("Personal Voice Assistant")

        self.chat_history = scrolledtext.ScrolledText(root, width=40, height=10)
        self.chat_history.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.user_input = Entry(root, width=30)
        self.user_input.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        self.mic_button = Button(root, text="Microphone", command=self.start_listening)
        self.mic_button.grid(row=1, column=2, padx=10, pady=10)

        self.conversations = conversations

        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self.recognizer = sr.Recognizer()
        self.listening_thread = None

    def chat(self, query):
        current_conversation = {"role": None, "content": None}
        chatStr = ""
        print(chatStr)
        current_conversation["role"] = "user"
        current_conversation["content"] = query.strip()
        self.conversations.append(current_conversation.copy())

        messages = [{"role": conversation["role"], "content": conversation["content"]} for conversation in
                    self.conversations]

        if len(self.conversations) > 0:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                messages=messages
            )
        else:
            response = openai.Completion.create(
                model="gpt-3.5-turbo",
                prompt=chatStr,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

        print(response.choices[0].message["content"])
        self.speaker.Speak(response.choices[0].message["content"])
        assistant_reply = response.choices[0].message["content"]
        current_conversation = {"role": None, "content": None}

        current_conversation["role"] = "assistant"
        current_conversation["content"] = assistant_reply.strip()
        self.conversations.append(current_conversation.copy())
        chatStr += f"{assistant_reply}\n"
        with open("conversation.json", "w") as json_file:
            json.dump(self.conversations, json_file, indent=4)
        self.update_chat_history(f"You: {query}")
        self.update_chat_history(f"Assistant: {assistant_reply}")

    def ai(self, prompt):
        openai.api_key = apikey
        text = f"OpenAI response for Prompt: {prompt} \n*\n"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        print(response["choices"][0]["text"])
        text += response["choices"][0]["text"]
        if not os.path.exists("Openai"):
            os.mkdir("Openai")

        with open(f"Openai/prompt- {random.randint(1, 1246785435355)}", "w") as f:
            f.write(text)

    def send_message(self):
        user_message = self.user_input.get().strip()
        if user_message:
            self.user_input.delete(0, tk.END)
            self.conversations.append({"role": "user", "content": user_message})
            self.update_chat_history(f"You: {user_message}")
            self.chat(user_message)

    def update_chat_history(self, message):
        self.chat_history.insert(tk.END, message + '\n')
        self.chat_history.see(tk.END)  # Scroll to the latest message

    def listen_and_chat(self):

        with sr.Microphone() as source:
            while True:
                print("Listening...")
                audio = self.recognizer.listen(source)

                try:
                    user_message = self.recognizer.recognize_google(audio)
                    self.user_input.delete(0, tk.END)
                    self.user_input.insert(0, user_message)
                    print(f"User said: {user_message}")

                    sites = [["youtube", "www.youtube.com"], ["wikipedia", "www.wikipedia.com"],
                             ["google", "www.google.com"]]
                    for site in sites:
                        if f"Open {site[0]}".lower() in user_message.lower():
                            speaker = win32com.client.Dispatch("SAPI.SpVoice")
                            speaker.Speak(f"opening {site[0]}")
                            webbrowser.open(site[1])


                    # Handle voice commands
                    if "open music" in user_message:
                        musicPath = "C:/Users/imposter/Downloads/speed-122837.mp3"
                        os.system(f"start {musicPath}")
                    elif "the time" in user_message:
                        strfTime = datetime.datetime.now().strftime("%H:%M:%S")
                        self.speaker.Speak(f"sir the time is {strfTime}")
                    elif "open notepad" in user_message:
                        os.system(f"start C:/Program Files (x86)/Notepad++")
                    elif "using artificial intelligence" in user_message:
                        self.ai(prompt=user_message)
                    elif "quit" in user_message:
                        with open("conversation.json", "w") as json_file:
                            json.dump(self.conversations, json_file, indent=4)
                        exit()
                    elif "reset chat" in user_message:
                        chatStr = ""

                    else :  self.send_message()

                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

    def start_listening(self):
        if self.listening_thread is None or not self.listening_thread.is_alive():
            self.listening_thread = threading.Thread(target=self.listen_and_chat)
            self.listening_thread.daemon = True
            self.listening_thread.start()
        else:
            print("Listening thread is already running.")

if _name_ == '_main_':
    root = tk.Tk()
    root.geometry("800x600")
    conversations=[]
    data={};
    try:
        with open("conversation.json", "r") as json_file:
            data = json.load(json_file)
    except:
        print("no file")
    if data:
        for item in data:
            role = item["role"]
            content = item["content"]
            current_conversation = {"role": role, "content": content}
            conversations.append(current_conversation)
    app = ChatbotApp(root,conversations)

    root.mainloop()
