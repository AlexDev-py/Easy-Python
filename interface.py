"""

Интерфейс приложения.

"""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk, messagebox
from functools import wraps
from typing import Any
from dataclasses import dataclass

from PIL import ImageTk, Image

from sources.quests.quests import Quests, Quest, Task
from main import (
    log_in, sign_in, complete_quest, reconnection,
    USER_NAME, USER_ID, interface, AttrMap
)

with open('settings.json') as settings:
    settings = AttrMap(json.load(settings))

root = tk.Tk()
profile: AttrMap
root.config(bg=settings.ROOT_BG)
root.geometry('800x500')
root.resizable(False, False)
root.title('Easy-Python: Учить Python легко!')


class Alert:
    """
    Виджет, показывающий сообщение на экран
    """

    alert_frame = tk.Frame(root, bg=settings.ROOT_BG)
    alert: Alert = None

    def __init__(self, message, *, can_hide=True, show_time=5):
        """
        :param message: Текст, который отобразится.
        :param can_hide:
            Для True - Сообщение само скроется через 5 секунд.
            Для False - Сообщение будет висеть постоянно.
        :param show_time: Длительность показа сообщения.
        """

        for alert in Alert.alert_frame.winfo_children():
            alert.destroy()
        self.can_hide = can_hide
        self.alert_frame = tk.Frame(Alert.alert_frame, bg=settings.CONSP_BG)
        self.alert_lb = tk.Label(
            self.alert_frame, text=message,
            bg=settings.CONSP_BG, fg=settings.CONSP_FG
        )
        self.alert_frame.pack(fill=tk.X)
        self.alert_lb.pack()
        if can_hide:
            root.after(show_time * 1000, self.destroy)

    def destroy(self):
        """
        Удаляет сообщение
        """

        self.alert_frame.destroy()
        self.alert_lb.destroy()
        Alert.alert_frame.update()
        Alert.alert = None

    @classmethod
    def show(cls, message: str, *, can_hide=True, show_time=5):
        """
        Показывает сообщение ```message```
        """

        if cls.alert:
            if cls.alert.can_hide is False:
                return
            cls.alert.destroy()
        cls.alert = Alert(message, can_hide=can_hide, show_time=show_time)

    @classmethod
    def prepare(cls):
        """
        Подготовка поля для вывода уведомлений.
        """

        cls.alert_frame.pack(side='top', fill='x')
        cls.show('Подготовка...', show_time=1)


class ScrollableFrame(tk.Frame):
    """
    Прокручиваемый фрейм
    """

    def __init__(self, master, width=None, bind_all=True):
        super().__init__(master)

        self.canvas = tk.Canvas(
            self, bg=settings.ROOT_BG, highlightthickness=0,
            width=width
        )
        if bind_all:
            self.canvas.bind_all('<MouseWheel>', self.wheel_scroll)
        else:
            self.canvas.bind('<MouseWheel>', self.wheel_scroll)
        self.scrollable_frame = tk.Frame(
            self.canvas, bg=settings.ROOT_BG, bd=10
        )
        self.scrollable_frame.bind(
            '<Configure>', lambda event:
            self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
        )
        self._scrollable_frame = self.canvas.create_window(
            0, 0, window=self.scrollable_frame, anchor=tk.NW
        )
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Vertical.TScrollbar', gripcount=0, backgroung=settings.CONSP_BG,
            darkcolor=settings.ROOT_BG, lightcolor=settings.ROOT_BG,
            troughcolor=settings.ROOT_BG, bordercolor=settings.ROOT_BG,
            arrowcolor=settings.ROOT_BG
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(
            self._scrollable_frame, width=event.width
        ))
        self.bind(
            '<Destroy>', lambda event: self.canvas.unbind_all('<MouseWheel>')
        )

    def wheel_scroll(self, event):
        """
        Прокрутка колёсиком мыши
        """

        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)
        except tk.TclError:
            pass


