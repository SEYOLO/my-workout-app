import streamlit as st
import pandas as pd
import os
import time
import random
from datetime import datetime
import urllib.parse
from PIL import Image

# 1. 페이지 기본 설정
st.set_page_config(page_title="WORKOUT", page_icon="⚡", layout="centered", initial_sidebar_state="collapsed")

USERS_FILE = "users.csv"
FOLLOWS_FILE = "follows.csv"
WORKOUT_FILE = "workout_data.csv"
PROFILE_DIR = "profile_pics"

if not os.path.exists(PROFILE_DIR):
    os.makedirs(PROFILE_DIR)

APP_ICON_URL = "https://cdn-icons-png.flaticon.com/512/2964/2964514.png"

# 모바일 상단 잘림 방지 + 모던 다크 스플래시 CSS
st.markdown(f"""
<head>
    <link rel="apple-touch-icon" href="{APP_ICON_URL}">
    <link rel="icon" type="image/png" sizes="192x192" href="{APP_ICON_URL}">
</head>
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif; }}
    
    /* Streamlit 상단 기본 헤더 요소 숨김 */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}

    .stApp {{
        background: #0D0E12;
        color: #E2E8F0;
    }}

    /* 모바일 노치 및 안전 구역(Safe Area) 반응형 패딩 */
    .block-container {{
        padding-top: max(3.2rem, env(safe-area-inset-top)) !important;
        padding-bottom: max(2.0rem, env(safe-area-inset-bottom)) !important;
    }}

    /* 네이티브 다크 스플래시 화면 */
    #splash-screen {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #0D0E12;
        z-index: 999999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: fadeOutSplash 0.5s ease-in-out 1.2s forwards;
        pointer-events: none;
    }}

    .splash-logo {{
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        color: #F8FAFC;
        animation: pulseLogo 1.0s cubic-bezier(0.16, 1, 0.3, 1) infinite alternate;
    }}

    .splash-sub {{
        font-size: 0.85rem;
        color: #38BDF8;
        font-weight: 700;
        letter-spacing: 0.2em;
        margin-top: 0.5rem;
    }}

    @keyframes pulseLogo {{
        0% {{ transform: scale(0.96); opacity: 0.8; }}
        100% {{ transform: scale(1.02); opacity: 1; text-shadow: 0 0 20px rgba(56, 189, 248, 0.4); }}
    }}

    @keyframes fadeOutSplash {{
        0% {{ opacity: 1; transform: translateY(0); }}
        100% {{ opacity: 0; transform: translateY(-20px); visibility: hidden; }}
    }}

    .brand-title {{
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        color: #F8FAFC;
        text-align: center;
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
    }}
    .brand-sub {{
        font-size: 0.85rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 1.5rem;
    }}

    .stButton > button {{
        width: 100% !important;
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{ background: #1D4ED8 !important; }}

    .prev-record-card {{
        background: rgba(56, 189, 248, 0.05);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px; padding: 10px 14px; margin-bottom: 10px;
        display: flex; align-items: center; justify-content: space-between;
    }}
    .prev-record-title {{ font-size: 0.82rem; color: #38BDF8; font-weight: 600; }}
    .prev-record-value {{ font-size: 0.9rem; color: #F8FAFC; font-weight: 700; }}
    
    .guide-box {{
        background: rgba(245, 158, 11, 0.05);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.83rem; color: #FBBF24;
    }}

    @media (max-width: 640px) {{
        .block-container {{ padding-left: 0.6rem !important; padding-right: 0.6rem !important; }}
        .brand-title {{ font-size: 1.6rem; }}
    }}
</style>

<!-- Splash Overlay -->
<div id="splash-screen">
    <div class="splash-logo">WORKOUT ⚡</div>
    <div class="splash-sub">PERFORMANCE LOG</div>
</div>
""", unsafe_allow_html=True)

# 2. DB 초기화
def init_db():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["user_id", "password", "nickname", "bio", "profile_pic"]).to_csv(USERS_FILE, index=False)
    else:
        users = pd.read_csv(USERS_FILE, dtype=str)
        if "profile_pic" not in users.columns:
            users["profile_pic"] = ""
            users.to_csv(USERS_FILE, index=False)
            
    if not os.path.exists(FOLLOWS_FILE):
        pd.DataFrame(columns=["follower_id", "following_id"]).to_csv(FOLLOWS_FILE, index=False)
    if not os.path.exists(WORKOUT_FILE):
        pd.DataFrame(columns=["date", "user_id", "nickname", "routine", "exercise", "set_num", "weight", "reps", "memo", "is_private"]).to_csv(WORKOUT_FILE, index=False)

init_db()

