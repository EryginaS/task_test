import json
from urllib.request import urlopen
import os
import datetime
import time
from glob import glob


def pars_todos(id):
    """
    Функция парсинга json файла  c задачами для каждого пользователя
    :param id: id работника, по которому составляется отчет
    :return: список с завершенными задачами, список с текущими задачами
     для конкретного работника
    """
    try:
        with urlopen('https://json.medrating.org/todos') as response:
            source = response.read()
    except:
        print('Connection refused')

    done = []
    task = []
    for key in json.loads(source):
        if key['userId'] == id:
            if key['completed'] == False:
                task.append(key['title'])
            if key['completed'] == True:
                done.append(key['title'])

    return done, task


def main():
    """
    Функция получает данные о работниках с API и составляет по ним отчет, в случает, если отчет уже существует,
    файл переименовывается.
    :return: pass
    """
    try:
        with urlopen('https://json.medrating.org/users') as res:
            src = res.read()
    except:
        print('Connection refused')
        exit()

    for i in json.loads(src):
        # time.sleep(60)  # Защита от создания двух файлов с одинаковым именем.
        if os.path.exists(os.path.join('tasks', i['username']) + '.txt') == True:
            file = open(os.path.join('tasks', i['username']) + '.txt')
            first_line = file.readline()
            file.close()
            list_line = first_line.split(' ')
            # for windows
            # os.rename(os.path.join('tasks', i['username']) + '.txt',
            #           os.path.join('tasks', i['username']) + '_' + list_line[-2].replace('.', '-') + 'T'
            #           + list_line[-1][:5].replace(':', '-') + '.txt')
            # for ubuntu
            print(i['username'])
            print(list_line)
            print(list_line[-1])
            os.rename(os.path.join('tasks', i['username']) + '.txt',
                      os.path.join('tasks', i['username']) + '_' + list_line[-2].replace('.', '-') + 'T'
                      + list_line[-1][:5] + '.txt')
        with open(os.path.join('tasks', i['username']) + '.txt', 'tw', encoding='utf-8') as f:
            f.write(i['name'] + ' <' + i['email'] + '> ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M") + '\n')
            f.write(i['company']['name'] + '\n')
            f.write('\n' + 'Завершённые задачи:\n')
            try:
                done, task = pars_todos(i['id'])
            except:
                f.close()
                os.remove(os.path.join('tasks', i['username']) + '.txt') # Удаление файла, в случае разрыва соединения
                file_list = []
                for j in glob(os.path.join('tasks', i['username'])+"*.txt"):
                    file_list.append(j)
                # В случае разрыва соединения текщий отчет заменяется последним из всех существующих в случае, если
                # они есть
                if file_list:
                    # Создадим список из путей к файлам и дат их создания.
                    date_list = [[x, os.path.getctime(x)] for x in file_list]
                    # Отсортируем список по дате создания в обратном порядке
                    sort_date_list = sorted(date_list, key=lambda x: x[1], reverse=True)
                    print(sort_date_list)
                    #  only for ubuntu
                    os.rename(sort_date_list[0][0],
                               os.path.join('tasks', i['username']) + '.txt')
                continue
            if len(done) == 0:
                f.write('Выполненных задач нет.' + '\n')
            else:
                for i in done:
                    if len(i) > 50:
                        i = i[:51] + '...'
                    f.write(i + '\n')
            if len(task) == 0:
                f.write('Оставшихся задач нет.' + '\n')
            else:
                f.write('\n' + 'Оставшиеся задачи:\n')
                for i in task:
                    if len(i) > 50:
                        i = i[:51] + '...'
                    f.write(i + '\n')


if __name__ == '__main__':
    # Создается директория tasks
    try:
        os.mkdir('tasks', mode=0o777)
    except FileExistsError:
        print('Directory already exists.')
    main()