class QuestWidget(tk.Canvas):
    """
    Виджет темы.
    """

    def __init__(self, master: tk.Frame, quest: Quest, _locals: dict):
        super().__init__(master, bg=settings.ROOT_BG, highlightthickness=0)
        self._img_dark_zone = Images.IMG_DARK_ZONE
        self.dark_zone = self.create_image(0, 0, image=self._img_dark_zone)
        self.bind('<Configure>', self._create_dark_zone)
        self.quest = quest
        self.frame = tk.Frame(self, bg=settings.SECONDARY_BG, bd=5)
        self.name = tk.Label(
            self.frame, text=quest.name,
            bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
            font=settings.BIG_FONT
        )
        self.tasks_count = tk.Label(
            self.frame, text=f'Количество заданий: {quest.tasks_count}',
            bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
            font=settings.SMALL_FONT
        )
        self.status_canvas = tk.Canvas(
            self.frame, bg=settings.SECONDARY_BG, highlightthickness=0
        )
        self.status_canvas.pack(side=tk.RIGHT, padx=30)
        if (
                quest.name in profile.completed_tasks and
                float(profile.completed_tasks[quest.name]['score']) > 0
        ):
            self.status = tk.Label(
                self.status_canvas, bg=settings.CONSP_BG,
                text='Выполнено', fg=settings.ROOT_BG
            )
            self.status.pack(pady=5, padx=5, side=tk.LEFT)
            self._img_yellow_zone = Images.IMG_YELLOW_ZONE
            self.status_ok = tk.Label(
                self.status_canvas, bg=settings.CONSP_BG, image=Images.IMG_OK
            )
            self.status_ok.pack(side=tk.RIGHT, padx=5)
            self.status_yellow_zone = self.status_canvas.create_image(
                0, 0, image=self._img_yellow_zone
            )
            self.status_canvas.bind('<Configure>', self._create_yellow_zone)

        else:
            self.status = tk.Label(
                self.status_canvas, bg=settings.SECONDARY_BG,
                text='Не выполнено', fg=settings.YELLOW
            )
            self.status.pack(pady=5, padx=5)
            self.status_canvas.bind(
                '<Configure>', lambda event: rounded_rect(
                    self.status_canvas, 0, 0,
                    event.width - 1, event.height - 1, 10
                ))
        if quest.name in profile.completed_tasks:
            self.completed_tasks = tk.Label(
                self.frame, font=settings.SMALL_FONT,
                text='Выполнено заданий: {}'.format(
                    profile.completed_tasks[quest.name]["completed_count"]),
                bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
            )
            self.score_tasks = tk.Label(
                self.frame, font=settings.SMALL_FONT,
                text='Получено баллов: '
                     f'{profile.completed_tasks[quest.name]["score"]}',
                bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
            )
            self.try_count_tasks = tk.Label(
                self.frame, font=settings.SMALL_FONT,
                text='Количество прохождений: '
                     f'{profile.completed_tasks[quest.name]["try_count"]}',
                bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
            )
            self.try_count_tasks.pack(side=tk.BOTTOM, anchor=tk.NW)
            self.score_tasks.pack(side=tk.BOTTOM, anchor=tk.NW)
            self.completed_tasks.pack(side=tk.BOTTOM, anchor=tk.NW)
        self.name.pack(side=tk.TOP, anchor=tk.NW)
        self.tasks_count.pack(anchor=tk.NW)
        self.frame.pack(fill=tk.X, padx=10, pady=20)
        self.pack(fill=tk.X, pady=10)
        self.frame.bind('<Button-1>', lambda event: quest_preview_view(
            home_view, _locals=_locals, quest=self.quest
        ))
        self.name.bind('<Button-1>', lambda event: quest_preview_view(
            home_view, _locals=_locals, quest=self.quest
        ))
        self.bind('<Destroy>', lambda event: self.unbind_all('<Button-1>'))

    def _create_dark_zone(self, event):
        width, height = event.width, event.height
        self._img_dark_zone = open_img(
            Images.dp + 'dark_zone.png',
            size=(width, height), proportions=False
        )
        self.coords(self.dark_zone, width / 2, height / 2)
        self.itemconfig(self.dark_zone, image=self._img_dark_zone)

    def _create_yellow_zone(self, event):
        width, height = event.width, event.height
        self._img_yellow_zone = open_img(
            Images.dp + 'yellow_zone.png',
            size=(width, height), proportions=False
        )
        self.status_canvas.coords(
            self.status_yellow_zone, width / 2, height / 2
        )
        self.status_canvas.itemconfig(
            self.status_yellow_zone, image=self._img_yellow_zone
        )


