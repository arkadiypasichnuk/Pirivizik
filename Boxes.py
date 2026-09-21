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
from kivy.graphics import Color, Line, PushMatrix, PopMatrix, Rotate
	

SizeBlocks = 100

R, L, U, D = "Right", "Left", "Up", "Down"
B, W = "Break", "Win"
DEFAULT_RAMKA = [.2, .6, .9, .5]

TrainPlay = False

class Box(FloatLayout):
	bg_color = ListProperty([.2, .6, .9, .3])

	ramkaUp = ListProperty(DEFAULT_RAMKA)
	ramkaDown = ListProperty(DEFAULT_RAMKA)
	ramkaLeft = ListProperty(DEFAULT_RAMKA)
	ramkaRight = ListProperty(DEFAULT_RAMKA)
	ramka = ListProperty([0.2, 0.6, 0.9, 0.5])
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.size_hint = (None, None)
		self.size = (SizeBlocks, SizeBlocks)
		self.pos = (0, 0)
#		self.image_angle = NumericProperty(0)
		
	def add_widget(self, widget, *args, **kwargs):
		widget.size_hint = (1, 1)
		widget.pos_hint = {'x': 0, 'y': 0}
		super().add_widget(widget, *args, **kwargs)

class RailBox(Box):
	DIRECTIONS = [U, L, D, R]

	def __init__(self, connections=None, image="", **kwargs):
		super().__init__(**kwargs)
		self.img = Image(source=image)
		self.add_widget(self.img)
		self.img.angle=0
		self.bg_color = [0, 0, 0, 0]
		self.ramkaRight = [0, 1, 0, .5]
		self.ramkaLeft = [0, 1, 0, .5]
		self.ramkaUp = [1, 0, 0, .5]
		self.ramkaDown = [1, 0, 0, .5]
		
		self.angle = 0
		
		self.connections = {L: R, R: L} if connections is None else connections
		
		self.current_connections = {}
		self.apply_rotation()

		with self.canvas.before:
			PushMatrix()
			self.rot = Rotate(angle=0, axis=(0, 0, 1))
		with self.canvas.after:
			PopMatrix()

		self.bind(pos=self._update_rotation_origin, size=self._update_rotation_origin)

	def _rotate_side_ccw(self, side):
		idx = self.DIRECTIONS.index(side)
		return self.DIRECTIONS[(idx + 1) % 4]

	def apply_rotation(self):
		steps = int(self.angle // 90) % 4
		result = self.connections.copy()
		
		for _ in range(steps):
			new_conn = {}
			for enter, exit_side in result.items():
				new_enter = self._rotate_side_ccw(enter)
				new_exit = self._rotate_side_ccw(exit_side)
				new_conn[new_enter] = new_exit
			result = new_conn
			
		self.current_connections = result

	def rotate(self,angle):
		self.angle = (self.angle + angle) % 360
		self.rot.angle = self.angle
		self.apply_rotation()

	def train_on_enter(self, enter):
		"""Возвращает сторону выезда из АКТУАЛЬНОГО графа."""
		return self.current_connections.get(enter, B)

	def _update_rotation_origin(self, *args):
		self.rot.origin = self.center

	def on_touch_down(self, touch):
		if TrainPlay:
			return False
		if self.collide_point(*touch.pos):
			if touch.is_double_tap:
				self.rotate(90)
				return True
		return super().on_touch_down(touch)

class MovableBox(RailBox):
	"""
	Подвижный блок рельс. Наследует поворот и рельсы от RailBox,
	добавляя возможность перетаскивания и привязки к StationBox.
	"""
	def __init__(self, connections=None, image="assets/forward_real.png", **kwargs):
		super().__init__(connections=connections, image=image, **kwargs)
		self.station = None
		self.is_moving = False

	def on_touch_down(self, touch):
		if super().on_touch_down(touch):
			return True

		if TrainPlay:
			return False

		if self.collide_point(*touch.pos):
			self.is_moving = True
			touch.grab(self)
			
			if self.parent:
				parent = self.parent
				parent.remove_widget(self)
				parent.add_widget(self)
			
			if self.station:
				self.station.opacity = 1
				self.station.box = None
				self.station = None
			
			return True
		return False

	def on_touch_move(self, touch):
		if touch.grab_current is self and self.is_moving:
			x, y = self.pos
			self.pos = (x + touch.dx, y + touch.dy)
			return True
		return super().on_touch_move(touch)

	def on_touch_up(self, touch):
		if touch.grab_current is self:
			touch.ungrab(self)
			self.is_moving = False
			
			app = App.get_running_app()
			game_screen = app.root.get_screen("game") 
			
			target_station = None
			for widget in game_screen.walk():
				if isinstance(widget, StationBox) and not isinstance(widget, Block):
					if widget.collide_point(*self.center):
						target_station = widget
						break

			if target_station and target_station.box is None:
				target_station.opacity = 0
				self.pos = target_station.pos
				target_station.box = self
				self.station = target_station
			
			return True
		return super().on_touch_up(touch)

class Rotation(MovableBox):
	def __init__(self,**kwargs):
		super().__init__({L: D, D: L}, "assets/rotation_real.png",**kwargs)
		self.ramkaDown = [0,1,0,.5]
		self.ramkaRight = [1,0,0,.5]
class Crossroads(MovableBox):
	def __init__(self,**kwargs):
		super().__init__({L:R,R:L,D:U,U:D}, "assets/crossroads_real.png",**kwargs)
		self.ramkaDown = [0,1,0,.5]
		self.ramkaUp = [0,1,0,.5]
class Rowation(MovableBox):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.ramkaUp = [0, 0, 1, 1]
		self.value = 0
		self.connections = {L: R, R: L}
		self.apply_rotation()

	def on_touch_down(self, touch):
		if TrainPlay:
			if self.collide_point(*touch.pos):
				self.value = (self.value + 1) % 3
				if self.value == 0:
					self.img.source="assets/forward_real.png"
					self.ramkaUp = [0, 0, 1, 1]
					self.ramkaRight = [0, 1, 0, .5]
					self.connections = {L: R, R: L}
				elif self.value == 1:
					self.img.source="assets/rotation_real.png"
					self.ramkaUp = [0, 1, 0, 1]
					self.ramkaLeft = [0, 0, 1, .5]
					self.connections = {R: U, U: R}
				elif self.value == 2:
					self.ramkaLeft = [0, 1, 0, 1]
					self.ramkaRight = [0, 0, 1, .5]
					self.connections = {L: U, U: L}

				self.apply_rotation()
				return True
		else:
			return super().on_touch_down(touch)
 

class StationBox(Box):
	def __init__(self, grid_x=0, grid_y=0, **kwargs):
		super().__init__(**kwargs)
		self.grid_pos = (grid_x, grid_y)
		self.box = None

	def train_on_enter(self, enter):
		if self.box:
			return self.box.train_on_enter(enter)
		return B

class Block(StationBox):
	def __init__(self, image="", **kwargs):
		super().__init__(**kwargs)
		img = Image(source=image)
		self.add_widget(img)
		self.box = self 

	def train_on_enter(self, enter):
		return B
class Point(StationBox):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.bg_color = [1, 1, 1, 0.3]
class Start(StationBox):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.bg_color = [1, 1, 0, 0.3]

class End(StationBox):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.bg_color = [0, 0, 1, 0.3]
		self.side = R

	def train_on_enter(self, enter):
		if self.box:
			r = self.box.train_on_enter(enter)
			return W if r == self.side else r
		return B