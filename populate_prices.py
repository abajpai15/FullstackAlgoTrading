import config, sqlite3
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT DISTINCT symbol, name FROM assets WHERE class <> 'crypto' and exchange = 'NASDAQ'
""")

rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]

cursor.execute("""
    SELECT DISTINCT asset_id, date, open, high, low, close, volume FROM asset_prices 
""")

price_data = cursor.fetchall()
unique_asset = [price['asset_id'] for price in price_data]
unique_date = [price['date'] for price in price_data]


api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)

api_calls = 200
for i in range(0, len(symbols), api_calls):
    symbols_received = symbols[i:i+api_calls]
    # print(symbols_received)
    today_10hourdelay = (datetime.today() - timedelta(hours=10)).strftime('%Y-%m-%d')
    bars = api.get_bars_iter(symbols_received, TimeFrame(1, TimeFrameUnit.Day), "2024-07-08", today_10hourdelay, adjustment='raw')
    for bar in bars:
        print(f"processing symbol {bar.S}")
        # asset_id = asset_dict[bar.S]
        if bar.S not in unique_asset or bar.date() not in unique_date: #only doesnt insert if we've already seen that asset in for that date
            cursor.execute("""
                    INSERT INTO asset_prices (asset_id, date, open, high, low, close, volume)
                    VALUES ((SELECT id FROM assets WHERE symbol = ?), ?, ?, ?, ?, ?, ?)
            """, (bar.S, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))
            # print(bar.S, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v) 

connection.commit()
#minute by minute not really available unless polygon
# bars = api.get_bars_iter(["AAPL", "MSFT", "MSFT"], TimeFrame(1, TimeFrameUnit.Hour), "2021-06-08", "2021-06-08", adjustment='raw')
# # print(bars)
# for bar in bars:
#     print(f"processing symbol {bar}")
#     print(f"processing symbol {bar.S}")
#     print(bar.t, bar.o, bar.h, bar.l, bar.c, bar.v) 
