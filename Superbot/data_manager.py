import MetaTrader5 as mt5
import pandas as pd
import os

def initialize_mt5():
    # ระบุ Path ของ MT5 ให้ชัดเจนตามที่คุณเทสผ่าน
    mt5_path = r"C:\Program Files\MetaTrader 5\terminal64.exe" 
    
    if not os.path.exists(mt5_path):
        print(f"[ERROR] Path not found: {mt5_path}")
        return False

    try:
        # บังคับเชื่อมต่อผ่าน Path ที่กำหนด
        if not mt5.initialize(path=mt5_path):
            print(f"[ERROR] Connect failed. Code: {mt5.last_error()}")
            return False
            
        acc = mt5.account_info()
        if acc:
            print(f"[SUCCESS] Connected to Login: {acc.login}")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

def get_market_data(symbol, timeframe_str, n_bars=1000):
    tf_mapping = {
        "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1
    }
    
    if timeframe_str not in tf_mapping: return None
    
    # ตรวจสอบคู่เงิน
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None: return None
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    
    # ดึงข้อมูลแท่งเทียน
    rates = mt5.copy_rates_from_pos(symbol, tf_mapping[timeframe_str], 0, n_bars)
    if rates is None or len(rates) == 0: return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df[['time', 'open', 'high', 'low', 'close', 'tick_volume']]