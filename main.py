from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from os.path import join
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.widget import Widget 
from kivy.properties import ObjectProperty 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
import requests
import json
import hashlib

class PopupWindow(Widget): 
    def btn(self): 
        popFun() 

class P(FloatLayout): 
    pass

def popFun(): 
    show = P() 
    window = Popup(title = "Invalid", content = show, 
                   size_hint = (None, None), size = (300, 300)) 
    window.open()

class correctGuessWindow(Screen):
    def on_enter(self):
        self.ids['correctFilm'].text = self.manager.get_screen('movieguess').ids['movieDropdown'].text
    
    def logOut(self):
        windowManager.store.clear()

class movieGuessWindow(Screen): 
    def on_enter(self):
        r = requests.get("https://ut7qnywcuo6ffotdpo56lu4fvi0ujuoh.lambda-url.eu-west-2.on.aws/")
        data = json.loads(r.text)
        self.filmName = data['Item']['filmName']['S']
        self.actor1 = data['Item']['actor1']['S']
        self.actor2 = data['Item']['actor2']['S']
        self.actor3 = data['Item']['actor3']['S']
        self.actor4 = data['Item']['actor4']['S']
        self.actor5 = data['Item']['actor5']['S']

        self.ids['act1'].text = self.actor1
        
        try:
            self.ids['email'].text = windowManager.store.get('credentials')['username']
        except:
            self.ids['email'].text = "Logged Out"

        r = requests.get("https://qyjs3zubzp4hmzovek2zwq4oju0toehi.lambda-url.eu-west-2.on.aws/")
        data = json.loads(r.text)
        dropdown = DropDown()
        for i in range(len(data)):
            btn = Button(text = data[i]['filmName'], size_hint_y = None, height = 40)
            btn.bind(on_release = lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        dropButton = self.ids['movieDropdown']
        dropButton.bind(on_release = dropdown.open)
        dropdown.bind(on_select = lambda instance, x: setattr(dropButton, 'text', x))

        self.guessesSubmitted = 0

    def submitGuess(self, *args):
        if True:
            currentGuess = self.ids['movieDropdown'].text
            if currentGuess == self.filmName:
                sm.current = "correct"
                return

            if self.guessesSubmitted == 0:
                self.ids['act2'].text = self.actor2
            elif self.guessesSubmitted == 1:
                self.ids['act3'].text = self.actor3
            elif self.guessesSubmitted == 2:
                self.ids['act4'].text = self.actor4
            elif self.guessesSubmitted == 3:
                self.ids['act5'].text = self.actor5
            else:
                popup = Popup(title = 'Out of guesses!',
                              content = Label(text = 'Try again tomorrow.'))
                popup.open()
            self.guessesSubmitted += 1
        else:
            return
        
class loginWindow(Screen):
    email = ObjectProperty(None) 
    pwd = ObjectProperty(None)
    def on_enter(self):
        try:
            windowManager.store.get('credentials')['username']
        except KeyError:
            self.username = ""
        else:
            self.username = windowManager.store.get('credentials')['username']

        try:
            windowManager.store.get('credentials')['password']
        except KeyError:
            self.password = ""
        else:
            self.password = windowManager.store.get('credentials')['password']

        if self.username != "" and self.password != "":
            r = requests.get("https://faqxpjcrfrlxcwjfxhvd4borpq0swshy.lambda-url.eu-west-2.on.aws/", json={"email": self.username, "password": self.password})
            if r.text == "Login successful": 
                sm.current = "movieguess"

    def validate(self):
        if self.pwd.text != "":
            enc = self.pwd.text.encode()
            hashed = hashlib.md5(enc).hexdigest()
            if self.email.text != "":
                r = requests.get("https://faqxpjcrfrlxcwjfxhvd4borpq0swshy.lambda-url.eu-west-2.on.aws/", json={"email": self.email.text, "password": hashed})
                if r.text == "Login successful": 
                    windowManager.store.put('credentials', username=self.email.text, password=hashed)
                    sm.current = "movieguess"
                else: 
                    popFun()
                    self.email.text = "" 
                    self.pwd.text = ""
            else:
                popFun()
        else:
            popFun()
    
    def signupbtn(self): 
        if self.pwd.text != "":
            enc = self.pwd.text.encode()
            hashed = hashlib.md5(enc).hexdigest()

            if self.email.text != "": 
                r = requests.post("https://husifsnku45fiipbsfqyvwzxji0ppleo.lambda-url.eu-west-2.on.aws/", json={"email": self.email.text, "password": hashed})
                data = json.loads(r.text)
                if data["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    windowManager.store.put('credentials', username=self.email.text, password=hashed)
                    sm.current = "movieguess"
                else:
                    popFun()
                    self.email.text = ""
                    self.pwd.text = ""
            else: 
                popFun()
        else:
            popFun()

class windowManager(ScreenManager): 
    data_dir = App().user_data_dir
    store = JsonStore(join(data_dir, 'storage.json'))
  
kv = Builder.load_file('MovieGuess.kv')
sm = windowManager()

widgets = [movieGuessWindow(name='movieguess'), loginWindow(name='login'), correctGuessWindow(name='correct')]
for widget in widgets:
    sm.add_widget(widget)

class MovieGuessApp(App): 
    def build(self): 
        sm.current = "login"
        return sm 


if __name__ == '__main__':
    MovieGuessApp().run()