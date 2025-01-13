from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from pandas import *
import requests
import json


class MovieGuess(GridLayout):
    pass

class MovieGuessApp(App):
    def build(self):
        self.movieGuess = MovieGuess()
        # r = requests.get("https://ut7qnywcuo6ffotdpo56lu4fvi0ujuoh.lambda-url.eu-west-2.on.aws/")
        # data = json.loads(r.text)
        # self.filmName = data['Item']['filmName']['S']
        # self.actor1 = data['Item']['actor1']['S']
        # self.actor2 = data['Item']['actor2']['S']
        # self.actor3 = data['Item']['actor3']['S']
        # self.actor4 = data['Item']['actor4']['S']
        # self.actor5 = data['Item']['actor5']['S']

        self.filmName = "Knives Out"
        self.actor1 = "LaKeith Stanfield"
        self.actor2 = "Jamie Lee Kurtis"
        self.actor3 = "Ana De Armas"
        self.actor4 = "Chris Evans"
        self.actor5 = "Daniel Craig"

        actor1Label = self.movieGuess.ids['act1']
        actor1Label.text = self.actor1

        data = read_csv("moviesData.csv")
        titles = data['filmName'].tolist()

        dropdown = DropDown()
        for val in titles:
            btn = Button(text = val, size_hint_y = None, height = 40)
            btn.bind(on_release = lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        dropButton = self.movieGuess.ids['movieDropdown']
        dropButton.bind(on_release = dropdown.open)
        dropdown.bind(on_select = lambda instance, x: setattr(dropButton, 'text', x))

        self.guessesSubmitted = 0

        return self.movieGuess
    
    def submitGuess(self, *args):
        if True:
            currentGuess = self.movieGuess.ids['movieDropdown'].text
            if currentGuess == self.filmName:
                popup = Popup(title = self.filmName,
                              content = Label(text = 'Correct!'))
                popup.open()


            if self.guessesSubmitted == 0:
                actor2Label = self.movieGuess.ids['act2']
                actor2Label.text = self.actor2
            elif self.guessesSubmitted == 1:
                actor3Label = self.movieGuess.ids['act3']
                actor3Label.text = self.actor3
            elif self.guessesSubmitted == 2:
                actor4Label = self.movieGuess.ids['act4']
                actor4Label.text = self.actor4
            elif self.guessesSubmitted == 3:
                actor5Label = self.movieGuess.ids['act5']
                actor5Label.text = self.actor5
            else:
                popup = Popup(title = 'Out of guesses!',
                              content = Label(text = 'Try again tomorrow.'))
                popup.open()
            self.guessesSubmitted += 1
        else:
            return


if __name__ == '__main__':
    MovieGuessApp().run()