def load_users(): return pd.read_csv(USERS_FILE, dtype=str)
def load_follows(): return pd.read_csv(FOLLOWS_FILE, dtype=str)
def load_workouts(): 
    df = pd.read_csv(WORKOUT_FILE, dtype=str)
    if not df.empty and "weight" in df.columns:
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0.0)
        df["reps"] = pd.to_numeric(df["reps"], errors="coerce").fillna(0)
        df["set_num"] = pd.to_numeric(df["set_num"], errors="coerce").fillna(1)
    return df

def save_data(df, filename): df.to_csv(filename, index=False)

def get_profile_path(user_id):
    users = load_users()
    u = users[users["user_id"] == user_id]
    if not u.empty and pd.notna(u.iloc[0].get("profile_pic")) and str(u.iloc[0]["profile_pic"]).strip():
        pic_file = os.path.join(PROFILE_DIR, u.iloc[0]["profile_pic"])
        if os.path.exists(pic_file): return pic_file
    return None

EXERCISE_TIPS = {
    # 가슴
    "벤치프레스": "견갑(날개뼈)을 패킹 후 가슴을 열고, 바벨을 쇄골이 아닌 명치 밑으로 내립니다.",
    "인클라인 벤치프레스": "벤치 각도를 30도로 맞추고, 바벨을 쇄골 살짝 아래 윗가슴 라인으로 이완시킵니다.",
    "덤벨 벤치프레스": "수축 시 덤벨을 부딪치지 말고, 이완 시 팔꿈치 각도를 75도로 유지하며 최대한 늘립니다.",
    "인클라인 덤벨 벤치프레스": "상체 각도를 세우고 덤벨을 윗가슴 바깥쪽까지 수평 이완 후 수직으로 밀어올립니다.",
    "체스트 프레스 머신": "등패드에 엉덩이와 어깨를 고정하고 손잡이가 가슴 중앙 수평선에 오도록 의자를 조절합니다.",
    "펙덱 플라이 머신": "팔꿈치를 살짝 구부려 고정하고, 손이 아닌 팔꿈치 안쪽으로 가슴을 쥐어짜듯 모옵니다.",
    "케이블 크로스오버": "상체를 살짝 숙이고 케이블 손잡이를 명치/아랫가슴 방향으로 둥글게 모아줍니다.",
    "딥스": "상체를 앞으로 30도 숙여 체중을 가슴 하부에 싣고, 팔꿈치가 90도가 될 때까지 내립니다.",
    "덤벨 플라이": "팔꿈치 각도를 변형하지 말고 포옹하듯 곡선을 그리며 가슴 외곽을 신장시킵니다.",
    "인클라인 덤벨 플라이": "윗가슴 장력을 유지하며 팔꿈치 각도를 고정하고 위쪽으로 모아줍니다.",

    # 등
    "데드리프트": "바벨을 신발끈 중앙 위에 두고, 바를 다리에 붙인 채 고관절(힙힌지)을 접어 들어올립니다.",
    "바벨로우": "상체를 45도 숙이고 복압을 잡은 뒤 바벨을 허벅지 타고 배꼽 방향으로 당깁니다.",
    "풀업": "숄더패킹으로 견갑을 먼저 내린 뒤 가슴을 봉에 맞닿는다는 느낌으로 광배근을 당깁니다.",
    "티바로우": "허리가 꺾이지 않도록 복압을 단단히 유지하고 팔꿈치를 명치 뒤쪽으로 찍어누르듯 당깁니다.",
    "렛풀다운": "상체를 살짝 뒤로 누르고 바를 쇄골 쪽으로 당기며 이완 시 광배가 뽑혀나가는 느낌을 유지합니다.",
    "시티드 케이블 로우": "상체 반동을 최소화하고 명치를 열면서 케이블을 아랫배 쪽으로 밀착 당깁니다.",
    "원암 덤벨로우": "골반과 척추 수평을 유지하고 팔꿈치를 골반 쪽으로 그리는 궤적으로 당깁니다.",
    "어시스트 풀업 머신": "무릎을 패드에 밀착하고 상체 우측/좌측 균형을 맞춰 광배 하부까지 이완시킵니다.",
    "암 풀다운": "팔꿈치를 살짝 구부려 고정하고 바를 허벅지 방향으로 호를 그리며 짓눌러 내려줍니다.",

    # 하체
    "스쿼트": "발바닥 전체로 지면을 지탱하고 무릎과 고관절이 동시에 접히며 척추 중립을 유지합니다.",
    "레그프레스": "발판 상단에 발을 두고 무릎이 안쪽으로 모이지 않게 하며 허리가 패드에서 뜨지 않게 내립니다.",
    "스티프 레그 데드리프트": "무릎을 살짝 구부린 상태로 고정하고 엉덩이를 뒤로 빼며 대퇴이두(햄스트링)를 늘립니다.",
    "레그 익스텐션": "엉덩이가 들리지 않게 손잡이를 강하게 잡고 발목을 당긴 상태에서 대퇴사두를 완전히 쥐어짭니다.",
    "레그 컬": "골반을 패드에 밀착시키고 발목을 세워 햄스트링 힘으로 패드를 엉덩이 쪽으로 접어올립니다.",
    "런지": "앞발 뒤꿈치에 체중의 70%를 싣고 무릎이 발끝을 과도하게 넘지 않게 직각으로 내립니다.",
    "이너사이 머신": "내전근(허벅지 안쪽)을 장력 유지 상태로 이완 후 튕기지 않고 지긋이 모아줍니다.",
    "아웃사이 머신": "상체를 살짝 숙여 둔근(엉덩이)에 자극을 집중시키고 무릎 외각으로 패드를 밀어냅니다.",
    "카프 레이즈": "가동범위를 최대한 사용하여 뒤꿈치를 끝까지 올렸다가 가자미근/비복근을 최대로 늘립니다.",

    # 어깨
    "오버헤드 프레스": "코어와 둔근에 수축을 유지하고 바벨을 턱을 스치며 머리 위 직수평으로 밀어 올립니다.",
    "덤벨 숄더프레스": "덤벨이 팔꿈치 수직 선상에서 벗어나지 않게 유지하며 귀 높이까지 내렸다 올립니다.",
    "숄더프레스 머신": "등받이에 허리를 밀착하고 팔꿈치가 몸 뒤로 빠지지 않도록 유의하며 밀어줍니다.",
    "사이드 레터럴 레이즈": "덤벨을 쥐는 힘을 빼고 팔꿈치를 측면으로 들어 올린다는 느낌으로 차올립니다.",
    "벤트오버 레터럴 레이즈": "상체를 90도 숙이고 후면 삼각근의 힘으로 새끼손가락 방향을 위로 들며 넓게 벌립니다.",
    "페이스풀": "케이블을 눈높이에 맞추고 로프를 이마/눈썹 방향으로 당기며 팔꿈치를 외회전시킵니다.",
    "아놀드 프레스": "손바닥이 자신을 향한 상태에서 회전시키며 올려 전면과 측면 삼각근을 동시에 타격합니다.",

    # 팔
    "트라이셉스 케이블 푸쉬다운": "팔꿈치를 옆구리에 박아두고 바/로프를 바닥 방향으로 삼두를 완전 압축시킵니다.",
    "라잉 트라이셉스 익스텐션": "팔꿈치를 수직보다 살짝 뒤로 기울여 고정하고 바를 정수리 뒤쪽으로 내립니다.",
    "딥스(삼두)": "상체를 수직으로 세운 상태를 유지하여 중량이 가슴이 아닌 삼두근에 쏠리게 합니다.",
    "바벨 컬": "팔꿈치가 앞으로 튀어나가지 않게 고정하고 이두의 힘만으로 바벨을 호를 그리며 올립니다.",
    "덤벨 컬": "손목을 밖으로 수피네이션(회전)시키며 이두근의 정점 수축을 극대화합니다.",
    "해머 컬": "손바닥이 서로 마주 보게 유지하여 상완근과 상완요골근(전완근)을 집중 타격합니다.",
    "프리처 컬": "패드에 삼두를 완전히 밀착시켜 반동을 차단하고 이두의 이완을 최대로 끌어냅니다.",

    # 복근 / 유산소
    "크런치": "허리를 바닥에 붙인 채 상복부만 말아 올려 갈비뼈와 골반이 가까워지게 만듭니다.",
    "레그 레이즈": "요추(허리)가 바닥에서 뜨지 않도록 복압을 유지하며 하복부 힘으로 다리를 들어 올립니다.",
    "플랭크": "어깨 아래 팔꿈치를 두고 머리부터 발끝까지 일직선을 만들어 코어 전체에 장력을 줍니다.",
    "천국의 계단(스텝밀)": "발바닥 전체로 계단을 딛고 발 뒤꿈치를 밀어내며 둔근 자극을 살립니다.",
    "런닝머신": "상체를 똑바로 세우고 호흡을 일정하게 유지하며 가벼운 경사도를 주어 관절 부담을 줄입니다.",
    "사이클": "페달이 가장 아래로 내려갔을 때 무릎이 살짝 구부러지도록 안장 높이를 조절합니다."
}

