# Предыстория
## Проектная работа 4 спринта

**Важное сообщение для тимлида:** для ускорения проверки проекта укажите ссылку на приватный репозиторий с командной работой в файле readme и отправьте свежее приглашение на аккаунт [BlueDeep](https://github.com/BigDeepBlue).

В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить в первом спринте второго модуля.  Обратите внимание на задачи **00_create_repo** и **01_create_basis**. Они расцениваются как блокирующие для командной работы, поэтому их необходимо выполнить как можно раньше.

Мы оценили задачи в стори поинтах, значения которых брались из [последовательности Фибоначчи](https://ru.wikipedia.org/wiki/Числа_Фибоначчи) (1,2,3,5,8,…).

Вы можете разбить имеющиеся задачи на более маленькие, например, распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа стори поинтов в спринте.**

## Перед запуском
1. Потребуется репозиторий, созданный в S3 (пример запуска описан в README.md проекта).
```https://github.com/IggiShal/new_admin_panel_sprint_3.git```

2. Настроить виртуальную среду, например:
```python.exe -m venv .venv```

3. Перейти в виртуальную среду, например:
``` & ./fastapi-solution/.venv/Scripts/Activate.ps1```

## Запуск проекта
1. Перейти в директорию ./fastapi-solutions

2. Создать файл .env по примеру из env.sample (можно просто переименовать)

3. Выполнить в оболочке команду:
```docker compose up``` . Проект развернется (дождаться логов работающего ETL)

## После запуска
1. При поднятии проекта S3 автоматически загружается данные из sqlite в postgres


3. Каждые 10 сек данные из postgres переливаются в elastic. Корректность переливки данных можно проверить тестами Postman из S3, файл с тестами лежит в fastapi-solution/etl/tests/

4. Для удобства оставил открытыми порты на postgres (5432), elastic (9200)

5. Сервис FastAPI доступен на порту 8000

## Проверить готовность стенда
1. В postgres (localhost:5432):
     * ```sql 
       select * from content.film_work where id = '3d825f60-9fff-4dfe-b294-1a45fa1e115d'```

2. В браузере:
     * http://127.0.0.1:9200/movies/_doc/3d825f60-9fff-4dfe-b294-1a45fa1e115d

3. В браузере:
     * http://127.0.0.1:8008/api/v1/films/3d825f60-9fff-4dfe-b294-1a45fa1e115d

4. В Postman 
     * ```fastapi-solution\tests\Async_API.postman_collection.json```

## Запуск тестов
1. Запустить докер в тестовом режиме (нужен в первый раз, далее можно запускать при наличии запущенного):
```docker-compose -f docker-compose.test.yaml up --build```

2. Выполнить тест:
```
pytest fastapi-solution/tests --docker-compose=docker-compose.test.yaml --docker-compose-no-build --use-running-containers -v
```

## Запуск в VSCode в debug режиме
1. Настройка запуска в файле .vscode\launch.json
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "port": 5678,
            "host": "localhost",
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/fastapi-solution",
                    "remoteRoot": "/opt/app"
                }
            ],
        },
    ]
}
```

2. Запустить докер в дебаг режиме:
```docker-compose -f docker-compose.debug.yaml up --build```

3. Перейти в меню дебага Ctrl-Shift-F5.
4. Выбрать ранее добавленный "Python: Remote Attach" и запустить.
5. Для проверки можно поставить брейкпоинт, например, в genres entrypoint и выполнить запрос на http://127.0.0.1:8000/api/openapi.