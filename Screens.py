from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, ObjectProperty 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.app import App
from random import randint
from kivy.core.audio import SoundLoader

import Boxes
from Boxes import MovableBox,StationBox,R,L,U,D,B,SizeBlocks


class Level(Button):
	def __init__(self,cols=3, rows=3, number="1",lab_text="", **kwargs):
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
		stations = {}
		for c in range(cols):
			for r in range(rows):
				stations[(c, r)] = "StationBox"
	
		pazls = []
		
		trains = [{
			"start": {
				"pos":(0,1),
				"side":L
		}, "end" : {
				"pos":(2,1),
				"side":R
		},"points" : []
		}]
		
	
		self.content = {
			"cols": cols,
			"rows": rows,
			"stations": stations,
			"pazls": pazls,
			"trains": trains
		}

	def on_press(self):
		app = App.get_running_app()
		app.root.transition.direction = 'left'
		app.root.current_content = self.content
		game_screen = app.root.get_screen('game')
		lab = game_screen.ids.input
		lab.text=self.lab_text
		app.root.current = "game"

sound = SoundLoader.load("assets/Music/fon_game.mp3")
if sound:
	sound.loop = True

class Levels(Screen):
	
	current_content = ObjectProperty(None)
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
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
		if sound and sound.state != "play":
			sound.play()

class Menu(Screen):
	def exit(self):
		App.get_running_app().stop()
	def on_enter(self, *args):
		if sound and sound.state == "play":
			sound.stop()
from Train import Train 

class Game(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.grid_map = {}
		self.trains = []

	def on_enter(self, *args):
		content = self.manager.current_content
		MP = self.ids.MainPlane
		MP.clear_widgets()
		self.grid_map.clear()
		self.trains=[]
		if not content:
			return

		cols = content["cols"]
		rows = content["rows"]

		# 1. Создаем сетку                                                                                               ---
		grid = GridLayout(
			cols=cols,
			rows=rows,
			size_hint=(None, None),
			size=(cols * SizeBlocks, rows * SizeBlocks),
			spacing=0,
			pos=(50, 100)
		)

		# 2. Генерируем поезда                                                                                  ---
		for p in content["trains"]:
			self.trains.append(Train(content["stations"],p))
		# 3. Генерируем станций
		for r in range(rows - 1, -1, -1):
			for c in range(cols):
				st_type = content["stations"].get((c, r), "StationBox")
				station_cls = getattr(Boxes, st_type, StationBox)
				station = station_cls()
				
				self.grid_map[(c, r)] = station
				grid.add_widget(station)

		MP.add_widget(grid)

		for p in self.trains:
			MP.add_widget(p)
			p.map=self.grid_map
			p.fill_path()
		
		# 4. Спавним подвижные пазлы                                                                                       ---
		spawn_x_start = cols * SizeBlocks + 100
		for i, pz_type in enumerate(content["pazls"]):
			pazl_cls = getattr(Boxes, pz_type, MovableBox)
			pazl = pazl_cls()
			pazl.pos = (spawn_x_start + (i % 2) * (SizeBlocks + 10), 
						100 + (i // 2) * (SizeBlocks + 10))
			MP.add_widget(pazl)

	def start_train(self):
		if Boxes.TrainPlay:return
		"""Вызывается по нажатию кнопки СТАРТ из KV-файла"""
		MP = self.ids.MainPlane
		Boxes.TrainPlay = True
		for train in self.trains:
			train.value=0
			train.points = train.def_points.copy()
			MP.remove_widget(train)
			MP.add_widget(train)
			try:
				train.MoveStep(None, None, train.start)
			except Exception as e:
				self.ids.input.text = str(e)
			

