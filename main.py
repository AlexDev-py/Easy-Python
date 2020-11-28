import os
import subprocess
from typing import Any

import requests

# HOST = 'http://127.0.0.1:5000/'
HOST = 'http://easypython.pythonanywhere.com/'
SERVER_ALLOWED = True


def request(path: str, **kwargs) -> dict:
    """
    Запрос на сервер.
    :param path: Конец url.
    :param kwargs: Аргументы, передаваемые в запрос.
    """

    if not SERVER_ALLOWED:
        return dict(response=0)

    return requests.post('{HOST}{path}?{args}'.format(
        HOST=HOST, path=path,
        args='&'.join(
            [f'{k}={v.replace("#", "<::>")}' for k, v in kwargs.items()]
        )
    )).json()


def log_in(root: Any, _locals: dict, login: str, password: str):
    """
    Авторизация пользователя
    """

    if login == '':
        _locals['entry_login'].focus()
        return root.Alert.show('Введите логин')
    elif password == '':
        _locals['entry_password'].focus()
        return root.Alert.show('Введите пароль')

    if request('auth', login=login, password=password)['response']:
        if os.path.exists('.auth'):
            os.remove('.auth')
        with open('.auth', 'w') as data:
            data.write(f'{login}::{password}')
        subprocess.check_call(['attrib', '+H', '.auth'])
        root.home_view(_locals)
    else:
        root.Alert.show('Неправильный логин или пароль')


def sign_in(
        root: Any, _locals: dict,
        login: str, password: str, password2: str
):
    """
    Регистрация пользователя
    """

    if login == '':
        _locals['entry_login'].focus()
        return root.Alert.show('Введите логин')
    elif password == '':
        _locals['entry_password'].focus()
        return root.Alert.show('Введите пароль')
    elif password2 == '':
        _locals['entry_password2'].focus()
        return root.Alert.show('Повторите пароль')
    elif password != password2:
        return root.Alert.show('Пароли не совпадают')

    if (
            response := request('sing_in', login=login, password=password)
    )['response']:
        if os.path.exists('.auth'):
            os.remove('.auth')
        with open('.auth', 'w') as data:
            data.write(f'{response["login"]}::{password}')
        subprocess.check_call(['attrib', '+H', '.auth'])
        root.home_view(_locals)


if __name__ == '__main__':
    import interface

    interface.Alert.alert_frame.pack(side='top', fill='x')
    interface.Alert.show('Подготовка...', show_time=1)

    try:
        request('test')
    except (requests.ConnectionError, requests.HTTPError):
        interface.Alert.show('Нет связи с сервером', can_hide=False)
        SERVER_ALLOWED = False

    interface.interface = interface
    interface.log_in_view()
    interface.root.mainloop()
