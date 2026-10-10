
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.app import App
from kivy.properties import ObjectProperty 
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout

class Level(Button):
    def __init__(self,number="1",lab_text="", **kwargs):
        super().__init__(**kwargs)
        self.text = str(number)
        self.background_color = [0.2, 0.6, 0.9, 1]  
        """
        структуру уровня:
        - grid_size: размер поля
        - stations: словарь {(col, row): "TypeName"}
        - pazls: список пазлов для спавна
        - trains: список с поиздами где есть начало и конец и станции через которые он должен проехать
        """
        self.lab_text=lab_text

    def on_press(self):
        app = App.get_running_app()
        app.root.transition.direction = 'left'
        app.root.current_content = self.content
        app.root.get_screen('game').Tip(self.lab_text)
        app.root.current = "game"

class MenuLevels(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound = SoundLoader.load("assets/Music/fon_game.mp3")
        if self.sound:
            self.sound.loop = True
        size=150
        self.grid_levels = GridLayout(
            cols=5,
            size_hint=(None, None),
            spacing=10,
            col_default_width=size, 
            row_default_height=size,
            pos_hint={'x': 0.1, 'top': 0.9}  
        )
        
        self.grid_levels.bind(minimum_size=self.grid_levels.setter('size'))
        
        self.add_widget(self.grid_levels)
    def on_enter(self, *args):
        if self.sound and self.sound.state != "play":
            self.sound.play()

class Levels(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound = SoundLoader.load("assets/Music/fon_game.mp3")
        if self.sound:
            self.sound.loop = True
        size=150
        self.grid_levels = GridLayout(
            cols=5,
            size_hint=(None, None),
            spacing=10,
            col_default_width=size, 
            row_default_height=size,
            pos_hint={'x': 0.1, 'top': 0.9}  
        )
        
        self.grid_levels.bind(minimum_size=self.grid_levels.setter('size'))
        
        self.add_widget(self.grid_levels)
    def on_enter(self, *args):
        if self.sound and self.sound.state != "play":
            self.sound.play()
