# config.py
SYMBOL_MAIN = "XAUUSDm"
SYMBOL_REF  = "EURUSDm"

TIMEFRAME_MACRO = "H1"  
TIMEFRAME_MICRO = "M5"  

# --- ปรับค่าวิเคราะห์สภาวะตลาด (Adaptive Settings) ---
ER_THRESHOLD = 0.4          # Efficiency Ratio (0.6 ขึ้นไปคือเทรนด์แรง)
VOL_Z_THRESHOLD = 1.5       # Z-Score (2.0 ขึ้นไปคือผันผวนหลุดโลก)

LOT_SIZE = 0.01
USE_DYNAMIC_LOT = True      # ใช้ระบบคำนวณ Lot ตามความเสี่ยง 1%
RISK_PER_TRADE = 0.01       # 1% Risk

TRAILING_ENABLE = True
TRAILING_START_PROFIT = 300 # 250 points (2.5 USD)
TRAILING_STEP = 100         # 150 points