def get_yt_url(exercise_name):
    query = f"{exercise_name} 자세"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.youtube.com/results?search_query={encoded_query}"

ANATOMICAL_POOL = {
    "가슴_상부_프레스": ["인클라인 벤치프레스", "인클라인 덤벨 벤치프레스"],
    "가슴_중하부_프레스": ["벤치프레스", "덤벨 벤치프레스", "체스트 프레스 머신"],
    "가슴_하부_고립": ["딥스", "케이블 크로스오버"],
    "가슴_수축_플라이": ["펙덱 플라이 머신", "덤벨 플라이", "인클라인 덤벨 플라이"],
    
    "등_수직_너비": ["풀업", "렛풀다운", "어시스트 풀업 머신", "암 풀다운"],
    "등_수평_두께": ["바벨로우", "시티드 케이블 로우", "티바로우", "원암 덤벨로우"],
    "등_전신_메인": ["데드리프트"],
    
    "하체_전면_스쿼트": ["스쿼트", "레그프레스", "레그 익스텐션"],
    "하체_후면_둔근": ["스티프 레그 데드리프트", "레그 컬", "런지"],
    "하체_내외전근": ["이너사이 머신", "아웃사이 머신", "카프 레이즈"],
    
    "어깨_전면": ["오버헤드 프레스", "덤벨 숄더프레스", "숄더프레스 머신", "아놀드 프레스"],
    "어깨_측면": ["사이드 레터럴 레이즈"],
    "어깨_후면": ["벤트오버 레터럴 레이즈", "페이스풀"],
    
    "삼두": ["트라이셉스 케이블 푸쉬다운", "라잉 트라이셉스 익스텐션", "딥스(삼두)"],
    "이두": ["바벨 컬", "덤벨 컬", "해머 컬", "프리처 컬"],
    "유산소/복근": ["크런치", "레그 레이즈", "플랭크", "천국의 계단(스텝밀)", "런닝머신", "사이클"]
}

