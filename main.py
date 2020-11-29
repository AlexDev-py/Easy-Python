import os
import subprocess
from typing import Any

import requests
from attrdict import AttrMap

HOST = 'http://127.0.0.1:5000/'
# HOST = 'http://easypython.pythonanywhere.com/'
SERVER_ALLOWED = True

if os.path.exists('.auth'):
    with open('.auth') as file:
        LOGIN, PASSWORD = file.read().split('::')
else:
    LOGIN, PASSWORD = None, None


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


def reconnection(root: Any, _locals: dict):
    """
    Повторная попытка подключиться к серверу.
    """

    _locals['lb2'].config(text='Подключение...')
    _locals['lb2'].update()

    try:
        _main(root, _locals)
    except (requests.ConnectionError, requests.HTTPError):
        _locals['lb2'].config(text='')
        root.root.after(5000, lambda: reconnection(root, _locals))


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
        root.LOGIN = login
        root.profile = AttrMap(request(
            f'profile/{login.split("#")[1]}'
        ))
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
        root.LOGIN = response['login']
        root.profile = AttrMap(request(
            f'profile/{response["login"].split("#")[1]}'
        ))
        root.home_view(_locals)


def _main(root: Any, _locals: dict = None):
    if LOGIN and PASSWORD:
        if request('auth', login=LOGIN, password=PASSWORD)['response']:
            root.profile = AttrMap(request(
                f'profile/{LOGIN.split("#")[1]}'
            ))
            root.home_view(_locals)
        else:
            os.remove('.auth')
            root.log_in_view(_locals)
    else:
        request('test')
        root.log_in_view(_locals)


if __name__ == '__main__':
    import interface
    from sources.quests.quests import Quests

    interface.Quests = Quests
    interface.interface = interface

    if not LOGIN:
        interface.Alert.alert_frame.pack(side='top', fill='x')
        interface.Alert.show('Подготовка...', show_time=1)

    try:
        _main(interface)
    except (requests.ConnectionError, requests.HTTPError):
        interface.connection_error_view()
        SERVER_ALLOWED = False

    interface.root.mainloop()
