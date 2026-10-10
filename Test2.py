"""
Space Miner — кликер на KivyMD 2.0.0 с меню уровней на MDCarousel
Установка:  pip install kivy kivymd==2.0.0
Запуск:     python space_miner_v2.py
"""
import os
import random

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import get_color_from_hex

from kivymd.app import MDApp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.carousel import MDCarousel, MDCarouselItem
from kivymd.uix.label import MDIcon, MDLabel

KV = """
MDScreen:
    md_bg_color: "#0d0d1f"

    MDBoxLayout:
        orientation: "vertical"

        MDScreenManager:
            id: sm

            # ---------------- ДОБЫЧА ----------------
            MDScreen:
                name: "Добыча"

                MDFloatLayout:
                    MDLabel:
                        id: planet
                        text: ""
                        halign: "center"
                        font_style: "Title"
                        role: "large"
                        theme_text_color: "Custom"
                        text_color: "#9aa0c8"
                        pos_hint: {"center_x": .5, "center_y": .94}
                        size_hint_y: None
                        height: "40dp"

                    MDLabel:
                        id: score
                        text: "0"
                        halign: "center"
                        font_style: "Display"
                        role: "medium"
                        theme_text_color: "Custom"
                        text_color: "#00e5ff"
                        pos_hint: {"center_x": .5, "center_y": .85}
                        size_hint_y: None
                        height: "70dp"

                    MDLabel:
                        id: stats
                        text: ""
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: "#9aa0c8"
                        pos_hint: {"center_x": .5, "center_y": .77}
                        size_hint_y: None
                        height: "30dp"

                    MDIcon:
                        id: planet_icon
                        icon: "moon-waning-crescent"
                        theme_font_size: "Custom"
                        font_size: "320sp"
                        theme_text_color: "Custom"
                        text_color: "#00e5ff"
                        opacity: .12
                        size_hint: None, None
                        adaptive_size: True
                        pos_hint: {"center_x": .5, "center_y": .45}

                    Gem:
                        id: gem
                        icon: "diamond-stone"
                        theme_font_size: "Custom"
                        font_size: "180sp"
                        theme_text_color: "Custom"
                        text_color: "#00e5ff"
                        size_hint: None, None
                        adaptive_size: True
                        pos_hint: {"center_x": .5, "center_y": .45}
                        on_release: app.mine()

                    MDLabel:
                        text: "Жми на кристалл!"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: "#5d628a"
                        pos_hint: {"center_x": .5, "center_y": .12}
                        size_hint_y: None
                        height: "30dp"

            # ---------------- УРОВНИ (КАРУСЕЛЬ) ----------------
            MDScreen:
                name: "Уровни"

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "0dp", "24dp", "0dp", "24dp"
                    spacing: "12dp"

                    MDLabel:
                        text: "Выбери планету"
                        halign: "center"
                        font_style: "Headline"
                        role: "small"
                        theme_text_color: "Custom"
                        text_color: "#ffffff"
                        size_hint_y: None
                        height: "48dp"

                    MDLabel:
                        text: "Дальше — больше множитель"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: "#5d628a"
                        size_hint_y: None
                        height: "24dp"

                    LevelCarousel:
                        id: carousel
                        layouts: "uncontained"
                        uncontained_item_width: "280dp"

            # ---------------- АПГРЕЙДЫ ----------------
            MDScreen:
                name: "Апгрейды"

                MDScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        id: upgrades
                        orientation: "vertical"
                        adaptive_height: True
                        padding: "12dp"
                        spacing: "12dp"

        MDNavigationBar:
            id: nav
            on_switch_tabs: app.on_switch_tabs(*args)

            MDNavigationItem:
                id: tab_mine
                active: True

                MDNavigationItemIcon:
                    icon: "pickaxe"

                MDNavigationItemLabel:
                    text: "Добыча"

            MDNavigationItem:

                MDNavigationItemIcon:
                    icon: "orbit-variant"

                MDNavigationItemLabel:
                    text: "Уровни"

            MDNavigationItem:

                MDNavigationItemIcon:
                    icon: "rocket-launch"

                MDNavigationItemLabel:
                    text: "Апгрейды"
"""

