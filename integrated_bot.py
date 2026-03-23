import FinanceDataReader as fdr
import requests
import time
import schedule
from bs4 import BeautifulSoup
import http.server
import socketserver
import threading
import os

# [1. Render 포트 체크 통과를 위한 가짜 서버]
def run_dummy_server():
    port = int(os.environ.get("PORT", 80))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"✅ 가짜 서버가 {port}번 포트에서 작동 중입니다.")
        httpd.serve_forever()

# 배경에서 가짜 서버 실행
threading.Thread(target=run_dummy_server, daemon=True).start()

# [2. 설정]
CHAT_ID = "7118209547"
TOKEN_FINANCE = "8057933847:AAH6NtEwgsfWO5-Cg785dqDVSSMM2Lgitp8"

def send_tg(token, msg):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

# [3. 종합 금융 지표 보고]
def report_finance_expanded():
    try:
        usd_krw = fdr.DataReader('USD/KRW').iloc[-1]['Close']
        kospi = fdr.DataReader('KS11').iloc[-1]['Close']
        kosdaq = fdr.DataReader('KQ11').iloc[-1]['Close']
        nasdaq = fdr.DataReader('IXIC').iloc[-1]['Close']
        sp500 = fdr.DataReader('S&P500').iloc[-1]['Close']
        btc = fdr.DataReader('BTC/USD').iloc[-1]['Close']
        eth = fdr.DataReader('ETH/USD').iloc[-1]['Close']
        tsla = fdr.DataReader('TSLA').iloc[-1]['Close']

        msg = (
            f"⏰ [종합 금융 지표 보고]\n"
            f"━━━━━━━━━━━━\n"
            f"💵 환율: {usd_krw:,.2f}원\n\n"
            f"🇰🇷 국내 증시\n"
            f"- 코스피: {kospi:,.2f}\n"
            f"- 코스닥: {kosdaq:,.2f}\n\n"
            f"🇺🇸 미국 증시\n"
            f"- 나스닥: {nasdaq:,.2f}\n"
            f"- S&P500: {sp500:,.2f}\n\n"
            f"₿ 가상화폐\n"
            f"- 비트코인: ${btc:,.2f}\n"
            f"- 이더리움: ${eth:,.2f}\n\n"
            f"🚗 주요종목\n"
            f"- 테슬라: ${tsla:,.2f}\n"
            f"━━━━━━━━━━━━"
        )
        send_tg(TOKEN_FINANCE, msg)
    except Exception as e:
        print(f"지표 수집 오류: {e}")

# [4. 트럼프 뉴스 감시]
last_news = ""
def check_trump():
    global last_news
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://search.naver.com/search.naver?where=news&query=트럼프&sort=1", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        news_item = soup.select_one('a.news_tit')
        if news_item:
            title = news_item.text
            if title != last_news:
                send_tg(TOKEN_FINANCE, f"🚨 [트럼프 속보]\n{title}")
                last_news = title
    except: pass

if __name__ == "__main__":
    report_finance_expanded()
    schedule.every(2).hours.do(report_finance_expanded)
    
    print("🚀 모든 비서 가동 시작!")
    
    while True:
        schedule.run_pending()
        check_trump()
        time.sleep(60)
