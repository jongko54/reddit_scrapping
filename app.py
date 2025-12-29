import streamlit as st
import feedparser
import time
from datetime import datetime
import urllib.parse

# 페이지 기본 설정
st.set_page_config(page_title="Reddit 정밀 검색기", page_icon="🎯")

st.title("🎯 Reddit 정밀 검색기 (RSS)")
st.markdown("RSS에서 가져온 결과 중, **키워드가 정확히 포함된 글**만 골라냅니다.")

# ---------------------------------------------------------
# 1. 사이드바 설정
# ---------------------------------------------------------
st.sidebar.header("설정")
keyword = st.sidebar.text_input("감시할 키워드", placeholder="예: Python")
interval_min = st.sidebar.number_input("자동 검색 주기 (분)", min_value=1, value=30, step=1)
use_strict_mode = st.sidebar.checkbox("정밀 필터 적용 (추천)", value=True)

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
        status_area.info(f"🔄 **[{now_str}]** '{keyword}' 검색 및 필터링 중...")

        try:
            # 1. RSS 주소 생성 (따옴표를 넣어 정확도 향상 시도)
            # 예: "Python" 처럼 검색하게 만듦
            search_query = f'"{keyword}"'
            encoded_query = urllib.parse.quote(search_query)

            # sort=new: 최신순
            rss_url = f"https://www.reddit.com/search.rss?q={encoded_query}&sort=new"

            # 2. 데이터 가져오기
            feed = feedparser.parse(rss_url)

            # 3. [핵심] 파이썬으로 2차 필터링 (엄격한 검사)
            filtered_entries = []

            for entry in feed.entries:
                title = entry.title.lower()
                # RSS는 content가 리스트 형태거나 없을 수 있음
                content = ""
                if 'summary' in entry:
                    content = entry.summary.lower()
                elif 'content' in entry:
                    content = entry.content[0].value.lower()

                target = keyword.lower()

                # 사용자가 정밀 필터를 켰다면?
                if use_strict_mode:
                    # 제목이나 본문에 키워드가 확실히 있어야만 통과!
                    if target in title or target in content:
                        filtered_entries.append(entry)
                else:
                    filtered_entries.append(entry)

            # 4. 결과 출력
            with result_area.container():
                st.subheader(f"🎯 '{keyword}' 정밀 검색 결과")

                if len(filtered_entries) == 0:
                    st.warning("검색 결과가 없거나, 필터링되어 제외되었습니다.")
                else:
                    st.success(f"정확한 결과 {len(filtered_entries)}개를 찾았습니다!")

                    for entry in filtered_entries[:10]:  # 10개만 표시
                        published_time = entry.get('published', '날짜 정보 없음')

                        with st.expander(f"{entry.title}"):
                            st.write(f"**작성일:** {published_time}")
                            st.write(f"**링크:** {entry.link}")
                            # 본문 미리보기 (HTML 태그 제거는 복잡해서 생략, RSS 기본 제공)
                            st.markdown(entry.get('summary', '')[:200], unsafe_allow_html=True)
                            st.write(f"[원문 보러가기]({entry.link})")

        except Exception as e:
            st.error(f"에러 발생: {e}")

        # 5. 대기 로직
        status_area.success(f"✅ 완료! {interval_min}분 뒤에 다시 검색합니다.")

        progress_bar = status_area.progress(0)
        total_seconds = interval_min * 60

        for i in range(100):
            time.sleep(total_seconds / 100)
            progress_bar.progress(i + 1)

        progress_bar.empty()

elif st.session_state['is_running'] and not keyword:
    st.warning("왼쪽 사이드바에서 키워드를 입력해주세요!")
else:
    status_area.info("👈 키워드를 입력하고 [시작] 버튼을 눌러주세요.")