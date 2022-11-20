# Магазин в Telegram (бот)

### Пример работы бота в Telegram:
![](https://dvmn.org/filer/canonical/1569215892/326/)

## Установка, настройки и запуск:
* Скачайте код.
* Установите зависимости:
```
pip install -r requirements.txt
```
* Запишите переменные окружения в файле .env в формате КЛЮЧ=ЗНАЧЕНИЕ:

`MOLTIN_CLIENT_ID` - Client id на [Moltin](https://euwest.cm.elasticpath.com/).

`MOLTIN_CLIENT_SECRET` - Client server на [Moltin](https://euwest.cm.elasticpath.com/).

`TG_TOKEN` - Телеграм токен. Получить у [BotFather](https://telegram.me/BotFather).

`DATABASE_HOST` - Адрес базы данных redis.

`DATABASE_PORT` - Порт базы данных redis.

`DATABASE_PASSWORD` - Пароль базы данных redis.

`TG_CHAT_ID` - ID чата в телеграм, в который будут приходить логи.

* Запустите бота:
```
python tg_bot.py
```