ALL_EXERCISES = list(set(sum(ANATOMICAL_POOL.values(), [])))

def generate_anatomical_routine(routine_type):
    random.seed(time.time())
    
    if routine_type == "가슴 전체 DAY":
        return [
            random.choice(ANATOMICAL_POOL["가슴_상부_프레스"]),
            random.choice(ANATOMICAL_POOL["가슴_중하부_프레스"]),
            random.choice(ANATOMICAL_POOL["가슴_수축_플라이"]),
            random.choice(ANATOMICAL_POOL["삼두"])
        ]
    elif routine_type == "윗가슴 집중 DAY":
        return [
            ANATOMICAL_POOL["가슴_상부_프레스"][0],
            ANATOMICAL_POOL["가슴_상부_프레스"][1],
            "인클라인 덤벨 플라이",
            random.choice(ANATOMICAL_POOL["삼두"])
        ]
    elif routine_type == "등 전체 DAY":
        return [
            random.choice(ANATOMICAL_POOL["등_수직_너비"]),
            random.choice(ANATOMICAL_POOL["등_수평_두께"]),
            random.choice(ANATOMICAL_POOL["등_수직_너비"]),
            random.choice(ANATOMICAL_POOL["이두"])
        ]
    elif routine_type == "등 너비(수직) 집중 DAY":
        return [
            "풀업",
            "렛풀다운",
            "암 풀다운",
            random.choice(ANATOMICAL_POOL["등_수평_두께"]),
            random.choice(ANATOMICAL_POOL["이두"])
        ]
    elif routine_type == "등 두께(수평) 집중 DAY":
        return [
            "바벨로우",
            "시티드 케이블 로우",
            "원암 덤벨로우",
            random.choice(ANATOMICAL_POOL["등_수직_너비"]),
            random.choice(ANATOMICAL_POOL["이두"])
        ]
    elif routine_type == "하체/복근 DAY":
        return [
            random.choice(ANATOMICAL_POOL["하체_전면_스쿼트"]),
            random.choice(ANATOMICAL_POOL["하체_후면_둔근"]),
            random.choice(ANATOMICAL_POOL["하체_내외전근"]),
            random.choice(ANATOMICAL_POOL["유산소/복근"])
        ]
    elif routine_type == "어깨 입체감 DAY":
        return [
            random.choice(ANATOMICAL_POOL["어깨_전면"]),
            random.choice(ANATOMICAL_POOL["어깨_측면"]),
            random.choice(ANATOMICAL_POOL["어깨_후면"]),
            random.choice([x for x in ANATOMICAL_POOL["유산소/복근"] if "런닝" in x or "계단" in x or "사이클" in x])
        ]
    return []

if "user_id" not in st.session_state: st.session_state.user_id = None
if "nickname" not in st.session_state: st.session_state.nickname = None
if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"
if "timer_running" not in st.session_state: st.session_state.timer_running = False

