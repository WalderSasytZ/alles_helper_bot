import asyncpg
import config
from datetime import datetime
from constants import time_zone


async def connection_init():
    db_conn = config.database_connection
    conn = await asyncpg.connect(user=db_conn['user'],
                                 password=db_conn['password'],
                                 database=db_conn['database'],
                                 host=db_conn['host'],
                                 port=db_conn['port'])
    return conn


async def drop_tables():
    conn = await connection_init()
    await conn.execute('''
        DROP TABLE IF EXISTS tag_event;
        DROP TABLE IF EXISTS tag_user;
        DROP TABLE IF EXISTS tags;
        DROP TABLE IF EXISTS general_events;
        DROP TABLE IF EXISTS personal_events;
        DROP TABLE IF EXISTS users;
    ''')
    await conn.close()


async def create_tables():
    conn = await connection_init()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
          id          SERIAL        PRIMARY KEY,
          name  	  VARCHAR(255),
          role		  INTEGER NOT NULL CHECK (role IN (0, 1, 2)),
          tg_chat_id  INTEGER NOT NULL UNIQUE,
          website_id  INTEGER UNIQUE
        );

        CREATE TABLE IF NOT EXISTS personal_events (
          id           SERIAL         NOT NULL PRIMARY KEY,
          user_id  	   INTEGER        NOT NULL REFERENCES users(id),
          title		   VARCHAR(100),
          description  TEXT,
          starts_at    TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS general_events (
          id           SERIAL         PRIMARY KEY,
          title		   VARCHAR(100),
          description  TEXT,
          starts_at    TIMESTAMP,
          added_at     TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tags (
          id    SERIAL      PRIMARY KEY,
          name  VARCHAR(30) NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS tag_user (
          id       SERIAL   PRIMARY KEY,
          user_id  INTEGER  NOT NULL REFERENCES users(id),
          tag_id   INTEGER  NOT NULL REFERENCES tags(id)
        );

        CREATE TABLE IF NOT EXISTS tag_event (
          id        SERIAL   PRIMARY KEY,
          event_id  INTEGER  NOT NULL REFERENCES general_events(id),
          tag_id    INTEGER  NOT NULL REFERENCES tags(id)
        );  
    ''')
    await conn.close()


async def recreate_tables():
    await drop_tables()
    await create_tables()


async def find_gen_event(event_id):
    conn = await connection_init()
    event_found = await conn.fetchval('''SELECT COUNT(*)
                                         FROM general_events
                                         WHERE id = $1;
                                      ''', int(event_id))
    await conn.close()
    return event_found == 1


async def get_tags_of_event(event_id):
    conn = await connection_init()
    tags = await conn.fetch('''SELECT name
                               FROM tags
                               JOIN tag_event ON tag_event.tag_id = tags.id
                               WHERE tag_event.event_id = $1
                               ORDER BY name;
                            ''', int(event_id))
    await conn.close()
    return tags


async def delete_event(event_id):
    conn = await connection_init()
    await conn.execute('''DELETE FROM tag_event WHERE event_id = $1;
                       ''', int(event_id))
    await conn.execute('''DELETE FROM general_events WHERE id = $1;
                       ''', int(event_id))
    await conn.close()


async def add_tag(tag_name):
    conn = await connection_init()
    await conn.execute('''INSERT INTO tags (name) VALUES ($1) ON CONFLICT DO NOTHING;
                       ''', str(tag_name))
    await conn.close()


async def delete_tag(tag_name):
    conn = await connection_init()
    exists = await conn.fetchval('''SELECT COUNT(*) FROM tags WHERE name = $1;
                                 ''', str(tag_name))
    if exists:
        await conn.execute('''DELETE FROM tag_event WHERE tag_id = (
                                  SELECT id FROM tags WHERE name = $1
                              );''', str(tag_name))
        await conn.execute('''DELETE FROM tags WHERE name = $1;
                           ''', str(tag_name))
    await conn.close()


async def create_tag_event(event_id, tag_name):
    conn = await connection_init()
    tag_id = await conn.fetchval('''SELECT id
                                    FROM tags
                                    WHERE name = $1;
                                 ''', str(tag_name))

    exists = await conn.fetchval('''SELECT COUNT(*)
                                    FROM tag_event
                                    WHERE event_id = $1 AND tag_id = $2;
                                 ''', int(event_id), int(tag_id))
    if not exists:
        await conn.execute('''INSERT INTO tag_event (event_id, tag_id) VALUES ($1, $2);
                           ''', int(event_id), int(tag_id))
    await conn.close()


async def get_tags_data():
    conn = await connection_init()
    tag_names = await conn.fetch('''SELECT name FROM tags ORDER BY name;''')
    await conn.close()
    return tag_names


async def add_general_event(title, description, start_time):
    conn = await connection_init()
    await conn.execute('''INSERT INTO general_events (title, description, starts_at, added_at) VALUES($1, $2, $3, $4)
                       ''', str(title), str(description), start_time, datetime.now() + time_zone)
    event_id = await conn.fetchval('''SELECT MAX(id) FROM general_events;''')
    await conn.close()
    return event_id


async def get_event_data(event_id):
    conn = await connection_init()
    event_data = await conn.fetchrow('''SELECT * FROM general_events WHERE id = $1;''', int(event_id))
    await conn.close()
    return event_data


async def get_events_data():
    conn = await connection_init()
    event_data = await conn.fetch('''SELECT * FROM general_events ORDER BY starts_at;''')
    await conn.close()
    return event_data


async def get_web_id(chat_id):
    conn = await connection_init()
    web_id = await conn.fetchval('''SELECT website_id FROM users WHERE tg_chat_id = $1;
                                 ''', int(chat_id))
    await conn.close()
    return web_id


async def get_users_data():
    conn = await connection_init()
    users_data = await conn.fetch('''SELECT * FROM users;''')
    await conn.close()
    return users_data


async def add_user(name, role, chat_id, website_id=None):
    conn = await connection_init()
    await conn.execute('''INSERT INTO users (name, role, tg_chat_id, website_id) VALUES($1, $2, $3, $4);
                       ''', str(name), int(role), int(chat_id), int(website_id) if website_id else None)
    await conn.close()


async def get_name(chat_id):
    conn = await connection_init()
    name = await conn.fetchval('''SELECT name
                                  FROM users
                                  WHERE tg_chat_id = $1;
                               ''', int(chat_id))
    await conn.close()
    return str(name)


async def find_user(chat_id):
    conn = await connection_init()
    user_found = await conn.fetchval('''SELECT COUNT(*)
                                        FROM users
                                        WHERE tg_chat_id = $1;
                                     ''', int(chat_id))
    await conn.close()
    return user_found == 1


async def has_main_access(chat_id):
    conn = await connection_init()
    has_access = await conn.fetchval('''SELECT COUNT(*)
                                        FROM users
                                        WHERE role = 2 AND tg_chat_id = $1;
                                     ''', int(chat_id))
    await conn.close()
    return has_access == 1


async def has_admin_access(chat_id):
    conn = await connection_init()
    has_access = await conn.fetchval('''SELECT COUNT(*)
                                        FROM users
                                        WHERE role > 0 AND tg_chat_id = $1;
                                     ''', int(chat_id))
    await conn.close()
    return has_access == 1


async def set_role(role, chat_id):
    conn = await connection_init()
    await conn.execute('''UPDATE users
                          SET role = $1
                          WHERE tg_chat_id = $2;
                       ''', int(role), int(chat_id))
    await conn.close()


async def delete_user(chat_id):
    conn = await connection_init()
    await conn.execute('''DELETE FROM users WHERE tg_chat_id = $1;
                       ''', int(chat_id))
    await conn.close()


async def delete_all_events():
    conn = await connection_init()
    await conn.execute('''TRUNCATE TABLE tag_event, general_events;''')
    await conn.close()
