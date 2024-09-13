import sqlite3, config
import alpaca_trade_api as tradeapi

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        class TEXT NOT NULL,
        exchange TEXT NOT NULL
    )
""")

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS asset_prices (
        id INTEGER PRIMARY KEY,
        asset_id INTEGER,
        date NOT NULL,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        FOREIGN KEY (asset_id)  REFERENCES assets (id)    
    )
""")

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS trading_strategies (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
""")

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS asset_strategy (
        asset_id INTEGER,
        strategy_id INTEGER NOT NULL,
        FOREIGN KEY (asset_id)  REFERENCES assets (id)
        FOREIGN KEY (strategy_id)  REFERENCES trading_strategies (id)     
    )
""") 

strategies = ['opening_range_breakout', 'opening_range_breakdown']

for strategy in strategies:
    cursor.execute("""
        INSERT INTO trading_strategies (name) VALUES (?)
""", (strategy,))

connection.commit()