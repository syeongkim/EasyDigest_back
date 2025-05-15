import requests
from bs4 import BeautifulSoup

def crawl_news_content(url: str) -> str:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 사이트 구조에 따라 수정 필요
        content = soup.select_one('#newsct_article')
        if content:
            return content.get_text(strip=True)
        return "본문을 찾을 수 없습니다."
    except Exception as e:
        return f"크롤링 실패: {str(e)}"