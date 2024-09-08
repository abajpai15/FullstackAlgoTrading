import sqlite3, config
import alpaca_trade_api as tradeapi

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT symbol, name FROM assets    
""")

rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)
assets = api.list_assets()

# cursor.execute("""
#     DELETE FROM stock WHERE id > 11000;   
# """)
for asset in assets:
    if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
        print(f"Added a new asset {asset.symbol} {asset.name} {getattr(asset, 'class', None)}")
        cursor.execute("INSERT INTO assets (symbol, name, class, exchange) VALUES (?, ?, ?, ?)", (asset.symbol, asset.name, getattr(asset, 'class', None), asset.exchange))
    # if asset.status == 'active' and asset.tradable and asset.exchange == 'NASDAQ':
    #     print(asset)
    #     i = i+1
# and getattr(asset, 'class', None) == 'us_equity'
connection.commit()