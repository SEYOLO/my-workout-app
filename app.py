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

# 스마트폰 홈 화면 전용 아이콘 URL (원하는 고화질 이미지 링크로 변경 가능)
APP_ICON_URL = "https://cdn-icons-png.flaticon.com/512/2964/2964514.png"

# PWA / 홈 화면 앱 아이콘 메타 태그 & Responsive UI CSS
st.markdown(f"""
<head>
    <link rel="apple-touch-icon" href="{APP_ICON_URL}">
    <link rel="icon" sizes="192x192" href="{APP_ICON_URL}">
</head>
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif; }}
    
    .stApp {{
        background: #0D0E12;
        color: #E2E8F0;
    }}

    .brand-title {{
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        color: #F8FAFC;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }}
    .brand-sub {{
        font-size: 0.85rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }}

    /* 탭 메뉴 균등 분할 레이아웃 */
    div[data-baseweb="tab-list"] {{
        display: flex !important;
        width: 100% !important;
        background-color: #14161D !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 2px !important;
        border: 1px solid #222634 !important;
        margin-bottom: 1.5rem !important;
    }}

    button[data-baseweb="tab"] {{
        flex: 1 1 0% !important;
        width: 100% !important;
        text-align: center !important;
        justify-content: center !important;
        border-radius: 8px !important;
        padding: 10px 0px !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.2s ease-in-out !important;
    }}

    button[aria-selected="true"] {{
        background: #1E293B !important;
        color: #38BDF8 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    }}

    /* 단일 폼 박스 */
    div[data-testid="stForm"] {{
        background: #14161D !important;
        border: 1px solid #222634 !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
    }}

    .stButton > button, div[data-testid="stForm"] button {{
        width: 100% !important;
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
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
        .block-container {{ padding-left: 0.6rem !important; padding-right: 0.6rem !important; padding-top: 0.8rem !important; }}
        .brand-title {{ font-size: 1.7rem; }}
        button[data-baseweb="tab"] {{ font-size: 0.75rem !important; padding: 8px 0px !important; }}
    }}
</style>
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
    "벤치프레스": "견갑(날개뼈)을 고정하고 바벨을 가슴 명치 살짝 위에 밀착시킵니다.",
    "인클라인 벤치프레스": "벤치 각도를 30도 정도로 맞춰 윗가슴 자극에 집중합니다.",
    "덤벨 벤치프레스": "가슴 근육을 최대한 이완하며 가동범위를 길게 가져갑니다.",
    "체스트 프레스 머신": "의자 높이를 조절해 손잡이가 가슴 중앙에 오도록 합니다.",
    "펙덱 플라이 머신": "팔꿈치를 살짝 구부린 상태를 유지하고 가슴을 모아줍니다.",
    "딥스": "상체를 앞으로 살짝 숙여 가슴 하부 및 삼두 자극을 극대화합니다.",
    "데드리프트": "허리가 굽지 않도록 척추 중립을 지키고 바벨을 몸에 붙여 올립니다.",
    "바벨로우": "상체를 45도 숙이고 바벨을 배꼽 방향으로 당겨 등 하부를 자극합니다.",
    "렛풀다운": "가슴을 열어주고 바를 쇄골 방향으로 당겨 등에 자극을 줍니다.",
    "시티드 케이블 로우": "상체가 뒤로 과도하게 젖혀지지 않도록 등 힘으로 당깁니다.",
    "스쿼트": "무릎이 고관절과 함께 접히며 복압을 유지하고 내려갑니다.",
    "레그프레스": "무릎을 완전히 펴지 말고 관절 부담을 줄입니다.",
    "오버헤드 프레스": "복근과 엉덩이에 힘을 주고 바벨을 머리 위 직선으로 밀어 올립니다.",
    "사이드 레터럴 레이즈": "손목이 아닌 팔꿈치를 들어 올려 측면 어깨를 사용합니다.",
    "트라이셉스 케이블 푸쉬다운": "팔꿈치를 옆구리에 고정하고 아래로 밀어 삼두를 삼각 압축합니다.",
    "라잉 트라이셉스 익스텐션": "팔꿈치를 고정하고 이마 수직 방향으로 바를 내렸다 밀어 올립니다.",
    "바벨 컬": "상체 반동을 줄이고 팔꿈치를 고정한 채 이두의 힘으로 끌어올립니다."
}

def get_yt_url(exercise_name):
    query = f"{exercise_name} 자세"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.youtube.com/results?search_query={encoded_query}"

EXERCISE_POOL = {
    "가슴_메인": ["벤치프레스", "인클라인 벤치프레스", "덤벨 벤치프레스", "인클라인 덤벨 벤치프레스"],
    "가슴_서브": ["체스트 프레스 머신", "펙덱 플라이 머신", "케이블 크로스오버", "딥스", "덤벨 플라이"],
    "등_메인": ["데드리프트", "바벨로우", "풀업", "티바로우"],
    "등_서브": ["렛풀다운", "시티드 케이블 로우", "원암 덤벨로우", "어시스트 풀업 머신", "암 풀다운"],
    "하체_메인": ["스쿼트", "레그프레스", "스티프 레그 데드리프트"],
    "하체_서브": ["레그 익스텐션", "레그 컬", "런지", "이너사이 머신", "아웃사이 머신", "카프 레이즈"],
    "어깨_메인": ["오버헤드 프레스", "덤벨 숄더프레스", "숄더프레스 머신"],
    "어깨_서브": ["사이드 레터럴 레이즈", "벤트오버 레터럴 레이즈", "페이스풀", "아놀드 프레스"],
    "삼두": ["트라이셉스 케이블 푸쉬다운", "라잉 트라이셉스 익스텐션", "딥스(삼두)"],
    "이두": ["바벨 컬", "덤벨 컬", "해머 컬", "프리처 컬"],
    "복근/유산소": ["크런치", "레그 레이즈", "플랭크", "천국의 계단(스텝밀)", "런닝머신", "사이클"]
}

ALL_EXERCISES = list(set(sum(EXERCISE_POOL.values(), [])))

def generate_dynamic_routine(routine_type):
    random.seed(time.time())
    if routine_type == "가슴/삼두 DAY":
        return random.sample(EXERCISE_POOL["가슴_메인"], 2) + random.sample(EXERCISE_POOL["가슴_서브"], 2) + random.sample(EXERCISE_POOL["삼두"], 1)
    elif routine_type == "등/이두 DAY":
        return random.sample(EXERCISE_POOL["등_메인"], 2) + random.sample(EXERCISE_POOL["등_서브"], 2) + random.sample(EXERCISE_POOL["이두"], 1)
    elif routine_type == "하체/복근 DAY":
        return random.sample(EXERCISE_POOL["하체_메인"], 2) + random.sample(EXERCISE_POOL["하체_서브"], 2) + random.sample(EXERCISE_POOL["복근/유산소"], 1)
    elif routine_type == "어깨/유산소 DAY":
        return random.sample(EXERCISE_POOL["어깨_메인"], 2) + random.sample(EXERCISE_POOL["어깨_서브"], 2) + random.sample([x for x in EXERCISE_POOL["복근/유산소"] if "런닝" in x or "계단" in x or "사이클" in x], 1)
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
            st.image(prof_path, width=55)
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
        
        routine_options = ["선택 안함", "가슴/삼두 DAY", "등/이두 DAY", "하체/복근 DAY", "어깨/유산소 DAY", "자율 운동"]
        routine_type = st.selectbox("루틴 선택", routine_options)
        
        selected_exercises = []
        if routine_type in ["가슴/삼두 DAY", "등/이두 DAY", "하체/복근 DAY", "어깨/유산소 DAY"]:
            if "random_routine" not in st.session_state or st.session_state.get("current_routine_type") != routine_type:
                st.session_state.random_routine = generate_dynamic_routine(routine_type)
                st.session_state.current_routine_type = routine_type
                
            col_rec1, col_rec2 = st.columns([3, 1])
            with col_rec1: st.info(f"💡 **[{routine_type}]** 추천 조합")
            with col_rec2:
                if st.button("🎲 재추천"):
                    st.session_state.random_routine = generate_dynamic_routine(routine_type)
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
            
            with st.form("workout_input_form"):
                workout_entries = []
                for ex in selected_exercises:
                    st.write(f"🏋️ **{ex}**")
                    
                    tip_text = EXERCISE_TIPS.get(ex, "자극 부위에 집중하여 바른 자세로 수행합니다.")
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
                            <span class="prev-record-title">💡 지난 최다 기록 ({last_date})</span>
                            <span class="prev-record-value">{max_w} kg × {max_r} 회</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.caption("💡 첫 수행 종목입니다.")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: num_sets = st.number_input(f"세트 ({ex})", 1, 10, 3, key=f"s_{ex}")
                    with c2: weight = st.number_input(f"무게kg ({ex})", 0.0, step=2.5, value=20.0, key=f"w_{ex}")
                    with c3: reps = st.number_input(f"횟수 ({ex})", 1, value=10, key=f"r_{ex}")
                    
                    for s in range(1, num_sets + 1):
                        workout_entries.append({
                            "date": str(today_date),
                            "user_id": st.session_state.user_id,
                            "nickname": st.session_state.nickname,
                            "routine": routine_type,
                            "exercise": ex,
                            "set_num": s,
                            "weight": weight,
                            "reps": reps
                        })
                    st.write("---")
                
                memo = st.text_input("오늘의 메모", placeholder="컨디션, 특이사항 등")
                is_private = st.checkbox("🔒 비공개로 저장")
                
                if st.form_submit_button("저장 완료"):
                    for entry in workout_entries:
                        entry["memo"] = memo
                        entry["is_private"] = "True" if is_private else "False"
                    
                    new_df = pd.DataFrame(workout_entries)
                    workouts_df = pd.concat([workouts_df, new_df], ignore_index=True)
                    save_data(workouts_df, WORKOUT_FILE)
                    st.success("성공적으로 저장되었습니다!")

    # TAB 2: 세트 간 휴식 타이머
    with tab_timer:
        st.subheader("⏱️ 휴식 타이머")
        tc1, tc2, tc3, tc4 = st.columns(4)
        
        target_sec = 0
        with tc1:
            if st.button("60초"): target_sec = 60
        with tc2:
            if st.button("90초"): target_sec = 90
        with tc3:
            if st.button("120초"): target_sec = 120
        with tc4:
            if st.button("180초"): target_sec = 180
            
        custom_sec = st.number_input("직접 초 입력", min_value=0, step=10, value=0)
        if custom_sec > 0 and st.button("타이머 시작"): target_sec = custom_sec
            
        if target_sec > 0:
            st.session_state.timer_running = True
            timer_box = st.empty()
            p_bar = st.progress(1.0)
            
            stop_col1, stop_col2 = st.columns([3, 1])
            with stop_col2:
                stop_btn = st.button("⏹️ 중단")
                
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
                        
                    total_vol = (group["weight"] * group["reps"] * group["set_num"]).sum()
                    st.write(f"**볼륨:** `{total_vol:,.0f} kg`")
                    ex_summary = group.groupby("exercise").agg({"set_num": "max", "weight": "max"}).reset_index()
                    for _, row in ex_summary.iterrows():
                        st.write(f"• **{row['exercise']}**: 최고 {row['weight']}kg ({row['set_num']}세트)")
                    memo_val = group["memo"].iloc[0]
                    if pd.notna(memo_val) and str(memo_val).strip():
                        st.caption(f"💬 {memo_val}")
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

    # TAB 6: 내 프로필 수정 및 리포트
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
        st.subheader("📊 내 성장 리포트")
        my_df = workouts_df[workouts_df["user_id"] == st.session_state.user_id]
        if not my_df.empty:
            my_df["volume"] = my_df["weight"] * my_df["reps"] * my_df["set_num"]
            total_vol = my_df["volume"].sum()
            st.metric("총 누적 볼륨", f"{total_vol:,.0f} kg")
            
            vol_by_date = my_df.groupby("date")["volume"].sum().reset_index()
            st.line_chart(vol_by_date.set_index("date"))
        else:
            st.info("등록된 기록이 없습니다.")