class TaskLabel(tk.Label):
    """
    Элемент из списка заданий
    """

    def __init__(
            self, master: tk.Frame, task_index: int, task: Task,
            open_task, **kwargs
    ):
        super().__init__(master, **kwargs)
        self.task = task
        self.task_index = task_index
        self.bind('<Button-1>', lambda event: open_task(self.task, task_index))
        self.pack(anchor=tk.NW)


def open_img(
        path: str, size: tuple = (80, 50),
        proportions=True, need_resize=True
) -> ImageTk.PhotoImage:
    """
    Открытие изображения
    """

    img = Image.open(f'{path}')
    if need_resize:
        if proportions:
            img.thumbnail(size, Image.ANTIALIAS)
        else:
            img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)


def rounded_rect(
        canvas, x, y, width, height, radius, color=settings.CONSP_BG
):
    """
    Рисует прямоугольник с закруглёнными краями
    """

    canvas.create_arc(
        x, y, x + 2 * radius, y + 2 * radius,
        start=90, extent=90, style="arc", outline=color)
    canvas.create_arc(
        x + width - 2 * radius, y + height - 2 * radius, x + width, y + height,
        start=270, extent=90, style="arc", outline=color)
    canvas.create_arc(
        x + width - 2 * radius, y, x + width, y + 2 * radius,
        start=0, extent=90, style="arc", outline=color)
    canvas.create_arc(
        x, y + height - 2 * radius, x + 2 * radius, y + height,
        start=180, extent=90, style="arc", outline=color)
    canvas.create_line(
        x + radius, y, x + width - radius, y, fill=color
    )
    canvas.create_line(
        x + radius, y + height, x + width - radius, y + height,
        fill=color
    )
    canvas.create_line(
        x, y + radius, x, y + height - radius, fill=color
    )
    canvas.create_line(
        x + width, y + height - radius, x + width, y + radius,
        fill=color
    )


class Images:
    """
    Все подгруженные изображения
    """

    dp = 'sources/images/'
    IMG_LOG_IN = open_img(dp + 'btn_log_in.png', size=(160, 60))
    IMG_SIGN_IN = open_img(dp + 'btn_sign_in.png', size=(180, 70))
    IMG_RUN = open_img(dp + 'btn_run.png', size=(160, 60))
    IMG_CANCEL = open_img(dp + 'btn_cancel.png', size=(160, 60))
    IMG_OK = open_img(dp + 'ok.png', size=(10, 10))
    IMG_DARK_ZONE = open_img(dp + 'dark_zone.png', need_resize=False)
    IMG_YELLOW_ZONE = open_img(dp + 'yellow_zone.png', need_resize=False)


@dataclass
class QuestProcess:
    """
    Класс, хранящий в себе информацию о тестировании
    """

    """ Выбранная тема """
    quest: Quest
    """ Страница с которой осуществлён переход """
    last_view: Any
    """ Функция, обновляющая ответ для выбранного задания """
    update_answer: Any
    """ Индекс выбранного задания """
    selected_task_index: int = None
    """ Кол-во секунд до завершения тестирования """
    time: int = None
    """ Время до завершения тестирования, которое видит пользователь """
    time_var: tk.StringVar = None
    """ Ответы, которые ввел пользователь {<task_index>: <value>} """
    answers: dict = None
    """ Кол-во выполненных заданий """
    completed_count: int = 0
    """ Набрано очков """
    score: float = 0
    widgets: dict = None
    process: bool = True

    def __post_init__(self):
        self.time = self.quest.time_limit
        self.time_var = tk.StringVar(
            value=f'{self.time // 60}м {self.time % 60}с'
        )
        self.answers = {i: '' for i in range(len(self.quest.tasks))}
        root.after(1000, self.timer)

    def timer(self):
        """
        Ведёт отсчёт времени
        """

        self.time -= 1
        self.time_var.set(f'{self.time // 60}м {self.time % 60}с')
        if self.time > 0:
            root.after(1000, self.timer)
        else:
            if self.process:
                self.stop_quest()

    def stop_quest(self):
        """
        Завершение тестирования
        """

        self.process = False
        self.update_answer()
        self.completed_count = len([
            True for i, task in enumerate(self.quest.tasks)
            if task.answer == self.answers[i]
        ])
        self.score = round(
            self.completed_count / self.quest.tasks_count * 10, 2
        )
        complete_quest(interface, self)
        quest_results_view(self.last_view, self, _locals=self.widgets)


