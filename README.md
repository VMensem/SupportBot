# SupportBot

Discord-бот для Support-верификации с guild slash-командами.

## Локальный запуск

1. Установи Python 3.11+.
2. Установи зависимости:

```powershell
python -m pip install -r requirements.txt
```

3. Для локального запуска можно заполнить `config.json`.
4. Запусти:

```powershell
python bot.py
```

## Render

Создавай **Background Worker**.

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
python bot.py
```

Environment Variable:

- `CONFIG_JSON` - весь JSON-конфиг бота одной переменной.
- `DATABASE_URL` - ссылка на PostgreSQL базу Render.

Пример `CONFIG_JSON`:

```json
{
  "token": "TOKEN_HERE",
  "guild_id": 1304590614163230741,
  "roles": {
    "unverify": 1521958991058567209,
    "female": 1521958744789880913,
    "male": 1521958748405633074,
    "no_access": 1521958738573922436
  },
  "passing_voice_channel_ids": [
    1304590614641508477
  ],
  "verifier_role_ids": [
    1521958636195151934
  ],
  "review_log_channel_id": 1521969810974441552,
  "review_image_url": "",
  "owner_ids": [],
  "staff_guild_id": 1304590614163230741,
  "verification_log_channel_id": 1521969810974441552,
  "daily_report_channel_id": 1521986974209282179
}
```

Важно: статистика и отзывы больше не пишутся в JSON. На Render они хранятся в PostgreSQL через `DATABASE_URL`. Если `DATABASE_URL` не указан, бот локально создаст SQLite-файл `supportbot.db`.

Для Render:

1. Создай PostgreSQL в Render.
2. Скопируй Internal Database URL.
3. Вставь его в Environment Variable `DATABASE_URL`.
4. В `CONFIG_JSON` вставь весь конфиг вместе с токеном.

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
