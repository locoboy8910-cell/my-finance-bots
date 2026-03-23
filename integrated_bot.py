import FinanceDataReader as fdr
import requests
import time
import schedule
from bs4 import BeautifulSoup
from datetime import datetime

# [설정] 본인의 정보를 확인하세요
CHAT_ID = "7118209547"
TOKEN_FINANCE = "8057933847:AAH6NtEwgsfWO5-Cg785dqDVSSMM2Lgitp8" # 지표/뉴스용
TOKEN_MARKET = "8762651451:AAEVxzq-EYFgjUYDZ4NbXCapuKiB-tvG9hc"  # 시황/경제일정용

def send_tg(token, msg):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

# 1. 금융 지표 보고 (3시간마다)
def report_finance():
    try:
        usd = fdr.DataReader('USD/KRW').iloc[-1]['Close']
        tsla = fdr.DataReader('TSLA').iloc[-1]['Close']
        msg = f"⏰ [금융 지표 요약]\n달러/원: {usd:,.2f}원\n테슬라(TSLA): ${tsla:,.2f}"
        send_tg(TOKEN_FINANCE, msg)
    except: pass

# 2. 테슬라 실시간 가격 감시 (3시간마다)
def check_price():
    try:
        tsla = fdr.DataReader('TSLA').iloc[-1]['Close']
        send_tg(TOKEN_MARKET, f"🔔 [현재가 보고] TSLA: ${tsla:,.2f}")
    except: pass

# 3. 트럼프 뉴스 감시 (실시간)
last_news = ""
def check_trump():
    global last_news
    try:
        res = requests.get("https://search.naver.com/search.naver?where=news&query=트럼프&sort=1", timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        news_item = soup.select_one('a.news_tit')
        if news_item:
            title = news_item.text
            if title != last_news:
                send_tg(TOKEN_FINANCE, f"🚨 [트럼프 속보]\n{title}")
                last_news = title
    except: pass

# 4. 미국 경제 지표 일정 (매일 아침 8시)
def get_economic_calendar():
    try:
        # 인베스팅닷컴 한국어 페이지 활용
        url = "https://ko.investing.com/economic-calendar/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        rows = soup.select('tr.eventRow')
        report = f"📅 [오늘의 주요 미국 경제 일정]\n(발표 시간은 현지 사정에 따라 다를 수 있음)\n"
        count = 0
        
        for row in rows:
            # 중요도(별) 확인 - 별 2개 이상만 필터링 (선택사항)
            bulls = len(row.select('.grayFullBullishIcon'))
            if bulls >= 2: # 중요도 높은 것만
                time_str = row.select_one('.time').text.strip()
                event_name = row.select_one('.event').text.strip()
                report += f"⏱ {time_str} | {event_name}\n"
                count += 1
            if count >= 7: break # 너무 많으면 상위 7개만
            
        if count == 0: report += "오늘 예정된 중요 지표가 없습니다."
        send_tg(TOKEN_MARKET, report)
    except:
        send_tg(TOKEN_MARKET, "⚠️ 경제 지표 일정을 가져오는 데 일시적인 오류가 발생했습니다.")

if __name__ == "__main__":
    # 시작 시 확인용 발송
    report_finance()
    get_economic_calendar()
    
    # 스케줄 설정
    schedule.every(3).hours.do(report_finance)
    schedule.every(3).hours.do(check_price)
    schedule.every().day.at("08:00").do(get_economic_calendar) # 매일 아침 8시 지표 브리핑
    
    print("🚀 모든 비서 가동 시작! (경제 지표 기능 추가)")
    
    while True:
        schedule.run_pending()
        check_trump()
        time.sleep(60)
