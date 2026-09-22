import streamlit as st
import pandas as pd
import plotly.express as px
 
# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 2", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
 
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
 
 
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
 
    # genre 열에 세로막대(|) 기호로 여러 장르가 적힌 경우 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()
 
    # openDt(개봉일)를 날짜 형식으로 변환 (여덟 자리 숫자 문자열/정수 형태)
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str).str.zfill(8), format="%Y%m%d", errors="coerce"
        )
 
    return df
 
 
df = load_data(DATA_URL)
 
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 해당 기간에 개봉한 216편의 요약 데이터입니다."
)
 
with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 1: 장르별 영화 편수 - 도넛 그래프
# ------------------------------------------------------------
st.header("1. 장르별 영화 편수")
 
genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["genre", "count"]
 
fig_donut = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_donut.update_traces(
    textinfo="label+percent",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_donut.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)
 
st.plotly_chart(fig_donut, use_container_width=True)
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 2: 장르 안의 영화 - 트리맵 (크기: 총 관객)
# ------------------------------------------------------------
st.header("2. 장르별 영화 - 총 관객 트리맵")
 
fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="%{label}<br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(margin=dict(t=30, b=30, l=10, r=10))
 
st.plotly_chart(fig_treemap, use_container_width=True)
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 3: 총 관객 히스토그램
# ------------------------------------------------------------
st.header("3. 총 관객 분포 - 히스토그램")
 
fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
)
fig_hist.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 수",
    margin=dict(t=30, b=30, l=10, r=10),
)
 
st.plotly_chart(fig_hist, use_container_width=True)
 
# 대부분의 영화가 몰려 있는 구간과 최고 흥행작을 계산
count_series = pd.cut(df["total_audi"], bins=30).value_counts(sort=False)
top_bin = count_series.idxmax()
top_movie_row = df.loc[df["total_audi"].idxmax()]
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info(
    f"대부분의 영화는 총 관객 {int(top_bin.left):,}명 ~ {int(top_bin.right):,}명 구간에 몰려 있고, "
    f"가장 관객이 많은 영화는 '{top_movie_row['movieNm']}'({int(top_movie_row['total_audi']):,}명)입니다."
)
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 4: 개봉일 스크린수 vs 총 관객 - 산점도
# ------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")
 
fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객"},
)
fig_scatter.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)
 
st.plotly_chart(fig_scatter, use_container_width=True)
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 5: 장르별 총 관객 - 상자 그림 (영화 10편 이상 장르만)
# ------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 - 상자 그림")
 
genre_size = df["genre"].value_counts()
valid_genres = genre_size[genre_size >= 10].index
box_df = df[df["genre"].isin(valid_genres)]
 
fig_box = px.box(
    box_df,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_data={"movieNm": True},
    labels={"genre": "장르", "total_audi": "총 관객"},
)
fig_box.update_layout(margin=dict(t=30, b=30, l=10, r=10))
 
st.plotly_chart(fig_box, use_container_width=True)
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 6: 개봉일 스크린수 vs 총 관객 - 버블 그래프 (크기: 첫 주 관객)
# ------------------------------------------------------------
st.header("6. 개봉일 스크린수와 총 관객의 관계 - 버블 그래프")
 
fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
    },
)
fig_bubble.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)
 
st.plotly_chart(fig_bubble, use_container_width=True)
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 7: 제작 국가 -> 장르 - 선버스트 그래프 (크기: 영화 편수)
# ------------------------------------------------------------
st.header("7. 제작 국가별 장르 구성 - 선버스트 그래프")
 
sunburst_df = (
    df.groupby(["nation", "genre"]).size().reset_index(name="count")
)
 
fig_sunburst = px.sunburst(
    sunburst_df,
    path=["nation", "genre"],
    values="count",
)
fig_sunburst.update_traces(
    hovertemplate="%{label}<br>편수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(margin=dict(t=30, b=30, l=10, r=10))
 
st.plotly_chart(fig_sunburst, use_container_width=True)
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")
 
st.divider()
 
# ------------------------------------------------------------
# 그래프 8: 10위권 체류 일수와 총 관객의 관계
# ------------------------------------------------------------
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")
 
fig_top10 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={"days_in_top10": "10위권에 머문 날수", "total_audi": "총 관객"},
)
fig_top10.update_layout(margin=dict(t=50, b=30, l=10, r=10))
 
st.plotly_chart(fig_top10, use_container_width=True)
 
st.markdown("**이 그래프로 알 수 있는 것:**")
st.info("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")
 
st.divider()
 