# --- [로그인 / 회원가입 랜딩] ---
if st.session_state.user_id is None:
    st.markdown("<div class='brand-title'>WORKOUT</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>Personal Set Log & Social Feed</div>", unsafe_allow_html=True)
    
    users_df = load_users()
    
    if st.session_state.auth_mode == "login":
        with st.form("clean_login_form"):
            st.write("### 로그인")
            login_id = st.text_input("아이디", key="l_id").strip()
            login_pw = st.text_input("비밀번호", type="password", key="l_pw").strip()
            submit_login = st.form_submit_button("시작하기")
            
            if submit_login:
                user_match = users_df[(users_df["user_id"] == login_id) & (users_df["password"] == login_pw)]
                if not user_match.empty:
                    st.session_state.user_id = login_id
                    st.session_state.nickname = user_match.iloc[0]["nickname"]
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                    
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1: st.caption("아직 계정이 없으신가요?")
        with col_m2:
            if st.button("회원가입"):
                st.session_state.auth_mode = "signup"
                st.rerun()

    else:
        with st.form("clean_signup_form"):
            st.write("### 회원가입")
            new_id = st.text_input("아이디", key="s_id").strip()
            new_pw = st.text_input("비밀번호", type="password", key="s_pw").strip()
            new_nick = st.text_input("닉네임", key="s_nick").strip()
            new_bio = st.text_input("한 줄 소개 (선택)", key="s_bio", placeholder="목표나 다짐").strip()
            uploaded_pic = st.file_uploader("프로필 사진 선택 (앨범)", type=["jpg", "jpeg", "png"])
            
            submit_signup = st.form_submit_button("가입 완료")
            
            if submit_signup:
                if not new_id or not new_pw or not new_nick:
                    st.error("필수 항목을 모두 입력해 주세요.")
                elif new_id in users_df["user_id"].values:
                    st.error("이미 사용 중인 아이디입니다.")
                elif new_nick in users_df["nickname"].values:
                    st.error("이미 사용 중인 닉네임입니다.")
                else:
                    pic_filename = ""
                    if uploaded_pic is not None:
                        pic_filename = f"{new_id}_{int(time.time())}.png"
                        img = Image.open(uploaded_pic)
                        img.save(os.path.join(PROFILE_DIR, pic_filename))
                        
                    new_user = pd.DataFrame([{
                        "user_id": new_id, "password": new_pw, 
                        "nickname": new_nick, "bio": new_bio, 
                        "profile_pic": pic_filename
                    }])
                    users_df = pd.concat([users_df, new_user], ignore_index=True)
                    save_data(users_df, USERS_FILE)
                    st.success("회원가입 완료! 로그인해 주세요.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                    
        if st.button("로그인 화면으로 돌아가기"):
            st.session_state.auth_mode = "login"
            st.rerun()

else:
    # --- [로그인 완료 메인 화면] ---
    prof_path = get_profile_path(st.session_state.user_id)
    
    col_h1, col_h2 = st.columns([1, 4])
    with col_h1:
        if prof_path:
            st.image(prof_path, width=50)
        else:
            st.write("👤")
    with col_h2:
        st.markdown(f"**{st.session_state.nickname}**")
        st.caption(f"ID: {st.session_state.user_id}")
        
    if st.sidebar.button("로그아웃"):
        st.session_state.user_id = None
        st.session_state.nickname = None
        st.rerun()
        
    st.markdown("<div class='brand-title' style='margin-top:0; font-size:1.6rem;'>WORKOUT ⚡</div>", unsafe_allow_html=True)
    
    tab_workout, tab_timer, tab_feed, tab_calendar, tab_friends, tab_profile = st.tabs([
        "기록", "타이머", "피드", "달력", "팔로우", "프로필"
    ])

    workouts_df = load_workouts()
    
    # TAB 1: 운동 기록 작성
    with tab_workout:
        st.subheader("오늘의 운동")
        today_date = st.date_input("운동 날짜", datetime.now())
        
        routine_options = [
            "선택 안함", 
            "가슴 전체 DAY", "윗가슴 집중 DAY", 
            "등 전체 DAY", "등 너비(수직) 집중 DAY", "등 두께(수평) 집중 DAY", 
            "하체/복근 DAY", "어깨 입체감 DAY", "자율 운동"
        ]
        routine_type = st.selectbox("루틴 및 타겟 선택", routine_options)
        
        selected_exercises = []
        if routine_type != "선택 안함" and routine_type != "자율 운동":
            if "random_routine" not in st.session_state or st.session_state.get("current_routine_type") != routine_type:
                st.session_state.random_routine = generate_anatomical_routine(routine_type)
                st.session_state.current_routine_type = routine_type
                
            col_rec1, col_rec2 = st.columns([3, 1])
            with col_rec1: st.info(f"💡 **[{routine_type}]** 해부학적 유기적 추천 조합")
            with col_rec2:
                if st.button("🎲 재추천"):
                    st.session_state.random_routine = generate_anatomical_routine(routine_type)
                    st.rerun()
                    
            selected_exercises = st.multiselect("종목 구성", options=ALL_EXERCISES, default=st.session_state.random_routine)
            
        elif routine_type == "자율 운동":
            selected_exercises = st.multiselect("종목 선택", options=ALL_EXERCISES)
            
        custom_ex = st.text_input("직접 종목 입력 (쉼표 구분)", placeholder="예: 케이블 로우, 스트레칭")
        if custom_ex:
            selected_exercises.extend([x.strip() for x in custom_ex.split(",") if x.strip()])
            
        if selected_exercises:
            st.divider()
            my_past_workouts = workouts_df[workouts_df["user_id"] == st.session_state.user_id]
            
            workout_entries = []
            for ex in selected_exercises:
                st.write(f"🏋️ **{ex}**")
                
                tip_text = EXERCISE_TIPS.get(ex, "관절 부상을 예방하도록 코어 복압을 유지하고 수축/이완 장력을 지킵니다.")
                yt_link = get_yt_url(ex)
                st.markdown(f"""
                <div class="guide-box">
                    📌 <b>팁:</b> {tip_text} <a href="{yt_link}" target="_blank" style="color: #38BDF8; margin-left: 8px; font-weight: 600; text-decoration: none;">[▶️ 자세 영상]</a>
                </div>
                """, unsafe_allow_html=True)
                
                ex_past = my_past_workouts[my_past_workouts["exercise"] == ex]
                if not ex_past.empty:
                    max_w = ex_past["weight"].max()
                    max_r = ex_past[ex_past["weight"] == max_w]["reps"].max()
                    last_date = ex_past["date"].max()
                    st.markdown(f"""
                    <div class="prev-record-card">
                        <span class="prev-record-title">💡 지난 최고 기록 ({last_date})</span>
                        <span class="prev-record-value">{max_w} kg × {max_r} 회</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("💡 첫 수행 종목입니다.")
                
                num_sets = st.number_input(f"총 세트 수 ({ex})", 1, 10, 3, key=f"setcnt_{ex}")
                
                for s in range(1, num_sets + 1):
                    sc1, sc2 = st.columns(2)
                    with sc1:
                        w = st.number_input(f"{s}세트 무게(kg)", 0.0, step=2.5, value=20.0, key=f"w_{ex}_{s}")
                    with sc2:
                        r = st.number_input(f"{s}세트 횟수(reps)", 1, value=10, key=f"r_{ex}_{s}")
                        
                    workout_entries.append({
                        "date": str(today_date),
                        "user_id": st.session_state.user_id,
                        "nickname": st.session_state.nickname,
                        "routine": routine_type,
                        "exercise": ex,
                        "set_num": s,
                        "weight": w,
                        "reps": r
                    })
                st.write("---")
            
            memo = st.text_input("오늘의 메모", placeholder="컨디션, 특이사항 등")
            is_private = st.checkbox("🔒 비공개로 저장")
            
            if st.button("💾 오늘 운동 저장 완료"):
                for entry in workout_entries:
                    entry["memo"] = memo
                    entry["is_private"] = "True" if is_private else "False"
                
                new_df = pd.DataFrame(workout_entries)
                workouts_df = pd.concat([workouts_df, new_df], ignore_index=True)
                save_data(workouts_df, WORKOUT_FILE)
                st.success("성공적으로 저장되었습니다!")

    # TAB 2: 휴식 타이머
    with tab_timer:
        st.subheader("⏱️ 휴식 타이머")
        
        t_cols = st.columns(4)
        target_sec = 0
        with t_cols[0]:
            if st.button("60초", key="btn_60"): target_sec = 60
        with t_cols[1]:
            if st.button("90초", key="btn_90"): target_sec = 90
        with t_cols[2]:
            if st.button("120초", key="btn_120"): target_sec = 120
        with t_cols[3]:
            if st.button("180초", key="btn_180"): target_sec = 180
            
        custom_sec = st.number_input("직접 초 입력", min_value=0, step=10, value=0)
        if custom_sec > 0 and st.button("타이머 시작"): target_sec = custom_sec
            
        if target_sec > 0:
            st.session_state.timer_running = True
            timer_box = st.empty()
            p_bar = st.progress(1.0)
            
            stop_btn = st.button("⏹️ 타이머 중단")
                
            for remaining in range(target_sec, -1, -1):
                if stop_btn or not st.session_state.timer_running:
                    st.session_state.timer_running = False
                    timer_box.markdown("<h3 style='text-align:center; color:#EF4444;'>⏹️ 타이머가 중단되었습니다.</h3>", unsafe_allow_html=True)
                    break
                    
                mins, secs = divmod(remaining, 60)
                timer_box.markdown(f"<h1 style='text-align: center; color: #38BDF8; font-size: 3.8rem; font-weight: 800;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
                p_bar.progress(remaining / target_sec)
                time.sleep(1)
                
            if remaining == 0 and st.session_state.timer_running:
                timer_box.markdown("<h1 style='text-align: center; color: #4ADE80; font-size: 1.8rem; font-weight: 700;'>🔥 휴식 끝! 다음 세트 시작!</h1>", unsafe_allow_html=True)
                st.session_state.timer_running = False

    # TAB 3: 팔로우 피드
    with tab_feed:
        st.subheader("📱 팔로워 피드")
        follows_df = load_follows()
        my_followings = follows_df[follows_df["follower_id"] == st.session_state.user_id]["following_id"].tolist()
        feed_users = set(my_followings + [st.session_state.user_id])
        
        feed_df = workouts_df[
            (workouts_df["user_id"].isin(feed_users)) & 
            ((workouts_df["is_private"] == "False") | (workouts_df["user_id"] == st.session_state.user_id))
        ]
        
        if not feed_df.empty:
            grouped = feed_df.groupby(["date", "nickname", "routine", "user_id"])
            for (date, nick, routine, uid), group in sorted(grouped, key=lambda x: x[0][0], reverse=True):
                is_me = (uid == st.session_state.user_id)
                card_title = f"💪 {nick} ({date})" if not is_me else f"💪 나 ({date})"
                
                with st.expander(f"{card_title} - [{routine}]", expanded=True):
                    f_pic = get_profile_path(uid)
                    if f_pic:
                        st.image(f_pic, width=40)
                        
                    total_vol = (group["weight"] * group["reps"]).sum()
                    st.write(f"**총 볼륨:** `{total_vol:,.0f} kg`")
                    
                    ex_list = group["exercise"].unique()
                    for ex in ex_list:
                        ex_sub = group[group["exercise"] == ex]
                        sets_str = ", ".join([f"{r['weight']}kg×{r['reps']}회" for _, r in ex_sub.iterrows()])
                        st.write(f"• **{ex}**: {sets_str}")
                        
                    memo_val = group["memo"].iloc[0]
                    if pd.notna(memo_val) and str(memo_val).strip():
                        st.caption(f"💬 {memo_val}")
                        
                    if is_me:
                        if st.button("🗑️ 해당 날짜 기록 삭제", key=f"del_{date}_{uid}"):
                            workouts_df = workouts_df[~((workouts_df["user_id"] == uid) & (workouts_df["date"] == date))]
                            save_data(workouts_df, WORKOUT_FILE)
                            st.success("기록이 삭제되었습니다.")
                            st.rerun()
        else:
            st.info("기록이 없습니다.")

    # TAB 4: 팔로워 출석 달력
    with tab_calendar:
        st.subheader("📅 출석 달력")
        follows_df = load_follows()
        my_followings = follows_df[follows_df["follower_id"] == st.session_state.user_id]["following_id"].tolist()
        feed_users = set(my_followings + [st.session_state.user_id])
        
        now = datetime.now()
        year = st.number_input("연도", value=now.year, min_value=2024, max_value=2030)
        month = st.slider("월 선택", 1, 12, now.month)
        
        cal_df = workouts_df[
            (workouts_df["user_id"].isin(feed_users)) & 
            ((workouts_df["is_private"] == "False") | (workouts_df["user_id"] == st.session_state.user_id))
        ]
        
        if not cal_df.empty:
            cal_df["month"] = pd.to_datetime(cal_df["date"]).dt.month
            cal_df["year"] = pd.to_datetime(cal_df["date"]).dt.year
            month_df = cal_df[(cal_df["year"] == year) & (cal_df["month"] == month)]
            
            if not month_df.empty:
                attendance = month_df.groupby(["date", "nickname"])["routine"].first().unstack(fill_value=None)
                st.dataframe(attendance.sort_index(ascending=False), use_container_width=True)
            else:
                st.info("해당 월의 출석 기록이 없습니다.")
        else:
            st.info("표시할 데이터가 없습니다.")

    # TAB 5: 친구 찾기 & 팔로우
    with tab_friends:
        st.subheader("👥 팔로우 관리")
        users_df = load_users()
        follows_df = load_follows()
        
        search_nick = st.text_input("닉네임 검색", placeholder="친구 닉네임").strip()
        if search_nick:
            target_user = users_df[users_df["nickname"] == search_nick]
            if not target_user.empty:
                t_id = target_user.iloc[0]["user_id"]
                t_nick = target_user.iloc[0]["nickname"]
                t_bio = target_user.iloc[0]["bio"]
                
                if t_id == st.session_state.user_id:
                    st.warning("자기 자신은 팔로우할 수 없습니다.")
                else:
                    st.write(f"**{t_nick}** ({t_bio if pd.notna(t_bio) else '소개 없음'})")
                    is_following = not follows_df[
                        (follows_df["follower_id"] == st.session_state.user_id) & 
                        (follows_df["following_id"] == t_id)
                    ].empty
                    
                    if is_following:
                        if st.button("언팔로우"):
                            follows_df = follows_df[~(
                                (follows_df["follower_id"] == st.session_state.user_id) & 
                                (follows_df["following_id"] == t_id)
                            )]
                            save_data(follows_df, FOLLOWS_FILE)
                            st.success(f"{t_nick}님을 언팔로우했습니다.")
                            st.rerun()
                    else:
                        if st.button("팔로우하기"):
                            new_follow = pd.DataFrame([{"follower_id": st.session_state.user_id, "following_id": t_id}])
                            follows_df = pd.concat([follows_df, new_follow], ignore_index=True)
                            save_data(follows_df, FOLLOWS_FILE)
                            st.success(f"{t_nick}님을 팔로우합니다!")
                            st.rerun()
            else:
                st.error("유저를 찾을 수 없습니다.")

        st.divider()
        st.write("### 내 팔로우 목록")
        my_follows = follows_df[follows_df["follower_id"] == st.session_state.user_id]
        if not my_follows.empty:
            followed_users = users_df[users_df["user_id"].isin(my_follows["following_id"])]
            for _, f_row in followed_users.iterrows():
                st.write(f"• **{f_row['nickname']}** (`{f_row['user_id']}`)")
        else:
            st.caption("팔로우 중인 친구가 없습니다.")

    # TAB 6: 프로필 관리 & 리포트
    with tab_profile:
        st.subheader("⚙️ 프로필 관리 & 리포트")
        users_df = load_users()
        user_idx = users_df[users_df["user_id"] == st.session_state.user_id].index
        
        if not user_idx.empty:
            curr_row = users_df.loc[user_idx[0]]
            
            with st.form("edit_profile_form"):
                st.write("### 프로필 정보 수정")
                
                mod_nick = st.text_input("닉네임 변경", value=curr_row["nickname"]).strip()
                mod_bio = st.text_input("한 줄 소개 변경", value=curr_row.get("bio", "")).strip()
                new_pic = st.file_uploader("프로필 사진 변경 (앨범)", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("프로필 저장"):
                    if not mod_nick:
                        st.error("닉네임은 비워둘 수 없습니다.")
                    elif mod_nick != curr_row["nickname"] and mod_nick in users_df["nickname"].values:
                        st.error("이미 사용 중인 닉네임입니다.")
                    else:
                        users_df.loc[user_idx[0], "nickname"] = mod_nick
                        users_df.loc[user_idx[0], "bio"] = mod_bio
                        
                        if new_pic is not None:
                            p_name = f"{st.session_state.user_id}_{int(time.time())}.png"
                            img = Image.open(new_pic)
                            img.save(os.path.join(PROFILE_DIR, p_name))
                            users_df.loc[user_idx[0], "profile_pic"] = p_name
                            
                        workouts_df.loc[workouts_df["user_id"] == st.session_state.user_id, "nickname"] = mod_nick
                        save_data(workouts_df, WORKOUT_FILE)
                        save_data(users_df, USERS_FILE)
                        
                        st.session_state.nickname = mod_nick
                        st.success("프로필 수정 완료!")
                        st.rerun()

        st.divider()
        st.subheader("📊 내 성장 리포트 & 기록 관리")
        my_df = workouts_df[workouts_df["user_id"] == st.session_state.user_id]
        if not my_df.empty:
            my_df["volume"] = my_df["weight"] * my_df["reps"]
            total_vol = my_df["volume"].sum()
            st.metric("총 누적 볼륨", f"{total_vol:,.0f} kg")
            
            vol_by_date = my_df.groupby("date")["volume"].sum().reset_index()
            st.line_chart(vol_by_date.set_index("date"))
            
            st.write("### 내 상세 운동 기록 및 삭제")
            my_grouped = my_df.groupby("date")
            for d, d_group in sorted(my_grouped, key=lambda x: x[0], reverse=True):
                with st.expander(f"📅 {d} 기록 상세 보기"):
                    for idx, row in d_group.iterrows():
                        rc1, rc2 = st.columns([4, 1])
                        with rc1:
                            st.write(f"• **{row['exercise']}** - {row['set_num']}세트: {row['weight']}kg × {row['reps']}회")
                        with rc2:
                            if st.button("삭제", key=f"del_single_{idx}"):
                                workouts_df = workouts_df.drop(idx)
                                save_data(workouts_df, WORKOUT_FILE)
                                st.success("선택한 세트 기록 삭제 완료")
                                st.rerun()
        else:
            st.info("등록된 기록이 없습니다.")