def view(func):
    """
    Декоратор для удобного перехода между страницами приложения.
    """

    @wraps(func)
    def _wrap(*args, _locals: dict = None, **kwargs):
        # Удаление элементов старой страницы
        if _locals:
            for obj in _locals.values():
                if hasattr(obj, 'destroy'):
                    obj.destroy()
        # Запуск новой страницы
        func(*args, **kwargs)

    return _wrap


@view
def log_in_view():
    """
    Страница авторизации.
    """

    root.geometry('620x465')
    root.title('Авторизация')
    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=5)
    canvas_input = tk.Canvas(
        frame_main, bg=settings.ROOT_BG, highlightthickness=0
    )
    dark_zone = canvas_input.create_image(0, 0, image=Images.IMG_DARK_ZONE)
    canvas_input.pack()
    frame_input = tk.Frame(canvas_input, bg=settings.SECONDARY_BG, bd=10)
    lb_login = tk.Label(
        frame_input, text='Логин', fg=settings.ROOT_FG,
        bg=settings.SECONDARY_BG, font=settings.FONT
    )
    entry_login = tk.Entry(
        frame_input, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG, font=settings.FONT,
        relief=tk.FLAT, insertbackground=settings.ROOT_FG, width=25
    )
    lb_password = tk.Label(
        frame_input, text='Пароль', fg=settings.ROOT_FG,
        bg=settings.SECONDARY_BG, font=settings.FONT
    )
    entry_password = tk.Entry(
        frame_input, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG, font=settings.FONT,
        relief=tk.FLAT, insertbackground=settings.ROOT_FG,
        show='*', width=25
    )
    lb_login.grid(row=0, column=0, sticky=tk.E)
    entry_login.grid(row=0, column=1, sticky=tk.W, padx=10)
    lb_password.grid(row=1, column=0, sticky=tk.E, pady=15)
    entry_password.grid(row=1, column=1, sticky=tk.W, pady=15, padx=10)
    frame_input.pack(pady=15, padx=25)

    def _create_dark_zone(event):
        width, height = event.width, event.height
        Images.IMG_DARK_ZONE_LOG_IN = open_img(
            Images.dp + 'dark_zone.png',
            size=(width, height), proportions=False
        )
        canvas_input.coords(dark_zone, width / 2, height / 2)
        canvas_input.itemconfig(dark_zone, image=Images.IMG_DARK_ZONE_LOG_IN)

    canvas_input.bind('<Configure>', _create_dark_zone)
    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)
    btn_log_in = tk.Label(
        frame_btns, image=Images.IMG_LOG_IN, bg=settings.ROOT_BG
    )
    btn_sign_in = tk.Label(
        frame_btns, text='Зарегистрироваться', font=settings.SMALL_FONT,
        bg=settings.ROOT_BG, fg=settings.CONSP_BG
    )
    btn_sign_in.pack(side=tk.BOTTOM)
    btn_log_in.pack(side=tk.BOTTOM)
    frame_btns.pack(pady=50)
    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE, pady=30)
    entry_login.focus()
    _locals = locals()
    btn_sign_in.bind('<Button-1>', lambda event: sign_in_view(_locals=_locals))
    root.bind_all('<Return>', lambda event: log_in(
        root=interface, _locals=_locals,
        login=entry_login.get(), password=entry_password.get()
    ))
    btn_log_in.bind('<Button-1>', lambda event: log_in(
        interface, _locals, entry_login.get(), entry_password.get()
    ))


