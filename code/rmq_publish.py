#подключаем необходимые библиотеки

import pika                             		# библиотека для работы с AMQP протоколом
import rmq_connection_parameters as rmq_params 	# конфигурационный файл с параметрами конекта к кроликам
from datetime import datetime           		# библиотека для вывода времени в консоль
import sys
import argparse                         		# парсер аргументов командной строки
import traceback                        		# модуль для вывода трейса ошибки

version = "0.2"

### 0.1 - Первый билд
### 0.2 - Добавлены обработчикм исключений

def createParser ():
    # Создаем класс парсера
    parser = argparse.ArgumentParser(prog = 'RMQ_PUBLISH_UTILS',
                                     description = '''Утилита для публикации сообщений в RabbitMQ по протоколу AMQP''',
                                     epilog = '''(c) Dmitry.V.Gusakov 2018.
                                     Автор программы, как всегда, не несет никакой ответственности ни за что.''',
                                     add_help = False
                                     )
    # Создаем группу параметров для родительского парсера,
    # ведь у него тоже должен быть параметр --help / -h
    parent_group = parser.add_argument_group (title='Параметры')
    parent_group.add_argument ('--help', '-h', action='help', help='Справка')
    parent_group.add_argument ('--version',
                               action='version',
                               help = 'Вывести номер версии',
                               version='%(prog)s {}'.format (version))

    # Создаем группу подпарсеров
    subparsers = parser.add_subparsers (dest = 'command',
                                        title = 'Возможные команды',
                                        description = 'Команды, которые должны быть в качестве первого параметра %(prog)s')

    # Создаем парсер для команды from_console
    from_console_parser = subparsers.add_parser ('from_console',
                                                 #add_help = False,
                                                 help = 'Режим публикации сообщения введенного через консоль',
                                                 description = '''Запуск в режиме публикации сообщения введенного через консоль''')
    # Создаем новую группу параметров
    from_console_group = from_console_parser.add_argument_group (title='Параметры')

    from_console_group.add_argument ('-rmq', '--rabbit_address', required=True,
                                     help = 'Hostname или IP кролика',
                                     metavar = 'Rabbit_address')
    from_console_group.add_argument ('-e', '--exch', required=True,
                                     help = 'Имя exchange',
                                     metavar = 'Exchange')
    from_console_group.add_argument ('-rk', '--r_key', required=True,
                                     help = 'Routing_key сообщения',
                                     metavar = 'Routing_key')
    from_console_group.add_argument ('-msg', '--message', required=True,
                                     help = 'Тело сообщения')
    from_console_group.add_argument ('-he', '--header',
                                     help = 'Заголовок сообщения')

    # Создаем парсер для команды from_file
    from_file_parser = subparsers.add_parser ('from_file',
                                              #add_help = False,
                                              help = 'Режим публикации сообщения из файла',
                                              description = '''Запуск в режиме публикации сообщения из файла''')
    # Создаем новую группу параметров
    from_file_group = from_file_parser.add_argument_group (title='Параметры')

    from_file_group.add_argument ('-rmq', '--rabbit_address', required=True,
                                  help = 'Hostname или IP кролика',
                                  metavar = 'Rabbit_address')
    from_file_group.add_argument ('-e', '--exch', required=True,
                                  help = 'Имя exchange',
                                  metavar = 'Exchange')
    from_file_group.add_argument ('-rk', '--r_key', required=True,
                                  help = 'Routing_key сообщения',
                                  metavar = 'Routing_key')
    from_file_group.add_argument ('-mf', '--message_file', required=True, type=argparse.FileType(),
                                  help = 'Имя файла с телом сообщения')
    from_file_group.add_argument ('-he', '--header',
                                  help = 'Заголовок сообщения')

    return parser

def time_now():
    return str(datetime.strftime(datetime.now(), "%H:%M:%S"))

def rmq_connect (rabbit_address):
    # устанавливаем соединение с сервером RabbitMQ
    parameters = pika.URLParameters(rmq_params.rabbit_connection_str(rabbit_address))
    print("[" + time_now() + "]", "- Работаем на кролике:", rabbit_address)
    connection = pika.BlockingConnection(parameters)
    print("[" + time_now() + "]", "- Подключение успешно")
    return connection

def rmq_disconnect (connection):
    connection.close()

def from_console (params,rmq_channel):
    try:
        rmq_channel.basic_publish(exchange = params.exch, routing_key = params.r_key, body = params.message)
        print("[" + time_now() + "]", "- Сообщение: \n", params.message, "\nс routing_key =", params.r_key, "\nуспешно опубликовано в exchange - ", params.exch)
    except Exception:
        print("[" + time_now() + "]"," - Ошибка:\n", traceback.format_exc())
        print("[" + time_now() + "]", "- Ошибка публикации сообщения!")

def from_file (params,rmq_channel):
    try:
        text = params.message_file.read()
        rmq_channel.basic_publish(exchange = params.exch, routing_key = params.r_key, body = text)
        print("[" + time_now() + "]", "- Сообщение: \n", text, "\nс routing_key =", params.r_key, "\nуспешно опубликовано в exchange - ", params.exch)
    except Exception:
        print("[" + time_now() + "]"," - Ошибка:\n", traceback.format_exc())
        print("[" + time_now() + "]", "- Ошибка публикации сообщения!")


parser = createParser()
params = parser.parse_args(sys.argv[1:])

if params.command not in ["from_console","from_file"]:
    parser.print_help()
    exit()


rmq_connection = rmq_connect(params.rabbit_address)
rmq_channel = rmq_connection.channel()

if params.command == "from_console":
    from_console(params,rmq_channel)
elif params.command == "from_file":
    from_file(params,rmq_channel)
else:
    print("Выбранная команда ничего не делает... Используйте -h для вызова справки")

rmq_disconnect(rmq_connection)