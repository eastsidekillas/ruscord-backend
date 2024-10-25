# Ruscord - Discord Clone (BE)

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