# название, иконка, множитель, сколько нужно добыть суммарно, фон карточки, цвет кристалла
LEVELS = [
    ("Луна", "moon-waning-crescent", 1, 0, "#1c2541", "#00e5ff"),
    ("Марс", "earth", 2, 500, "#3d1c1c", "#ff7043"),
    ("Юпитер", "orbit", 5, 5_000, "#3b2e1a", "#ffb300"),
    ("Туманность", "creation", 12, 50_000, "#2d1b4e", "#d500f9"),
    ("Зона НЛО", "ufo", 30, 500_000, "#12352b", "#00e676"),
]

# key: (название, описание, база цены, рост цены, +за клик, +в секунду)
UPGRADES = {
    "pick": ("Лазерная кирка", "+1 за клик", 10, 1.15, 1, 0),
    "drone": ("Дрон-шахтёр", "+1 в секунду", 25, 1.15, 0, 1),
    "drill": ("Плазменный бур", "+8 в секунду", 200, 1.17, 0, 8),
    "quantum": ("Квантовый резонатор", "+10 за клик", 500, 1.18, 10, 0),
    "station": ("Орбитальная станция", "+60 в секунду", 3000, 1.2, 0, 60),
}


def fmt(n):
    n = float(n)
    for suffix in ("", "K", "M", "B", "T"):
        if abs(n) < 1000:
            return f"{n:.0f}" if suffix == "" else f"{n:.2f}{suffix}"
        n /= 1000
    return f"{n:.2f}Q"


class Gem(ButtonBehavior, MDIcon):
    """Большой кликабельный кристалл."""


class LevelCarousel(MDCarousel):
    """MDCarousel забирает все касания себе (grab) — из-за этого кнопки на
    карточках не нажимались. Если касание попало на кнопку, отдаём его ей."""

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            for w in self.walk(restrict=True):
                if isinstance(w, MDButton) and w.collide_point(*touch.pos):
                    return w.on_touch_down(touch)
        return super().on_touch_down(touch)


def white_btn_text(text):
    return MDButtonText(text=text, theme_text_color="Custom", text_color="#ffffff")


