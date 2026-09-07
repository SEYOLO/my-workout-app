import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 다크 테마 레이아웃
st.set_page_config(page_title="운동일지", page_icon="⚡", layout="centered", initial_sidebar_state="collapsed")

USERS_FILE = "users.csv"
FOLLOWS_FILE = "follows.csv"
WORKOUT_FILE = "workout_data.csv"

# 모바일 반응형 및 고급 모던 다크 커스텀 CSS
st.markdown("""
<style>
    /* 전체 배경 및 폰트 설정 */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* 헤더 타이틀 스타일링 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(45deg, #00F2FE, #4FACFE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #8A99AD;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 카드형 컨테이너 스타일링 (글래스모피즘) */
    div[data-testid="stForm"], div.css-1r6sl80, div.stExpander {
        background: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }

    /* 모바일 버튼 터치 영역 최적화 및 스타일 */
    .stButton > button, div[data-testid="stForm"] button {
        width: 100% !important;
        background: linear-gradient(90deg, #2563EB, #1D4ED8) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1D4ED8, #1E40AF) !important;
        transform: translateY(-1px);
    }

    /* 탭 스타일 조정 */
    button[data-baseweb="tab"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #8A99AD !important;
    }
    button[aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom-color: #38BDF8 !important;
    }

    /* 모바일 가로 여백 줄이기 */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 2. 데이터베이스 초기화 함수
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

# 3. 운동 DB 및 루틴
EXERCISE_DB = {
    "가슴": ["벤치프레스", "인클라인 벤치프레스", "덤벨 벤치프레스", "인클라인 덤벨 벤치프레스", "덤벨 플라이", "체스트 프레스 머신", "펙덱 플라이 머신", "케이블 크로스오버", "딥스", "푸쉬업"],
    "등": ["데드리프트", "바벨로우", "렛풀다운", "시티드 케이블 로우", "원암 덤벨로우", "풀업", "어시스트 풀업 머신", "티바로우", "암 풀다운"],
    "하체": ["스쿼트", "레그프레스", "레그 익스텐션", "레그 컬", "런지", "이너사이 머신", "아웃사이 머신", "스티프 레그 데드리프트", "카프 레이즈"],
    "어깨": ["오버헤드 프레스", "덤벨 숄더프레스", "사이드 레터럴 레이즈", "벤트오버 레터럴 레이즈", "페이스풀", "아놀드 프레스", "숄더프레스 머신"],
    "팔": ["바벨 컬", "덤벨 컬", "해머 컬", "프리처 컬", "트라이셉스 케이블 푸쉬다운", "라잉 트라이셉스 익스텐션", "딥스(삼두)"],
    "복근/유산소": ["크런치", "레그 레이즈", "플랭크", "아브슬라이드", "천국의 계단(스텝밀)", "런닝머신", "사이클", "인클라인 런닝머신"]
}
ALL_EXERCISES = list(set(sum(EXERCISE_DB.values(), [])))

ROUTINE_PRESETS = {
    "가슴/삼두 DAY": ["벤치프레스", "인클라인 덤벨 벤치프레스", "체스트 프레스 머신", "펙덱 플라이 머신", "트라이셉스 케이블 푸쉬다운"],
    "등/이두 DAY": ["렛풀다운", "바벨로우", "시티드 케이블 로우", "암 풀다운", "바벨 컬", "해머 컬"],
    "하체/복근 DAY": ["스쿼트", "레그프레스", "레그 익스텐션", "레그 컬", "크런치", "플랭크"],
    "어깨/유산소 DAY": ["오버헤드 프레스", "덤벨 숄더프레스", "사이드 레터럴 레이즈", "페이스풀", "천국의 계단(스텝밀)"]
}

# 4. 세션 관리
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "nickname" not in st.session_state:
    st.session_state.nickname = None

# --- 로그인 / 회원가입 화면 ---
if st.session_state.user_id is None:
    st.markdown("<div class='main-title'>⚡ 운동일지</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>스마트한 루틴 추천과 소셜 세트 일지</div>", unsafe_allow_html=True)
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])
    users_df = load_users()
    
    with auth_tab1:
        # Form으로 감싸서 엔터키 누르면 즉시 로그인 처리
        with st.form("login_form", clear_on_submit=False):
            st.subheader("로그인")
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
            st.subheader("새 계정 만들기")
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
                    st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인해 주세요.")

else:
    # --- 로그인 후 메인 앱 화면 ---
    st.sidebar.title(f"⚡ {st.session_state.nickname}")
    st.sidebar.caption(f"ID: {st.session_state.user_id}")
    if st.sidebar.button("로그아웃"):
        st.session_state.user_id = None
        st.session_state.nickname = None
        st.rerun()
        
    st.markdown("<div class='main-title'>⚡ 운동일지</div>", unsafe_allow_html=True)
    
    tab_workout, tab_feed, tab_friends, tab_history = st.tabs([
        "🔥 운동 기록", "📱 피드", "👥 팔로우", "📅 내 일지"
    ])
    
    # TAB 1: 운동 기록 작성
    with tab_workout:
        st.subheader("오늘의 운동")
        today_date = st.date_input("운동 날짜", datetime.now())
        routine_type = st.selectbox("추천 DAY 선택 또는 자율 구성", ["선택 안함"] + list(ROUTINE_PRESETS.keys()) + ["자율 운동"])
        
        selected_exercises = []
        if routine_type in ROUTINE_PRESETS:
            default_exercises = [ex for ex in ROUTINE_PRESETS[routine_type] if ex in ALL_EXERCISES]
            selected_exercises = st.multiselect("종목 확인 및 변경", options=ALL_EXERCISES, default=default_exercises)
        elif routine_type == "자율 운동":
            selected_exercises = st.multiselect("수행할 종목을 고르세요", options=ALL_EXERCISES)
            
        custom_ex = st.text_input("커스텀 종목 입력 (쉼표 구분)", placeholder="예: 케이블 로우, 스트레칭")
        if custom_ex:
            selected_exercises.extend([x.strip() for x in custom_ex.split(",") if x.strip()])
            
        if selected_exercises:
            st.divider()
            with st.form("workout_input_form"):
                workout_entries = []
                for ex in selected_exercises:
                    st.write(f"🏋️ **{ex}**")
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
                    workouts_df = load_workouts()
                    for entry in workout_entries:
                        entry["memo"] = memo
                        entry["is_private"] = "True" if is_private else "False"
                    
                    new_df = pd.DataFrame(workout_entries)
                    workouts_df = pd.concat([workouts_df, new_df], ignore_index=True)
                    save_data(workouts_df, WORKOUT_FILE)
                    st.balloons()
                    st.success("운동 기록이 성공적으로 저장되었습니다!")

    # TAB 2: 팔로우 소셜 피드
    with tab_feed:
        st.subheader("📱 팔로워 오운완 피드")
        follows_df = load_follows()
        workouts_df = load_workouts()
        
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
            st.info("팔로워들의 운동 기록이 없습니다. 친구를 팔로우하거나 오늘 첫 기록을 작성해 보세요!")

    # TAB 3: 친구 찾기 & 팔로우 관리
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

    # TAB 4: 내 일지 전용 조회
    with tab_history:
        st.subheader("📅 내 개인 운동 기록")
        workouts_df = load_workouts()
        my_df = workouts_df[workouts_df["user_id"] == st.session_state.user_id]
        
        if not my_df.empty:
            st.dataframe(my_df.sort_values(by="date", ascending=False), use_container_width=True)
        else:
            st.info("아직 등록된 운동 기록이 없습니다.")
