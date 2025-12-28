# executor.py
import MetaTrader5 as mt5
import config

def place_order(symbol, signal, lot, sl_dist_points, tp_dist_points):
    if mt5.positions_total() > 0: return 

    tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)
    if not tick or not symbol_info: return

    price = tick.ask if signal == "BUY" else tick.bid
    sl = price - (sl_dist_points) if signal == "BUY" else price + (sl_dist_points)
    tp = price + (tp_dist_points) if signal == "BUY" else price - (tp_dist_points)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot),
        "type": mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": float(price),
        "sl": round(float(sl), symbol_info.digits),
        "tp": round(float(tp), symbol_info.digits),
        "magic": 999,
        "comment": "SuperBot_V2",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    res = mt5.order_send(request)
    if res.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"✅ {signal} Order Placed: {lot} Lots")
    else:
        print(f"❌ Order Error: {res.comment}")

def manage_trailing_stop(symbol):
    if not config.TRAILING_ENABLE: return
    positions = mt5.positions_get(symbol=symbol)
    if not positions: return
    
    tick = mt5.symbol_info_tick(symbol)
    point = mt5.symbol_info(symbol).point

    for pos in positions:
        pnt_profit = (tick.bid - pos.price_open)/point if pos.type == 0 else (pos.price_open - tick.ask)/point
        
        if pnt_profit > config.TRAILING_START_PROFIT:
            new_sl = 0
            if pos.type == 0: # BUY
                target = tick.bid - (config.TRAILING_STEP * point)
                if target > pos.sl: new_sl = target
            else: # SELL
                target = tick.ask + (config.TRAILING_STEP * point)
                if target < pos.sl or pos.sl == 0: new_sl = target

            if new_sl > 0 and new_sl != pos.sl:
                req = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "sl": round(new_sl, mt5.symbol_info(symbol).digits),
                    "tp": pos.tp
                }
                mt5.order_send(req)