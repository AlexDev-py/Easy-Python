from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from functools import wraps

from PIL import ImageTk, Image

from main import *

if __name__ == '__main__':
    from sources.quests.quests import Quest

with open('settings.json') as settings:
    settings = AttrMap(json.load(settings))

root = tk.Tk()
Quests: "Quests" = ...
interface = ...
profile = ...
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
        """

        for lb in Alert.alert_frame.winfo_children():
            lb.destroy()

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
        del self
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


class ScrollableFrame(tk.Frame):
    """
    Прокручиваемый фрейм
    """

    def __init__(self, master):
        super().__init__(master)

        self._y = 0
        self._move_count = 0

        self.canvas = tk.Canvas(
            self, bg=settings.ROOT_BG, highlightthickness=0
        )
        self.canvas.bind_all('<MouseWheel>', self.wheel_scroll)

        self.scrollable_frame = tk.Frame(
            self.canvas, bg=settings.CONSP_BG, bd=10
        )
        self.scrollable_frame.bind(
            "<Configure>", lambda event:
            self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
        )
        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor=tk.NW
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

    def wheel_scroll(self, event):
        """
        Прокрутка колёсиком мыши
        """

        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)


class QuestWidget(tk.Frame):
    """
    Виджет темы.
    """

    def __init__(self, master: tk.Frame, quest: "Quest"):
        super().__init__(master, bg=settings.SECONDARY_BG, bd=20)
        self.quest = quest
        self.name = tk.Label(
            self, text=quest.name,
            bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
            font=settings.BIG_FONT
        )

        self.name.pack(side=tk.LEFT)
        self.pack(fill=tk.X, pady=10)


def open_img(path: str, size: tuple = (80, 50)) -> ImageTk.PhotoImage:
    """
    Открытие изображения
    """

    img = Image.open(f'{path}')
    img.thumbnail(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)


def rounded_rect(canvas, x, y, width, height, radius):
    """
    Рисует прямоугольник с закруглёнными краями
    """

    canvas.create_arc(
        x, y, x + 2 * radius, y + 2 * radius,
        start=90, extent=90, style="arc", outline=settings.CONSP_BG)
    canvas.create_arc(
        x + width - 2 * radius, y + height - 2 * radius, x + width, y + height,
        start=270, extent=90, style="arc", outline=settings.CONSP_BG)
    canvas.create_arc(
        x + width - 2 * radius, y, x + width, y + 2 * radius,
        start=0, extent=90, style="arc", outline=settings.CONSP_BG)
    canvas.create_arc(
        x, y + height - 2 * radius, x + 2 * radius, y + height,
        start=180, extent=90, style="arc", outline=settings.CONSP_BG)
    canvas.create_line(
        x + radius, y, x + width - radius, y, fill=settings.CONSP_BG
    )
    canvas.create_line(
        x + radius, y + height, x + width - radius, y + height,
        fill=settings.CONSP_BG
    )
    canvas.create_line(
        x, y + radius, x, y + height - radius, fill=settings.CONSP_BG
    )
    canvas.create_line(
        x + width, y + height - radius, x + width, y + radius,
        fill=settings.CONSP_BG
    )


# Подгрузка всех изображений
try:

    dp = 'sources/images/'
    IMG_LOG_IN = open_img(dp + 'btn_log_in.png', size=(160, 60))
    IMG_SIGN_IN = open_img(dp + 'btn_sign_in.png', size=(180, 70))

except FileNotFoundError:
    settings.USE_PICTURES = False


def view(func):
    """
    Декоратор для удобного перехода между страницами приложения.
    """

    @wraps(func)
    def _wrap(_locals: dict = None, *args, **kwargs):
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
    canvas_input.pack()

    frame_input = tk.Frame(canvas_input, bg=settings.ROOT_BG, bd=10)

    lb_login = tk.Label(
        frame_input, text='Логин', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_login = tk.Entry(
        frame_input, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG, font=settings.FONT,
        relief=tk.FLAT, insertbackground=settings.ROOT_FG, width=25
    )

    lb_password = tk.Label(
        frame_input, text='Пароль', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
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
    root.after(20, lambda: rounded_rect(
        canvas_input, 0, 0,
        canvas_input.winfo_width() - 1, canvas_input.winfo_height() - 1, 20
    ))

    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)

    btn_log_in = tk.Label(
        frame_btns, image=IMG_LOG_IN, bg=settings.ROOT_BG
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

    btn_sign_in.bind('<Button-1>', lambda event: sign_in_view(_locals))
    root.bind_all('<Return>', lambda event: log_in(
        interface, _locals, entry_login.get(), entry_password.get()
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
    canvas_input.pack()

    frame_input = tk.Frame(canvas_input, bg=settings.ROOT_BG, bd=10)

    lb_login = tk.Label(
        frame_input, text='Имя пользователя', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_login = tk.Entry(
        frame_input, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        highlightthickness=1, highlightcolor=settings.CONSP_BG,
        highlightbackground=settings.CONSP_BG, font=settings.FONT,
        relief=tk.FLAT, insertbackground=settings.ROOT_FG, width=22
    )

    lb_password = tk.Label(
        frame_input, text='Пароль', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
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
        bg=settings.ROOT_BG, font=settings.FONT
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
    root.after(20, lambda: rounded_rect(
        canvas_input, 0, 0,
        canvas_input.winfo_width() - 1, canvas_input.winfo_height() - 1, 20
    ))

    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)

    btn_sign_in = tk.Label(
        frame_btns, image=IMG_SIGN_IN, bg=settings.ROOT_BG
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

    btn_log_in.bind('<Button-1>', lambda event: log_in_view(_locals))
    root.bind_all('<Return>', lambda event: sign_in(
        interface, _locals, entry_login.get(),
        entry_password.get(), entry_password2.get()
    ))
    btn_sign_in.bind('<Button-1>', lambda event: sign_in(
        interface, _locals, entry_login.get(),
        entry_password.get(), entry_password2.get()
    ))


@view
def home_view():
    """
    Главная страница приложения.
    Страница выбора темы.
    """

    Alert.alert_frame.destroy()

    root.title('Easy-Python: Учить Python легко!')
    root.geometry('800x500')
    root.minsize(650, 400)
    root.resizable(True, True)

    frame_main = tk.Frame(bg=settings.ROOT_BG)

    frame_tools = tk.Frame(frame_main, bg=settings.SECONDARY_BG, bd=10)

    frame_profile = tk.Frame(frame_tools, bg=settings.SECONDARY_BG)
    frame_profile_lbs = tk.Frame(frame_profile, bg=settings.SECONDARY_BG)

    profile_icon = tk.Canvas(frame_profile, width=50, height=50, bg='#FFF')
    profile_name = tk.Label(
        frame_profile_lbs, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        font=settings.FONT, text=LOGIN
    )
    profile_score = tk.Label(
        frame_profile_lbs, bg=settings.SECONDARY_BG, fg=settings.ROOT_FG,
        font=settings.SMALL_FONT, text=f'Счёт: {profile.score}'
    )

    profile_icon.pack(side=tk.LEFT)
    profile_name.grid(row=0, column=0, sticky=tk.EW)
    profile_score.grid(row=1, column=0, sticky=tk.NW)
    frame_profile_lbs.pack(padx=10)
    frame_profile.pack(side=tk.TOP)

    frame_filters = tk.Frame(frame_tools, bg=settings.SECONDARY_BG)
    frame_filters.pack(fill=tk.Y)

    frame_tools.pack(side=tk.LEFT, fill=tk.Y)

    frame_content = tk.Frame(frame_main, bg=settings.ROOT_BG)
    Alert.alert_frame = tk.Frame(frame_content, bg=settings.ROOT_BG)
    Alert.alert_frame.pack(side='top', fill='x')
    Alert.show('Подготовка...', show_time=1)

    frame_quests = ScrollableFrame(frame_content)
    quests = [QuestWidget(
        frame_quests.scrollable_frame, q
    ) for q in Quests.quests]
    frame_quests.pack(fill=tk.BOTH, expand=tk.TRUE)

    frame_content.pack(fill=tk.BOTH, expand=tk.TRUE)

    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE)

    print(Quests.quests)


@view
def connection_error_view(error_info: str = ''):
    """
    Окно, сообщающее об ошибке подключения к серверу
    """

    root.geometry('560x420')
    root.title('Ошибка соединения')

    frame_main = tk.Frame(bg=settings.ROOT_BG)
    lb1 = tk.Label(
        frame_main, text=f'Нет связи с сервером.',
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
