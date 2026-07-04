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
  "stats_file": "voice_stats.json",
  "review_log_channel_id": 1521969810974441552,
  "review_image_url": "",
  "owner_ids": [],
  "staff_guild_id": 1304590614163230741,
  "verification_log_channel_id": 1521969810974441552,
  "daily_report_channel_id": 1521986974209282179
}
```

Важно: на Render бесплатный диск может сбрасываться при перезапуске. Текущая статистика хранится в `voice_stats.json`, поэтому для полной надёжности потом лучше перенести статистику в базу данных.

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
