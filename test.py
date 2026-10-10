from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window

# Данные для категорий и уровней в стиле скриншота
MENU_DATA = [
    {
        "category_title": "CUSTOM LEVELS",
        "title_color": (0.9, 0.3, 0.9, 1),  # Фиолетовый/Неоновый
        "border_color": (0.8, 0.2, 0.8, 1),
        "levels": [
            {"id": 1, "name": "BLOCK BLASTER", "diff": "Normal 4★", "progress": 75},
            {"id": 2, "name": "NEON RUSH", "diff": "Hard 6★", "progress": 20},
            {"id": 3, "name": "GEOMETRIC TRAP", "diff": "Easy 2★", "progress": 100},
            {"id": 4, "name": "CYBER DASH", "diff": "Harder 7★", "progress": 15},
        ]
    },
    {
        "category_title": "WINTER SEASON",
        "title_color": (0.4, 0.8, 1, 1),  # Голубой/Ледяной
        "border_color": (0.2, 0.6, 0.9, 1),
        "levels": [
            {"id": 101, "name": "FROST FLIGHT", "diff": "Normal 3★", "progress": 90},
            {"id": 102, "name": "ICE SPIKE DASH", "diff": "Hard 5★", "progress": 45},
            {"id": 103, "name": "SNOWBALL HAVOC", "diff": "Easy 2★", "progress": 100},
            {"id": 104, "name": "BLIZZARD PEAK", "diff": "Insane 8★", "progress": 5},
        ]
    },
    {
        "category_title": "SUMMER VIBES",
        "title_color": (1, 0.7, 0.2, 1),  # Оранжевый/Солнечный
        "border_color": (0.9, 0.5, 0.1, 1),
        "levels": [
            {"id": 201, "name": "BEACH DASH", "diff": "Easy 2★", "progress": 100},
            {"id": 202, "name": "SUNSET SURF", "diff": "Normal 4★", "progress": 30},
            {"id": 203, "name": "TROPICAL TRAP", "diff": "Hard 6★", "progress": 0},
            {"id": 204, "name": "PALM SHADOWS", "diff": "Medium 5★", "progress": 60},
        ]
    }
]


