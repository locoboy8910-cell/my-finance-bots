import FinanceDataReader as fdr
import requests
import time
import schedule
from bs4 import BeautifulSoup

# [설정]
CHAT_ID = "7118209547"
TOKEN_FINANCE = "8057933847:AAH6NtEwgsfWO5-Cg785dqDVSSMM2Lgitp8" # 모든 알림 통합용

def send_tg(token, msg):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

# 1. 종합 금융 지표 보고 (2시간마다)
def report_finance_expanded():
    try:
        # 데이터 수집 (지수 및 가격)
        usd_krw = fdr.DataReader('USD/KRW').iloc[-1]['Close'] # 환율
        kospi = fdr.DataReader('KS11').iloc[-1]['Close']      # 코스피
        kosdaq = fdr.DataReader('KQ11').iloc[-1]['Close']     # 코스닥
        nasdaq = fdr.DataReader('IXIC').iloc[-1]['Close']     # 나스닥
        sp500 = fdr.DataReader('S&P500').iloc[-1]['Close']    # S&P500
        btc = fdr.DataReader('BTC/USD').iloc[-1]['Close']     # 비트코인
        eth = fdr.DataReader('ETH/USD').iloc[-1]['Close']     # 이더리움
        tsla = fdr.DataReader('TSLA').iloc[-1]['Close']       # 테슬라

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

# 2. 트럼프 뉴스 감시 (실시간)
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
    # 시작 시 즉시 한 번 보고
    report_finance_expanded()
    
    # 2시간마다 금융 지표 보고 스케줄링
    schedule.every(2).hours.do(report_finance_expanded)
    
    print("🚀 금융 지표 & 트럼프 속보 비서 가동 시작!")
    
    while True:
        schedule.run_pending()
        check_trump() # 트럼프 뉴스는 1분마다 실시간 체크
        time.sleep(60)
