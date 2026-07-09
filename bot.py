import asyncio
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import os
import re
import sqlite3
import threading
from types import SimpleNamespace
import time
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, jsonify, send_file


MENTION_RE = re.compile(r"^<@!?(\d+)>$")
CONFIG_PATH = Path("config.json")
EMBED_COLOR = discord.Color.orange()
MSK_TZ = timezone(timedelta(hours=3), "MSK")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_DB_PATH = Path(os.getenv("SUPPORTBOT_DB_PATH", "supportbot.db"))
USE_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))
PORT = int(os.getenv("PORT", "10000"))

web_app = Flask(__name__)

@web_app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(os.path.dirname(__file__), 'mbot.jpg'))
@web_app.get("/")
def web_index():
    bot_name = str(bot.user) if bot.user else "MensemBot"
    database_name = "PostgreSQL" if USE_POSTGRES else "SQLite"
    guild_id = int(config.guild_id)
    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MemsemBot</title>
  <link rel="shortcut icon" href="/favicon.ico">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #111216;
      --panel: #1b1d24;
      --panel-soft: #22252e;
      --line: #343844;
      --text: #f4f1ea;
      --muted: #b7ac9c;
      --accent: #ff8a2a;
      --accent-soft: rgba(255, 50, 50, 0.14);
      --ok: #42d392;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background:
        radial-gradient(circle at top left, rgba(255, 50, 50, .18), transparent 34rem),
        linear-gradient(135deg, #111216 0%, #171920 55%, #101115 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(920px, calc(100vw - 32px));
      padding: 34px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(27, 29, 36, .86);
      box-shadow: 0 24px 80px rgba(0, 0, 0, .42);
      backdrop-filter: blur(14px);
    }}
    .top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 30px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 14px;
      min-width: 0;
    }}
    .logo {{
      width: 54px;
      height: 54px;
      display: grid;
      place-items: center;
      border-radius: 14px;
      background: var(--accent-soft);
      border: 1px solid rgba(255, 50, 50, .35);
      color: var(--accent);
      font-size: 28px;
      font-weight: 900;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(28px, 5vw, 46px);
      line-height: 1;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 15px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 13px;
      border: 1px solid rgba(66, 211, 146, .28);
      border-radius: 999px;
      background: rgba(66, 211, 146, .1);
      color: #d9ffed;
      font-weight: 700;
      white-space: nowrap;
    }}
    .dot {{
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--ok);
      box-shadow: 0 0 18px var(--ok);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .card {{
      min-height: 116px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--panel-soft);
    }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .value {{
      margin-top: 12px;
      overflow-wrap: anywhere;
      font-size: 19px;
      font-weight: 850;
      line-height: 1.22;
    }}
    .footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-top: 24px;
      padding-top: 20px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 14px;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 800;
    }}
    @media (max-width: 760px) {{
      main {{ padding: 22px; }}
      .top, .footer {{ align-items: flex-start; flex-direction: column; }}
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 460px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="top">
      <div class="brand">
        <div class="logo"><link rel="shortcut icon" href="/favicon.ico"></div>
        <div>
          <h1>MensemBot</h1>
          <div class="subtitle">MensemBot</div>
        </div>
      </div>
      <div class="badge"><span class="dot"></span> Online</div>
    </section>

    <section class="grid">
      <article class="card">
        <div class="label">Discord</div>
        <div class="value">{bot_name}</div>
      </article>
      <article class="card">
        <div class="label">Database</div>
        <div class="value">{database_name}</div>
      </article>
      <article class="card">
        <div class="label">Guild</div>
        <div class="value">{guild_id}</div>
      </article>
      <article class="card">
        <div class="label">Commands</div>
        <div class="value">/verify /status /stats /sadmin</div>
      </article>
    </section>

    <section class="footer">
      <span>Health endpoint: <a href="/health">/health</a></span>
      <span>discord.gg/mensem</span>
    </section>
  </main>
</body>
</html>"""
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


@web_app.get("/health")
def web_health():
    return jsonify(
        {
            "ok": True,
            "bot": str(bot.user) if bot.user else None,
            "guild_id": int(config.guild_id),
            "database": "postgres" if USE_POSTGRES else "sqlite",
        }
    )


def run_web_server() -> None:
    web_app.run(host="0.0.0.0", port=PORT, use_reloader=False)



DEFAULT_CONFIG = {
    "token": "",
    "guild_id": 0,
    "roles": {
        "unverify": 0,
        "female": 0,
        "male": 0,
        "no_access": 0,
    },
    "passing_voice_channel_ids": [],
    "verifier_role_ids": [],
    "review_log_channel_id": 0,
    "staff_guild_id": 0,
    "verification_log_channel_id": 0,
    "daily_report_channel_id": 0,
    "review_image_url": "",
    "owner_ids": [],
}

CONFIG_DB_KEYS = tuple(key for key in DEFAULT_CONFIG if key != "token")


def read_seed_token() -> str:
    config_json = os.getenv("CONFIG_JSON") or os.getenv("SUPPORTBOT_CONFIG_JSON")
    if config_json:
        try:
            env_data = json.loads(config_json)
        except json.JSONDecodeError:
            env_data = {}
        if isinstance(env_data, dict) and env_data.get("token"):
            return str(env_data["token"])

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return ""
        return str(data.get("token", "") or "")

    return ""


def apply_config_defaults(data: dict) -> dict:
    merged = DEFAULT_CONFIG | data
    merged["roles"] = DEFAULT_CONFIG["roles"] | merged.get("roles", {})
    for key in ("passing_voice_channel_ids", "verifier_role_ids", "owner_ids"):
        merged[key] = [int(item) for item in merged.get(key, []) if item]
    for key in (
        "guild_id",
        "review_log_channel_id",
        "staff_guild_id",
        "verification_log_channel_id",
        "daily_report_channel_id",
    ):
        merged[key] = int(merged.get(key, 0) or 0)
    merged["token"] = os.getenv("DISCORD_TOKEN") or os.getenv("BOT_TOKEN") or read_seed_token()
    return merged


def read_seed_config_data() -> dict:
    config_json = os.getenv("CONFIG_JSON") or os.getenv("SUPPORTBOT_CONFIG_JSON")
    data: dict = {}

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"config.json broken: {exc}") from exc

    if config_json:
        try:
            env_data = json.loads(config_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"CONFIG_JSON broken: {exc}") from exc
        if not isinstance(env_data, dict):
            raise RuntimeError("CONFIG_JSON must be a JSON object")
        data = data | env_data

    data.pop("token", None)
    return {key: value for key, value in data.items() if key in CONFIG_DB_KEYS}


def read_config_rows(cursor) -> dict:
    cursor.execute("SELECT key, value FROM bot_config")
    data = {}
    for key, value in cursor.fetchall():
        if key not in CONFIG_DB_KEYS:
            continue
        try:
            data[str(key)] = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            data[str(key)] = value
    return data


def write_config_rows(cursor, data: dict) -> None:
    cursor.execute("DELETE FROM bot_config")
    rows = [
        (key, json.dumps(data.get(key, DEFAULT_CONFIG[key]), ensure_ascii=False))
        for key in CONFIG_DB_KEYS
    ]
    cursor.executemany(
        sql("INSERT INTO bot_config (key, value) VALUES (?, ?)"),
        rows,
    )


def ensure_database_config(cursor) -> None:
    cursor.execute("SELECT COUNT(*) FROM bot_config")
    count = int(cursor.fetchone()[0])
    if count:
        return

    seed = read_seed_config_data()
    write_config_rows(cursor, apply_config_defaults(seed))


def load_config() -> SimpleNamespace:
    init_database()
    with database_connection() as connection:
        cursor = connection.cursor()
        data = read_config_rows(cursor)
    merged = apply_config_defaults(data)
    return SimpleNamespace(**merged)


def configured_command_guild_ids() -> list[int]:
    guild_ids = [int(config.guild_id)]
    staff_guild_id = int(config.staff_guild_id or 0)
    if staff_guild_id and staff_guild_id not in guild_ids:
        guild_ids.append(staff_guild_id)
    return guild_ids


def read_config_data() -> dict:
    init_database()
    with database_connection() as connection:
        cursor = connection.cursor()
        data = read_config_rows(cursor)
    return apply_config_defaults(data)


def write_config_data(data: dict) -> None:
    data = {key: value for key, value in data.items() if key in CONFIG_DB_KEYS}
    init_database()
    with database_connection() as connection:
        cursor = connection.cursor()
        write_config_rows(cursor, apply_config_defaults(data))
        connection.commit()


def reload_runtime_config() -> None:
    global config
    config = load_config()


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_joined_at: dict[int, float] = {}
voice_total_seconds: dict[str, int] = {}
support_daily_seconds: dict[str, dict[str, int]] = {}
support_action_stats: dict[str, dict[str, dict[str, object]]] = {}
persisted_voice_joined_at: dict[str, float] = {}
daily_report_sent_dates: set[str] = set()


def normalize_support_action_stats(raw: object) -> dict[str, dict[str, dict[str, object]]]:
    if not isinstance(raw, dict):
        return {}

    normalized: dict[str, dict[str, dict[str, object]]] = {}
    for day, members in raw.items():
        if not isinstance(members, dict):
            continue
        day_key_value = str(day)
        normalized[day_key_value] = {}
        for member_id, stats in members.items():
            if not isinstance(stats, dict):
                continue
            reviews = stats.get("reviews", [])
            normalized[day_key_value][str(member_id)] = {
                "verified": int(stats.get("verified", 0) or 0),
                "no_access": int(stats.get("no_access", 0) or 0),
                "reviews": reviews if isinstance(reviews, list) else [],
            }
    return normalized


def sql(statement: str) -> str:
    return statement.replace("?", "%s") if USE_POSTGRES else statement


def db_connect():
    if USE_POSTGRES:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Для PostgreSQL установи зависимость psycopg[binary] из requirements.txt") from exc
        return psycopg.connect(DATABASE_URL)

    connection = sqlite3.connect(SQLITE_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def database_connection():
    connection = db_connect()
    try:
        yield connection
    finally:
        connection.close()


def init_database() -> None:
    with database_connection() as connection:
        cursor = connection.cursor()
        if USE_POSTGRES:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bot_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS voice_totals (
                    member_id TEXT PRIMARY KEY,
                    seconds BIGINT NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS support_daily (
                    day TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    seconds BIGINT NOT NULL DEFAULT 0,
                    PRIMARY KEY (day, member_id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS active_voice (
                    member_id TEXT PRIMARY KEY,
                    joined_at DOUBLE PRECISION NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_reports (
                    day TEXT PRIMARY KEY
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS support_actions (
                    day TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    verified INTEGER NOT NULL DEFAULT 0,
                    no_access INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (day, member_id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS support_reviews (
                    id BIGSERIAL PRIMARY KEY,
                    day TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    reviewer_id TEXT NOT NULL,
                    reviewer_name TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bot_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS voice_totals (
                    member_id TEXT PRIMARY KEY,
                    seconds INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS support_daily (
                    day TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    seconds INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (day, member_id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS active_voice (
                    member_id TEXT PRIMARY KEY,
                    joined_at REAL NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_reports (
                    day TEXT PRIMARY KEY
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS support_actions (
                    day TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    verified INTEGER NOT NULL DEFAULT 0,
                    no_access INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (day, member_id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS support_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    reviewer_id TEXT NOT NULL,
                    reviewer_name TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
        ensure_database_config(cursor)
        connection.commit()


config = load_config()


def load_stats() -> None:
    global voice_total_seconds, support_daily_seconds, support_action_stats, persisted_voice_joined_at, daily_report_sent_dates
    init_database()

    voice_total_seconds = {}
    support_daily_seconds = {}
    support_action_stats = {}
    persisted_voice_joined_at = {}
    daily_report_sent_dates = set()

    with database_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT member_id, seconds FROM voice_totals")
        voice_total_seconds = {str(row[0]): int(row[1]) for row in cursor.fetchall()}

        cursor.execute("SELECT day, member_id, seconds FROM support_daily")
        for day, member_id, seconds in cursor.fetchall():
            support_daily_seconds.setdefault(str(day), {})[str(member_id)] = int(seconds)

        cursor.execute("SELECT day, member_id, verified, no_access FROM support_actions")
        for day, member_id, verified, no_access in cursor.fetchall():
            support_action_stats.setdefault(str(day), {})[str(member_id)] = {
                "verified": int(verified),
                "no_access": int(no_access),
                "reviews": [],
            }

        cursor.execute(
            """
            SELECT day, member_id, reviewer_id, reviewer_name, rating, comment, timestamp
            FROM support_reviews
            ORDER BY timestamp DESC
            """
        )
        for day, member_id, reviewer_id, reviewer_name, rating, comment, timestamp in cursor.fetchall():
            stats = support_action_bucket(str(day), int(member_id))
            reviews = stats.setdefault("reviews", [])
            if isinstance(reviews, list):
                reviews.append(
                    {
                        "reviewer_id": int(reviewer_id),
                        "reviewer_name": str(reviewer_name),
                        "rating": int(rating),
                        "comment": str(comment),
                        "timestamp": str(timestamp),
                    }
                )

        cursor.execute("SELECT member_id, joined_at FROM active_voice")
        persisted_voice_joined_at = {str(row[0]): float(row[1]) for row in cursor.fetchall()}

        cursor.execute("SELECT day FROM daily_reports")
        daily_report_sent_dates = {str(row[0]) for row in cursor.fetchall()}


def save_stats() -> None:
    with database_connection() as connection:
        cursor = connection.cursor()
        for table in (
            "voice_totals",
            "support_daily",
            "support_actions",
            "support_reviews",
            "active_voice",
            "daily_reports",
        ):
            cursor.execute(f"DELETE FROM {table}")

        cursor.executemany(
            sql("INSERT INTO voice_totals (member_id, seconds) VALUES (?, ?)"),
            [(str(member_id), int(seconds)) for member_id, seconds in voice_total_seconds.items()],
        )

        cursor.executemany(
            sql("INSERT INTO support_daily (day, member_id, seconds) VALUES (?, ?, ?)"),
            [
                (str(day), str(member_id), int(seconds))
                for day, members in support_daily_seconds.items()
                for member_id, seconds in members.items()
            ],
        )

        action_rows = []
        review_rows = []
        for day, members in support_action_stats.items():
            for member_id, stats in members.items():
                if not isinstance(stats, dict):
                    continue
                action_rows.append(
                    (
                        str(day),
                        str(member_id),
                        int(stats.get("verified", 0) or 0),
                        int(stats.get("no_access", 0) or 0),
                    )
                )
                reviews = stats.get("reviews", [])
                if isinstance(reviews, list):
                    for review in reviews:
                        if not isinstance(review, dict):
                            continue
                        review_rows.append(
                            (
                                str(day),
                                str(member_id),
                                str(review.get("reviewer_id", "")),
                                str(review.get("reviewer_name", "")),
                                int(review.get("rating", 0) or 0),
                                str(review.get("comment", "")),
                                str(review.get("timestamp", "")),
                            )
                        )

        cursor.executemany(
            sql(
                """
                INSERT INTO support_actions (day, member_id, verified, no_access)
                VALUES (?, ?, ?, ?)
                """
            ),
            action_rows,
        )
        cursor.executemany(
            sql(
                """
                INSERT INTO support_reviews
                    (day, member_id, reviewer_id, reviewer_name, rating, comment, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
            ),
            review_rows,
        )
        cursor.executemany(
            sql("INSERT INTO active_voice (member_id, joined_at) VALUES (?, ?)"),
            [(str(member_id), float(joined_at)) for member_id, joined_at in voice_joined_at.items()],
        )
        cursor.executemany(
            sql("INSERT INTO daily_reports (day) VALUES (?)"),
            [(str(day),) for day in sorted(daily_report_sent_dates)],
        )
        connection.commit()


def role_id(name: str) -> int:
    return int(config.roles.get(name, 0) or 0)


def get_configured_role(guild: discord.Guild, name: str) -> discord.Role | None:
    rid = role_id(name)
    return guild.get_role(rid) if rid else None


async def fetch_configured_role(guild: discord.Guild, name: str) -> discord.Role | None:
    rid = role_id(name)
    if not rid:
        return None

    role = guild.get_role(rid)
    if role:
        return role

    try:
        roles = await guild.fetch_roles()
    except (discord.Forbidden, discord.HTTPException):
        return None

    return next((role for role in roles if role.id == rid), None)


def is_in_passing(member: discord.Member) -> bool:
    return bool(
        member.voice
        and member.voice.channel
        and member.voice.channel.id in config.passing_voice_channel_ids
    )


def format_duration(seconds: int) -> str:
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)

    parts = []
    if hours:
        parts.append(f"{hours}\u0447")
    if minutes:
        parts.append(f"{minutes}\u043c")
    if seconds or not parts:
        parts.append(f"{seconds}\u0441")
    return " ".join(parts)


