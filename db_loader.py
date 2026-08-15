import json
import psycopg2
from datetime import datetime

# Connect to your local PostgreSQL instance
conn = psycopg2.connect(dbname="Youtube_Analytics", user="postgres", password="Tiku@pgsql1020", host="localhost")
cur = conn.cursor()

with open('raw_transactions.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

for event in events:
    author_name = event.get('author')
    user_id = author_name 
    
    date_str = event.get('datetime')
    try:
        event_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        continue 
    
    event_type = event.get('type')
    amount = event.get('amount', 0.0)
    currency = event.get('currency', 'NONE')
    msg_id = f"{user_id}_{date_str}"

    cur.execute("""
        INSERT INTO users (user_id, author_name) 
        VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING;
    """, (user_id, author_name))

    cur.execute("""
        INSERT INTO transactions (transaction_id, user_id, event_time, amount, currency, event_type)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (transaction_id) DO NOTHING;
    """, (msg_id, user_id, event_time, amount, currency, event_type))

conn.commit()
cur.close()
conn.close()