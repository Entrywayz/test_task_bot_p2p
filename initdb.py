import sqlite3

def init_db():
    conn = sqlite3.connect('exchange.sqlite3')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        full_name TEXT
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS balances (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        currency TEXT,
                        amount REAL DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS support_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        message TEXT,
                        admin_id INTEGER,
                        response TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS p2p_orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        type TEXT,
                        currency TEXT,
                        amount REAL,
                        price REAL,
                        status TEXT DEFAULT 'active',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )''')
    
    conn.commit()
    conn.close()