class LevelCard(BoxLayout):
    """Виджет карточки одного уровня со стилизованной рамкой и прогресс-баром"""
    def __init__(self, level, border_color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (260, 85)
        self.padding = [10, 6, 10, 6]
        self.spacing = 2

        with self.canvas.before:
            # Внешняя цветная рамка категории
            Color(*border_color)
            self.border_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            # Темный внутренний фон карточки
            Color(0.08, 0.1, 0.15, 1)
            self.bg_rect = RoundedRectangle(
                pos=(self.pos[0] + 3, self.pos[1] + 3),
                size=(self.size[0] - 6, self.size[1] - 6),
                radius=[8]
            )
        self.bind(pos=self._update_rects, size=self._update_rects)

        # Верхняя строка: Название и Иконка-заглушка
        top_box = BoxLayout(size_hint_y=0.4, spacing=5)
        
        # Иконка превью (квадратная плашка)
        icon_box = BoxLayout(size_hint=(None, 1), width=28)
        with icon_box.canvas.before:
            Color(0.3, 0.3, 0.4, 1)
            RoundedRectangle(pos=icon_box.pos, size=(28, 28), radius=[4])
        
        title_lbl = Label(
            text=f"LEVEL {level['id'] % 100}: {level['name']}",
            font_size='11sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))

        top_box.add_widget(icon_box)
        top_box.add_widget(title_lbl)
        self.add_widget(top_box)

        # Средняя строка: Сложность
        diff_lbl = Label(
            text=level['diff'],
            font_size='10sp',
            color=(0.8, 0.8, 0.2, 1),
            size_hint_y=0.3,
            halign='left',
            valign='middle'
        )
        diff_lbl.bind(size=diff_lbl.setter('text_size'))
        self.add_widget(diff_lbl)

        # Нижняя строка: Прогресс-бар + %
        progress_box = BoxLayout(size_hint_y=0.3, spacing=5)
        
        pb = ProgressBar(max=100, value=level['progress'], size_hint_x=0.75)
        percent_lbl = Label(
            text=f"{level['progress']}%",
            font_size='10sp',
            bold=True,
            size_hint_x=0.25,
            halign='right',
            valign='middle'
        )
        percent_lbl.bind(size=percent_lbl.setter('text_size'))

        progress_box.add_widget(pb)
        progress_box.add_widget(percent_lbl)
        self.add_widget(progress_box)

    def _update_rects(self, instance, value):
        self.border_rect.pos = instance.pos
        self.border_rect.size = instance.size
        self.bg_rect.pos = (instance.pos[0] + 3, instance.pos[1] + 3)
        self.bg_rect.size = (instance.size[0] - 6, instance.size[1] - 6)


class CategoryRow(BoxLayout):
    """Горизонтальный ряд уровней со стрелками прокрутки влево/вправо"""
    def __init__(self, category_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 2
        self.size_hint_y = None
        self.height = 130

        # Заголовок серии/категории
        title = Label(
            text=category_data["category_title"],
            font_size='16sp',
            bold=True,
            color=category_data["title_color"],
            size_hint_y=None,
            height=25
        )
        self.add_widget(title)

        # Контейнер: Стрелка влево -> ScrollView -> Стрелка вправо
        row_content = BoxLayout(orientation='horizontal', spacing=5)

        btn_left = Button(text="<", size_hint=(None, 1), width=25, background_color=(0.2, 0.2, 0.3, 0.8))
        btn_right = Button(text=">", size_hint=(None, 1), width=25, background_color=(0.2, 0.2, 0.3, 0.8))

        # Сам горизонтальный скролл с картами
        self.scroll = ScrollView(do_scroll_x=True, do_scroll_y=False, bar_width=0)
        
        cards_grid = GridLayout(rows=1, spacing=10, size_hint_x=None, padding=[5, 5, 5, 5])
        cards_grid.bind(minimum_width=cards_grid.setter('width'))

        for lvl in category_data["levels"]:
            card = LevelCard(level=lvl, border_color=category_data["border_color"])
            cards_grid.add_widget(card)

        self.scroll.add_widget(cards_grid)

        # Привязка кнопок со стрелками к смещению скролла
        btn_left.bind(on_release=lambda x: self.scroll_step(-0.3))
        btn_right.bind(on_release=lambda x: self.scroll_step(0.3))

        row_content.add_widget(btn_left)
        row_content.add_widget(self.scroll)
        row_content.add_widget(btn_right)

        self.add_widget(row_content)

    def scroll_step(self, step):
        # Программное смещение ленты при клике на стрелки
        new_x = max(0.0, min(1.0, self.scroll.scroll_x + step))
        self.scroll.scroll_x = new_x


class BottomBar(BoxLayout):
    """Нижняя панель статистики и центральная кнопка PLAY"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 65
        self.padding = [10, 5, 10, 5]
        self.spacing = 10

        with self.canvas.before:
            Color(0.05, 0.05, 0.08, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Левая часть: Игрок и звезды
        left_box = BoxLayout(orientation='vertical', size_hint_x=0.35)
        left_box.add_widget(Label(text="PLAYER123", font_size='11sp', bold=True, color=(0.8, 0.8, 0.8, 1)))
        left_box.add_widget(Label(text="STARS: 1520 ★", font_size='12sp', bold=True, color=(1, 0.9, 0.2, 1)))
        
        # Центр: Зеленая кнопка PLAY
        play_btn = Button(
            text="PLAY",
            font_size='20sp',
            bold=True,
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.2, 0.8, 0.2, 1)
        )

        # Правая часть: Монеты и Алмазы
        right_box = BoxLayout(orientation='vertical', size_hint_x=0.35)
        right_box.add_widget(Label(text="COINS: 250 🪙", font_size='11sp', color=(1, 0.8, 0.2, 1)))
        right_box.add_widget(Label(text="DIAMONDS: 4100 💎", font_size='11sp', color=(0.3, 0.8, 1, 1)))

        self.add_widget(left_box)
        self.add_widget(play_btn)
        self.add_widget(right_box)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size


class GDMultiCategoryMenu(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Главный вертикальный контейнер
        main_layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 0], spacing=5)

        # 1. Шапка меню
        header = Label(
            text="LEVEL SELECT",
            font_size='22sp',
            bold=True,
            color=(0.3, 0.9, 1, 1),
            size_hint_y=None,
            height=35
        )
        main_layout.add_widget(header)

        # 2. Основная область с тремя рядами категорий
        content_scroll = ScrollView(do_scroll_y=True, do_scroll_x=False)
        rows_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        rows_container.bind(minimum_height=rows_container.setter('height'))

        for category_info in MENU_DATA:
            row = CategoryRow(category_data=category_info)
            rows_container.add_widget(row)

        content_scroll.add_widget(rows_container)
        main_layout.add_widget(content_scroll)

        # 3. Нижняя панель
        main_layout.add_widget(BottomBar())

        self.add_widget(main_layout)


class GDApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.04, 0.07, 1)
        return GDMultiCategoryMenu()

if __name__ == '__main__':
    GDApp().run()