from __future__ import annotations

import json
import tkinter as tk
from functools import wraps

from PIL import ImageTk, Image
from attrdict import AttrMap

from main import *

with open('settings.json') as settings:
    settings = AttrMap(json.load(settings))

root = tk.Tk()
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


def open_img(path: str, size: tuple = (80, 50)) -> ImageTk.PhotoImage:
    """
    Открытие изображения
    """

    img = Image.open(f'{path}')
    img.thumbnail(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)


# Подгрузка всех изображений
try:
    if not settings.USE_PICTURES:
        raise RuntimeError

    dp = 'sources/images/'
    IMG_LOG_IN = open_img(dp + 'btn_log_in.png', size=(150, 70))
    IMG_SIGN_IN = open_img(dp + 'btn_sign_in.png', size=(150, 70))

except (RuntimeError, FileNotFoundError):
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

    root.geometry('350x420')
    root.title('Авторизация')
    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=5)

    frame_login = tk.Frame(frame_main, bg=settings.ROOT_BG)

    lb_login = tk.Label(
        frame_login, text='Логин', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_login = tk.Entry(
        frame_login, bg=settings.ROOT_FG, fg=settings.ROOT_BG,
        font=settings.FONT, relief=tk.FLAT, width=27
    )

    lb_login.grid(row=0, column=0)
    entry_login.grid(row=1, column=0, columnspan=100, sticky=tk.W)
    frame_login.pack()

    frame_password = tk.Frame(frame_main, bg=settings.ROOT_BG)

    lb_password = tk.Label(
        frame_password, text='Пароль', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_password = tk.Entry(
        frame_password, bg=settings.ROOT_FG, fg=settings.ROOT_BG,
        font=settings.FONT, relief=tk.FLAT, show='*', width=27
    )

    lb_password.grid(row=0, column=0, sticky=tk.W)
    entry_password.grid(row=1, column=0, columnspan=100, sticky=tk.W)
    frame_password.pack(pady=20)

    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)

    if not settings.USE_PICTURES:
        btn_log_in = tk.Button(
            frame_btns, text='Войти',
            bg=settings.CONSP_BG, activebackground='#f3a505',
            fg=settings.CONSP_FG, padx=15, font=settings.FONT
        )
    else:
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

    root.geometry('350x420')
    root.title('Регистрация')

    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=5)

    frame_login = tk.Frame(frame_main, bg=settings.ROOT_BG)

    lb_login = tk.Label(
        frame_login, text='Имя пользователя', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_login = tk.Entry(
        frame_login, bg=settings.ROOT_FG, fg=settings.ROOT_BG,
        font=settings.FONT, relief=tk.FLAT, width=27
    )

    lb_login.grid(row=0, column=0)
    entry_login.grid(row=1, column=0, columnspan=100, sticky=tk.W)
    frame_login.pack()

    frame_password = tk.Frame(frame_main, bg=settings.ROOT_BG)

    lb_password = tk.Label(
        frame_password, text='Пароль', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_password = tk.Entry(
        frame_password, bg=settings.ROOT_FG, fg=settings.ROOT_BG,
        font=settings.FONT, relief=tk.FLAT, show='*', width=27
    )

    lb_password2 = tk.Label(
        frame_password, text='Повторите пароль', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_password2 = tk.Entry(
        frame_password, bg=settings.ROOT_FG, fg=settings.ROOT_BG,
        font=settings.FONT, relief=tk.FLAT, show='*', width=27
    )

    lb_password.grid(row=0, column=0, sticky=tk.W)
    entry_password.grid(row=1, column=0, columnspan=100, sticky=tk.W)
    lb_password2.grid(row=2, column=0, sticky=tk.W)
    entry_password2.grid(row=3, column=0, columnspan=100, sticky=tk.W)
    frame_password.pack(pady=20)

    frame_btns = tk.Frame(frame_main, bg=settings.ROOT_BG)

    if not settings.USE_PICTURES:
        btn_sign_in = tk.Button(
            frame_btns, text='Создать профиль',
            bg=settings.CONSP_BG, activebackground='#f3a505',
            fg=settings.CONSP_FG, padx=15, font=settings.FONT
        )
    else:
        btn_sign_in = tk.Label(
            frame_btns, image=IMG_SIGN_IN, bg=settings.ROOT_BG
        )

    btn_log_in = tk.Label(
        frame_btns, text='Войти в существующий профиль',
        font=settings.SMALL_FONT, bg=settings.ROOT_BG, fg=settings.CONSP_BG
    )

    btn_log_in.pack(side=tk.BOTTOM)
    btn_sign_in.pack(side=tk.BOTTOM)
    frame_btns.pack(pady=15)

    frame_main.pack(fill=tk.BOTH, expand=tk.TRUE, pady=30)

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

    root.title('Easy-Python: Учить Python легко!')
    root.geometry('800x500')
    root.minsize(650, 400)
    root.resizable(True, True)

    print('Вы на главной, но тут ничего нет')
    lb = tk.Label(
        bg=settings.ROOT_BG, font=settings.BIG_FONT, fg=settings.ROOT_FG,
        text='Вы на главной, но тут ничего нет'
    )
    lb.pack(pady=50)


if __name__ == '__main__':
    home_view()
    root.mainloop()
