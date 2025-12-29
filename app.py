import streamlit as st
import praw
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="Reddit 실시간 검색기", page_icon="🔍")

# 제목 및 설명
st.title("🔍 Reddit 키워드 검색기 (최신순)")
st.markdown("Reddit **전체**에서 키워드를 검색하고, **최신순(New)**으로 결과를 보여줍니다.")

# ---------------------------------------------------------
# 1. API 설정 (Streamlit Secrets에서 가져오기)
# ---------------------------------------------------------
try:
    CLIENT_ID = st.secrets["reddit"]["client_id"]
    CLIENT_SECRET = st.secrets["reddit"]["client_secret"]
    USER_AGENT = st.secrets["reddit"]["user_agent"]
except:
    st.error("🚨 API 키 설정이 필요합니다! Streamlit Secrets를 확인해주세요.")
    st.stop()

# ---------------------------------------------------------
# 2. 검색 인터페이스
# ---------------------------------------------------------
# 엔터 키를 쳐도 검색되게 하려면 st.form을 사용합니다.
with st.form(key='search_form'):
    col1, col2 = st.columns([4, 1])

    with col1:
        keyword = st.text_input("검색어를 입력하세요", placeholder="예: Python, Samsung, AI")
    with col2:
        # 폼 안의 버튼은 submit_button이어야 합니다.
        submit_btn = st.form_submit_button(label='검색')

# ---------------------------------------------------------
# 3. 검색 로직 실행
# ---------------------------------------------------------
if submit_btn and keyword:
    st.divider()
    st.subheader(f"Results for: '{keyword}'")

    try:
        # Reddit 연결
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT
        )

        # ✨ 핵심 로직: 전체(all)에서 검색하고, 최신순(new)으로 정렬
        # limit=30 : 결과 30개만 가져오기 (숫자 조절 가능)
        search_results = reddit.subreddit("all").search(f"{keyword}", sort="new", limit=30)

        count = 0

        # 결과 출력 반복문
        for post in search_results:
            count += 1

            # 날짜 변환 (유닉스 시간 -> 읽기 쉬운 시간)
            dt_object = datetime.fromtimestamp(post.created_utc)
            time_str = dt_object.strftime('%Y-%m-%d %H:%M:%S')

            # 디자인: Expander(접이식 상자) 사용
            # 제목에 게시판 이름(r/Python)과 제목 표시
            with st.expander(f"[{time_str}] r/{post.subreddit} : {post.title}"):

                # 내용이 있으면 보여주기
                if post.selftext:
                    st.info(post.selftext[:200] + "..." if len(post.selftext) > 200 else post.selftext)
                elif post.url:
                    # 이미지나 외부 링크인 경우
                    st.write(f"🔗 링크: {post.url}")

                st.markdown(f"""
                - **작성자:** {post.author}
                - **추천수:** {post.score}
                - **[Reddit에서 원본 보기](https://www.reddit.com{post.permalink})**
                """)

        if count == 0:
            st.warning("검색 결과가 없습니다. (오타가 있거나 너무 드문 키워드일 수 있습니다)")
        else:
            st.success(f"검색 완료! 최신 글 {count}개를 가져왔습니다.")

    except Exception as e:
        st.error(f"에러가 발생했습니다: {e}")

elif submit_btn and not keyword:
    st.warning("검색어를 입력해주세요!")