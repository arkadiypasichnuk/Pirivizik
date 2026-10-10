from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.app import App


import Boxes
from Boxes import MovableBox,StationBox,R,L,U,D,B,SizeBlocks

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
	def Tip(self,text):
		lab = self.ids.input
		lab.text = text
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
			