@view
def sign_in_view():
    """
    Страница регистрации.
    """

    root.geometry('620x465')
    root.title('Регистрация')
    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=5)
    canvas_input = tk.Canvas(
        frame_main, bg=settings.ROOT_BG, highlightthickness=0
    )
    dark_zone = canvas_input.create_image(0, 0, image=Images.IMG_DARK_ZONE)
    canvas_input.pack()
    frame_input = tk.Frame(canvas_input, bg=settings.SECONDARY_BG, bd=10)
    lb_login = tk.Label(
        frame_input, text='Имя пользователя', fg=settings.ROOT_FG,
        bg=settings.SECONDARY_BG, font=settings.FONT
    )
    entry_login = tk.Entry(
        frame_input, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG, font=settings.FONT,
        relief=tk.FLAT, insertbackground=settings.ROOT_FG, width=22
    )
    lb_password = tk.Label(
        frame_input, text='Пароль', fg=settings.ROOT_FG,
        bg=settings.SECONDARY_BG, font=settings.FONT
    )
    entry_password = tk.Entry(
        frame_input, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG, font=settings.FONT,
        relief=tk.FLAT, insertbackground=settings.ROOT_FG,
        show='*', width=22
    )
    lb_password2 = tk.Label(
        frame_input, text='Повторите пароль', fg=settings.ROOT_FG,
        bg=settings.SECONDARY_BG, font=settings.FONT
    )
    entry_password2 = tk.Entry(
        frame_input, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG, font=settings.FONT,
        relief=tk.FLAT, insertbackground=settings.ROOT_FG,
        show='*', width=22
    )
    lb_login.grid(row=0, column=0, sticky=tk.E)
    entry_login.grid(row=0, column=1, sticky=tk.SW, padx=10)
    lb_password.grid(row=1, column=0, sticky=tk.E, pady=15)
    entry_password.grid(row=1, column=1, sticky=tk.SW, pady=15, padx=10)
    lb_password2.grid(row=2, column=0, sticky=tk.E)
    entry_password2.grid(row=2, column=1, sticky=tk.SW, padx=10)
    frame_input.pack(pady=15, padx=15)

    def _create_dark_zone(event):
        width, height = event.width, event.height
        Images.IMG_DARK_ZONE_SIGN_IN = open_img(
            Images.dp + 'dark_zone.png',
            size=(width, height), proportions=False
        )
        canvas_input.coords(dark_zone, width / 2, height / 2)
        canvas_input.itemconfig(dark_zone, image=Images.IMG_DARK_ZONE_SIGN_IN)

    canvas_input.bind('<Configure>', _create_dark_zone)
    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)
    btn_sign_in = tk.Label(
        frame_btns, image=Images.IMG_SIGN_IN, bg=settings.ROOT_BG
    )
    btn_log_in = tk.Label(
        frame_btns, text='Войти в существующий профиль',
        font=settings.SMALL_FONT, bg=settings.ROOT_BG, fg=settings.CONSP_BG
    )
    btn_log_in.pack(side=tk.BOTTOM)
    btn_sign_in.pack(side=tk.BOTTOM)
    frame_btns.pack(pady=55)
    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE, pady=15)
    entry_login.focus()
    _locals = locals()
    btn_log_in.bind('<Button-1>', lambda event: log_in_view(_locals=_locals))
    root.bind_all('<Return>', lambda event: sign_in(
        root=interface, _locals=_locals, login=entry_login.get(),
        password=entry_password.get(), password2=entry_password2.get()
    ))
    btn_sign_in.bind('<Button-1>', lambda event: sign_in(
        interface, _locals, entry_login.get(),
        entry_password.get(), entry_password2.get()
    ))


