import streamlit as st
import pandas as pd
import os
import time
import random
from datetime import datetime
import urllib.parse

# 1. 페이지 기본 설정 및 모던 패션 브랜드풍 스타일링
st.set_page_config(page_title="운동일지 ⚡", page_icon="⚡", layout="centered", initial_sidebar_state="collapsed")

USERS_FILE = "users.csv"
FOLLOWS_FILE = "follows.csv"
WORKOUT_FILE = "workout_data.csv"

# Ultra Dark Glassmorphic Modern UI CSS
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif; }
    
    .stApp {
        background: #0B0E14;
        color: #F1F5F9;
    }

    /* 메인 히어로 브랜딩 타이틀 */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: radial-gradient(circle at top, rgba(56, 189, 248, 0.15) 0%, rgba(11, 14, 20, 0) 70%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1.8rem;
    }
    .hero-logo {
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 50%, #60A5FA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        text-shadow: 0 0 30px rgba(56, 189, 248, 0.3);
    }
    .hero-subtitle {
        font-size: 0.95rem;
        font-weight: 600;
        color: #94A3B8;
        letter-spacing: -0.02em;
    }
    .hero-tags {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    .tag {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(51, 65, 85, 0.8);
        color: #38BDF8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* 하이라이트 기능 피처 카드 */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .feature-card {
        background: #131722;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
    }
    .feature-icon { font-size: 1.4rem; margin-bottom: 4px; }
    .feature-title { font-size: 0.8rem; font-weight: 700; color: #E2E8F0; }
    .feature-desc { font-size: 0.7rem; color: #64748B; margin-top: 2px; }

    /* 고급 카드 컨테이너 */
    div[data-testid="stForm"], div.stExpander {
        background: #131722 !important;
        border: 1px solid #1E293B !important;
        border-radius: 18px !important;
        padding: 22px !important;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7) !important;
    }

    /* 터치 버튼 디자인 */
    .stButton > button, div[data-testid="stForm"] button {
        width: 100% !important;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        letter-spacing: -0.02em !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:active { transform: scale(0.98); }

    /* 지난 기록 팁 카드 */
    .prev-record-card {
        background: rgba(56, 189, 248, 0.08);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 12px; padding: 12px 16px; margin-bottom: 10px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .prev-record-title { font-size: 0.85rem; color: #38BDF8; font-weight: 700; }
    .prev-record-value { font-size: 0.95rem; color: #F8FAFC; font-weight: 800; }
    .guide-box {
        background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.85rem; color: #FBBF24;
    }

    /* 탭 헤더 스타일링 */
    button[data-baseweb="tab"] { font-size: 0.92rem !important; font-weight: 700 !important; color: #64748B !important; }
    button[aria-selected="true"] { color: #38BDF8 !important; border-bottom: 2.5px solid #38BDF8 !important; }

    @media (max-width: 640px) {
        .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; padding-top: 0.5rem !important; }
        .hero-logo { font-size: 2.5rem; }
        .feature-grid { grid-template-columns: repeat(3, 1fr); gap: 6px; }
        .feature-title { font-size: 0.72rem; }
        .feature-desc { font-size: 0.62rem; }
    }
</style>
""", unsafe_allow_html=True)

# 2. DB 초기화 함수
def init_db():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["user_id", "password", "nickname", "bio"]).to_csv(USERS_FILE, index=False)
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

# --- [고급 랜딩 메인 화면 (로그인 전)] ---
if st.session_state.user_id is None:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-logo">WORKOUT ⚡</div>
        <div class="hero-subtitle">스마트 세트일지 & 소셜 피드 시스템</div>
        <div class="hero-tags">
            <span class="tag">#점진적과부하</span>
            <span class="tag">#동적루틴추천</span>
            <span class="tag">#소셜출석</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])
    users_df = load_users()
    
    with auth_tab1:
        with st.form("login_form", clear_on_submit=False):
            st.subheader("계정 접속")
            login_id = st.text_input("아이디", key="login_id").strip()
            login_pw = st.text_input("비밀번호", type="password", key="login_pw").strip()
            submit_login = st.form_submit_button("로그인 (Enter)")
            
            if submit_login:
                user_match = users_df[(users_df["user_id"] == login_id) & (users_df["password"] == login_pw)]
                if not user_match.empty:
                    st.session_state.user_id = login_id
                    st.session_state.nickname = user_match.iloc[0]["nickname"]
                    st.success(f"환영합니다, {st.session_state.nickname}님!")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

    with auth_tab2:
        with st.form("signup_form"):
            st.subheader("새 계정 생성")
            new_id = st.text_input("사용할 아이디", key="new_id").strip()
            new_pw = st.text_input("비밀번호", type="password", key="new_pw").strip()
            new_nick = st.text_input("앱에서 사용할 닉네임", key="new_nick").strip()
            new_bio = st.text_input("한 줄 상태메시지 (선택)", key="new_bio", placeholder="예: 3대 500 목표!").strip()
            submit_signup = st.form_submit_button("회원가입 완료")
            
            if submit_signup:
                if not new_id or not new_pw or not new_nick:
                    st.error("아이디, 비밀번호, 닉네임은 필수 항목입니다.")
                elif new_id in users_df["user_id"].values:
                    st.error("이미 존재하는 아이디입니다.")
                elif new_nick in users_df["nickname"].values:
                    st.error("이미 사용 중인 닉네임입니다.")
                else:
                    new_user = pd.DataFrame([{"user_id": new_id, "password": new_pw, "nickname": new_nick, "bio": new_bio}])
                    users_df = pd.concat([users_df, new_user], ignore_index=True)
                    save_data(users_df, USERS_FILE)
                    st.success("회원가입 완료! 로그인 탭에서 로그인해 주세요.")

    # 앱 하이라이트 기능 안내 피처 카드
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🎲</div>
            <div class="feature-title">동적 루틴</div>
            <div class="feature-desc">매일 새로운 자극 조합</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⏱️</div>
            <div class="feature-title">휴식 타이머</div>
            <div class="feature-desc">세트간 원클릭 측정</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <div class="feature-title">소셜 피드</div>
            <div class="feature-desc">팔로워 출석 달력</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # --- [로그인 후 메인 앱 화면] ---
    st.sidebar.title(f"⚡ {st.session_state.nickname}")
    st.sidebar.caption(f"ID: {st.session_state.user_id}")
    if st.sidebar.button("로그아웃"):
        st.session_state.user_id = None
        st.session_state.nickname = None
        st.rerun()
        
    st.markdown("""
    <div style="text-align: center; margin-top: 0.5rem; margin-bottom: 1.2rem;">
        <span style="font-size: 2rem; font-weight: 900; background: linear-gradient(135deg, #00F2FE, #4FACFE); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            WORKOUT ⚡
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    tab_workout, tab_timer, tab_feed, tab_calendar, tab_friends, tab_history = st.tabs([
        "🔥 운동 기록", "⏱️ 타이머", "📱 피드", "📅 소셜 달력", "👥 팔로우", "📊 내 리포트"
    ])
    
    workouts_df = load_workouts()
    
    # TAB 1: 운동 기록 작성
    with tab_workout:
        st.subheader("오늘의 운동")
        today_date = st.date_input("운동 날짜", datetime.now())
        
        routine_options = ["선택 안함", "가슴/삼두 DAY", "등/이두 DAY", "하체/복근 DAY", "어깨/유산소 DAY", "자율 운동"]
        routine_type = st.selectbox("추천 DAY 선택 또는 자율 구성", routine_options)
        
        selected_exercises = []
        if routine_type in ["가슴/삼두 DAY", "등/이두 DAY", "하체/복근 DAY", "어깨/유산소 DAY"]:
            if "random_routine" not in st.session_state or st.session_state.get("current_routine_type") != routine_type:
                st.session_state.random_routine = generate_dynamic_routine(routine_type)
                st.session_state.current_routine_type = routine_type
                
            col_rec1, col_rec2 = st.columns([3, 1])
            with col_rec1: st.info(f"💡 **[{routine_type}]** 오늘의 추천 무작위 조합입니다.")
            with col_rec2:
                if st.button("🎲 다시 추천"):
                    st.session_state.random_routine = generate_dynamic_routine(routine_type)
                    st.rerun()
                    
            selected_exercises = st.multiselect("수행할 종목 수정 및 추가", options=ALL_EXERCISES, default=st.session_state.random_routine)
            
        elif routine_type == "자율 운동":
            selected_exercises = st.multiselect("수행할 종목을 고르세요", options=ALL_EXERCISES)
            
        custom_ex = st.text_input("커스텀 종목 입력 (쉼표 구분)", placeholder="예: 케이블 로우, 스트레칭")
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
                        📌 <b>자세 팁:</b> {tip_text} <a href="{yt_link}" target="_blank" style="color: #38BDF8; margin-left: 8px; font-weight: 700; text-decoration: none;">[▶️ 유튜브 자세 영상]</a>
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
                
                memo = st.text_input("오늘의 피드백/메모", placeholder="컨디션 최상, 삼두 자극 잘 옴")
                is_private = st.checkbox("🔒 나만 보기 (팔로우 피드에 비공개)")
                
                if st.form_submit_button("오늘 운동 저장 완료! 💪"):
                    for entry in workout_entries:
                        entry["memo"] = memo
                        entry["is_private"] = "True" if is_private else "False"
                    
                    new_df = pd.DataFrame(workout_entries)
                    workouts_df = pd.concat([workouts_df, new_df], ignore_index=True)
                    save_data(workouts_df, WORKOUT_FILE)
                    st.success("운동 기록이 성공적으로 저장되었습니다!")

    # TAB 2: 세트 간 휴식 타이머
    with tab_timer:
        st.subheader("⏱️ 세트 간 휴식 카운트다운")
        tc1, tc2, tc3, tc4 = st.columns(4)
        set_seconds = 0
        with tc1:
            if st.button("60초"): set_seconds = 60
        with tc2:
            if st.button("90초"): set_seconds = 90
        with tc3:
            if st.button("120초"): set_seconds = 120
        with tc4:
            if st.button("180초"): set_seconds = 180
            
        custom_sec = st.number_input("직접 초 입력", min_value=0, step=10, value=0)
        if custom_sec > 0 and st.button("타이머 시작"): set_seconds = custom_sec
            
        if set_seconds > 0:
            timer_placeholder = st.empty()
            progress_bar = st.progress(1.0)
            for remaining in range(set_seconds, -1, -1):
                mins, secs = divmod(remaining, 60)
                timer_placeholder.markdown(f"<h1 style='text-align: center; color: #38BDF8; font-size: 4rem; font-weight: 900;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
                progress_bar.progress(remaining / set_seconds)
                time.sleep(1)
            timer_placeholder.markdown("<h1 style='text-align: center; color: #4ADE80; font-size: 2rem; font-weight: 800;'>🔥 휴식 끝! 다음 세트 시작!</h1>", unsafe_allow_html=True)

    # TAB 3: 팔로우 피드
    with tab_feed:
        st.subheader("📱 팔로워 오운완 피드")
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
                card_title = f"💪 {nick}님의 오운완 ({date})" if not is_me else f"💪 나의 운동 ({date})"
                with st.expander(f"{card_title} - [{routine}]", expanded=True):
                    total_vol = (group["weight"] * group["reps"] * group["set_num"]).sum()
                    st.write(f"**총 누적 볼륨:** `{total_vol:,.0f} kg`")
                    ex_summary = group.groupby("exercise").agg({"set_num": "max", "weight": "max"}).reset_index()
                    for _, row in ex_summary.iterrows():
                        st.write(f"• **{row['exercise']}**: 최고 {row['weight']}kg ({row['set_num']} 세트)")
                    memo_val = group["memo"].iloc[0]
                    if pd.notna(memo_val) and str(memo_val).strip():
                        st.caption(f"💬 메모: {memo_val}")
        else:
            st.info("팔로워들의 운동 기록이 아직 없습니다.")

    # TAB 4: 팔로워 통합 출석 달력
    with tab_calendar:
        st.subheader("📅 팔로워 출석 현황 달력")
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
                st.write(f"### 🗓️ {year}년 {month}월 출석 현황")
                attendance = month_df.groupby(["date", "nickname"])["routine"].first().unstack(fill_value=None)
                st.dataframe(attendance.sort_index(ascending=False), use_container_width=True)
            else:
                st.info(f"{year}년 {month}월에 등록된 운동 출석 기록이 없습니다.")
        else:
            st.info("출석 데이터를 표출할 기록이 없습니다.")

    # TAB 5: 친구 찾기 & 팔로우
    with tab_friends:
        st.subheader("👥 친구 찾기 및 팔로우")
        users_df = load_users()
        follows_df = load_follows()
        
        search_nick = st.text_input("친구 닉네임 검색", placeholder="닉네임 입력").strip()
        if search_nick:
            target_user = users_df[users_df["nickname"] == search_nick]
            if not target_user.empty:
                t_id = target_user.iloc[0]["user_id"]
                t_nick = target_user.iloc[0]["nickname"]
                t_bio = target_user.iloc[0]["bio"]
                
                if t_id == st.session_state.user_id:
                    st.warning("자기 자신은 팔로우할 수 없습니다.")
                else:
                    st.write(f"**{t_nick}** ({t_bio if pd.notna(t_bio) else '소개글 없음'})")
                    is_following = not follows_df[
                        (follows_df["follower_id"] == st.session_state.user_id) & 
                        (follows_df["following_id"] == t_id)
                    ].empty
                    
                    if is_following:
                        if st.button(f"{t_nick}님 언팔로우"):
                            follows_df = follows_df[~(
                                (follows_df["follower_id"] == st.session_state.user_id) & 
                                (follows_df["following_id"] == t_id)
                            )]
                            save_data(follows_df, FOLLOWS_FILE)
                            st.success(f"{t_nick}님을 언팔로우했습니다.")
                            st.rerun()
                    else:
                        if st.button(f"{t_nick}님 팔로우하기"):
                            new_follow = pd.DataFrame([{"follower_id": st.session_state.user_id, "following_id": t_id}])
                            follows_df = pd.concat([follows_df, new_follow], ignore_index=True)
                            save_data(follows_df, FOLLOWS_FILE)
                            st.success(f"{t_nick}님을 팔로우합니다!")
                            st.rerun()
            else:
                st.error("해당 닉네임을 가진 유저를 찾을 수 없습니다.")

        st.divider()
        st.write("### 내 팔로우 목록")
        my_follows = follows_df[follows_df["follower_id"] == st.session_state.user_id]
        if not my_follows.empty:
            followed_users = users_df[users_df["user_id"].isin(my_follows["following_id"])]
            for _, f_row in followed_users.iterrows():
                st.write(f"• **{f_row['nickname']}** (`{f_row['user_id']}`)")
        else:
            st.caption("아직 팔로우한 친구가 없습니다.")

    # TAB 6: 내 리포트 및 성장 분석
    with tab_history:
        st.subheader("📊 내 개인 운동 리포트")
        my_df = workouts_df[workouts_df["user_id"] == st.session_state.user_id]
        
        if not my_df.empty:
            my_df["volume"] = my_df["weight"] * my_df["reps"] * my_df["set_num"]
            total_vol = my_df["volume"].sum()
            st.metric("총 누적 운동 볼륨", f"{total_vol:,.0f} kg")
            
            vol_by_date = my_df.groupby("date")["volume"].sum().reset_index()
            st.line_chart(vol_by_date.set_index("date"))
            
            st.divider()
            st.write("### 전체 세부 기록 데이터")
            st.dataframe(my_df.sort_values(by="date", ascending=False), use_container_width=True)
        else:
            st.info("아직 등록된 운동 기록이 없습니다.")