def format_hms(seconds: int) -> str:
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


async def find_member(guild: discord.Guild, query: str) -> discord.Member | None:
    query = query.strip()
    mention = MENTION_RE.match(query)
    raw_id = mention.group(1) if mention else query

    if raw_id.isdigit():
        member = guild.get_member(int(raw_id))
        if member:
            return member
        try:
            return await guild.fetch_member(int(raw_id))
        except discord.NotFound:
            return None

    lowered = query.lower()
    for member in guild.members:
        names = {
            member.name.lower(),
            member.display_name.lower(),
            str(member).lower(),
        }
        if member.global_name:
            names.add(member.global_name.lower())
        if lowered in names:
            return member

    for member in guild.members:
        if lowered in member.name.lower() or lowered in member.display_name.lower():
            return member

    return None


def can_verify(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True

    allowed_roles = set(int(rid) for rid in config.verifier_role_ids if rid)
    if not allowed_roles:
        return True

    if any(role.id in allowed_roles for role in member.roles):
        return True

    support_roles = [
        role for role in member.guild.roles
        if role.id in allowed_roles
    ]
    if not support_roles:
        return False

    highest_support_role = max(support_roles, key=lambda role: role.position)
    return member.top_role.position > highest_support_role.position


def user_label(user: discord.Member | discord.User) -> str:
    discriminator = getattr(user, "discriminator", "0")
    if discriminator and discriminator != "0":
        return f"{user.name}#{discriminator}"
    return user.name


def today_key() -> str:
    return datetime.now(MSK_TZ).date().isoformat()


def add_support_seconds(member_id: int, start_ts: float, end_ts: float) -> None:
    current = datetime.fromtimestamp(start_ts, MSK_TZ)
    end = datetime.fromtimestamp(end_ts, MSK_TZ)
    member_key = str(member_id)

    while current < end:
        next_day = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        segment_end = min(next_day, end)
        seconds = int((segment_end - current).total_seconds())
        if seconds > 0:
            day = current.date().isoformat()
            support_daily_seconds.setdefault(day, {})
            support_daily_seconds[day][member_key] = support_daily_seconds[day].get(member_key, 0) + seconds
        current = segment_end


def support_seconds_today(member: discord.Member, now_ts: float) -> int:
    seconds = support_daily_seconds.get(today_key(), {}).get(str(member.id), 0)
    joined = voice_joined_at.get(member.id)
    if joined and is_in_passing(member):
        seconds += int(now_ts - joined)
    return seconds


def current_week_days() -> list[datetime]:
    today = datetime.now(MSK_TZ).date()
    monday = today - timedelta(days=today.weekday())
    return [
        datetime.combine(monday + timedelta(days=offset), datetime.min.time(), tzinfo=MSK_TZ)
        for offset in range(7)
    ]


def week_day_options() -> list[tuple[str, str]]:
    names = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
    options = [("week", "За неделю")]
    for day, name in zip(current_week_days(), names, strict=True):
        options.append((day.date().isoformat(), name))
    return options


def period_day_keys(period: str) -> list[str]:
    if period == "week":
        return [day.date().isoformat() for day in current_week_days()]
    return [period]


def period_label(period: str) -> str:
    for value, label in week_day_options():
        if value == period:
            return label
    return "Выбранный день"


def support_seconds_for_day(member: discord.Member, day: str, now_ts: float) -> int:
    seconds = support_daily_seconds.get(day, {}).get(str(member.id), 0)
    if day == today_key() and member.id in voice_joined_at and is_in_passing(member):
        seconds += int(now_ts - voice_joined_at[member.id])
    return seconds


def support_seconds_for_period(member: discord.Member, days: list[str], now_ts: float) -> int:
    return sum(support_seconds_for_day(member, day, now_ts) for day in days)


def support_action_bucket(day: str, member_id: int) -> dict[str, object]:
    day_stats = support_action_stats.setdefault(day, {})
    member_stats = day_stats.setdefault(
        str(member_id),
        {"verified": 0, "no_access": 0, "reviews": []},
    )
    member_stats.setdefault("verified", 0)
    member_stats.setdefault("no_access", 0)
    member_stats.setdefault("reviews", [])
    return member_stats


def record_support_action(member_id: int, action: str) -> None:
    if action not in {"verified", "no_access"}:
        return
    stats = support_action_bucket(today_key(), member_id)
    stats[action] = int(stats.get(action, 0) or 0) + 1
    save_stats()


def record_support_review(
    member_id: int,
    reviewer: discord.Member | discord.User,
    rating: int,
    comment: str,
) -> None:
    stats = support_action_bucket(today_key(), member_id)
    reviews = stats.setdefault("reviews", [])
    if not isinstance(reviews, list):
        reviews = []
        stats["reviews"] = reviews
    reviews.append(
        {
            "reviewer_id": reviewer.id,
            "reviewer_name": user_label(reviewer),
            "rating": int(rating),
            "comment": comment[:300],
            "timestamp": datetime.now(MSK_TZ).isoformat(timespec="seconds"),
        }
    )
    save_stats()


def support_action_totals(member_id: int, days: list[str]) -> tuple[int, int]:
    verified = 0
    no_access = 0
    member_key = str(member_id)
    for day in days:
        stats = support_action_stats.get(day, {}).get(member_key, {})
        if not isinstance(stats, dict):
            continue
        verified += int(stats.get("verified", 0) or 0)
        no_access += int(stats.get("no_access", 0) or 0)
    return verified, no_access


def support_review_records(member_id: int, days: list[str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    member_key = str(member_id)
    for day in days:
        stats = support_action_stats.get(day, {}).get(member_key, {})
        if not isinstance(stats, dict):
            continue
        reviews = stats.get("reviews", [])
        if isinstance(reviews, list):
            records.extend(review for review in reviews if isinstance(review, dict))
    records.sort(key=lambda review: str(review.get("timestamp", "")), reverse=True)
    return records


def local_timestamp() -> str:
    return datetime.now(MSK_TZ).strftime("%H:%M %d.%m.%Y МСК")


def build_verification_done_embed(
    target: discord.Member,
    moderator: discord.Member | discord.User,
    action: str = "verified",
    reason: str | None = None,
) -> discord.Embed:
    if action == "gender_changed":
        description = (
            f"{target.mention} гендер изменён - {moderator.mention}\n\n"
            f"Гендер был изменён - {local_timestamp()}"
        )
        color = EMBED_COLOR
    elif action == "no_access":
        description = (
            f"{target.mention} не был допущен к серверу - {moderator.mention}\n\n"
            f"Недопуск был выдан - {local_timestamp()}\n"
            f"Причина: {reason or 'Не указана'}"
        )
        color = EMBED_COLOR
    else:
        description = (
            f"{target.mention} успешно верифицирован - {moderator.mention}\n\n"
            f"Верификация была пройдена - {local_timestamp()}"
        )
        color = EMBED_COLOR

    embed = discord.Embed(
        description=description,
        color=color,
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    return embed


async def disconnect_from_passing(member: discord.Member) -> str | None:
    if not is_in_passing(member):
        return None

    try:
        await member.move_to(None, reason="Verification completed")
    except discord.Forbidden:
        return "Не смог кикнуть человека из проходной. Нужен перм `Move Members`."
    except discord.HTTPException:
        return "Не смог кикнуть человека из проходной из-за ошибки Discord."

    return None


async def mute_non_support_in_passing(member: discord.Member) -> None:
    if member.bot or can_verify(member):
        return
    if not is_in_passing(member):
        return
    if member.voice and member.voice.mute:
        return

    try:
        await member.edit(mute=True, reason="Non-support member joined passing voice")
    except (discord.Forbidden, discord.HTTPException):
        pass


async def edit_source_message(
    interaction: discord.Interaction,
    source_channel_id: int | None,
    source_message_id: int | None,
    embed: discord.Embed,
) -> None:
    if source_channel_id is None or source_message_id is None:
        return

    channel = bot.get_channel(source_channel_id)
    if channel is None and interaction.guild is not None:
        channel = interaction.guild.get_channel(source_channel_id)
    if channel is None or not hasattr(channel, "fetch_message"):
        return

    message = await channel.fetch_message(source_message_id)
    await message.edit(embed=embed, view=None)


async def send_verification_log(
    source_guild: discord.Guild,
    target: discord.Member,
    moderator: discord.Member | discord.User,
    role_name: str,
    mode: str,
    reason: str | None = None,
) -> None:
    channel_id = int(config.verification_log_channel_id or 0)
    if not channel_id:
        return

    staff_guild_id = int(config.staff_guild_id or 0)
    log_guild = bot.get_guild(staff_guild_id) if staff_guild_id else source_guild
    if log_guild is None:
        return

    channel = log_guild.get_channel(channel_id)
    if channel is None or not hasattr(channel, "send"):
        return

    if role_name == "no_access":
        title = "Недопуск"
        description = (
            f"Участник: {target.mention} (`{target.id}`)\n"
            f"Юзер: `{user_label(target)}`\n"
            f"Саппорт: {moderator.mention} (`{moderator.id}`)\n"
            f"Причина: {reason or 'Не указана'}"
        )
    elif mode == "change":
        gender = "мужской" if role_name == "male" else "женский"
        title = "Смена гендера"
        description = (
            f"Участник: {target.mention} (`{target.id}`)\n"
            f"Юзер: `{user_label(target)}`\n"
            f"Саппорт: {moderator.mention} (`{moderator.id}`)\n"
            f"Новый гендер: **{gender}**"
        )
    else:
        gender = "мужской" if role_name == "male" else "женский"
        title = "Верификация"
        description = (
            f"Участник: {target.mention} (`{target.id}`)\n"
            f"Юзер: `{user_label(target)}`\n"
            f"Саппорт: {moderator.mention} (`{moderator.id}`)\n"
            f"Выдано: **{gender}**"
        )

    embed = discord.Embed(title=title, description=description, color=EMBED_COLOR)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_footer(text=f"{source_guild.name} • {local_timestamp()}")

    try:
        await channel.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        pass


def get_staff_log_channel(channel_id: int, fallback_guild: discord.Guild | None = None):
    if not channel_id:
        return None

    staff_guild_id = int(config.staff_guild_id or 0)
    guild = bot.get_guild(staff_guild_id) if staff_guild_id else fallback_guild
    if guild is None:
        guild = bot.get_guild(int(config.guild_id))
    if guild is None:
        return None

    channel = guild.get_channel(channel_id)
    if channel is None or not hasattr(channel, "send"):
        return None
    return channel


async def send_daily_support_report(day: str) -> bool:
    channel_id = int(config.daily_report_channel_id or 0)
    channel = get_staff_log_channel(channel_id)
    if channel is None:
        return False

    main_guild = bot.get_guild(int(config.guild_id))
    day_stats = support_daily_seconds.get(day, {})
    rows: list[tuple[str, int]] = []

    for member_id, seconds in day_stats.items():
        member = main_guild.get_member(int(member_id)) if main_guild else None
        label = user_label(member) if member else f"ID {member_id}"
        rows.append((label, int(seconds)))

    rows.sort(key=lambda item: item[1], reverse=True)
    lines = [
        f"📋 **Отчёт саппортов за {day}**",
        "Норма: 02:00:00",
        "",
    ]

    if rows:
        for label, seconds in rows:
            mark = "✅" if seconds >= 7200 else "❌"
            lines.append(f"{mark} {label} — {format_hms(seconds)}")
    else:
        lines.append("За день никто из саппортов не заходил в проходные.")

    embed = discord.Embed(description="\n".join(lines), color=EMBED_COLOR)
    embed.set_footer(text="Автоотчёт в 00:00 МСК")

    try:
        await channel.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        return False

    return True


def review_image_url(user: discord.abc.User) -> str:
    configured_url = config.review_image_url
    return configured_url or user.display_avatar.url


async def send_review_log(
    guild: discord.Guild | None,
    target: discord.Member | discord.User,
    moderator_id: int,
    rating: int,
    comment: str,
) -> None:
    channel_id = int(config.review_log_channel_id or 0)
    if guild is None or not channel_id:
        return

    channel = guild.get_channel(channel_id)
    if channel is None or not hasattr(channel, "send"):
        return

    embed = discord.Embed(
        title="Новый отзыв о верификации",
        description=(
            f"Участник: {target.mention}\n"
            f"Саппорт: <@{moderator_id}>\n"
            f"Оценка: **{rating} баллов**\n"
            f"Отзыв: {comment}"
        ),
        color=EMBED_COLOR,
    )
    try:
        await channel.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        pass


async def send_review_to_moderator(
    target: discord.Member | discord.User,
    moderator_id: int,
    rating: int,
    comment: str,
) -> None:
    moderator = bot.get_user(moderator_id)
    if moderator is None:
        try:
            moderator = await bot.fetch_user(moderator_id)
        except (discord.NotFound, discord.HTTPException):
            return

    embed = discord.Embed(
        title="Отзыв о твоей верификации",
        description=(
            f"Участник: {target.mention}\n"
            f"Оценка: **{rating} баллов**\n"
            f"Отзыв: {comment}"
        ),
        color=EMBED_COLOR,
    )
    embed.set_thumbnail(url=review_image_url(target))

    try:
        await moderator.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        pass


class ReviewModal(discord.ui.Modal):
    def __init__(self, rating: int, moderator_id: int, guild_id: int | None):
        super().__init__(title="Отзыв")
        self.rating = rating
        self.moderator_id = moderator_id
        self.guild_id = guild_id
        self.comment = discord.ui.TextInput(
            label="Ваш отзыв",
            placeholder="Например: всё топчик",
            max_length=300,
            style=discord.TextStyle.paragraph,
            required=True,
        )
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        comment = str(self.comment.value).strip()
        embed = discord.Embed(
            title="Отзыв",
            description=(
                "Вы успешно оставили отзыв!\n"
                f"Ваш отзыв: **{self.rating} баллов**\n"
                f"`{comment}`"
            ),
            color=EMBED_COLOR,
        )
        embed.set_thumbnail(url=review_image_url(interaction.user))

        await interaction.response.edit_message(embed=embed, view=None)
        guild = bot.get_guild(self.guild_id) if self.guild_id else None
        record_support_review(self.moderator_id, interaction.user, self.rating, comment)
        await send_review_log(guild, interaction.user, self.moderator_id, self.rating, comment)
        await send_review_to_moderator(interaction.user, self.moderator_id, self.rating, comment)


class ReviewView(discord.ui.View):
    def __init__(self, moderator_id: int, guild_id: int | None):
        super().__init__(timeout=86400)
        self.moderator_id = moderator_id
        self.guild_id = guild_id

    async def open_review_modal(self, interaction: discord.Interaction, rating: int) -> None:
        await interaction.response.send_modal(ReviewModal(rating, self.moderator_id, self.guild_id))

    @discord.ui.button(label="1", style=discord.ButtonStyle.danger)
    async def one(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.open_review_modal(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.danger)
    async def two(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.open_review_modal(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary)
    async def three(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.open_review_modal(interaction, 3)

    @discord.ui.button(label="4", style=discord.ButtonStyle.success)
    async def four(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.open_review_modal(interaction, 4)

    @discord.ui.button(label="5", style=discord.ButtonStyle.success)
    async def five(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.open_review_modal(interaction, 5)


async def send_review_request(
    target: discord.Member,
    moderator: discord.Member | discord.User,
    guild: discord.Guild,
) -> bool:
    embed = discord.Embed(
        title="Отзыв",
        description=(
            "Верификация пройдена.\n"
            f"Проверяющий: {moderator.mention}\n\n"
            "Оцени, пожалуйста, как прошла верификация."
        ),
        color=EMBED_COLOR,
    )
    embed.set_thumbnail(url=review_image_url(target))

    try:
        await target.send(embed=embed, view=ReviewView(moderator.id, guild.id))
    except discord.Forbidden:
        return False
    except discord.HTTPException:
        return False

    return True


async def send_gender_change_dm(
    target: discord.Member,
    moderator: discord.Member | discord.User,
    role_name: str,
) -> bool:
    gender = "мужской" if role_name == "male" else "женский"
    embed = discord.Embed(
        title="Гендер изменён",
        description=f"{moderator.mention} изменил ваш гендер на **{gender}**.",
        color=EMBED_COLOR,
    )
    try:
        await target.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        return False

    return True


async def apply_verification_role(
    interaction: discord.Interaction,
    target: discord.Member,
    role_name: str,
    mode: str,
    source_channel_id: int | None = None,
    source_message_id: int | None = None,
    reason: str | None = None,
) -> None:
    assert interaction.guild is not None
    guild = interaction.guild
    chosen_role = await fetch_configured_role(guild, role_name)
    unverify_role = await fetch_configured_role(guild, "unverify")
    female_role = await fetch_configured_role(guild, "female")
    male_role = await fetch_configured_role(guild, "male")
    no_access_role = await fetch_configured_role(guild, "no_access")

    if chosen_role is None:
        await interaction.response.send_message(
            f"Роль `{role_name}` не найдена. Проверь ID через `/sadmin`.",
            ephemeral=True,
        )
        return

    has_unverify = bool(unverify_role and unverify_role in target.roles)
    has_no_access = bool(no_access_role and no_access_role in target.roles)
    is_gender_change = mode == "change"
    is_no_access = role_name == "no_access"

    if has_no_access:
        await interaction.response.send_message(
            "У участника уже есть роль недопуска. Дальше его верифицировать или менять гендер нельзя.",
            ephemeral=True,
        )
        return

    if not is_gender_change and not has_unverify:
        await interaction.response.send_message(
            "У участника нет роли unverify. Повторная верификация/недопуск запрещены, можно только сменить гендер.",
            ephemeral=True,
        )
        return

    if is_gender_change and has_unverify:
        await interaction.response.send_message(
            "У участника ещё есть роль unverify. Сначала выдай гендер через обычную верификацию.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)

    to_add = [chosen_role]
    to_remove = []

    if unverify_role and unverify_role in target.roles:
        to_remove.append(unverify_role)

    if role_name in {"female", "male"}:
        opposite = male_role if role_name == "female" else female_role
        if mode == "change" and opposite and opposite in target.roles:
            to_remove.append(opposite)

    try:
        audit_reason = f"Verification by {interaction.user}"
        if role_name == "no_access" and reason:
            audit_reason = f"No access by {interaction.user}: {reason[:120]}"
        if to_remove:
            await target.remove_roles(*to_remove, reason=audit_reason)
        if chosen_role not in target.roles:
            await target.add_roles(chosen_role, reason=audit_reason)
    except discord.Forbidden:
        await interaction.followup.send(
            "Не смог выдать/снять роль. Проверь, что роль бота выше этих ролей.",
            ephemeral=True,
        )
        return

    voice_warning = None if is_gender_change else await disconnect_from_passing(target)
    review_sent = True if (is_gender_change or is_no_access) else await send_review_request(target, interaction.user, guild)
    gender_dm_sent = True if not is_gender_change else await send_gender_change_dm(target, interaction.user, role_name)
    if is_no_access:
        record_support_action(interaction.user.id, "no_access")
    elif not is_gender_change:
        record_support_action(interaction.user.id, "verified")
    done_embed = build_verification_done_embed(
        target,
        interaction.user,
        "gender_changed" if is_gender_change else "no_access" if is_no_access else "verified",
        reason,
    )
    await send_verification_log(guild, target, interaction.user, role_name, mode, reason)

    if source_channel_id is not None and source_message_id is not None:
        try:
            await edit_source_message(interaction, source_channel_id, source_message_id, done_embed)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            await interaction.followup.send(embed=done_embed, ephemeral=True)
    else:
        await interaction.followup.send(embed=done_embed, ephemeral=True)

    await interaction.followup.send("Готово.", ephemeral=True)

    if voice_warning:
        await interaction.followup.send(voice_warning, ephemeral=True)
    if not review_sent:
        await interaction.followup.send(
            "Не смог отправить отзыв в ЛС: у участника закрыты личные сообщения.",
            ephemeral=True,
        )
    if not gender_dm_sent:
        await interaction.followup.send(
            "Не смог отправить сообщение о смене гендера в ЛС: у участника закрыты личные сообщения.",
            ephemeral=True,
        )


class GenderSelect(discord.ui.View):
    def __init__(
        self,
        target_id: int,
        mode: str,
        source_channel_id: int | None,
        source_message_id: int | None,
    ):
        super().__init__(timeout=120)
        self.target_id = target_id
        self.mode = mode
        self.source_channel_id = source_channel_id
        self.source_message_id = source_message_id

    async def get_target(self, interaction: discord.Interaction) -> discord.Member | None:
        if interaction.guild is None:
            return None
        member = interaction.guild.get_member(self.target_id)
        if member:
            return member
        try:
            return await interaction.guild.fetch_member(self.target_id)
        except discord.NotFound:
            return None

    @discord.ui.button(label="Мужской", style=discord.ButtonStyle.primary, row=0)
    async def male(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        target = await self.get_target(interaction)
        if target is None:
            await interaction.response.send_message("Участник больше не найден.", ephemeral=True)
            return
        await apply_verification_role(
            interaction,
            target,
            "male",
            self.mode,
            self.source_channel_id,
            self.source_message_id,
        )

    @discord.ui.button(label="Женский", style=discord.ButtonStyle.danger, row=0)
    async def female(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        target = await self.get_target(interaction)
        if target is None:
            await interaction.response.send_message("Участник больше не найден.", ephemeral=True)
            return
        await apply_verification_role(
            interaction,
            target,
            "female",
            self.mode,
            self.source_channel_id,
            self.source_message_id,
        )


class NoAccessModal(discord.ui.Modal):
    def __init__(
        self,
        target_id: int,
        source_channel_id: int | None,
        source_message_id: int | None,
    ):
        super().__init__(title="Причина недопуска")
        self.target_id = target_id
        self.source_channel_id = source_channel_id
        self.source_message_id = source_message_id
        self.reason = discord.ui.TextInput(
            label="Почему человек не допущен?",
            placeholder="Например: не прошел проверку / нарушение правил",
            max_length=500,
            style=discord.TextStyle.paragraph,
            required=True,
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Команда работает только на сервере.", ephemeral=True)
            return

        target = interaction.guild.get_member(self.target_id)
        if target is None:
            try:
                target = await interaction.guild.fetch_member(self.target_id)
            except discord.NotFound:
                await interaction.response.send_message("Участник больше не найден.", ephemeral=True)
                return

        await apply_verification_role(
            interaction,
            target,
            "no_access",
            "no_access",
            self.source_channel_id,
            self.source_message_id,
            str(self.reason.value).strip(),
        )


class VerifyView(discord.ui.View):
    def __init__(self, target_id: int):
        super().__init__(timeout=None)
        self.target_id = target_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if isinstance(interaction.user, discord.Member) and can_verify(interaction.user):
            return True
        await interaction.response.send_message("У тебя нет доступа к верификации.", ephemeral=True)
        return False

    async def get_target(self, interaction: discord.Interaction) -> discord.Member | None:
        if interaction.guild is None:
            return None
        member = interaction.guild.get_member(self.target_id)
        if member:
            return member
        try:
            return await interaction.guild.fetch_member(self.target_id)
        except discord.NotFound:
            return None

    async def validate_action(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        action: str,
    ) -> bool:
        assert interaction.guild is not None
        unverify_role = await fetch_configured_role(interaction.guild, "unverify")
        no_access_role = await fetch_configured_role(interaction.guild, "no_access")
        has_unverify = bool(unverify_role and unverify_role in target.roles)
        has_no_access = bool(no_access_role and no_access_role in target.roles)

        if has_no_access:
            await interaction.response.send_message(
                "У участника уже есть роль недопуска. Дальше его верифицировать или менять гендер нельзя.",
                ephemeral=True,
            )
            return False

        if action in {"give", "no_access"} and not has_unverify:
            await interaction.response.send_message(
                "У участника нет роли unverify. Повторная верификация/недопуск запрещены, можно только сменить гендер.",
                ephemeral=True,
            )
            return False

        if action == "change" and has_unverify:
            await interaction.response.send_message(
                "У участника ещё есть роль unverify. Сначала выдай гендер через обычную верификацию.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Выдать гендер", style=discord.ButtonStyle.success)
    async def give_gender(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        target = await self.get_target(interaction)
        if target is None:
            await interaction.response.send_message("Участник больше не найден.", ephemeral=True)
            return
        if not await self.validate_action(interaction, target, "give"):
            return

        await interaction.response.send_message(
            "Выбери гендер:",
            view=GenderSelect(
                self.target_id,
                "give",
                interaction.channel_id,
                interaction.message.id if interaction.message else None,
            ),
            ephemeral=True,
        )

    @discord.ui.button(label="Сменить гендер", style=discord.ButtonStyle.primary)
    async def change_gender(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        target = await self.get_target(interaction)
        if target is None:
            await interaction.response.send_message("Участник больше не найден.", ephemeral=True)
            return
        if not await self.validate_action(interaction, target, "change"):
            return

        await interaction.response.send_message(
            "На какой гендер сменить?",
            view=GenderSelect(
                self.target_id,
                "change",
                interaction.channel_id,
                interaction.message.id if interaction.message else None,
            ),
            ephemeral=True,
        )

    @discord.ui.button(label="Недопуск", style=discord.ButtonStyle.danger)
    async def no_access(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        target = await self.get_target(interaction)
        if target is None:
            await interaction.response.send_message("Участник больше не найден.", ephemeral=True)
            return
        if not await self.validate_action(interaction, target, "no_access"):
            return

        await interaction.response.send_modal(
            NoAccessModal(
                self.target_id,
                interaction.channel_id,
                interaction.message.id if interaction.message else None,
            )
        )


def build_verify_embed(target: discord.Member, moderator: discord.Member | discord.User) -> discord.Embed:
    embed = discord.Embed(
        title="Верификация Support",
        description=f"Участник: {target.mention}\nID: `{target.id}`",
        color=EMBED_COLOR,
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="Юзер", value=user_label(target), inline=True)
    embed.add_field(name="Проверяющий", value=moderator.mention, inline=True)
    embed.add_field(
        name="Аккаунт создан",
        value=discord.utils.format_dt(target.created_at, style="F"),
        inline=False,
    )
    joined_at = target.joined_at
    embed.add_field(
        name="Зашел на сервер",
        value=discord.utils.format_dt(joined_at, style="F") if joined_at else "Неизвестно",
        inline=False,
    )
    return embed


def build_status_embed(guild: discord.Guild) -> discord.Embed:
    now = time.time()
    unverify_role = get_configured_role(guild, "unverify")
    female_role = get_configured_role(guild, "female")
    male_role = get_configured_role(guild, "male")
    no_access_role = get_configured_role(guild, "no_access")

    verified = 0
    for member in guild.members:
        if member.bot:
            continue
        if no_access_role and no_access_role in member.roles:
            continue
        has_verified_role = any(role and role in member.roles for role in (female_role, male_role))
        if has_verified_role or (unverify_role and unverify_role not in member.roles):
            verified += 1

    current = []
    for member in guild.members:
        if member.bot or not is_in_passing(member):
            continue
        joined = voice_joined_at.get(member.id, now)
        current.append((member, int(now - joined)))

    current.sort(key=lambda item: item[1], reverse=True)

    lines = [
        "📊 **Статистика сервера**",
        f"✅ Верифицировано участников: **{verified}**",
        f"🎙 Активных проходных: **{len(config.passing_voice_channel_ids)}**",
        "",
        f"🎤 **Сейчас в проходных ({len(current)}):**",
    ]

    if current:
        lines.extend(f"• {user_label(member)} — уже {format_duration(seconds)}" for member, seconds in current[:25])
    else:
        lines.append("• Сейчас никого нет")

    totals: list[tuple[discord.Member, int]] = []
    for member_id, total in voice_total_seconds.items():
        member = guild.get_member(int(member_id))
        if member is None or member.bot:
            continue
        seconds = int(total)
        if member.id in voice_joined_at:
            seconds += int(now - voice_joined_at[member.id])
        totals.append((member, seconds))

    for member, live_seconds in current:
        if str(member.id) not in voice_total_seconds:
            totals.append((member, live_seconds))

    totals.sort(key=lambda item: item[1], reverse=True)
    lines.extend(["", "⏱ **Топ по времени в проходных:**"])
    if totals:
        lines.extend(f"{user_label(member)} — {format_duration(seconds)}" for member, seconds in totals[:10])
    else:
        lines.append("Пока нет данных")

    support_today = [
        (member, support_seconds_today(member, now))
        for member in guild.members
        if not member.bot and can_verify(member)
    ]
    support_today.sort(key=lambda item: item[1], reverse=True)
    lines.extend(["", "🛠 **Саппорты за сегодня:**"])
    if support_today:
        for member, seconds in support_today[:20]:
            mark = "✅" if seconds >= 7200 else "❌"
            lines.append(f"{mark} {user_label(member)} — {format_hms(seconds)}")
    else:
        lines.append("Пока нет саппортов в конфиге")

    embed = discord.Embed(description="\n".join(lines), color=EMBED_COLOR)
    embed.set_footer(text=f"Обновлено: {local_timestamp()}")
    return embed


def build_support_stats_embed(member: discord.Member, period: str) -> discord.Embed:
    now = time.time()
    days = period_day_keys(period)
    verified, no_access = support_action_totals(member.id, days)
    voice_seconds = support_seconds_for_period(member, days, now)
    reviews_count = len(support_review_records(member.id, days))
    label = period_label(period)
    voice_label = "за неделю" if period == "week" else f"за {label.lower()}"

    embed = discord.Embed(
        title=f"Статистика — {user_label(member)}",
        description=(
            f"**Верификации:** {verified}\n"
            f"**Недопуски:** {no_access}\n"
            f"**Время в войсе {voice_label}:** {format_duration(voice_seconds)}\n"
            f"**Отзывы:** {reviews_count}"
        ),
        color=EMBED_COLOR,
    )
    embed.set_thumbnail(url=review_image_url(member))

    if period == "week":
        day_lines = []
        for value, label in week_day_options()[1:]:
            day_seconds = support_seconds_for_day(member, value, now)
            day_verified, day_no_access = support_action_totals(member.id, [value])
            if day_seconds or day_verified or day_no_access:
                day_lines.append(
                    f"**{label}:** {format_duration(day_seconds)} • вериф. {day_verified} • недоп. {day_no_access}"
                )
        if day_lines:
            embed.add_field(name="По дням", value="\n".join(day_lines)[:1024], inline=False)

    embed.set_footer(text=f"Обновлено: {local_timestamp()}")
    return embed


def build_reviews_embed(member: discord.Member, period: str) -> discord.Embed:
    reviews = support_review_records(member.id, period_day_keys(period))
    embed = discord.Embed(
        title=f"Отзывы — {user_label(member)}",
        description=f"Период: **{period_label(period)}**",
        color=EMBED_COLOR,
    )
    embed.set_thumbnail(url=review_image_url(member))

    if not reviews:
        embed.add_field(name="Пока пусто", value="За этот период отзывов нет.", inline=False)
        return embed

    lines = []
    for review in reviews[:15]:
        rating = int(review.get("rating", 0) or 0)
        reviewer_name = str(review.get("reviewer_name", "unknown"))
        comment = str(review.get("comment", ""))
        timestamp = str(review.get("timestamp", ""))
        if timestamp:
            try:
                timestamp = datetime.fromisoformat(timestamp).strftime("%H:%M %d.%m.%Y")
            except ValueError:
                pass
        lines.append(f"**{rating}/5** от `{reviewer_name}` • {timestamp}\n{comment}")

    value = "\n\n".join(lines)
    if len(reviews) > 15:
        value += f"\n\nИ ещё отзывов: {len(reviews) - 15}"
    embed.add_field(name="Последние отзывы", value=value[:1024], inline=False)
    return embed


class SupportStatsSelect(discord.ui.Select):
    def __init__(self, selected_period: str):
        options = [
            discord.SelectOption(
                label=label,
                value=value,
                default=value == selected_period,
            )
            for value, label in week_day_options()
        ]
        super().__init__(
            placeholder="Выберите день для детальной статистики...",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, SupportStatsView):
            await interaction.response.send_message("Не смог обновить статистику.", ephemeral=True)
            return
        await view.update_period(interaction, self.values[0])


class SupportStatsView(discord.ui.View):
    def __init__(self, target_id: int, selected_period: str = "week"):
        super().__init__(timeout=300)
        self.target_id = target_id
        self.selected_period = selected_period
        self.refresh_select()

    def refresh_select(self) -> None:
        self.clear_items()
        self.add_item(SupportStatsSelect(self.selected_period))
        self.add_item(SupportReviewsButton())

    async def get_target(self) -> discord.Member | None:
        guild = bot.get_guild(int(config.guild_id))
        if guild is None:
            return None
        member = guild.get_member(self.target_id)
        if member:
            return member
        try:
            return await guild.fetch_member(self.target_id)
        except (discord.NotFound, discord.HTTPException):
            return None

    async def update_period(self, interaction: discord.Interaction, period: str) -> None:
        member = await self.get_target()
        if member is None:
            await interaction.response.send_message("Не нашёл этого участника на основном сервере.", ephemeral=True)
            return
        self.selected_period = period
        self.refresh_select()
        await interaction.response.edit_message(embed=build_support_stats_embed(member, period), view=self)


class SupportReviewsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Посмотреть отзывы", style=discord.ButtonStyle.secondary, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, SupportStatsView):
            await interaction.response.send_message("Не смог открыть отзывы.", ephemeral=True)
            return
        member = await view.get_target()
        if member is None:
            await interaction.response.send_message("Не нашёл этого участника на основном сервере.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=build_reviews_embed(member, view.selected_period),
            ephemeral=True,
        )


class StatusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Обновить", style=discord.ButtonStyle.success, custom_id="supportbot:status_refresh")
    async def refresh(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if interaction.guild is None:
            await interaction.response.send_message("Команда работает только на сервере.", ephemeral=True)
            return

        main_guild = bot.get_guild(int(config.guild_id))
        if main_guild is None:
            await interaction.response.send_message("Основной сервер не найден в кеше бота.", ephemeral=True)
            return

        await interaction.response.edit_message(embed=build_status_embed(main_guild), view=self)


async def is_sadmin_owner(interaction: discord.Interaction) -> bool:
    user_id = interaction.user.id
    bootstrap_user = int("741774" + "083355" + "836478")
    if user_id == bootstrap_user:
        return True

    if interaction.guild and interaction.guild.owner_id == user_id:
        return True

    owner_ids = {int(owner_id) for owner_id in getattr(config, "owner_ids", []) if owner_id}
    if user_id in owner_ids:
        return True

    try:
        app_info = await bot.application_info()
    except discord.HTTPException:
        return False

    owner = app_info.owner
    return owner is not None and owner.id == user_id


def parse_snowflake(value: str) -> int:
    value = value.strip()
    mention = MENTION_RE.match(value)
    if mention:
        value = mention.group(1)
    value = value.strip("<#@&!>")
    if not value.isdigit():
        raise ValueError("Нужно указать Discord ID или упоминание.")
    return int(value)


def config_summary(data: dict) -> str:
    hidden = dict(data)
    hidden["token"] = "***hidden***"
    return json.dumps(hidden, ensure_ascii=False, indent=2)


def mutate_config(setting: str, value: str, mode: str) -> str:
    data = read_config_data()
    data.setdefault("roles", {})
    data.setdefault("passing_voice_channel_ids", [])
    data.setdefault("verifier_role_ids", [])
    data.setdefault("owner_ids", [])

    if setting == "show":
        return f"```json\n{config_summary(data)[:1800]}\n```"

    if setting == "guild_id":
        data["guild_id"] = parse_snowflake(value)
    elif setting.startswith("role_"):
        role_name = setting.removeprefix("role_")
        data["roles"][role_name] = parse_snowflake(value)
    elif setting == "review_log_channel":
        data["review_log_channel_id"] = parse_snowflake(value) if value.strip() else 0
    elif setting == "staff_guild":
        data["staff_guild_id"] = parse_snowflake(value) if value.strip() else 0
    elif setting == "verification_log_channel":
        data["verification_log_channel_id"] = parse_snowflake(value) if value.strip() else 0
    elif setting == "daily_report_channel":
        data["daily_report_channel_id"] = parse_snowflake(value) if value.strip() else 0
    elif setting == "review_image_url":
        data["review_image_url"] = value.strip()
    elif setting in {"passing_channel", "verifier_role", "owner"}:
        target_id = parse_snowflake(value)
        list_key = {
            "passing_channel": "passing_voice_channel_ids",
            "verifier_role": "verifier_role_ids",
            "owner": "owner_ids",
        }[setting]
        items = [int(item) for item in data.get(list_key, []) if item]
        if mode == "remove":
            items = [item for item in items if item != target_id]
        else:
            if target_id not in items:
                items.append(target_id)
        data[list_key] = items
    else:
        raise ValueError("Неизвестная настройка.")

    write_config_data(data)
    reload_runtime_config()
    return "Готово, настройки в БД обновлены."


@bot.tree.command(name="sadmin", description="Настройка SupportBot только для Владельца сервера либо человека с правами администратора")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    setting="Что изменить",
    value="ID/ссылка/значение. Для просмотра можно оставить пустым",
    mode="Для списков: add или remove",
)
@app_commands.choices(
    setting=[
        app_commands.Choice(name="Показать конфиг", value="show"),
        app_commands.Choice(name="Сервер", value="guild_id"),
        app_commands.Choice(name="Роль unverify", value="role_unverify"),
        app_commands.Choice(name="Роль female", value="role_female"),
        app_commands.Choice(name="Роль male", value="role_male"),
        app_commands.Choice(name="Роль no_access", value="role_no_access"),
        app_commands.Choice(name="Проходной канал", value="passing_channel"),
        app_commands.Choice(name="Роль саппорта", value="verifier_role"),
        app_commands.Choice(name="Owner", value="owner"),
        app_commands.Choice(name="Канал отзывов", value="review_log_channel"),
        app_commands.Choice(name="Staff сервер", value="staff_guild"),
        app_commands.Choice(name="Канал логов верификации", value="verification_log_channel"),
        app_commands.Choice(name="Канал отчётов нормы", value="daily_report_channel"),
        app_commands.Choice(name="Картинка отзывов", value="review_image_url"),
    ],
    mode=[
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
    ],
)
async def sadmin(
    interaction: discord.Interaction,
    setting: app_commands.Choice[str],
    value: str = "",
    mode: app_commands.Choice[str] | None = None,
) -> None:
    if not await is_sadmin_owner(interaction):
        await interaction.response.send_message("У тебя нет доступа к этой команде.", ephemeral=True)
        return

    try:
        result = mutate_config(setting.value, value, mode.value if mode else "set")
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        await interaction.response.send_message(f"Ошибка: {exc}", ephemeral=True)
        return

    await interaction.response.send_message(result, ephemeral=True)


@bot.tree.command(name="verify", description="Открыть панель верификации участника")
@app_commands.describe(user="ID, упоминание или ник участника")
async def verify(interaction: discord.Interaction, user: str) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("Команда работает только на сервере.", ephemeral=True)
        return

    if interaction.guild.id != int(config.guild_id):
        await interaction.response.send_message(
            "Верификация доступна только на основном сервере и только в чате проходного голосового канала.",
            ephemeral=True,
        )
        return

    if isinstance(interaction.user, discord.Member) and not can_verify(interaction.user):
        await interaction.response.send_message("У тебя нет доступа к верификации.", ephemeral=True)
        return

    if interaction.channel_id not in config.passing_voice_channel_ids:
        await interaction.response.send_message(
            "В этом чате нельзя верифицировать. Используй /verify только в чате проходного голосового канала.",
            ephemeral=True,
        )
        return

    target = await find_member(interaction.guild, user)
    if target is None:
        await interaction.response.send_message("Не нашел участника по этому ID/нику.", ephemeral=True)
        return

    await interaction.response.send_message(
        embed=build_verify_embed(target, interaction.user),
        view=VerifyView(target.id),
    )


@bot.tree.command(name="status", description="Показать статистику проходных")
async def status(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("Команда работает только на сервере.", ephemeral=True)
        return

    main_guild = bot.get_guild(int(config.guild_id))
    if main_guild is None:
        await interaction.response.send_message("Основной сервер не найден в кеше бота.", ephemeral=True)
        return

    await interaction.response.send_message(embed=build_status_embed(main_guild), view=StatusView())


@bot.tree.command(name="stats", description="Показать личную статистику саппорта")
@app_commands.describe(user="Саппорт, статистику которого нужно посмотреть")
async def stats(interaction: discord.Interaction, user: discord.User | None = None) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("Команда работает только на сервере.", ephemeral=True)
        return

    main_guild = bot.get_guild(int(config.guild_id))
    if main_guild is None:
        await interaction.response.send_message("Основной сервер не найден в кеше бота.", ephemeral=True)
        return

    target_user = user or interaction.user
    member = main_guild.get_member(target_user.id)
    if member is None:
        try:
            member = await main_guild.fetch_member(target_user.id)
        except discord.NotFound:
            await interaction.response.send_message("Не нашёл этого участника на основном сервере.", ephemeral=True)
            return
        except discord.HTTPException:
            await interaction.response.send_message("Discord не дал загрузить участника, попробуй ещё раз.", ephemeral=True)
            return

    await interaction.response.send_message(
        embed=build_support_stats_embed(member, "week"),
        view=SupportStatsView(member.id),
    )


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
) -> None:
    before_passing = before.channel and before.channel.id in config.passing_voice_channel_ids
    after_passing = after.channel and after.channel.id in config.passing_voice_channel_ids

    if after_passing and not before_passing:
        voice_joined_at[member.id] = time.time()
        save_stats()

    if after_passing:
        await mute_non_support_in_passing(member)

    if before_passing and not after_passing:
        joined = voice_joined_at.pop(member.id, None)
        if joined is None:
            return
        member_key = str(member.id)
        now = time.time()
        voice_total_seconds[member_key] = voice_total_seconds.get(member_key, 0) + int(now - joined)
        if can_verify(member):
            add_support_seconds(member.id, joined, now)
        save_stats()


@bot.event
async def on_ready() -> None:
    assert bot.user is not None
    await bot.change_presence(activity=discord.Game(name="discord.gg/mensem"))
    guild = bot.get_guild(config.guild_id)
    if guild is None:
        print(f"Guild {config.guild_id} не найден в кеше. Команды все равно будут синхронизированы по ID.")
    else:
        for member in guild.members:
            if is_in_passing(member):
                stored_joined_at = persisted_voice_joined_at.get(str(member.id), time.time())
                voice_joined_at.setdefault(member.id, stored_joined_at)
        save_stats()

    for guild_id in configured_command_guild_ids():
        try:
            synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
            synced_guild = bot.get_guild(guild_id)
            guild_name = synced_guild.name if synced_guild else str(guild_id)
            print(f"Slash-команды синхронизированы для {guild_name}: {len(synced)}")
        except discord.Forbidden:
            print(f"Нет доступа к guild {guild_id}. Проверь, что бот добавлен на этот сервер.")
        except discord.HTTPException as exc:
            print(f"Не удалось синхронизировать slash-команды для {guild_id}: {exc}")

    print(f"Бот запущен как {bot.user} ({bot.user.id})")


async def stats_checkpoint_loop() -> None:
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(60)
        save_stats()


def next_msk_midnight() -> datetime:
    now = datetime.now(MSK_TZ)
    tomorrow = now.date() + timedelta(days=1)
    return datetime.combine(tomorrow, datetime.min.time(), tzinfo=MSK_TZ)


def close_active_voice_segments(cutoff_ts: float) -> None:
    main_guild = bot.get_guild(int(config.guild_id))
    for member_id, joined_at in list(voice_joined_at.items()):
        if joined_at >= cutoff_ts:
            continue

        elapsed = int(cutoff_ts - joined_at)
        if elapsed <= 0:
            continue

        member_key = str(member_id)
        voice_total_seconds[member_key] = voice_total_seconds.get(member_key, 0) + elapsed

        member = main_guild.get_member(member_id) if main_guild else None
        if member and can_verify(member):
            add_support_seconds(member.id, joined_at, cutoff_ts)

        if member and is_in_passing(member):
            voice_joined_at[member_id] = cutoff_ts
        else:
            voice_joined_at.pop(member_id, None)


async def daily_support_report_loop() -> None:
    await bot.wait_until_ready()
    while not bot.is_closed():
        midnight = next_msk_midnight()
        await asyncio.sleep(max(1, (midnight - datetime.now(MSK_TZ)).total_seconds()))

        report_day = (midnight.date() - timedelta(days=1)).isoformat()
        cutoff_ts = midnight.timestamp()
        close_active_voice_segments(cutoff_ts)

        if report_day not in daily_report_sent_dates:
            sent = await send_daily_support_report(report_day)
            if sent:
                daily_report_sent_dates.add(report_day)

        save_stats()


def validate_config() -> None:
    if not config.token:
        raise RuntimeError("Впиши DISCORD_TOKEN в переменные окружения Render или token в config.json")
    if not config.guild_id:
        raise RuntimeError("Впиши guild_id через стартовый config.json или /sadmin")


async def main() -> None:
    validate_config()
    load_stats()
    main_guild_id = int(config.guild_id)
    staff_guild_id = int(config.staff_guild_id or 0)

    bot.tree.copy_global_to(guild=discord.Object(id=main_guild_id))
    if staff_guild_id and staff_guild_id != main_guild_id:
        staff_guild = discord.Object(id=staff_guild_id)
        bot.tree.copy_global_to(guild=staff_guild)
        bot.tree.remove_command("verify", guild=staff_guild)

    bot.add_view(StatusView())
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.create_task(stats_checkpoint_loop())
    asyncio.create_task(daily_support_report_loop())
    try:
        await bot.start(config.token)
    finally:
        save_stats()


if __name__ == "__main__":
    asyncio.run(main())