@view
def home_view(need_resize=True):
    """
    Главная страница приложения.
    Страница выбора темы.
    """

    Alert.alert_frame.destroy()
    root.title('Easy-Python: Учить Python легко!')
    if need_resize:
        root.geometry('800x500')
        root.minsize(650, 400)
        root.resizable(True, True)
    frame_main = tk.Frame(bg=settings.ROOT_BG)
    frame_tools = tk.Frame(frame_main, bg=settings.ROOT_BG, bd=10)
    canvas_profile = tk.Canvas(
        frame_tools, bg=settings.ROOT_BG, highlightthickness=0
    )
    dark_zone = canvas_profile.create_image(0, 0, image=Images.IMG_DARK_ZONE)
    canvas_profile.pack()
    frame_profile = tk.Frame(canvas_profile, bg=settings.SECONDARY_BG, bd=2)
    frame_profile_lbs = tk.Frame(frame_profile, bg=settings.SECONDARY_BG)
    profile_icon = tk.Canvas(frame_profile, width=35, height=35, bg='#FFF')
    profile_name = tk.Label(
        frame_profile_lbs, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        font=settings.FONT, text=USER_NAME
    )
    profile_id = tk.Label(
        frame_profile_lbs, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        text=f'#{USER_ID}'
    )
    profile_icon.pack(side=tk.LEFT)
    profile_name.pack(side=tk.TOP, anchor=tk.SW)
    profile_id.pack(anchor=tk.NW)
    frame_profile_lbs.pack(padx=10)
    frame_profile.pack(side=tk.TOP, pady=5, padx=10)

    def _create_dark_zone(event):
        width, height = event.width, event.height
        Images.IMG_DARK_ZONE_PROFILE = open_img(
            Images.dp + 'dark_zone.png',
            size=(width, height), proportions=False
        )
        canvas_profile.coords(dark_zone, width / 2, height / 2)
        canvas_profile.itemconfig(
            dark_zone, image=Images.IMG_DARK_ZONE_PROFILE
        )

    canvas_profile.bind('<Configure>', _create_dark_zone)
    frame_filters = tk.Frame(frame_tools, bg=settings.SECONDARY_BG)
    frame_filters.pack(fill=tk.Y)
    frame_tools.pack(side=tk.LEFT, fill=tk.Y)
    frame_content = tk.Frame(frame_main, bg=settings.ROOT_BG)
    Alert.alert_frame = tk.Frame(frame_content, bg=settings.ROOT_BG)
    Alert.alert_frame.pack(side='top', fill='x')
    Alert.show('Подготовка...', show_time=1)
    frame_quests = ScrollableFrame(frame_content)
    _locals = locals()
    for quest in Quests.quests:
        QuestWidget(
            frame_quests.scrollable_frame, quest=quest, _locals=_locals
        )
    frame_quests.pack(fill=tk.BOTH, expand=tk.TRUE)
    frame_content.pack(fill=tk.BOTH, expand=tk.TRUE)
    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE)

    def root_configure_handler(_event):
        """
        Обработчик изменений в окне
        """

        if root.winfo_width() < 800 and len(USER_NAME) > 10:
            profile_name.config(text=USER_NAME[:5].strip() + '...')
        elif root.winfo_width() > 1200:
            if len(USER_NAME) < 25:
                profile_name.config(text=USER_NAME)
            else:
                profile_name.config(text=USER_NAME[:17].strip() + '...')
        else:
            if len(USER_NAME) < 15:
                profile_name.config(text=USER_NAME)
            else:
                profile_name.config(text=USER_NAME[:12].strip() + '...')

    root.bind('<Configure>', root_configure_handler)
    frame_main.bind('<Destroy>', lambda event: root.unbind('<Configure>'))


@view
def quest_preview_view(last_view, quest: Quest):
    """
    Страница подтверждения начала тестирования.
    :param last_view: Пред идущая страница.
    :param quest: Данные о выбранном задании.
    """

    root.title(f'Тема: {quest.name}')

    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=5)
    canvas_info = tk.Canvas(
        frame_main, bg=settings.ROOT_BG, highlightthickness=0
    )
    dark_zone = canvas_info.create_image(0, 0, image=Images.IMG_DARK_ZONE)
    canvas_info.pack()
    frame_info = tk.Frame(canvas_info, bg=settings.SECONDARY_BG, bd=10)
    lb_info = tk.Label(
        frame_info, font=settings.FONT,
        text=f'Вы хотите начать прохождение теста на тему\n"{quest.name}"?\n'
             'Чтобы пройти тест, необходимо выполнить хотя бы\n'
             f'одно из {quest.tasks_count} заданий.',
        bg=settings.SECONDARY_BG, fg=settings.ROOT_FG
    )
    lb_info.pack()
    frame_info.pack(padx=10, pady=10)

    def _create_dark_zone(event):
        width, height = event.width, event.height
        Images.IMG_DARK_ZONE_PREVIEW_QUEST = open_img(
            Images.dp + 'dark_zone.png',
            size=(width, height), proportions=False
        )
        canvas_info.coords(dark_zone, width / 2, height / 2)
        canvas_info.itemconfig(
            dark_zone, image=Images.IMG_DARK_ZONE_PREVIEW_QUEST
        )

    canvas_info.bind('<Configure>', _create_dark_zone)
    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)
    btn_cancel = tk.Label(
        frame_btns, image=Images.IMG_CANCEL, bg=settings.ROOT_BG
    )
    btn_submit = tk.Label(
        frame_btns, image=Images.IMG_RUN, bg=settings.ROOT_BG
    )
    btn_cancel.pack(side=tk.LEFT, padx=5)
    btn_submit.pack(side=tk.RIGHT, padx=5)
    frame_btns.pack(pady=30)
    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE, pady=30)
    _locals = locals()
    btn_cancel.bind('<Button-1>', lambda event: last_view(
        need_resize=False, _locals=_locals
    ))
    btn_submit.bind('<Button-1>', lambda event: quest_view(
        last_view, quest, _locals=_locals
    ))


