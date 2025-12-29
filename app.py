import streamlit as st
import feedparser
import time
from datetime import datetime
import urllib.parse

# 페이지 기본 설정
st.set_page_config(page_title="Reddit RSS 검색기", page_icon="⚡")

st.title("⚡ Reddit 검색기 (No-API 버전)")
st.markdown("Reddit API 키 없이, **RSS 피드**를 이용해 실시간 검색 결과를 보여줍니다.")

# ---------------------------------------------------------
# 1. 사이드바 설정
# ---------------------------------------------------------
st.sidebar.header("설정")
keyword = st.sidebar.text_input("감시할 키워드", placeholder="예: Python")
interval_min = st.sidebar.number_input("자동 검색 주기 (분)", min_value=1, value=30, step=1)

# 상태 저장
if 'is_running' not in st.session_state:
    st.session_state['is_running'] = False

if st.sidebar.button("▶️ 모니터링 시작"):
    st.session_state['is_running'] = True
    st.rerun()

if st.sidebar.button("⏹️ 중지"):
    st.session_state['is_running'] = False
    st.rerun()

# ---------------------------------------------------------
# 2. 메인 로직
# ---------------------------------------------------------
status_area = st.empty()
result_area = st.empty()

if st.session_state['is_running'] and keyword:

    while True:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 1. 상태 메시지
        status_area.info(f"🔄 **[{now_str}]** '{keyword}' 검색 중... (RSS 방식)")

        try:
            # 2. RSS 주소 생성 (API 키 없이 접근 가능!)
            # URL 인코딩 (한글/특수문자 처리)
            encoded_keyword = urllib.parse.quote(keyword)
            rss_url = f"https://www.reddit.com/search.rss?q={encoded_keyword}&sort=new"

            # 피드 읽기
            feed = feedparser.parse(rss_url)

            # 결과 출력
            with result_area.container():
                st.subheader(f"📡 '{keyword}' 검색 결과")

                if len(feed.entries) == 0:
                    st.warning("결과를 가져오지 못했습니다. (검색어가 없거나 차단됨)")
                else:
                    st.success(f"최신 글 {len(feed.entries)}개를 가져왔습니다.")

                    for entry in feed.entries[:10]:  # 최대 10개만 표시
                        # 날짜 정리
                        published_time = entry.get('published', '날짜 정보 없음')

                        with st.expander(f"{entry.title}"):
                            st.write(f"**작성일:** {published_time}")
                            st.write(f"**링크:** {entry.link}")
                            # RSS는 본문이 'summary'나 'content'에 들어있음
                            content = entry.get('summary', '')[:200]
                            st.markdown(content, unsafe_allow_html=True)
                            st.write(f"[원문 보러가기]({entry.link})")

        except Exception as e:
            st.error(f"에러 발생: {e}")

        # 3. 대기 로직 (Progress Bar)
        status_area.success(f"✅ 검색 완료! {interval_min}분 뒤에 다시 검색합니다.")

        progress_bar = status_area.progress(0)
        total_seconds = interval_min * 60

        # 100단계로 나눠서 진행바 채우기
        for i in range(100):
            time.sleep(total_seconds / 100)
            progress_bar.progress(i + 1)

        progress_bar.empty()

elif st.session_state['is_running'] and not keyword:
    st.warning("왼쪽 사이드바에서 키워드를 입력해주세요!")
else:
    status_area.info("👈 키워드를 입력하고 [시작] 버튼을 눌러주세요.")