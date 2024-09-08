import sqlite3, config

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute(""" 
    DROP TABLE assets
""")

cursor.execute(""" 
    DROP TABLE asset_prices
""")

connection.commit()