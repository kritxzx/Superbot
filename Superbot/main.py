# main.py
import MetaTrader5 as mt5
import time, json
import config, data_manager, brain, strategies, executor, risk_manager, external_data

def update_bot_status(data):
    with open("bot_status.json", "w") as f:
        json.dump(data, f)

def main():
    print("🚀 SuperBot V2.0 - Institutional Grade Started")
    if not data_manager.initialize_mt5(): return

    while True:
        try:
            df_h1 = data_manager.get_market_data(config.SYMBOL_MAIN, config.TIMEFRAME_MACRO)
            df_ref = data_manager.get_market_data(config.SYMBOL_REF, config.TIMEFRAME_MACRO)
            df_m5 = data_manager.get_market_data(config.SYMBOL_MAIN, config.TIMEFRAME_MICRO)

            if all(df is not None for df in [df_h1, df_ref, df_m5]):
                er, vol_z = brain.analyze_regime(df_h1, df_ref)
                is_news = external_data.is_news_time()
                mode = strategies.select_mode(er, vol_z, is_news=False)
                
                # Update Status for Dashboard
                update_bot_status({
                    "mode": mode, "price": df_m5['close'].iloc[-1],
                    "corr": er, "vol": vol_z, # บอร์ดเดิมจะโชว์ ER ในช่อง Corr
                    "buy_limit": 0, "sell_limit": 0 
                })

                signal, sl_pts, tp_pts = None, 0, 0
                if mode == "MODE_HYBRID_HUNTER":
                    signal, sl_pts, tp_pts = strategies.run_hybrid_hunter(df_m5, df_h1)
                elif mode == "MODE_MOMENTUM_SNIPER":
                    signal, sl_pts, tp_pts = strategies.run_momentum_sniper(df_m5)
                elif mode == "MODE_SCALPING_GRID":
                    signal, sl_pts, tp_pts = strategies.run_scalping_grid_stoch(df_m5)

                if signal:
                    bal = mt5.account_info().balance
                    lot = risk_manager.calculate_dynamic_lot(bal, sl_pts) if config.USE_DYNAMIC_LOT else config.LOT_SIZE
                    executor.place_order(config.SYMBOL_MAIN, signal, lot, sl_pts, tp_pts)

            executor.manage_trailing_stop(config.SYMBOL_MAIN)
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()