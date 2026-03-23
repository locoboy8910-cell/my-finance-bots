import FinanceDataReader as fdr
import requests
import time
import schedule
from bs4 import BeautifulSoup

# [공통 설정]
CHAT_ID = "7118209547"
TOKEN_FINANCE = "8057933847:AAH6NtEwgsfWO5-Cg785dqDVSSMM2Lgitp8" # 지표/트럼프용
TOKEN_MARKET = "8762651451:AAEVxzq-EYFgjUYDZ4NbXCapuKiB-tvG9hc" # 시황용

def send_tg(token, msg):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": msg})

# 1. 지표 보고
def report_finance():
    try:
        usd = fdr.DataReader('USD/KRW').iloc[-1]['Close']
        tsla = fdr.DataReader('TSLA').iloc[-1]['Close']
        msg = f"⏰ [금융 지표]\n달러/원: {usd:,.2f}원\nTSLA: ${tsla:,.2f}"
        send_tg(TOKEN_FINANCE, msg)
    except: pass

# 2. 실시간 가격 감시 (3번째 봇 역할)
def check_price():
    try:
        tsla = fdr.DataReader('TSLA').iloc[-1]['Close']
        send_tg(TOKEN_MARKET, f"🔔 [현재가 보고] TSLA: ${tsla:,.2f}")
    except: pass

# 3. 트럼프 뉴스 감시
last_news = ""
def check_trump():
    global last_news
    try:
        res = requests.get("https://search.naver.com/search.naver?where=news&query=트럼프&sort=1")
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.select_one('a.news_tit').text
        if title != last_news:
            send_tg(TOKEN_FINANCE, f"🚨 [속보] 트럼프: {title}")
            last_news = title
    except: pass

if __name__ == "__main__":
    report_finance() # 시작 시 한 번 전송
    schedule.every(3).hours.do(report_finance)
    schedule.every(3).hours.do(check_price)
    
    while True:
        schedule.run_pending()
        check_trump()
        time.sleep(60)
