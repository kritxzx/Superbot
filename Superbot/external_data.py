# external_data.py
import datetime

def is_news_time():
    """
    คืนค่า True ถ้าเป็นช่วงตลาดอเมริกาเปิด (19:30 - 21:00)
    ซึ่งมักจะมีข่าวแรงๆ และความผันผวนสูง
    """
    now = datetime.datetime.now()
    h = now.hour
    m = now.minute
    
    # ตั้งเวลาช่วงอันตราย (ปรับได้ตามต้องการ)
    if (h == 19 and m >= 30) or (h == 20):
        return True
        
    return False