# Телеграм бот с интеграцией [PepeMossRobot](https://t.me/PepeMossRobot)

## Репозиторий [обучения моделей](https://git.pepemoss.com/universitat/ml/sam_train.git)

## Манифест

### Пользовательское желание - предсказывать бинарную маску льдов на изображении

## Базовые настройки для разработки

0. Интерпретатор ```>=3.10,<3.13```
1. Black - ``` $FilePath$ -l 120 --target-version py310 -S ```
2. ``` .env_example``` - содержит базовые настройки экземпляра `Backend`

## Начиная работу

0. Разверните проект используя poetry
1. Линковка вебхука - запросом в строке браузера ```https://api.telegram.org/bot<TELEGRAM_API_TOKEN>/setWebHook?url=https://example.com/dvc_example_robot/bot```
2. Запуск приложения через uvicorn, сделав его доступным внутри локальной сети - ``` uvicorn app.main:app --reload --host 0.0.0.0 ```

## GQL запрос для предсказания

```graphql
mutation($file: Upload!){
  genImage(file: $file)
}
```

## Важное

- Контейнер сделан на для запуска на `gpu`
- Скачать базовую модель `wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth`
- Модели генерируются [sam_train](https://git.pepemoss.com/universitat/ml/sam_train)

## Alina