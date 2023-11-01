# Парсер документации python и PEP
## Описание
Парсер информации о Python с **https://docs.python.org/3/** и **https://peps.python.org/**
### Перед использованием
1. Клонировать репозиторий:
```
git clone https://github.com/QuiShimo/bs4_parser_pep.git
```

2. В корневой папке нужно создать виртуальное окружение и установить зависимости.
```
python -m venv venv
```
```
pip install -r requirements.txt
```
3. Сменить директорию на папку ./src/
```
cd src/
```

4. Запустить файл main.py выбрав необходимый парсер и аргументы(приведены ниже)
```
python main.py [вариант парсера] [аргументы]
```
### Варианты парсеров
- whats-new - парсер выводящий список изменений в Python.
```
python main.py whats-new [аргументы]
```
- latest_versions - парсер выводящий список версий Python и ссылки на их документацию.
```
python main.py latest-versions [аргументы]
```
- download - парсер скачивающий zip архив с документацией Python в pdf формате.
```
python main.py download [аргументы]
```
- pep - парсер выводящий список статусов документов PEP и количество документов в каждом статусе.
```
python main.py pep [аргументы]
```
### Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- h, --help - общая информация о командах.
```
python main.py -h
```
- -c, --clear-cache - очистка кеша перед выполнением парсинга.
```
python main.py [вариант парсера] -c
```
- -o {pretty,file}, --output {pretty,file} - дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/
```
python main.py [вариант парсера] -o file
```
### Автор
- [Mikhail Bondarenko](https://github.com/quishimo "GitHub аккаунт")