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
root.title('Easy-Python: Учить Python легко!')


def open_img(path: str, size: tuple = (80, 50)) -> ImageTk.PhotoImage:
    """ Открытие изображения """

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

    root.geometry('350x400')
    root.minsize(350, 400)
    root.title('Авторизация')
    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=10)

    frame_user_name = tk.Frame(frame_main, bg=settings.ROOT_BG)
    frame_lb_user_name = tk.Frame(frame_user_name, bg=settings.ROOT_BG)

    lb_user_name1 = tk.Label(
        frame_lb_user_name, text='Логин', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )
    lb_user_name2 = tk.Label(
        frame_lb_user_name, text='(Имя пользователя)', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.SMALL_FONT
    )

    entry_user_name = tk.Entry(
        frame_user_name, bg=settings.ROOT_FG, fg=settings.ROOT_BG,
        font=settings.FONT, relief=tk.FLAT, width=27
    )

    lb_user_name1.grid(row=0, column=0)
    lb_user_name2.grid(row=0, column=1, sticky=tk.SE)
    frame_lb_user_name.grid(row=0, column=0)
    entry_user_name.grid(row=1, column=0, columnspan=100, sticky=tk.W)
    frame_user_name.pack()

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

    entry_user_name.focus()
    _locals = locals()

    btn_sign_in.bind('<Button-1>', lambda event: sign_in_view(_locals))
    root.bind_all('<Return>')


@view
def sign_in_view():
    """
    Страница регистрации.
    """

    root.geometry('350x400')
    root.minsize(350, 400)
    root.title('Регистрация')

    frame_main = tk.Frame(bg=settings.ROOT_BG, bd=10)

    frame_user_name = tk.Frame(frame_main, bg=settings.ROOT_BG)

    lb_user_name1 = tk.Label(
        frame_user_name, text='Имя пользователя', fg=settings.ROOT_FG,
        bg=settings.ROOT_BG, font=settings.FONT
    )

    entry_user_name = tk.Entry(
        frame_user_name, bg=settings.ROOT_FG, fg=settings.ROOT_BG,
        font=settings.FONT, relief=tk.FLAT, width=27
    )

    lb_user_name1.grid(row=0, column=0)
    entry_user_name.grid(row=1, column=0, columnspan=100, sticky=tk.W)
    frame_user_name.pack()

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

    entry_user_name.focus()
    _locals = locals()

    btn_log_in.bind('<Button-1>', lambda event: log_in_view(_locals))
    root.bind_all('<Return>')


if __name__ == '__main__':
    sign_in_view()
    root.mainloop()
