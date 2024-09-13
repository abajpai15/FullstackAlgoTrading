from fastapi import FastAPI, Request, Form
import sqlite3, config
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta



app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    asset_filter = request.query_params.get('filter', False)
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    date_param = (datetime.today() - timedelta(hours=10)).strftime('%Y-%m-%d')
    date = (datetime.today() - timedelta(days=13)).strftime('%Y-%m-%d')

    if asset_filter == 'new_closing_highs':
        cursor.execute("""
            select * from (
                SELECT symbol, name, a.id, max(close), date
                FROM asset_prices ap JOIN assets a ON 
                ap.asset_id = a.id GROUP BY asset_id ORDER BY symbol
            ) AS subquery
            where date = ? 
        """, ('2024-06-06',))
    else:
        cursor.execute("""
            SELECT symbol, name FROM assets ORDER BY symbol LIMIT 50   
        """)

    rows = cursor.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "assets": rows})

@app.get("/asset/{symbol}")
def asset_price_info(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT * FROM trading_strategies
    """)

    strategies = cursor.fetchall()

    cursor.execute("""
        SELECT id, symbol, name, exchange FROM assets WHERE symbol = ?
    """, (symbol,))

    row = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM asset_prices WHERE asset_id = ? ORDER BY date DESC
    """, (row['id'],))
    prices = cursor.fetchall()

    return templates.TemplateResponse("asset_details.html", {"request": request, "asset": row, "bars":prices, "strategies": strategies })

@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), asset_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO asset_strategy (asset_id, strategy_id) VALUES (?, ?)
    """, (asset_id, strategy_id))

    connection.commit()
    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code = 303)

@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM trading_strategies
        WHERE id = ?
    """, (strategy_id))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, name
        FROM assets ts JOIN asset_strategy ast ON ts.id = ast.asset_id
        WHERE strategy_id = ?
    """, (strategy_id))

    assets = cursor.fetchall()
    print(assets)

    return templates.TemplateResponse("strategy.html", {"request": request, "assets": assets, "strategies": strategy })
