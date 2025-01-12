# Ruscord - Discord Clone (BE)

## Установка Poetry Windows

Ставим этой командой poetry:
```shell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Делаем переменную в системе так:

```shell
C:\Users\ИМЯ ПОЛЬЗОВАТЕЛЯ ПК\AppData\Roaming\Python\Scripts
```

## Запуск стартовый  
```shell
poetry install
poetry run python -m manage createsuperuser
poetry run python -m manage runserver
```

## Запуск с вебсокетами 
```shell
poetry install
poetry run python -m manage createsuperuser
poetry run daphne -p 8000 ruscord.asgi:application
```


## Для работы вебсокетов потребуется Redis
### Ставим Docker Desktop и разворачиваем контейнер :)

https://docs.docker.com/desktop/install/windows-install/

```shell
   docker pull redis
```