@view
def quest_view(last_view, quest: Quest):
    """
    Страница тестирования.
    :param last_view: Пред идущая страница.
    :param quest: Данные о выбранном задании.
    """

    def update_answer():
        """
        Обновляем ответ
        """

        quest_proc.answers[quest_proc.selected_task_index] =\
            input_answer.get(1.0, tk.END).strip()

    def stop_quest_control():
        """
        Запрос на подтверждение о завершении тестирования
        """

        if messagebox.askquestion(
                'Подтверждение действий',
                'Вы действительно хотите завершить тестирование?'
        ) == 'yes':
            quest_proc.time = 0
            Alert.show('Тестирование завершено')
            quest_proc.stop_quest()

    quest_proc = QuestProcess(
        quest=quest, last_view=last_view, update_answer=update_answer
    )
    Alert.alert_frame.destroy()
    frame_main = tk.Frame(bg=settings.ROOT_BG)
    frame_tools = tk.Frame(frame_main, bg=settings.ROOT_BG, bd=10)
    canvas_tools = tk.Canvas(
        frame_tools, bg=settings.ROOT_BG, highlightthickness=0
    )
    dark_zone_tools = canvas_tools.create_image(
        0, 0, image=Images.IMG_DARK_ZONE
    )
    canvas_tools.pack()
    frame_info = tk.Frame(canvas_tools, bg=settings.SECONDARY_BG, bd=2)
    time_limit = tk.Label(
        frame_info, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        font=settings.BIG_FONT, textvariable=quest_proc.time_var
    )
    btn_exit = tk.Button(
        frame_info, bg=settings.CONSP_BG, fg=settings.CONSP_FG,
        text='Завершить тестирование'
    )
    time_limit.pack(side=tk.TOP, anchor=tk.SW)
    btn_exit.pack(anchor=tk.SW, pady=15)
    frame_info.pack(padx=10, pady=10)
    frame_tools.pack(side=tk.TOP, pady=5, padx=10)

    def _create_dark_zone(event):
        width, height = event.width, event.height
        Images.IMG_DARK_ZONE_QUEST_INFO = open_img(
            Images.dp + 'dark_zone.png',
            size=(width, height), proportions=False
        )
        canvas_tools.coords(dark_zone_tools, width / 2, height / 2)
        canvas_tools.itemconfig(
            dark_zone_tools, image=Images.IMG_DARK_ZONE_QUEST_INFO
        )
        rounded_rect(
            canvas_tools, 2, 2, event.width - 4,
            event.height - 4, 12
        )

    canvas_tools.bind('<Configure>', _create_dark_zone)
    lb_tasks_info = tk.Label(
        frame_tools, text='Список заданий',
        bg=settings.ROOT_BG, fg=settings.ROOT_FG, font=settings.FONT
    )
    frame_tasks = ScrollableFrame(frame_tools, width=200, bind_all=False)

    def open_task(selected_task: Task, task_index: int):
        """
        Отображает выбранное задание
        """

        update_answer()
        quest_proc.selected_task_index = task_index
        input_answer.delete(1.0, tk.END)
        input_answer.insert(1.0, quest_proc.answers[task_index])
        tz_zone.config(state=tk.NORMAL)
        tz_zone.delete(1.0, tk.END)
        tz_zone.insert(1.0, selected_task.task)
        tz_zone.config(state=tk.DISABLED)

    for i, task in enumerate(quest.tasks):
        TaskLabel(
            frame_tasks.scrollable_frame, text=f'{i}. {task.question[:20]}...',
            task_index=i, task=task, open_task=open_task,
            bg=settings.ROOT_BG, fg=settings.ROOT_FG,
        )
    lb_tasks_info.pack(pady=10)
    frame_tasks.pack(fill=tk.Y, pady=5)
    canvas_tools.bind('<Configure>', _create_dark_zone)
    frame_tools.pack(side=tk.LEFT, fill=tk.Y)
    frame_content = tk.Frame(frame_main, bg=settings.ROOT_BG)
    Alert.alert_frame = tk.Frame(frame_content, bg=settings.ROOT_BG)
    Alert.alert_frame.pack(side='top', fill='x')
    Alert.show('Начинайте решать', show_time=1)
    lb_tz = tk.Label(
        frame_content, text='Задание', font=settings.BIG_FONT,
        bg=settings.ROOT_BG, fg=settings.ROOT_FG
    )
    tz_zone = tk.Text(
        frame_content, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        relief=tk.FLAT, highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG,
        insertbackground=settings.ROOT_FG
    )
    input_answer = tk.Text(
        frame_content, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        relief=tk.FLAT, highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG,
        insertbackground=settings.ROOT_FG
    )
    open_task(quest.tasks[0], 0)
    frame_content.bind('<Configure>', lambda event: tz_zone.config(
        height=event.height * 0.7 / 20
    ))
    btn_exit.bind('<Button-1>', lambda event: stop_quest_control())
    lb_tz.pack(pady=3, padx=10, anchor=tk.W)
    tz_zone.pack(fill=tk.X, padx=10)
    input_answer.pack(fill=tk.X, pady=5, padx=10)
    frame_content.pack(fill=tk.BOTH, expand=tk.TRUE)
    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE)
    _locals = locals()
    quest_proc.widgets = _locals


