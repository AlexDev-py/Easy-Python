"""

Правила написания файла с заданиями.
1. Назвать файл нужно названием темы(<Тема>.txt)
2. на первой строке нужно указать кол-во задач в данной теме(задач::<число>)
3. на второй строке нужно указать лимит времени(время::<число секунд>)
4. Далее следуют задачи в таком шаблоне:
    ::(
    <Вопрос задачи>
    ::input::<Входные данные>:: (если есть. см. пункт 4.2)
    ::answer::<Ответ на задание>:: (если необходимо. см. пункт 4.4)
    <код задачи> (см. пункт 4.3)
    )::

    4.1. Вопрос задачи.
        Вопрос задачи — тот вопрос,
         на который должен будет ответить пользователь.
        Вопрос может состоять из нескольких строк
         и не должен содержать в себе сочетания символов:
          "::", ">>> ", "... "
    4.2. Входные данные.
        Входные данные — то что нужно ввести с клавиатуры.(команда input())
        Входные данные должны быть оформлены по шаблону:
            ::input::<значение><значение> и тд.::
        Данную строку можно пропустить если в коде задачи нет команд input().
        Пример задачи с входными данными:
            ::(
            Что выведет на экран программа, если сначала ввести 6, а потом 2?
            ::input::<6><2>::
            >>> a = input()
            >>> b = int(input())
            >>> print(a * b)
            )::
    4.3. Код задачи.
        Код задачи — программа на Python.
        Код должен оформляться по нескольким правилам:
            4.3.1. Каждая строка нулевого уровня
                должна начинаться с символов ">>> "
            4.3.2. Каждая строка не нулевого уровня
                должна начинаться с символов "... "
            4.3.3. В каждой задаче должна быть команда print(),
                которая будет выводить правильный ответ
                (если не указан ::answer::)
            4.4.4. Сколько раз в коде нужно использовать ввод с клавиатуры,
                Столько и должно быть значений в параметре ::input::
        Примеры:
            ::(
            Что ответит интерпретатор Python при вводе строки?
            >>> print("It" * 5)
            )::

            ::(
            Что будет выведено?
            >>> a = 6
            >>> if a > 5:
            ...     print('1')
            >>> elif a == 5:
            ...     print('2')
            >>> else:
            ...     if True:
            ...         print('3')
            )::
    4.4. Ответ на задание.
        Данный параметр нужно указывать в случае,
         если ответом к задаче не является значение,
         которое выводит команда print().
        Примеры:
            ::(
            Какое число нужно ввести, что бы программа вывела 14?
            ::answer::<2>::
            >>> a = int(input())
            >>> print(10 + a * 2)
            )::

            ::(
            Что необходимо написать вместо "<**>",
            чтобы переменная `a` имела значение введённое с клавиатуры?
            ::answer::<input()>::
            >>> a = <**>
            )::
        Примечание:
            Если указан параметр ::answer::
             то в коде не обязательна команда print()
             и не обязателен параметр ::input::

"""

from __future__ import annotations
from typing import List
import re
import os
from dataclasses import dataclass

PATH = 'sources/quests/' if __name__ != '__main__' else ''


class Quests:
    """
    Хранилище всех тем. Инструменты сортировки.
    """

    quests = []


@dataclass
class Task:
    """
    Модель задания
    """

    task: str

    question: str = ...
    code: str = ...
    answer: str = ''

    def __post_init__(self):
        self.question = re.split(
            r'>>> ', self.task, flags=re.DOTALL
        )[0].strip()

        if answer_data := re.search(
                r'::answer::<(?P<answer>.+)>::',
                self.question, flags=re.DOTALL
        ):
            self.task = re.sub(
                r'\n::answer::<.+>::', '', self.task, flags=re.DOTALL
            )
            self.question = self.question[:answer_data.start()].strip()
            self.answer = answer_data.group('answer')

        if input_data := re.search(
                r'::input::(?P<input_data>.+)::',
                self.question, flags=re.DOTALL
        ):
            self.task = re.sub(
                r'\n::input::.+::', '', self.task, flags=re.DOTALL
            )
            self.question = self.question[:input_data.start()].strip()
            input_data = input_data.group('input_data')
            input_data = [
                d.group('d')
                for d in re.finditer(r'<(?P<d>[^>])>', input_data)
            ]

        if self.answer == '':
            self.code = re.search(
                r'(?P<c>>>> .+)', self.task, flags=re.DOTALL
            ).group('c')
            self.code = self.code\
                .replace('>>> ', '')\
                .replace('... ', '')\
                .replace('print', 'self._print')

            if input_data:
                code: list = self.code.split('input()')
                self.code = ''
                for i, obj in enumerate(code):
                    self.code += obj
                    if i < len(input_data):
                        self.code += input_data[i]

            exec(self.code)

    def _print(self, *args, sep=' ', end='\n'):
        text = sep.join(map(str, args))
        if self.answer == '':
            self.answer += text
        else:
            self.answer += end + text


@dataclass
class Quest:
    """
    Модель темы.
    """

    """ Название темы """
    name: str
    """ Кол-во задач по теме """
    tasks_count: int
    """ Лимит по времени """
    time_limit: int
    """ Список заданий """
    tasks: List[Task]

    def __post_init__(self):
        Quests.quests.append(self)


for root, dirs, files in os.walk(PATH):
    for file_name in files:
        if file_name.endswith('.txt'):
            with open(f'{root}/{file_name}', encoding='utf-8') as file:
                quest_data = file.read()
                _data = re.search(
                    r'задач::(?P<tasks_count>\d+)\n'
                    r'время::(?P<time_limit>\d+)$',
                    quest_data, flags=re.MULTILINE
                )
                tasks_count = _data.group('tasks_count')
                time_limit = _data.group('time_limit')
                tasks = re.finditer(
                    r'::\((?P<task>.+?)\)::', quest_data,
                    flags=re.DOTALL
                )

                Quest(
                    name=file_name.split('.txt')[0],
                    tasks_count=int(tasks_count),
                    time_limit=int(time_limit),
                    tasks=[Task(t.group('task').strip()) for t in tasks]
                )
