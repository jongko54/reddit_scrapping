import streamlit as st
import praw
from datetime import datetime
import time

# 페이지 기본 설정
st.set_page_config(page_title="Reddit 자동 감시기", page_icon="🕵️")

st.title("🕵️ Reddit 30분 자동 검색기")
st.markdown("키워드를 입력하고 **'모니터링 시작'**을 누르면, **30분마다** 자동으로 새 글을 찾아 화면을 갱신합니다.")

# ---------------------------------------------------------
# 1. API 설정 (Streamlit Secrets)
# ---------------------------------------------------------
try:
    CLIENT_ID = st.secrets["reddit"]["client_id"]
    CLIENT_SECRET = st.secrets["reddit"]["client_secret"]
    USER_AGENT = st.secrets["reddit"]["user_agent"]
except:
    st.error("🚨 API 키 설정이 필요합니다! Streamlit Secrets를 확인해주세요.")
    st.stop()

# ---------------------------------------------------------
# 2. 사이드바 설정 (검색어 및 주기)
# ---------------------------------------------------------
st.sidebar.header("설정")
keyword = st.sidebar.text_input("감시할 키워드", placeholder="예: Python, Samsung")
interval_min = st.sidebar.number_input("검색 주기 (분)", min_value=1, value=30, step=1)

# 상태 저장 (모니터링 중인지 아닌지)
if 'is_running' not in st.session_state:
    st.session_state['is_running'] = False

# 버튼 클릭 시 상태 변경
if st.sidebar.button("▶️ 모니터링 시작"):
    st.session_state['is_running'] = True
    st.rerun()  # 화면 새로고침하여 상태 반영

if st.sidebar.button("⏹️ 중지"):
    st.session_state['is_running'] = False
    st.rerun()

# ---------------------------------------------------------
# 3. 메인 로직 (반복 실행)
# ---------------------------------------------------------
# 결과를 보여줄 빈 공간(컨테이너) 미리 확보
status_area = st.empty()
result_area = st.empty()

if st.session_state['is_running'] and keyword:

    # Reddit 연결 인스턴스 생성
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    # 무한 반복 (브라우저가 켜져 있는 동안)
    while True:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 1. 상태 메시지 업데이트
        with status_area.container():
            st.info(f"🔄 **[{now_str}]** 검색 실행 중... (주기: {interval_min}분)")

        # 2. 검색 수행
        try:
            # 전체(all)에서 최신순(new)으로 20개 가져오기
            search_results = reddit.subreddit("all").search(f"{keyword}", sort="new", limit=20)

            # 결과 화면 갱신
            with result_area.container():
                st.subheader(f"📡 '{keyword}' 검색 결과")
                count = 0
                for post in search_results:
                    count += 1
                    # 시간 변환
                    dt_object = datetime.fromtimestamp(post.created_utc)
                    time_str = dt_object.strftime('%Y-%m-%d %H:%M:%S')

                    with st.expander(f"[{time_str}] r/{post.subreddit} : {post.title}"):
                        st.write(f"**링크:** https://www.reddit.com{post.permalink}")
                        if post.selftext:
                            st.text(post.selftext[:100] + "...")

                if count == 0:
                    st.warning("발견된 최신 글이 없습니다.")
                else:
                    st.success(f"최신 글 {count}개를 가져왔습니다.")

        except Exception as e:
            st.error(f"에러 발생: {e}")

        # 3. 대기 (설정한 시간만큼 멈춤)
        # 30분 대기면 화면이 멈춘 것처럼 보일 수 있으니, 프로그래스 바를 보여줌
        with status_area.container():
            st.success(f"✅ 검색 완료! 다음 검색까지 대기 중... ({now_str} 기준)")

            # 진행률 바 표시 (시각적 효과)
            progress_text = "다음 검색 대기 중..."
            my_bar = st.progress(0, text=progress_text)

            total_seconds = interval_min * 60
            for i in range(100):
                time.sleep(total_seconds / 100)  # 쪼개서 대기
                my_bar.progress(i + 1, text=f"{progress_text} ({i + 1}%)")

            my_bar.empty()  # 바 지우고 다시 루프 시작

elif st.session_state['is_running'] and not keyword:
    st.warning("⚠️ 사이드바에서 키워드를 먼저 입력해주세요.")
else:
    status_area.info("👈 사이드바에서 키워드를 입력하고 [시작] 버튼을 눌러주세요.")