from kivy.app import App
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from random import randint
import Boxes 
from Boxes import MovableBox, StationBox, R, L, U, D, B, W, SizeBlocks, DEFAULT_RAMKA 

DEFAULT_RAMKA[3] = 1

SizeTrainx, SizeTrainy = SizeBlocks * 1.8, SizeBlocks * 1.6

Naprotiv = {
	L: R,
	R: L,
	D: U,
	U: D
}

OFFSET = {
	R: (1, 0),
	L: (-1, 0),
	U: (0, 1),
	D: (0, -1)
}

SP, SS, EP, ES = (0, 1), L, (2, 1), R
povorot = 90
class Train(Image):
	speed = NumericProperty(200)
	angle = NumericProperty(0)

	def __init__(self, st, p, **kwargs):
		super().__init__(source="assets/train.png", **kwargs)
		self.size_hint = (None, None)
		self.size = (SizeTrainx, SizeTrainy)
		self.pos_hint = (None, None)
		self.start =p['start']
		self.end = p["end"]
		self.map = None
		self.points = p["points"]
		self.def_points = self.points.copy()
		self.value = 0
		self.need = len(self.points)
		st[self.start["pos"]] = "Start"
		st[self.end["pos"]] = "End"
		for point in self.points:
			st[point] = "Point"
			
		app = App.get_running_app()
		game_screen = app.root.get_screen('game')
		self.lab = game_screen.ids.input
		

		with self.canvas.before:
			PushMatrix()
			self.rot = Rotate(angle=self.angle, origin=self.center)
		with self.canvas.after:
			PopMatrix()

		self.bind(pos=self._update_rotation_origin, angle=self._update_rotation_angle)
	def inPoint(self,pos):
		for point in self.points:
			if pos == point:
				self.points.remove(point)
				self.value+=1
				break
	def GetPosSide(self, box, side):
		if side == "Up" or side == U:
			return (box.center_x - SizeTrainx / 2, box.top), 90+povorot
		elif side == "Down" or side == D:
			return (box.center_x - SizeTrainx / 2, box.y - SizeTrainy), 270+povorot
		elif side == "Right" or side == R:
			return (box.right, box.center_y - SizeTrainy / 2), 0+povorot
		elif side == "Left" or side == L:
			return (box.x - SizeTrainx, box.center_y - SizeTrainy / 2), 180+povorot
		return (box.x, box.y), 0+povorot

	def get_shortest_target_angle(self, target_angle):
		diff = (target_angle - self.angle + 180) % 360 - 180
		return self.angle + diff
	
	def _update_rotation_origin(self, *args):
		self.rot.origin = self.center

	def _update_rotation_angle(self, *args):
		self.rot.angle = self.angle

	def fill_path(self):
		start = self.map[self.start["pos"]]
		end = self.map[self.end["pos"]]
		
		# Ставим поезд на стартовую позицию и выставляем правильный угол
		target_pos, target_angle = self.GetPosSide(start, self.start["side"])
		anim = Animation(pos=target_pos, angle=target_angle, duration=0.8)
		anim.start(self)
		
		end.side = self.end["side"]
		
		if start:
			setattr(start, "ramka" + self.start["side"], DEFAULT_RAMKA)
		if end:
			setattr(end, "ramka" + end.side, DEFAULT_RAMKA)
		
	def MoveStep(self, anim, instance, cFrame):
		lab = self.lab
		
		pos = cFrame["pos"]
		side = cFrame["side"]
		box = self.map[pos]
		
		r = box.train_on_enter(side)

		if r in (B, W):
			win=True if r == W and self.value==self.need else False
			Boxes.TrainPlay = False
			target_side = getattr(box, "side", Naprotiv[side])
			target_pos,mysor = self.GetPosSide(box, target_side)
			mysor,base_angle = self.GetPosSide(box, Naprotiv[target_side])
			base_angle+=randint(-90,90) if not win else 0
			target_angle = self.get_shortest_target_angle(base_angle)
			
			anim = Animation(pos=target_pos, angle=target_angle, duration=0.8)
			anim.start(self)
			lab.text = "Win" if win else "Loose"
			return
		
		self.inPoint(pos)
		
		np = OFFSET[r]
		new_pos = (pos[0] + np[0], pos[1] + np[1])
		next_box = self.map.get(new_pos, False)
		
		if next_box:
			# Позиция входа в следующий блок и угол, в котором поезд должен оказаться
			next_pos, base_angle = self.GetPosSide(next_box, Naprotiv[r])
			target_angle = self.get_shortest_target_angle(base_angle)
			
			# Движение и поворот синхронно направляются к следующей точке
			anim = Animation(pos=next_pos, angle=target_angle, duration=0.8)
			anim.bind(on_complete=lambda anim_obj, widget: self.MoveStep(
				anim_obj, widget, {"pos": new_pos, "side": Naprotiv[r]}
			))
			anim.start(self)
		else:
			self.pos = (0, 0)
