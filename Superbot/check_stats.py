import pandas as pd
import data_manager
import brain
import config
import numpy as np

print("📊 กำลังวิเคราะห์สถิติตลาด 1,000 แท่งล่าสุด...")

if data_manager.initialize_mt5():
    # 1. ดึงข้อมูลเยอะๆ (1000 แท่ง = ประมาณ 2 เดือนของ H1)
    df_gold = data_manager.get_market_data(config.SYMBOL_MAIN, "H1", n_bars=1000)
    df_ref  = data_manager.get_market_data(config.SYMBOL_REF, "H1", n_bars=1000)
    
    if df_gold is not None and df_ref is not None:
        # 2. คำนวณค่าต่างๆ แบบทั้งกระดาน
        # รวมตาราง
        data = pd.merge(df_gold, df_ref, on='time', suffixes=('_main', '_ref'))
        
        # คำนวณ Correlation (Rolling 30)
        data['corr'] = data['close_main'].rolling(window=30).corr(data['close_ref'])
        
        # คำนวณ Volatility (Rolling 30)
        data['pct'] = data['close_main'].pct_change()
        data['vol'] = data['pct'].rolling(window=30).std()
        
        # 3. สรุปผลทางสถิติ (ตัดค่า NaN ออก)
        corrs = data['corr'].dropna()
        vols = data['vol'].dropna()
        
        print("\n" + "="*40)
        print(f"📌 สถิติ {config.SYMBOL_MAIN} vs {config.SYMBOL_REF} (H1)")
        print("="*40)
        
        print(f"1️⃣ Correlation (ความสัมพันธ์):")
        print(f"   - เฉลี่ย (Mean):      {corrs.mean():.2f}")
        print(f"   - ต่ำสุด/สูงสุด:       {corrs.min():.2f} ถึง {corrs.max():.2f}")
        print(f"   - ค่า P75 (แข็งแกร่ง):  {np.percentile(corrs, 75):.2f}  <-- แนะนำค่านี้เป็น Threshold")
        
        print(f"\n2️⃣ Volatility (ความผันผวน):")
        print(f"   - เฉลี่ย (Mean):      {vols.mean():.5f}")
        print(f"   - ค่า P90 (เหวี่ยงจัด): {np.percentile(vols, 90):.5f}  <-- แนะนำค่านี้เป็น High Threshold")
        
        print("="*40)