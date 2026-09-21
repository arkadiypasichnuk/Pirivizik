import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from random import randint
if "KIVY_GL_BACKEND" in os.environ:
	Window.size = (1000, 1000)
	del os.environ["KIVY_GL_BACKEND"]

from Screens import Menu, Levels, Level, Game

lvls = []

from random import choice

import tomllib

def CreateLvlsScreen(toml_path,name="main_lvls"):
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    screen = Levels(name=name)
    grid = screen.grid_levels
    for l_data in data.get("levels", []):
        width = l_data.get("cols",3)
        height = l_data.get("rows",3)
        num_id = l_data.get("id",1)
        lab_text = l_data.get("lab_text", "")

        # Створення екземпляра Level
        lvl = Level(width, height, num_id, lab_text)

        pz = lvl.content["pazls"]
        st = lvl.content["stations"]

        # 1. Заповнення пазлів
        for pazl in l_data.get("pazls", []):
            for i in range(0,pazl["count"]):
                pz.append(pazl["type"])

        # 2. Заповнення станцій/блоків
        stations_data = l_data.get("stations", {})
        for pos_str, val in stations_data.items():
            pos = eval(pos_str)
            st[pos] = val

        # 3. Налаштування потяга
        trains_data = l_data.get("trains", [])
        if trains_data and len(lvl.content["trains"]) > 0:
            tr = lvl.content["trains"][0]
            t_info = trains_data[0]

            if "start" in t_info:
                if "pos" in t_info["start"]:
                    tr["start"]["pos"] = tuple(t_info["start"]["pos"])
                if "side" in t_info["start"]:
                    tr["start"]["side"] = t_info["start"]["side"]

            if "end" in t_info:
                if "pos" in t_info["end"]:
                    tr["end"]["pos"] = tuple(t_info["end"]["pos"])
                elif "pos_options" in t_info["end"]:
                    idx = choice(range(len(t_info["end"]["pos_options"])))
                    tr["end"]["pos"] = tuple(t_info["end"]["pos_options"][idx])
                    if "side_options" in t_info["end"]:
                        tr["end"]["side"] = t_info["end"]["side_options"][idx]

                if "side" in t_info["end"]:
                    tr["end"]["side"] = t_info["end"]["side"]

            if "points" in t_info:
                for pt in t_info["points"]:
                    tr["points"].append(tuple(pt))

        # Додавання готового рівня до сітки
        grid.add_widget(lvl)
    lvls.append(screen)

# Замість ручного створення всіх 8 рівнів:
CreateLvlsScreen("suns/Main.toml")

class WidgetsApp(App):
	def build(self):
		sm = ScreenManager()
		sm.current_content = None 
		sm.current_box = None
		sm.add_widget(Menu(name="menu"))
		for l in lvls:
			sm.add_widget(l)
		
		sm.add_widget(Game(name="game"))
		
		return sm

if __name__ == "__main__":
	WidgetsApp().run()
