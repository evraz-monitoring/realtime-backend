# Realtime-backend
## Описание
Посылает по вебсокету новые метрики с сенсоров, предупреждения(warnings)
и критические уведомления(alarms).
## Запуск
```shell
poetry install
uvicorn main:app --reload
```
## Сборка docker-образа
```shell
docker build --target production --tag realtime-backend:latest .
```