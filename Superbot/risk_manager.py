# risk_manager.py
import config

def calculate_dynamic_lot(balance, sl_points):
    """คำนวณ Lot ให้เสียไม่เกิน 1% ของพอร์ต"""
    if balance <= 0 or sl_points <= 0: return 0.01
    
    risk_money = balance * config.RISK_PER_TRADE
    # ทอง 1 Lot, SL 100 points = $100
    lot = risk_money / (sl_points * 100)
    
    lot = round(max(0.01, min(lot, 1.0)), 2)
    return lot