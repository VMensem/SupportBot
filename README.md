# SupportBot

Discord-бот для Support-верификации с guild slash-командами.

## Локальный запуск

1. Установи Python 3.11+.
2. Установи зависимости:

```powershell
python -m pip install -r requirements.txt
```

3. Заполни `config.json`. Это стартовый конфиг для первой инициализации БД.
4. Токен можно вписать в `config.json` локально или передать переменной `DISCORD_TOKEN`.
5. Запусти:

```powershell
python bot.py
```

Локально, если `DATABASE_URL` не указан, бот создаст SQLite-файл `supportbot.db`.

## Render

Создавай сервис через `render.yaml` как Blueprint. Он поднимет:

- Background Worker `supportbot`
- PostgreSQL `supportbot-db`
- `DATABASE_URL` автоматически из базы

Руками в Render нужно добавить только:

- `DISCORD_TOKEN` - токен Discord-бота

`config.json` из репозитория нужен только для первого заполнения таблицы `bot_config`. После этого все настройки живут в БД, а `/sadmin` меняет именно БД. При рестарте Render настройки не слетят.

Если базу создаёшь руками, тогда добавь в Environment ещё:

- `DATABASE_URL` - Internal Database URL PostgreSQL

## Что хранится в БД

- конфиг бота из `/sadmin`
- роли и каналы
- owner IDs
- статистика войса
- активные войс-сессии
- статистика саппортов
- отзывы
- отметки дневных отчётов

## Команды

- `/verify user:<id/ник/упоминание>` - открывает панель верификации.
- `/status` - показывает общую статистику проходных.
- `/stats` - показывает личную статистику саппорта.
- `/sadmin` - скрытая настройка конфига для владельца.

## Интенты и права

В Discord Developer Portal включи `SERVER MEMBERS INTENT`.

Боту нужны права:

- Manage Roles
- Mute Members
- Move Members
- Send Messages
- Embed Links
- Use Slash Commands

## Приглашение бота

```text
https://discord.com/oauth2/authorize?client_id=1521950034445209793&permissions=289491968&integration_type=0&scope=bot+applications.commands
```