@view
def quest_results_view(last_view, quest_proc: QuestProcess):
    """
    Страница показывающая результаты тестирования.
    :param last_view: Пред идущая страница.
    :param quest_proc: Данные о тестировании.
    """

    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=5)
    canvas_info = tk.Canvas(
        frame_main, bg=settings.ROOT_BG, highlightthickness=0
    )
    dark_zone = canvas_info.create_image(0, 0, image=Images.IMG_DARK_ZONE)
    canvas_info.pack()
    frame_info = tk.Frame(canvas_info, bg=settings.SECONDARY_BG, bd=10)
    lb_info = tk.Label(
        frame_info, font=settings.FONT,
        text=(
            f'Вы провалили тестирование на тему\n"{quest_proc.quest.name}",\n'
            'так как не выполнили ни одного задания.'
            if quest_proc.completed_count < 1 else
            f'Вы успешно прошли тестирование по теме\n'
            f'"{quest_proc.quest.name}"\n'
            f'Вы выполнили {quest_proc.completed_count} '
            f'из {quest_proc.quest.tasks_count} заданий\n'
            f'и набрали {quest_proc.score} баллов!' + (
                '\nВы можете пройти тестирование заново\n'
                'и повысить свои результаты!'
                if quest_proc.score != 10 else '')
        ),
        bg=settings.SECONDARY_BG, fg=settings.ROOT_FG
    )
    lb_info.pack()
    frame_info.pack(padx=10, pady=10)

    def _create_dark_zone(event):
        width, height = event.width, event.height
        Images.IMG_DARK_ZONE_PREVIEW_QUEST = open_img(
            Images.dp + 'dark_zone.png',
            size=(width, height), proportions=False
        )
        canvas_info.coords(dark_zone, width / 2, height / 2)
        canvas_info.itemconfig(
            dark_zone, image=Images.IMG_DARK_ZONE_PREVIEW_QUEST
        )

    canvas_info.bind('<Configure>', _create_dark_zone)
    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)
    btn_continue = tk.Label(
        frame_btns, image=Images.IMG_RUN, bg=settings.ROOT_BG
    )
    btn_continue.pack()
    frame_btns.pack(pady=30)
    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE, pady=30)
    _locals = locals()
    btn_continue.bind('<Button-1>', lambda event: last_view(
        need_resize=False, _locals=_locals
    ))


@view
def connection_error_view(error_info: str = ''):
    """
    Окно, сообщающее об ошибке подключения к серверу
    """

    root.geometry('560x420')
    root.title('Ошибка соединения')
    frame_main = tk.Frame(bg=settings.ROOT_BG)
    lb1 = tk.Label(
        frame_main, text='Нет связи с сервером.',
        bg=settings.ROOT_BG, fg=settings.ROOT_FG, font=settings.BIG_FONT
    )
    lb2 = tk.Label(
        frame_main, text=error_info,
        bg=settings.ROOT_BG, fg=settings.ROOT_FG, font=settings.SMALL_FONT
    )
    lb1.pack()
    lb2.pack()
    frame_main.pack(pady=100)
    _locals = locals()
    root.after(5000, lambda: reconnection(interface, _locals))
