import FinanceDataReader as fdr
import requests
import time
import schedule
from bs4 import BeautifulSoup
import os
import threading
import http.server
import socketserver

# [1. Render 체크용 가짜 서버]
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=run_dummy_server, daemon=True).start()

# [2. 설정]
CHAT_ID = "7118209547"
TOKEN_FINANCE = "8057933847:AAH6NtEwgsfWO5-Cg785dqDVSSMM2Lgitp8"

def send_tg(msg):
    url = f"https://api.telegram.org/bot{TOKEN_FINANCE}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

# [3. 종합 금융 보고서 전용 함수 (이것만 실행됨)]
def report_all_in_one():
    print("📊 종합 보고서 수집 시작...")
    try:
        # 하나라도 실패하면 에러 메시지를 띄우도록 함
        usd = fdr.DataReader('USD/KRW').iloc[-1]['Close']
        ks = fdr.DataReader('KS11').iloc[-1]['Close']
        kd = fdr.DataReader('KQ11').iloc[-1]['Close']
        nq = fdr.DataReader('IXIC').iloc[-1]['Close']
        sp = fdr.DataReader('S&P500').iloc[-1]['Close']
        btc = fdr.DataReader('BTC/USD').iloc[-1]['Close']
        eth = fdr.DataReader('ETH/USD').iloc[-1]['Close']
        tsla = fdr.DataReader('TSLA').iloc[-1]['Close']

        report = (
            f"✅ [통합 금융 지표 브리핑]\n"
            f"━━━━━━━━━━━━\n"
            f"💵 환율: {usd:,.2f}원\n\n"
            f"🇰🇷 국내: 코스피 {ks:,.2f} / 코스닥 {kd:,.2f}\n"
            f"🇺🇸 미국: 나스닥 {nq:,.2f} / S&P500 {sp:,.2f}\n\n"
            f"₿ 코인: BTC ${btc:,.2f} / ETH ${eth:,.2f}\n"
            f"🚗 주식: 테슬라 ${tsla:,.2f}\n"
            f"━━━━━━━━━━━━"
        )
        send_tg(report)
        print("✅ 보고서 발송 완료")
    except Exception as e:
        send_tg(f"⚠️ 지표 수집 중 오류 발생: {e}")

# [4. 트럼프 뉴스]
last_news = ""
def check_trump():
    global last_news
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://search.naver.com/search.naver?where=news&query=트럼프&sort=1", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        news_item = soup.select_one('a.news_tit')
        if news_item and news_item.text != last_news:
            send_tg(f"🚨 [트럼프 속보]\n{news_item.text}")
            last_news = news_item.text
    except: pass

if __name__ == "__main__":
    # 시작하자마자 종합 보고서 한 번 쏘기!
    report_all_in_one()
    
    # 2시간마다 종합 보고서
    schedule.every(2).hours.do(report_all_in_one)
    
    while True:
        schedule.run_pending()
        check_trump()
        time.sleep(60)
