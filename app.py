import streamlit as st
import json
import yt_dlp
from google import genai

# ==========================================
# 0. 비밀번호 인증 게이트 (기본 비밀번호: tjb)
# ==========================================
DEFAULT_PASSWORD = "tjb"  # 원하는 접속 비밀번호로 변경 가능합니다.

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 썸네일 브레인 접근 인증")
    st.write("접속을 위해 비밀번호를 입력해 주세요.")
    entered_pw = st.text_input("비밀번호:", type="password")
    
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
# 1. 메인 화면 구성 (API 관련 UI 완전 제거)
# ==========================================
st.set_page_config(page_title="유튜브 썸네일 브레인", layout="wide")
st.title("🎯 유튜브 썸네일 2줄 카피 & 비주얼 생성기")
st.caption("EBS 다큐 & 포크포크 알고리즘 후킹 엔진")

# API Key는 서버 백엔드(Secrets)에서만 은밀하게 로드
api_key = st.secrets.get("GEMINI_API_KEY", "")

video_url = st.text_input("유튜브 영상 URL을 입력하세요:", placeholder="https://www.youtube.com/watch?v=...")

def extract_info(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', ''), info.get('description', '')

# ==========================================
# 2. 분석 및 결과 생성 실행
# ==========================================
if st.button("🚀 후킹 문구 및 비주얼 도출", type="primary"):
    if not video_url:
        st.warning("유튜브 영상 URL을 입력해 주세요.")
    elif not api_key:
        # 일반 사용자에게 API 키를 요구하지 않고 시스템 상태만 알림
        st.error("시스템 설정 오류가 발생했습니다. 서비스 관리자에게 문의하세요.")
    else:
        with st.spinner("영상 분석 및 최적의 후킹 카피를 생성하는 중입니다..."):
            try:
                title, desc = extract_info(video_url)
                
                system_prompt = f"""
                영상 제목: {title}
                영상 설명/내용: {desc[:1000]}
                
                당신은 유튜브 채널 'EBS 다큐'와 '포크포크'의 썸네일 카피라이팅 및 비주얼 디렉팅 최고 전문가입니다.
                위 영상의 핵심 갈등과 가장 강렬한 후킹 포인트를 분석하여, 아래 5개 유형별 '2줄 썸네일 카피'와 '썸네일 비주얼 콘셉트'를 작성하세요.
                
                [카피라이팅 작성 원칙]
                1. 반드시 1줄과 2줄로 엄격히 분리할 것.
                2. 모바일 가독성을 위해 각 줄은 공백 포함 11~17자 내외로 작성할 것.
                3. 1줄은 발단/조건/상황/도발, 2줄은 반전/대처/구체적 수치/보상을 제시하여 극적인 호기심 갭을 만들 것.
                
                반드시 아래 JSON 포맷으로만 응답하세요:
                {{
                  "hook_summary": "영상의 가장 핵심적인 후킹 포인트 요약 (2문장 내외)",
                  "categories": [
                    {{
                      "type": "발단-사이다 반전형 (포크포크 스타일)",
                      "line1": "1줄 문구",
                      "line2": "2줄 문구",
                      "image_concept": "추천 캡처 장면 및 화면 구도 설명",
                      "ai_image_prompt": "Midjourney용 영문 프롬프트"
                    }},
                    {{
                      "type": "극단적 고난-현실 보상형 (EBS 극한직업 스타일)",
                      "line1": "1줄 문구",
                      "line2": "2줄 문구",
                      "image_concept": "추천 캡처 장면 및 화면 구도 설명",
                      "ai_image_prompt": "Midjourney용 영문 프롬프트"
                    }},
                    {{
                      "type": "상식 파괴-현실 폭로형 (EBS 다큐프라임 스타일)",
                      "line1": "1줄 문구",
                      "line2": "2줄 문구",
                      "image_concept": "추천 캡처 장면 및 화면 구도 설명",
                      "ai_image_prompt": "Midjourney용 영문 프롬프트"
                    }},
                    {{
                      "type": "기적적 인연-따옴표 대사형 (포크포크 스타일)",
                      "line1": "1줄 문구",
                      "line2": "2줄 문구",
                      "image_concept": "추천 캡처 장면 및 화면 구도 설명",
                      "ai_image_prompt": "Midjourney용 영문 프롬프트"
                    }},
                    {{
                      "type": "미스터리-현장 목격형 (공통 스타일)",
                      "line1": "1줄 문구",
                      "line2": "2줄 문구",
                      "image_concept": "추천 캡처 장면 및 화면 구도 설명",
                      "ai_image_prompt": "Midjourney용 영문 프롬프트"
                    }}
                  ]
                }}
                """
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=system_prompt,
                    config={'response_mime_type': 'application/json'}
                )
                data = json.loads(response.text)
                
                # 결과 출력
                st.subheader("💡 핵심 훅(Hook) 분석")
                st.info(data.get("hook_summary", ""))
                
                st.subheader("🎨 유형별 2줄 썸네일 카피 & 비주얼 디렉션")
                for cat in data.get("categories", []):
                    with st.expander(f"📌 {cat['type']}", expanded=True):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown("#### ✍️ 썸네일 2줄 카피")
                            st.markdown(f"> **1줄:** `{cat['line1']}`  \n> **2줄:** `{cat['line2']}`")
                        with col2:
                            st.markdown("#### 🖼️ 비주얼 디렉션")
                            st.write(f"**화면 연출:** {cat['image_concept']}")
                            st.caption("AI 이미지 생성 프롬프트:")
                            st.code(cat['ai_image_prompt'], language="text")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
