import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="루틴 추천 & 운동 일지", page_icon="🏋️‍♂️", layout="centered")

DATA_FILE = "workout_data.csv"

# 2. 운동 기구 및 종목 데이터베이스 (50여 개)
EXERCISE_DB = {
    "가슴": ["벤치프레스", "인클라인 벤치프레스", "덤벨 벤치프레스", "덤벨 플라이", "체스트 프레스 머신", "펙덱 플라이 머신", "케이블 크로스오버", "딥스", "푸쉬업"],
    "등": ["데드리프트", "바벨로우", "렛풀다운", "시티드 케이블 로우", "원암 덤벨로우", "풀업", "어시스트 풀업 머신", "티바로우", "암 풀다운"],
    "하체": ["스쿼트", "레그프레스", "레그 익스텐션", "레그 컬", "런지", "이너사이 머신", "아웃사이 머신", "스티프 레그 데드리프트", "카프 레이즈"],
    "어깨": ["오버헤드 프레스", "덤벨 숄더프레스", "사이드 레터럴 레이즈", "벤트오버 레터럴 레이즈", "페이스풀", "아놀드 프레스", "숄더프레스 머신"],
    "팔": ["바벨 컬", "덤벨 컬", "해머 컬", "프리처 컬", "트라이셉스 케이블 푸쉬다운", "라잉 트라이셉스 익스텐션", "딥스(삼두)"],
    "복근/유산소": ["크런치", "레그 레이즈", "플랭크", "아브슬라이드", "천국의 계단(스텝밀)", "런닝머신", "사이클", "인클라인 런닝머신"]
}

# 3. DAY별 추천 루틴 프리셋
ROUTINE_PRESETS = {
    "가슴/삼두 DAY": ["벤치프레스", "인클라인 덤벨 프레스", "체스트 프레스 머신", "펙덱 플라이 머신", "트라이셉스 케이블 푸쉬다운"],
    "등/이두 DAY": ["렛풀다운", "바벨로우", "시티드 케이블 로우", "암 풀다운", "바벨 컬", "해머 컬"],
    "하체/복근 DAY": ["스쿼트", "레그프레스", "레그 익스텐션", "레그 컬", "크런치", "플랭크"],
    "어깨/유산소 DAY": ["오버헤드 프레스", "덤벨 숄더프레스", "사이드 레터럴 레이즈", "페이스풀", "천국의 계단(스텝밀)"]
}

# 데이터 로드
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["date", "user", "routine", "exercise", "set_num", "weight", "reps", "memo"])

# 데이터 저장
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

st.title("🏋️‍♂️ 운동 루틴 추천 & 세트 일지")

# 상단 로그인/사용자 선택
col_u1, col_u2 = st.columns([2, 2])
with col_u1:
    user_name = st.text_input("사용자 이름 (로그인)", value="세열")
with col_u2:
    today_date = st.date_input("운동 날짜", datetime.now())

st.divider()

# TAB 구성
tab1, tab2 = st.tabs(["🔥 오늘의 운동 (루틴/입력)", "📅 기록 조회"])

# TAB 1: 운동 선택 및 입력
with tab1:
    st.subheader("1. 오늘 수행할 루틴 선택")
    routine_type = st.selectbox("추천 DAY 선택 또는 직접 구성", ["선택 안함"] + list(ROUTINE_PRESETS.keys()) + ["자율 운동"])
    
    selected_exercises = []
    
    if routine_type in ROUTINE_PRESETS:
        st.info(f"💡 **[{routine_type}]** 추천 운동 목록입니다. 헬스장 환경에 맞게 종목을 변경/추가할 수 있습니다.")
        default_exercises = ROUTINE_PRESETS[routine_type]
        selected_exercises = st.multiselect("수행할 종목 확인 및 수정", options=sum(EXERCISE_DB.values(), []), default=default_exercises)
    elif routine_type == "자율 운동":
        selected_exercises = st.multiselect("오늘 수행할 종목을 고르세요", options=sum(EXERCISE_DB.values(), []))
    
    # 직접 입력 종목 추가
    custom_ex = st.text_input("목록에 없는 운동이 있다면 직접 입력하세요 (쉼표로 구분)", placeholder="예: 케이블 언더그립 로우, 폼롤러 스트레칭")
    if custom_ex:
        custom_list = [x.strip() for x in custom_ex.split(",") if x.strip()]
        selected_exercises.extend(custom_list)

    if selected_exercises:
        st.divider()
        st.subheader("2. 세트별 무게 및 횟수 입력")
        
        with st.form("workout_input_form"):
            workout_entries = []
            
            for ex in selected_exercises:
                st.write(f"🏋️ **{ex}**")
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    num_sets = st.number_input(f"세트 수 ({ex})", min_value=1, max_value=10, value=3, key=f"sets_{ex}")
                with col_s2:
                    weight = st.number_input(f"무게 kg ({ex})", min_value=0.0, step=2.5, value=20.0, key=f"weight_{ex}")
                with col_s3:
                    reps = st.number_input(f"횟수 Reps ({ex})", min_value=1, value=10, key=f"reps_{ex}")
                
                for s in range(1, num_sets + 1):
                    workout_entries.append({
                        "date": str(today_date),
                        "user": user_name,
                        "routine": routine_type,
                        "exercise": ex,
                        "set_num": s,
                        "weight": weight,
                        "reps": reps
                    })
                st.write("---")
            
            memo = st.text_input("오늘의 운동 총평/메모", placeholder="컨디션 좋음, 자극 잘 들어옴")
            submit_btn = st.form_submit_button("오늘 운동 저장 완료! 💪")
            
            if submit_btn:
                for entry in workout_entries:
                    entry["memo"] = memo
                new_df = pd.DataFrame(workout_entries)
                df = pd.concat([df, new_df], ignore_index=True)
                save_data(df)
                st.balloons()
                st.success("운동 기록이 성공적으로 저장되었습니다!")

# TAB 2: 기록 조회
with tab2:
    st.subheader("전체 운동 기록 데이터")
    if not df.empty:
        users = ["전체"] + list(df["user"].unique())
        sel_u = st.selectbox("유저 필터", users)
        
        filtered = df if sel_u == "전체" else df[df["user"] == sel_u]
        st.dataframe(filtered.sort_values(by="date", ascending=False), use_container_width=True)
    else:
        st.info("아직 기록이 없습니다.")