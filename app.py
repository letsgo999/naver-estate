# file: app.py
import os
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import requests
import streamlit as st

# ──────────────────────────────────────────────────────────────────────
# 0) 환경 변수 / secrets 에 인증정보 저장하기 ─────────────────────────
#    - Streamlit Cloud에 배포할 땐 Settings ▸ Secrets 탭에서 입력
# ──────────────────────────────────────────────────────────────────────
COOKIES = {
    "NNB": st.secrets["NNB"],
    "NAC": st.secrets["NAC"],
    # 필요 시 추가 쿠키…
}
HEADERS = {
    "accept": "*/*",
    "accept-language": "ko,en-US;q=0.9",
    "referer": "https://new.land.naver.com/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "authorization": f"Bearer {st.secrets['JWT']}",
}

# ──────────────────────────────────────────────────────────────────────
# 1) API 호출 & 데이터 전처리 함수
# ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_complex_overview(complex_no: str) -> Dict[str, Any]:
    """단지 번호(complex_no)의 개요 정보 조회"""
    url = f"https://new.land.naver.com/api/complexes/overview/{complex_no}"
    resp = requests.get(
        url,
        params={"complexNo": complex_no},
        cookies=COOKIES,
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def flatten_overview(data: Dict[str, Any]) -> Dict[str, Any]:
    """API 응답 JSON → 1-레벨 dict (CSV/표용)"""
    rp = data.get("realPrice", {})
    return {
        "단지번호": data.get("complexNo"),
        "단지명": data.get("complexName"),
        "준공일": data.get("useApproveYmd"),
        "세대수": data.get("totalHouseHoldCount"),
        "동수": data.get("totalDongCount"),
        "위도": data.get("latitude"),
        "경도": data.get("longitude"),
        "최저매매가(만)": data.get("minPrice"),
        "최고매매가(만)": data.get("maxPrice"),
        "최근거래일": rp.get("formattedTradeYearMonth"),
        "최근거래가(만)": rp.get("dealPrice"),
        "층": rp.get("floor"),
        "전용면적": rp.get("exclusiveArea"),
    }


def collect_overviews(complex_list: List[str]) -> pd.DataFrame:
    """여러 단지를 조회해 DataFrame 반환"""
    records = []
    for cplx in complex_list:
        try:
            raw = fetch_complex_overview(cplx.strip())
            records.append(flatten_overview(raw))
        except Exception as e:
            st.warning(f"⚠️ {cplx} 조회 실패: {e}")
    return pd.DataFrame(records)


# ──────────────────────────────────────────────────────────────────────
# 2) Streamlit UI
# ──────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="네이버 부동산 단지 개요 수집기",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏙️ 네이버 부동산 단지 개요 수집기")
st.markdown(
    """
단지 번호를 **콤마(,)** 로 구분해서 입력하고 **[데이터 수집]** 을 누르세요.  
CSV로 저장한 뒤 바로 다운로드할 수 있습니다.
"""
)

# 입력 폼
with st.form("input_form"):
    complex_input = st.text_input(
        "단지 번호 목록 (예: 110991,123456…)", value="110991"
    )
    filename = st.text_input(
        "저장할 CSV 파일명", value="complex_overview.csv"
    )
    submitted = st.form_submit_button("데이터 수집")

# 버튼 클릭 시 실행
if submitted:
    complex_numbers = [x for x in complex_input.split(",") if x.strip()]
    if not complex_numbers:
        st.error("단지 번호를 한 개 이상 입력해 주세요.")
        st.stop()

    with st.spinner("데이터 수집 중…"):
        df = collect_overviews(complex_numbers)

    if df.empty:
        st.error("조회된 데이터가 없습니다.")
    else:
        st.success(f"{len(df):,}건의 데이터를 가져왔습니다!")

        # 표 출력
        st.dataframe(df, use_container_width=True)

        # CSV 다운로드
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="CSV 다운로드",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
        )

        # 선택: 저장 경로에도 파일 기록 (로컬 실행용)
        try:
            Path(filename).write_bytes(csv_data.encode("utf-8-sig"))
        except Exception:
            pass

# 사이드바 도움말
with st.sidebar.expander("❓ 사용법"):
    st.write(
        """
1. `.streamlit/secrets.toml` 또는 **Streamlit Cloud → Secrets** 에  
