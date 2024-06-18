import psycopg2

conn = psycopg2.connect(
    "postgres://reward_db_6744_user:9JafL71tVDrsGmrjYa4hiRnHNhNWAoZW@dpg-cpoeicqj1k6c73a67klg-a.virginia-postgres.render.com/reward_db_6744"
)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE,
    points INTEGER DEFAULT 0
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id SERIAL PRIMARY KEY,
    description TEXT,
    points INTEGER
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS services (
    service_id SERIAL PRIMARY KEY,
    description TEXT,
    points_required INTEGER
);
''')

conn.commit()
cur.close()
conn.close()
