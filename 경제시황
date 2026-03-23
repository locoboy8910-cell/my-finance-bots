import FinanceDataReader as fdr
import time
import requests
import schedule

# [설정]
TOKEN = "8762651451:AAEVxzq-EYFgjUYDZ4NbXCapuKiB-tvG9hc"
CHAT_ID = "7118209547"
TARGET = 'TSLA'  # 감시 종목

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    requests.get(url, params=params)

def check_market():
    try:
        # 최신 가격 데이터 가져오기
        df = fdr.DataReader(TARGET).iloc[-1]
        price = df['Close']
        msg = f"🔔 [실시간 가격 보고]\n{TARGET}: ${price:,.2f}"
        send_msg(msg)
    except Exception as e:
        print(f"⚠️ 오류 발생: {e}")

if __name__ == "__main__":
    check_market() # 시작하자마자 한 번 전송 (테스트용)
    # 3시간마다 보고
    schedule.every(3).hours.do(check_market)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
