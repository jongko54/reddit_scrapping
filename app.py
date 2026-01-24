import streamlit as st
import feedparser
import time
from datetime import datetime
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

# ==================================================
# FastAPI (API 전용)
# ==================================================
api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/api/rss")
def get_filtered_rss(
    keyword: str = "bts",
    strict: bool = True,
    limit: int = 5
):
    search_query = f'"{keyword}"'
    encoded_query = urllib.parse.quote(search_query)
    rss_url = f"https://www.reddit.com/search.rss?q={encoded_query}&sort=new"

    feed = feedparser.parse(rss_url)

    results = []
    target = keyword.lower()

    for entry in feed.entries:
        title = entry.title.lower()
        content = ""

        if 'summary' in entry:
            content = entry.summary.lower()
        elif 'content' in entry:
            content = entry.content[0].value.lower()

        if strict:
            if target not in title and target not in content:
                continue

        results.append({
            "title": entry.title,
            "summary": entry.get("summary", ""),
            "link": entry.link,
            "published": entry.get("published", "")
        })

        if len(results) >= limit:
            break

    return {
        "keyword": keyword,
        "strict_mode": strict,
        "count": len(results),
        "items": results
    }

# FastAPI 서버 병렬 실행
def run_api():
    uvicorn.run(api, host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

# ==================================================
# Streamlit UI (기존 코드 거의 그대로)
# ==================================================
st.set_page_config(page_title="Reddit 정밀 검색기", page_icon="🎯")
st.title("🎯 Reddit 정밀 검색기 (RSS)")
st.markdown("RSS에서 가져온 결과 중, **키워드가 정확히 포함된 글**만 골라냅니다.")

# 초기 상태
if 'keyword' not in st.session_state:
    st.session_state['keyword'] = "bts"

if 'is_running' not in st.session_state:
    st.session_state['is_running'] = True

# 사이드바
st.sidebar.header("설정")
keyword = st.sidebar.text_input("감시할 키워드", value=st.session_state['keyword'])
interval_min = st.sidebar.number_input("자동 검색 주기 (분)", min_value=1, value=30, step=1)
use_strict_mode = st.sidebar.checkbox("정밀 필터 적용 (추천)", value=True)

if st.sidebar.button("▶️ 모니터링 시작"):
    st.session_state['is_running'] = True
    st.rerun()

if st.sidebar.button("⏹️ 중지"):
    st.session_state['is_running'] = False
    st.rerun()

status_area = st.empty()
result_area = st.empty()

if st.session_state['is_running'] and keyword:
    while True:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status_area.info(f"🔄 [{now_str}] '{keyword}' 검색 중...")

        try:
            encoded_query = urllib.parse.quote(f'"{keyword}"')
            rss_url = f"https://www.reddit.com/search.rss?q={encoded_query}&sort=new"
            feed = feedparser.parse(rss_url)

            filtered_entries = []
            target = keyword.lower()

            for entry in feed.entries:
                title = entry.title.lower()
                content = entry.get("summary", "").lower()

                if use_strict_mode:
                    if target not in title and target not in content:
                        continue

                filtered_entries.append(entry)

            with result_area.container():
                st.subheader(f"🎯 '{keyword}' 검색 결과")

                if not filtered_entries:
                    st.warning("결과 없음")
                else:
                    st.success(f"{len(filtered_entries)}개 발견")

                    for entry in filtered_entries[:50]:
                        with st.expander(entry.title):
                            st.write(entry.get("published", ""))
                            st.markdown(entry.get("summary", ""), unsafe_allow_html=True)
                            st.write(f"[원문 보기]({entry.link})")

        except Exception as e:
            st.error(str(e))

        status_area.success(f"✅ 완료! {interval_min}분 후 재검색")
        time.sleep(interval_min * 60)
        st.rerun()
