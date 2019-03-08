# md5_light
Веб-сервис, позволяющий посчитать MD5-хеш от файла, расположенного в сети Интернет.

### Подготовка
Для запуска сервиса нужен python 3.6+.

Необходимо установить environs:

```
pip install environs
```

Для отправки сообщений на почту, необходимо в файле .env указать email и пароль для подключения к SMTP серверу.

Для сохранения результатов используется sqlite.

### Запуск

```
python3 server.py
```
