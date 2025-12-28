# brain.py
import pandas as pd
import numpy as np

def analyze_regime(df_main, df_ref, window=20):
    if len(df_main) < 50: return 0, 0
    
    # 1. Efficiency Ratio (ER) - วัดความแรงเทรนด์ (0.0 - 1.0)
    direction = abs(df_main['close'].iloc[-1] - df_main['close'].iloc[-window])
    volatility = (df_main['close'].diff().abs()).rolling(window=window).sum().iloc[-1]
    er = direction / volatility if volatility != 0 else 0
    
    # 2. Volatility Z-Score - วัดความบ้าคลั่งของราคา
    returns = df_main['close'].pct_change()
    current_vol = returns.rolling(window=window).std()
    mean_vol = current_vol.rolling(window=100).mean()
    std_vol = current_vol.rolling(window=100).std()
    
    vol_z = (current_vol.iloc[-1] - mean_vol.iloc[-1]) / std_vol.iloc[-1] if std_vol.iloc[-1] != 0 else 0
    
    return er, vol_z