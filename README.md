## Запуск проекта
### Требования:
1. Потребуется репозиторий, созданный в S3 (пример запуска описан в README.md проекта): https://github.com/IggiShal/new_admin_panel_sprint_3.git

2. Настроить виртуальную среду, например:
```sh
python.exe -m venv .venv
```

3. Перейти в виртуальную среду, например:
```sh
& ./fastapi-solution/.venv/Scripts/Activate.ps1
```

### Запуск:
1. Перейти в директорию ./fastapi-solutions

2. Создать файл .env по примеру из env.sample (можно просто переименовать)

3. Выполнить в оболочке команду:
```docker compose up``` . Проект развернется (дождаться логов работающего ETL)

### Дополнительная информация:
1. При поднятии проекта S3 автоматически загружается данные из sqlite в postgres

3. Каждые 10 сек данные из postgres переливаются в elastic. Корректность переливки данных можно проверить тестами Postman из S3, файл с тестами лежит в fastapi-solution/etl/tests/

5. Сервис FastAPI доступен на порту 80

## Проверить готовность стенда
1. В Postman 
```sh
 fastapi-solution\tests\Async_API.postman_collection.json
 ```

## Запуск тестов
### Требования:
1. Для работы, возможно, потребуется установить Microsoft C++ Build  Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. Установить пакеты для тестирования:
```sh
pip install -r .\fastapi-solution\tests\functional\requirements.txt
```

### Тестирование:
1. Запустить докер в тестовом режиме (нужен в первый раз, далее можно запускать при наличии запущенного):
```sh
docker-compose -f docker-compose.test.yaml up --build
```

2. Выполнить тест:
```sh
pytest fastapi-solution/tests --docker-compose=docker-compose.test.yaml --docker-compose-no-build --use-running-containers -v
```

## Запуск в VSCode в debug режиме
### Требования:
1. Настройка запуска в файле .vscode\launch.json
```json
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
### Отладка проекта:
1. Запустить докер в отладочном режиме:
```sh
docker-compose -f docker-compose.debug.yaml up --build
```
2. Перейти в меню отладки (debug) ```Ctrl-Shift-F5```.
3. Выбрать ранее добавленный "Python: Remote Attach" и запустить.
4. Сервис FastAPI доступен на порту 8000

## Проверить готовность стенда
1. В postgres (localhost:5432):
```sql 
select * from content.film_work where id = '3d825f60-9fff-4dfe-b294-1a45fa1e115d'
```
2. В браузере (ElasticSearch):
http://127.0.0.1:9200/movies/_doc/3d825f60-9fff-4dfe-b294-1a45fa1e115d
3. В браузере (REST API):
http://127.0.0.1:8008/api/v1/films/3d825f60-9fff-4dfe-b294-1a45fa1e115d
4. В Postman:
```sh
 fastapi-solution\tests\Async_API.postman_collection.json
 ```
### Отладка тестов
1. В среде VsCode понадобится добавить конфиг*:
```json
{
    "python.testing.pytestArgs": [
        "--rootdir", "fastapi-solution/tests",
        "--docker-compose=docker-compose.test.yaml",
        "--docker-compose-no-build",
        "--use-running-containers",
        "-v",
    ],
    "python.analysis.extraPaths": [
        "fastapi-solution/src/",
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.formatting.blackArgs": [
        "--line-length",
        "79"
    ]
}
```
*- только python.testing относится к текущему пункту, осатльное прикопал для информации.