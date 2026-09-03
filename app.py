import streamlit as st
import json
import yt_dlp
from google import genai

# ==========================================
# 0. 비밀번호 인증 게이트 (보안 설정)
# ==========================================
DEFAULT_PASSWORD = "tjb"  # 원하는 비밀번호로 변경하세요

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 썸네일 브레인 접근 인증")
    entered_pw = st.text_input("비밀번호를 입력하세요:", type="password")
    
    if st.button("로그인"):
        if entered_pw == DEFAULT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 일치하지 않습니다.")
    return False

if not check_password():
    st.stop()

# ==========================================
# 1. 본 화면 (로그인 성공 시 표시)
# ==========================================
st.set_page_config(page_title="유튜브 썸네일 브레인", layout="wide")
st.title("🎯 유튜브 썸네일 2줄 카피 & 비주얼 생성기")
st.caption("EBS 다큐 & 포크포크의 알고리즘 후킹 문법 기반")

# 사이드바 API 키 설정 (또는 Streamlit Secrets에 저장 가능)
api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")

video_url = st.text_input("유튜브 영상 URL을 입력하세요:", placeholder="https://www.youtube.com/watch?v=...")

def extract_info(url):
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', ''), info.get('description', '')

if st.button("🚀 후킹 문구 및 비주얼 도출"):
    if not video_url:
        st.warning("유튜브 URL을 입력해 주세요.")
    elif not api_key:
        st.warning("사이드바에 Gemini API Key를 입력해 주세요.")
    else:
        with st.spinner("영상 정보 분석 및 두뇌 엔진 가동 중..."):
            try:
                title, desc = extract_info(video_url)
                
                prompt = f"""
                영상 제목: {title}
                영상 설명/내용: {desc[:1000]}
                
                당신은 유튜브 채널 'EBS 다큐'와 '포크포크'의 썸네일 카피라이팅 전문가입니다.
                영상의 가장 자극적이고 궁금증을 유발하는 훅(Hook)을 찾아내어 아래 5개 유형의 2줄 카피와 이미지 디렉션을 작성하세요.
                
                [규칙]
                - 1줄과 2줄로 엄격히 분리 (각 줄당 11~17자 내외).
                - 1줄은 발단/조건/갈등 제시, 2줄은 반전/대응/구체적 수치 제시.
                
                JSON 형식으로만 응답:
                {{
                  "hook_summary": "핵심 후킹 포인트 요약 (2문장)",
                  "categories": [
                    {{"type": "발단-사이다 반전형 (포크포크)", "line1": "...", "line2": "...", "image": "...", "prompt": "..."}},
                    {{"type": "극단적 고난-현실 보상형 (EBS 극한직업)", "line1": "...", "line2": "...", "image": "...", "prompt": "..."}},
                    {{"type": "상식 파괴-현실 폭로형 (EBS 다큐프라임)", "line1": "...", "line2": "...", "image": "...", "prompt": "..."}},
                    {{"type": "기적적 인연-따옴표 대사형 (포크포크)", "line1": "...", "line2": "...", "image": "...", "prompt": "..."}},
                    {{"type": "미스터리-현장 목격형 (공통)", "line1": "...", "line2": "...", "image": "...", "prompt": "..."}}
                  ]
                }}
                """
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
                data = json.loads(response.text)
                
                st.subheader("💡 핵심 훅 분석")
                st.info(data.get("hook_summary", ""))
                
                st.subheader("🎨 2줄 카피 & 비주얼 디렉션")
                for cat in data.get("categories", []):
                    with st.expander(f"📌 {cat['type']}", expanded=True):
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            st.markdown(f"> **1줄:** `{cat['line1']}`  \n> **2줄:** `{cat['line2']}`")
                        with c2:
                            st.write(f"**추천 구도:** {cat['image']}")
                            st.code(cat['prompt'], language="text")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