class SpaceMiner(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"

        self.store = JsonStore(os.path.join(self.user_data_dir, "space_miner_v2.json"))
        self.score = 0.0
        self.total = 0.0
        self.level = 0
        self.levels = {k: 0 for k in UPGRADES}
        self.upgrade_widgets = {}
        self.level_widgets = {}
        self.load()
        return Builder.load_string(KV)

    def on_start(self):
        self.build_levels()
        self.build_upgrades()
        self.apply_level()
        self.refresh()
        Clock.schedule_interval(self.tick, 0.1)
        Clock.schedule_interval(lambda dt: self.save(), 10)

    def on_stop(self):
        self.save()

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        self.root.ids.sm.current = item_text

    # ---------- сохранение ----------
    def load(self):
        if self.store.exists("data"):
            d = self.store.get("data")
            self.score = d.get("score", 0.0)
            self.total = d.get("total", 0.0)
            self.level = d.get("level", 0)
            self.levels.update(d.get("levels", {}))

    def save(self):
        self.store.put(
            "data",
            score=self.score,
            total=self.total,
            level=self.level,
            levels=self.levels,
        )

    # ---------- экономика ----------
    def mult(self):
        return LEVELS[self.level][2]

    def per_click(self):
        base = 1 + sum(UPGRADES[k][4] * lv for k, lv in self.levels.items())
        return base * self.mult()

    def per_sec(self):
        base = sum(UPGRADES[k][5] * lv for k, lv in self.levels.items())
        return base * self.mult()

    def cost(self, key):
        _, _, base, growth, _, _ = UPGRADES[key]
        return int(base * growth ** self.levels[key])

    # ---------- игра ----------
    def mine(self):
        crit = random.random() < 0.1
        gain = self.per_click() * (5 if crit else 1)
        self.score += gain
        self.total += gain
        self.refresh()
        self.pop_text(f"+{fmt(gain)}" + ("!" if crit else ""), crit)

    def pop_text(self, text, crit):
        gem = self.root.ids.gem
        lbl = MDLabel(
            text=text,
            halign="center",
            font_style="Headline",
            role="medium" if crit else "small",
            theme_text_color="Custom",
            text_color="#ffd600" if crit else "#ffffff",
            size_hint=(None, None),
            size=(dp(160), dp(48)),
            pos=(
                gem.center_x - dp(80) + random.randint(-50, 50),
                gem.center_y + dp(30),
            ),
        )
        gem.parent.add_widget(lbl)
        anim = Animation(y=lbl.y + dp(140), opacity=0, duration=0.8, t="out_quad")
        anim.bind(on_complete=lambda *_: gem.parent.remove_widget(lbl))
        anim.start(lbl)

        # «поп» кристалла и вспышка цвета
        Animation.cancel_all(gem, "font_size")
        (
            Animation(font_size=sp(205), duration=0.05)
            + Animation(font_size=sp(180), duration=0.09)
        ).start(gem)
        gem.text_color = "#ffd600" if crit else "#ffffff"
        Clock.schedule_once(lambda dt: self.apply_gem_color(), 0.1)

    def tick(self, dt):
        income = self.per_sec() * dt
        if income:
            self.score += income
            self.total += income
            self.refresh()

    def buy(self, key):
        price = self.cost(key)
        if self.score >= price:
            self.score -= price
            self.levels[key] += 1
            self.refresh()
        else:
            self.toast(f"Не хватает кристаллов: нужно {fmt(price)}")

    def select_level(self, index):
        name, _icon, mult, need, _bg, _col = LEVELS[index]
        if self.total < need:
            self.toast(f"{name} откроется после {fmt(need)} добытых кристаллов")
            return
        self.level = index
        self.apply_level()
        self.refresh()
        ids = self.root.ids
        # возвращаемся на экран добычи и подсвечиваем нужную вкладку внизу
        bar = ids.tab_mine.parent
        bar.set_active_item(bar.children[-1])  # children идут в обратном порядке
        self.toast(f"Летим на «{name}»! Множитель ×{mult}")

    def toast(self, text):
        """Своя всплывающая подсказка (MDSnackbar падает с FBO-ошибкой из-за ripple)."""
        root = self.root
        old = getattr(self, "_toast", None)
        if old is not None and old.parent is not None:
            Animation.cancel_all(old)
            root.remove_widget(old)

        box = MDBoxLayout(
            theme_bg_color="Custom",
            md_bg_color="#2e2e4d",
            radius=[dp(14)],
            padding=[dp(16), dp(10)],
            size_hint=(0.9, None),
            height=dp(52),
            pos_hint={"center_x": 0.5},
            y=dp(100),
            opacity=0,
        )
        box.add_widget(
            MDLabel(
                text=text,
                halign="center",
                valign="middle",
                theme_text_color="Custom",
                text_color="#ffffff",
            )
        )
        root.add_widget(box)
        self._toast = box
        anim = (
            Animation(opacity=1, duration=0.2)
            + Animation(opacity=1, duration=2.0)
            + Animation(opacity=0, duration=0.4)
        )
        anim.bind(
            on_complete=lambda *_: box.parent and box.parent.remove_widget(box)
        )
        anim.start(box)

    # ---------- UI ----------
    def apply_gem_color(self):
        self.root.ids.gem.text_color = LEVELS[self.level][5]

    def apply_level(self):
        """Визуально переключает планету: фон, фоновая иконка, цвет кристалла."""
        _name, icon, _mult, _need, bg, col = LEVELS[self.level]
        ids = self.root.ids
        ids.planet_icon.icon = icon
        ids.planet_icon.text_color = col
        self.apply_gem_color()
        Animation(md_bg_color=get_color_from_hex(bg), duration=0.6).start(self.root)

    def build_levels(self):
        carousel = self.root.ids.carousel
        for i, (name, icon, mult, need, bg, col) in enumerate(LEVELS):
            item = MDCarouselItem(theme_bg_color="Custom", md_bg_color=bg)
            box = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))

            icon_box = MDAnchorLayout(
                anchor_x="center", anchor_y="center", size_hint_y=None, height=dp(130)
            )
            icon_box.add_widget(
                MDIcon(
                    icon=icon,
                    theme_font_size="Custom",
                    font_size="96sp",
                    theme_text_color="Custom",
                    text_color=col,
                )
            )

            title = MDLabel(
                text=name,
                halign="center",
                font_style="Headline",
                role="small",
                theme_text_color="Custom",
                text_color="#ffffff",
                adaptive_height=True,
            )
            info = MDLabel(
                text="",
                halign="center",
                valign="top",
                theme_text_color="Custom",
                text_color="#b0b4d6",
            )

            btn_box = MDAnchorLayout(
                anchor_x="center", anchor_y="center", size_hint_y=None, height=dp(56)
            )
            btn_text = white_btn_text("")
            btn = MDButton(
                btn_text,
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=col,
            )
            btn.bind(on_release=lambda _b, idx=i: self.select_level(idx))
            btn_box.add_widget(btn)

            for w in (icon_box, title, info, btn_box):
                box.add_widget(w)
            item.add_widget(box)
            carousel.add_widget(item)
            self.level_widgets[i] = (info, btn, btn_text)

    def build_upgrades(self):
        box = self.root.ids.upgrades
        for key, (name, desc, *_rest) in UPGRADES.items():
            card = MDCard(
                style="filled",
                theme_bg_color="Custom",
                md_bg_color="#1b1b38",
                orientation="horizontal",
                padding=dp(14),
                spacing=dp(12),
                size_hint_y=None,
                height=dp(96),
                radius=[dp(16)],
            )
            text_box = MDBoxLayout(orientation="vertical")
            title = MDLabel(
                text=name,
                font_style="Title",
                role="medium",
                theme_text_color="Custom",
                text_color="#00e5ff",
            )
            sub = MDLabel(text=desc, theme_text_color="Custom", text_color="#b0b4d6")
            lvl = MDLabel(text="", theme_text_color="Custom", text_color="#5d628a")
            for w in (title, sub, lvl):
                text_box.add_widget(w)

            btn_text = white_btn_text("")
            btn = MDButton(
                btn_text,
                style="filled",
                theme_bg_color="Custom",
                md_bg_color="#37374f",
                pos_hint={"center_y": 0.5},
            )
            btn.bind(on_release=lambda _b, k=key: self.buy(k))

            card.add_widget(text_box)
            card.add_widget(btn)
            box.add_widget(card)
            self.upgrade_widgets[key] = (lvl, btn, btn_text)

    def refresh(self):
        ids = self.root.ids
        name, _icon, mult, _need, _bg, _col = LEVELS[self.level]
        ids.planet.text = f"{name}  ×{mult}"
        ids.score.text = fmt(self.score)
        ids.stats.text = (
            f"{fmt(self.per_click())} за клик  |  {fmt(self.per_sec())} в сек"
            f"  |  всего {fmt(self.total)}"
        )

        for key, (lvl, btn, btn_text) in self.upgrade_widgets.items():
            price = self.cost(key)
            lvl.text = f"Уровень: {self.levels[key]}"
            btn_text.text = fmt(price)
            btn.md_bg_color = "#00acc1" if self.score >= price else "#37374f"

        for i, (lname, _i, lmult, need, _bg, col) in enumerate(LEVELS):
            info, btn, btn_text = self.level_widgets[i]
            unlocked = self.total >= need
            if unlocked:
                info.text = f"Множитель ×{lmult}\nОткрыто"
            else:
                info.text = (
                    f"Множитель ×{lmult}\nОткроется после {fmt(need)} добытых\n"
                    f"(сейчас {fmt(self.total)})"
                )
            if i == self.level:
                btn_text.text = "Ты здесь"
                btn.md_bg_color = "#37374f"
            elif unlocked:
                btn_text.text = "Лететь"
                btn.md_bg_color = col
            else:
                btn_text.text = "Закрыто"
                btn.md_bg_color = "#37374f"


if __name__ == "__main__":
    SpaceMiner().run()