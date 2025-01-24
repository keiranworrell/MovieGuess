from kivy.uix.screenmanager import ScreenManager, Screen # type: ignore
from kivy.clock import Clock # type: ignore
from kivy.storage.jsonstore import JsonStore # type: ignore
from os.path import join
from kivy.app import App # type: ignore
from kivy.lang import Builder # type: ignore
from kivy.uix.label import Label # type: ignore
from kivy.uix.widget import Widget  # type: ignore
from kivy.properties import ObjectProperty  # type: ignore
from kivy.uix.floatlayout import FloatLayout # type: ignore
from kivy.uix.popup import Popup # type: ignore
from kivy.uix.button import Button # type: ignore
from kivy.uix.dropdown import DropDown # type: ignore
import requests # type: ignore
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

class completedWindow(Screen):
    def on_enter(self):
        self.ids['correctFilm'].text = self.manager.get_screen('movieguess').filmName
        vic = self.manager.get_screen('movieguess').victory
        guesses_required = self.manager.get_screen('movieguess').guessesSubmitted

        if vic:
            self.ids['today'].text = "You got it right in " + str(guesses_required) + "!"
        else:
            self.ids['success'].text = "Unlucky!"
            self.ids['today'].text = "You didn't get it today."

        r = requests.post("https://7hhij52kubulqpxun5r2v4gbay0jawhe.lambda-url.eu-west-2.on.aws/", json={"email": windowManager.store.get('credentials')['username'], "guesses": guesses_required})
        print(r)

    def logOut(self):
        windowManager.store.clear()
        sm.current = "login"

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
            self.guessesSubmitted += 1
            currentGuess = self.ids['movieDropdown'].text
            if currentGuess == self.filmName:
                self.victory = True
                sm.current = "complete"
                return

            if self.guessesSubmitted == 1:
                latestGuess = 'act1'
                self.ids['act2'].text = self.actor2
            elif self.guessesSubmitted == 2:
                latestGuess = 'act2'
                self.ids['act3'].text = self.actor3
            elif self.guessesSubmitted == 3:
                latestGuess = 'act3'
                self.ids['act4'].text = self.actor4
            elif self.guessesSubmitted == 4:
                latestGuess = 'act4'
                self.ids['act5'].text = self.actor5
            else:
                latestGuess = 'act5'
            
            if self.guessesSubmitted > 4:
                self.victory = False
                sm.current = "complete"

            if currentGuess == "Pick A Movie":
                self.ids[latestGuess].background_color = 200,0,0,0.6
            else:
                self.ids[latestGuess].text = self.ids[latestGuess].text + '\nYou guessed: ' + currentGuess
                self.ids[latestGuess].background_color = 200,100,0,0.6
            

        else:
            return
        
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
            sm.current = "movieguess"


    def validate(self):
        if self.pwd.text != "":
            enc = self.pwd.text.encode()
            hashed = hashlib.md5(enc).hexdigest()
            if self.email.text != "":
                r = requests.get("https://faqxpjcrfrlxcwjfxhvd4borpq0swshy.lambda-url.eu-west-2.on.aws/", json={"email": self.email.text, "password": hashed})
                if r.text == "Login successful": 
                    windowManager.store.put('credentials', username=self.email.text)
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
  
kv = Builder.load_string('''
#:kivy 1.0.9

windowManager: 
    loginWindow: 
    movieGuessWindow: 
    correctGuessWindow:

<loginWindow>: 
    email: email 
    pwd: pwd 
    FloatLayout: 
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
    FloatLayout: 
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
        Button:
            size_hint: 0.6, 0.1
            pos_hint: {"right" : 0.6, "top" : 0.2} 
            id: movieDropdown
            halign: 'center'
            text: 'Pick A Movie'
        Button:
            size_hint: 0.4, 0.1
            pos_hint: {"right" : 1, "top" : 0.2} 
            text: 'Submit Guess'
            halign: 'center'
            on_press: root.submitGuess()

<completedWindow>:
    FloatLayout: 
        size: root.width, root.height 
        Label: 
            size_hint: 0.5, 0.15
            pos_hint: {"right" : 0.75, "top" : 0.95}
            text: 'Correct!'
            id: success
            font_size: 50          
        Label: 
            size_hint: 0.5, 0.25
            pos_hint: {"right" : 0.75, "top" : 0.75}
            text: 'You got it right in x.'
            id: today
            font_size: 50
        Label:
            size_hint: 0.5, 0.1
            pos_hint: {"right" : 0.75, "top" : 0.45}
            text: "Today's film is:"
        Label:
            size_hint: 0.5, 0.15
            pos_hint: {"right" : 0.75, "top" : 0.35}
            id: correctFilm
            font_size: 50
        Button:
            size_hint: 0.3, 0.1
            pos_hint: {"right" : 0.65, "top" : 0.15} 
            text: 'Log Out'
            on_press: root.logOut()


<P>: 
    Label: 
        text : "Please enter valid information"
        size_hint : 0.2, 0.1
        pos_hint : {"x" : 0.3, "top" : 0.8} 
                         ''')
sm = windowManager()

widgets = [loginWindow(name='login'), movieGuessWindow(name='movieguess'), completedWindow(name='complete')]
for widget in widgets:
    sm.add_widget(widget)

class MovieGuessApp(App): 
    def build(self): 
        return sm 


if __name__ == '__main__':
    MovieGuessApp().run()