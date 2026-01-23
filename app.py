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
# 1. 초기 상태 설정 (수정된 부분)
# ---------------------------------------------------------
# 앱이 처음 실행될 때 bts를 기본값으로 검색 시작하게 설정
if 'keyword' not in st.session_state:
    st.session_state['keyword'] = "bts"

if 'is_running' not in st.session_state:
    st.session_state['is_running'] = True  # 처음부터 실행 상태로 변경

# ---------------------------------------------------------
# 2. 사이드바 설정
# ---------------------------------------------------------
st.sidebar.header("설정")
# value값에 session_state를 연결하여 초기값 유지
keyword = st.sidebar.text_input("감시할 키워드", value=st.session_state['keyword'])
interval_min = st.sidebar.number_input("자동 검색 주기 (분)", min_value=1, value=30, step=1)
use_strict_mode = st.sidebar.checkbox("정밀 필터 적용 (추천)", value=True)

if st.sidebar.button("▶️ 모니터링 시작"):
    st.session_state['is_running'] = True
    st.rerun()

if st.sidebar.button("⏹️ 중지"):
    st.session_state['is_running'] = False
    st.rerun()

# ---------------------------------------------------------
# 3. 메인 로직
# ---------------------------------------------------------
status_area = st.empty()
result_area = st.empty()

# 실행 조건 확인
if st.session_state['is_running'] and keyword:
    # 루프 진입
    while True:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status_area.info(f"🔄 **[{now_str}]** '{keyword}' 검색 및 필터링 중...")

        try:
            # RSS 주소 생성
            search_query = f'"{keyword}"'
            encoded_query = urllib.parse.quote(search_query)
            rss_url = f"https://www.reddit.com/search.rss?q={encoded_query}&sort=new"

            # 데이터 가져오기 (User-Agent를 추가하면 Reddit 차단을 방지하기 더 좋습니다)
            feed = feedparser.parse(rss_url)

            filtered_entries = []
            for entry in feed.entries:
                title = entry.title.lower()
                content = ""
                if 'summary' in entry:
                    content = entry.summary.lower()
                elif 'content' in entry:
                    content = entry.content[0].value.lower()

                target = keyword.lower()

                if use_strict_mode:
                    if target in title or target in content:
                        filtered_entries.append(entry)
                else:
                    filtered_entries.append(entry)

            # 결과 출력
            with result_area.container():
                st.subheader(f"🎯 '{keyword}' 정밀 검색 결과")

                if len(filtered_entries) == 0:
                    st.warning("검색 결과가 없거나, 필터링되어 제외되었습니다.")
                else:
                    st.success(f"정확한 결과 {len(filtered_entries)}개를 찾았습니다!")

                    for entry in filtered_entries[:100]:
                        published_time = entry.get('published', '날짜 정보 없음')
                        with st.expander(f"{entry.title}"):
                            st.write(f"**작성일:** {published_time}")
                            st.write(f"**링크:** {entry.link}")
                            st.markdown(entry.get('summary', '')[:500], unsafe_allow_html=True)
                            st.write(f"[원문 보러가기]({entry.link})")

        except Exception as e:
            st.error(f"에러 발생: {e}")

        # 대기 로직
        status_area.success(f"✅ 완료! {interval_min}분 뒤에 다시 검색합니다.")
        progress_bar = status_area.progress(0)
        total_seconds = interval_min * 60

        for i in range(100):
            # 중지 버튼을 누르면 루프를 빠져나가기 위한 장치
            if not st.session_state['is_running']:
                break
            time.sleep(total_seconds / 100)
            progress_bar.progress(i + 1)
        
        # 중지 시 루프 탈출
        if not st.session_state['is_running']:
            break
            
        progress_bar.empty()
        st.rerun() # 다음 주기를 위해 다시 시작

elif st.session_state['is_running'] and not keyword:
    st.warning("왼쪽 사이드바에서 키워드를 입력해주세요!")
else:
    status_area.info("👈 키워드를 입력하고 [시작] 버튼을 눌러주세요.")
