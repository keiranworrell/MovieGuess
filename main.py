from kivy.uix.screenmanager import ScreenManager, Screen # type: ignore
from kivy.uix.textinput import TextInput # type: ignore
from kivy.clock import Clock # type: ignore
from kivy.storage.jsonstore import JsonStore # type: ignore
from kivy.core.window import Window # type: ignore
from os.path import join
from kivymd.app import MDApp # type: ignore
from kivy.lang import Builder # type: ignore
from kivy.uix.widget import Widget  # type: ignore
from kivy.properties import ObjectProperty  # type: ignore
from kivy.uix.floatlayout import FloatLayout # type: ignore
from kivy.uix.popup import Popup # type: ignore
from kivy.core.clipboard import Clipboard # type: ignore
from fast_autocomplete import AutoComplete # type: ignore
import requests # type: ignore
import json
import hashlib

class PopupWindow(Widget): 
    def btn(self): 
        popFun() 

class P(FloatLayout): 
    pass

class MyTextInput(TextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # Add support for tab as an 'autocomplete' using the suggestion text.
        if self.suggestion_text and keycode[1] == 'tab':
            self.insert_text(self.suggestion_text + ' ')
            return True
        return super(MyTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

def popFun(): 
    show = P() 
    window = Popup(title = "Invalid", content = show, 
                   size_hint = (None, None), size = (300, 300)) 
    window.open()

class completedWindow(Screen):
    def on_enter(self):
        self.ids['correctFilm'].text = self.manager.get_screen('loader').filmName
        self.guessesRequired = self.manager.get_screen('movieguess').guessesSubmitted

        if self.guessesRequired == "failed":
            self.ids['success'].text = "Unlucky!"
            self.ids['today'].text = "You didn't get it today."
            self.ids['streak'].text = "Your streak is now 0"
        else:
            self.ids['today'].text = "You got it right in " + str(self.guessesRequired) + "!"
            self.ids['streak'].text = "Your current streak is " + str(self.manager.get_screen('loader').streak)

    def logOut(self):
        windowManager.store.clear()
        sm.current = "login"
    
    def copyClipboard(self):
        if self.guessesRequired == "failed":
            text = "I didn't guess today's movie :("
        else:
            text = "I guessed today's movie in " + str(self.guessesRequired) + " so now my streak is " + str(self.manager.get_screen('loader').streak) + " days!"
        Clipboard.copy(text)

class movieGuessWindow(Screen): 
    def on_enter(self):
        self.ids['act1'].text = self.manager.get_screen('loader').actor1
        self.ids['guessInput'].hint_text = ""
        
        try:
            self.ids['email'].text = windowManager.store.get('credentials')['username']
        except:
            self.ids['email'].text = "Logged Out"

        self.word_list = ('The quick brown fox jumps over the lazy old dog').split(' ')
        self.suggest_list = {}
        for item in self.manager.get_screen('loader').filmList:
            self.suggest_list.update({item['filmName']: {}})
        self.autocomplete = AutoComplete(words=self.suggest_list)
        self.ids['guessInput'].bind(text=self.on_text)
        self.guessesSubmitted = 0
    
    def on_text(self, instance, value):
        word = self.autocomplete.search(word=value, max_cost=3, size=3)
        if not word:
            self.ids['guessInput'].hint_text = ""
            return
        self.ids['guessInput'].hint_text = word[0][0]

    def submitGuess(self, *args):
        if True:
            self.guessesSubmitted += 1
            currentGuess = self.ids['guessInput'].hint_text
            if currentGuess.upper() == self.manager.get_screen('loader').filmName.upper():
                self.manager.get_screen('loader').streak = self.manager.get_screen('loader').streak + 1
                r = requests.post("https://7hhij52kubulqpxun5r2v4gbay0jawhe.lambda-url.eu-west-2.on.aws/", json={"email": windowManager.store.get('credentials')['username'], "guesses": self.guessesSubmitted})
                sm.current = "complete"
                return

            if self.guessesSubmitted == 1:
                latestGuess = 'act1'
                self.ids['act2'].text = self.manager.get_screen('loader').actor2
            elif self.guessesSubmitted == 2:
                latestGuess = 'act2'
                self.ids['act3'].text = self.manager.get_screen('loader').actor3
            elif self.guessesSubmitted == 3:
                latestGuess = 'act3'
                self.ids['act4'].text = self.manager.get_screen('loader').actor4
            elif self.guessesSubmitted == 4:
                latestGuess = 'act4'
                self.ids['act5'].text = self.manager.get_screen('loader').actor5
            else:
                latestGuess = 'act5'
            
            if self.guessesSubmitted > 4:
                self.guessesSubmitted = "failed"
                self.manager.get_screen('loader').streak = 0
                r = requests.post("https://7hhij52kubulqpxun5r2v4gbay0jawhe.lambda-url.eu-west-2.on.aws/", json={"email": windowManager.store.get('credentials')['username'], "guesses": self.guessesSubmitted})
                sm.current = "complete"

            if currentGuess == "Pick A Movie":
                self.ids[latestGuess].background_color = 200,0,0,0.6
            else:
                self.ids[latestGuess].text = self.ids[latestGuess].text + '\nYou guessed: ' + currentGuess
                self.ids[latestGuess].background_color = 200,100,0,0.6
        
class loginWindow(Screen):
    email = ObjectProperty(None) 
    pwd = ObjectProperty(None)
    def on_enter(self):
        Clock.schedule_once(self.change_screen)

    def change_screen(self, dt):
        try:
            windowManager.store.get('credentials')['username']
        except KeyError:
            self.username = ""
        else:
            self.username = windowManager.store.get('credentials')['username']

        if self.username != "":
            sm.current = "loader"


    def validate(self):
        if self.pwd.text != "":
            enc = self.pwd.text.encode()
            hashed = hashlib.md5(enc).hexdigest()
            if self.email.text != "":
                r = requests.get("https://faqxpjcrfrlxcwjfxhvd4borpq0swshy.lambda-url.eu-west-2.on.aws/", json={"email": self.email.text, "password": hashed})
                if r.text == "Login successful": 
                    windowManager.store.put('credentials', username=self.email.text)
                    sm.current = "loader"
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
                    sm.current = "loader"
                else:
                    popFun()
                    self.email.text = ""
                    self.pwd.text = ""
            else: 
                popFun()
        else:
            popFun()

class loadingWindow(Screen):
    def on_enter(self):
        s = requests.get("https://ldj6biyny5htkmafqcrvnt3am40sottu.lambda-url.eu-west-2.on.aws/", json={"email": windowManager.store.get('credentials')['username']})
        resultsData = json.loads(s.text)

        self.d0Result = resultsData[0]
        self.streak = resultsData[1]

        r = requests.get("https://ut7qnywcuo6ffotdpo56lu4fvi0ujuoh.lambda-url.eu-west-2.on.aws/")
        data = json.loads(r.text)
        self.actor1 = data[0]['actor1']
        self.actor2 = data[0]['actor2']
        self.actor3 = data[0]['actor3']
        self.actor4 = data[0]['actor4']
        self.actor5 = data[0]['actor5']
        self.filmName = data[0]['filmName']

        self.filmList = data[1]
        
        if self.d0Result == "":
            sm.current = "movieguess"
        else:
            self.manager.get_screen('movieguess').guessesSubmitted = self.d0Result
            sm.current = "complete"

class windowManager(ScreenManager): 
    data_dir = MDApp().user_data_dir
    store = JsonStore(join(data_dir, 'storage.json'))
  
kv = Builder.load_string('''
#:kivy 1.0.9

windowManager: 
    loginWindow: 
    movieGuessWindow: 
    correctGuessWindow:
    loadingWindow:

<loginWindow>: 
    email: email 
    pwd: pwd 
    MDFloatLayout:
        canvas:
            Color:
                rgba: 0,0,0,.8
            Rectangle:
                size: self.size
                pos: self.pos
        size: root.width, root.height 
        Label: 
            text: "Email: "
            size_hint: 0.2, 0.1
            pos_hint: {"x":0.25, "top":0.9} 
        TextInput: 
            id: email 
            multiline: False
            size_hint: 0.3, 0.1
            pos_hint: {"x" : 0.45, "top" : 0.9} 
        Label: 
            text: "Password: "
            size_hint: 0.2, 0.1
            pos_hint: {"x" : 0.25, "top" : 0.7} 
        TextInput: 
            id: pwd 
            password: True
            multiline: False
            size_hint: 0.3, 0.1
            pos_hint: {"x" : 0.45, "top" : 0.7} 
        Button: 
            text: "Create an account"
            size_hint: 0.4, 0.1
            pos_hint: {"x" : 0.3, "top" : 0.4} 
            on_release:  
                root.signupbtn()
                root.manager.transition.direction = "left"
        Button: 
            text: "Login"
            size_hint: 0.3, 0.1
            pos_hint: {"x" : 0.35, "top" : 0.2} 
            on_release:  
                root.validate() 
                root.manager.transition.direction = "up"
  
<movieGuessWindow>: 
    MDFloatLayout: 
        canvas:
            Color:
                rgba: 0,0,0,.8
            Rectangle:
                size: self.size
                pos: self.pos
        size: root.width, root.height  
        Label:
            size_hint: 0.4, 0.05
            pos_hint: {"right" : 0.45, "top" : 0.05} 
            text: "Logged in as:"
        Label:
            size_hint: 0.4, 0.05
            pos_hint: {"right" : 0.95, "top" : 0.05} 
            id: email
        Label:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.45, "top" : 0.95} 
            text: 'Actor 1:'
        Button:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.95, "top" : 0.95} 
            id: act1
            halign: 'center'
            text: 'Hidden'
        Label:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.45, "top" : 0.8} 
            text: 'Actor 2:'
        Button:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.95, "top" : 0.8} 
            id: act2
            halign: 'center'
        Label:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.45, "top" : 0.65} 
            text: 'Actor 3:'
        Button:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.95, "top" : 0.65} 
            id: act3
            halign: 'center'
        Label:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.45, "top" : 0.5} 
            text: 'Actor 4:'
        Button:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.95, "top" : 0.5} 
            id: act4
            halign: 'center'
        Label:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.45, "top" : 0.35} 
            text: 'Actor 5:'
        Button:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 0.95, "top" : 0.35} 
            id: act5
            halign: 'center'
        MDTextField:
            size_hint: 0.575, 0.1
            pos_hint: {"right" : 0.58825, "top" : 0.2} 
            line_color_normal: 1,1,1,1
            id: guessInput
        Button:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 1, "top" : 0.2} 
            text: 'Submit Guess'
            halign: 'center'
            on_press: root.submitGuess()

<completedWindow>:
    MDFloatLayout:
        canvas:
            Color:
                rgba: 0,0,0,.8
            Rectangle:
                size: self.size
                pos: self.pos
        size: root.width, root.height 
        Label: 
            size_hint: 0.5, 0.15
            pos_hint: {"right" : 0.75, "top" : 0.95}
            text: 'Correct!'
            id: success
            font_size: 50          
        Label: 
            size_hint: 0.5, 0.25
            pos_hint: {"right" : 0.75, "top" : 0.8}
            text: 'You got it right in x'
            id: today
            font_size: 50
        Label: 
            size_hint: 0.5, 0.25
            pos_hint: {"right" : 0.75, "top" : 0.6}
            text: 'Your current streak is y'
            id: streak
            font_size: 25
        Label:
            size_hint: 0.5, 0.1
            pos_hint: {"right" : 0.75, "top" : 0.4}
            text: "Today's film is:"
        Label:
            size_hint: 0.5, 0.15
            pos_hint: {"right" : 0.75, "top" : 0.35}
            id: correctFilm
            font_size: 50
        Button:
            size_hint: 0.3, 0.1
            pos_hint: {"right" : 0.4, "top" : 0.15} 
            text: 'Copy results to share'
            on_press: root.copyClipboard()
        Button:
            size_hint: 0.3, 0.1
            pos_hint: {"right" : 0.9, "top" : 0.15} 
            text: 'Log Out'
            on_press: root.logOut()
                        
<loadingWindow>:
    MDFloatLayout:
        canvas:
            Color:
                rgba: 0,0,0,.8
            Rectangle:
                size: self.size
                pos: self.pos
        size: root.width, root.height 
        Label: 
            size_hint: 0.5, 0.15
            pos_hint: {"right" : 0.75, "top" : 0.7}
            text: 'Loading...'
            id: success
            font_size: 50    

<P>: 
    Label: 
        text : "Please enter valid information"
        size_hint : 0.2, 0.1
        pos_hint : {"x" : 0.3, "top" : 0.8} 
                         ''')
sm = windowManager()
widgets = [loginWindow(name='login'), movieGuessWindow(name='movieguess'), completedWindow(name='complete'), loadingWindow(name='loader')]
for widget in widgets:
    sm.add_widget(widget)

class MovieGuessApp(MDApp): 
    def build(self): 
        # adding theme_color 
        self.theme_cls.theme_style="Dark"   
        return sm 


if __name__ == '__main__':
    MovieGuessApp().run()