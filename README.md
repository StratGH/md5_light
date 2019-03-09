# md5_light
Веб-сервис, позволяющий посчитать MD5-хеш от файла, расположенного в сети Интернет.

### Подготовка
Для запуска сервиса нужен python 3.6+.

Необходимо установить environs:

```
pip3 install environs
```

Для отправки сообщений на почту, необходимо в файле .env указать email и пароль для подключения к SMTP серверу.

Для сохранения результатов используется sqlite.

### Запуск

```
python3 server.py
```

### Примеры работы

POST:

```
curl -X POST -d "email=user@example.com&url=https://speed.hetzner.de/100MB.bin" http://localhost:8000/submit
{'id': '7719a3e7-a980-48ca-a1e9-4efead2bdb44'}
```

GET, когда расчёт MD5-хеш суммы не закончен:

```
curl -X GET http://localhost:8000/check?id=7719a3e7-a980-48ca-a1e9-4efead2bdb44
{'status': 'running'}
```

GET, когда MD5-хеш ещё не рассчитан:

```
curl -X GET http://localhost:8000/check?id=7719a3e7-a980-48ca-a1e9-4efead2bdb44
{'status': 'running'}
```

GET, когда MD5-хеш рассчитан:

```
curl -X GET http://localhost:8000/check?id=7719a3e7-a980-48ca-a1e9-4efead2bdb44
{'status': 'done', 'md5': '2f282b84e7e608d5852449ed940bfc51', 'url': 'https://speed.hetzner.de/100MB.bin'}
```
