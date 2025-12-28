# strategies.py
import pandas as pd
import numpy as np
import config

def calculate_rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0); down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / (ema_down + 1e-10)
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]

def select_mode(er, vol_z, is_news):
    if is_news: return "MODE_WAIT_NEWS"
    if vol_z > config.VOL_Z_THRESHOLD: return "MODE_MOMENTUM_SNIPER"
    if er > config.ER_THRESHOLD: return "MODE_HYBRID_HUNTER"
    return "MODE_SCALPING_GRID"

def calculate_stochastic(df, k_period=14, d_period=3):
    """คำนวณ Stochastic Oscillator (%K, %D)"""
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    
    # คำนวณ %K
    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
    # คำนวณ %D (Moving Average ของ %K)
    stoch_d = stoch_k.rolling(window=d_period).mean()
    
    return stoch_k, stoch_d

def run_scalping_grid_stoch(df):
    """Mean Reversion: เข้าเมื่อหลุด Bollinger Bands + Stochastic Cross"""
    # Bollinger Bands (ปรับ SD เป็น 1.2 เพื่อความไวที่สมดุล)
    sma = df['close'].rolling(20).mean().iloc[-1]
    std = df['close'].rolling(20).std().iloc[-1]
    
    # Stochastic
    stoch_k, stoch_d = calculate_stochastic(df)
    k = stoch_k.iloc[-1]
    d = stoch_d.iloc[-1]
    
    atr = calculate_atr(df)
    last = df['close'].iloc[-1]
    
    # เงื่อนไข BUY: ราคาต่ำกว่าเส้นล่าง BB และ Stochastic %K ตัด %D ขึ้นในโซน Oversold (< 20)
    if last < (sma - 1.2*std) and k < 20 and k > d:
        return "BUY", atr * 2, atr * 1.5
        
    # เงื่อนไข SELL: ราคาสูงกว่าเส้นบน BB และ Stochastic %K ตัด %D ลงในโซน Overbought (> 80)
    if last > (sma + 1.2*std) and k > 80 and k < d:
        return "SELL", atr * 2, atr * 1.5
        
    return None, 0, 0

def run_hybrid_hunter(df_m5, df_h1):
    """Trend Following: ย่อซื้อ-เด้งขาย ตามเทรนด์ H1"""
    ema_h1 = df_h1['close'].ewm(span=50).mean().iloc[-1]
    trend_up = df_h1['close'].iloc[-1] > ema_h1
    rsi = calculate_rsi(df_m5['close']).iloc[-1]
    atr = calculate_atr(df_m5)

    if trend_up and rsi < 45: return "BUY", atr * 2.5, atr * 4
    if not trend_up and rsi > 55: return "SELL", atr * 2.5, atr * 4
    return None, 0, 0

def run_momentum_sniper(df):
    """Breakout: เล่นตามแรงเหวี่ยงเมื่อ Volatility สูง"""
    upper = df['high'].rolling(10).max().iloc[-2]
    lower = df['low'].rolling(10).min().iloc[-2]
    atr = calculate_atr(df)
    last = df['close'].iloc[-1]

    if last > upper: return "BUY", atr * 1.5, atr * 5
    if last < lower: return "SELL", atr * 1.5, atr * 5
    return None, 0, 0