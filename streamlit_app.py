import streamlit as st
from google.cloud import language_v1
import os
from dotenv import load_dotenv
import json

# .env 파일에서 환경 변수를 로드합니다.
# .env 파일이 루트 폴더에 있으므로 경로를 따로 지정하지 않습니다.
load_dotenv()

# Google Cloud 서비스 계정 키 파일 경로를 환경 변수에서 가져옵니다.
# 이 경로는 .env 파일에 정의되어 있습니다.
# try:
#     key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#     if key_path is None:
#         raise ValueError(
#             "환경 변수 'GOOGLE_APPLICATION_CREDENTIALS'를 찾을 수 없습니다."
#         )

#     # 환경 변수에 키 파일 경로를 설정합니다.
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

# except Exception as e:
#     st.error(f"환경 변수 로드 오류: {e}")
#     st.stop()


try:
    # Use st.secrets to access the content of the JSON key file
    credentials_dict = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])

    # Initialize the client with the credentials
    client = language_v1.LanguageServiceClient.from_service_account_info(
        credentials_dict
    )
except Exception as e:
    st.error(f"Google Cloud API 클라이언트 초기화 오류: {e}")
    st.stop()


# 구글 자연어 API 클라이언트 초기화
try:
    client = language_v1.LanguageServiceClient()
except Exception as e:
    st.error(f"Google Cloud API 클라이언트 초기화 오류: {e}")
    st.stop()


def analyze_sentiment(text_content):
    """
    구글 자연어 API를 사용해 텍스트의 감성을 분석하는 함수
    """
    try:
        document = language_v1.Document(
            content=text_content,
            type_=language_v1.Document.Type.PLAIN_TEXT,
            language="ko",
        )
        sentiment = client.analyze_sentiment(
            request={"document": document}
        ).document_sentiment
        return sentiment.score, sentiment.magnitude
    except Exception as e:
        st.error(f"감성 분석 중 오류가 발생했습니다: {e}")
        return None, None


# --- Streamlit 웹 앱 UI 구성 ---
st.set_page_config(page_title="감성 분석기", layout="wide")

st.title("텍스트 감성 분석기")
st.markdown(
    """
    이 앱은 구글 클라우드 자연어 처리 API를 사용하여 입력한 텍스트의 감성을 분석합니다.
    """
)

# 사용자 입력
text_input = st.text_area("여기에 감성 분석을 원하는 문장을 입력하세요:", height=150)

if st.button("분석하기"):
    if not text_input:
        st.warning("분석할 텍스트를 입력해주세요.")
    else:
        with st.spinner("분석 중..."):
            score, magnitude = analyze_sentiment(text_input)

            if score is not None and magnitude is not None:
                st.subheader("분석 결과")

                # 감성 점수와 강도 표시
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("감성 점수 (Score)", f"{score:.2f}")

                with col2:
                    st.metric("감정 강도 (Magnitude)", f"{magnitude:.2f}")

                st.markdown("---")

                # 결과 해석
                if score > 0.2:
                    st.success(
                        f"**긍정적인 문장**입니다! 점수: {score:.2f}, 강도: {magnitude:.2f}"
                    )
                elif score < -0.2:
                    st.error(
                        f"**부정적인 문장**입니다! 점수: {score:.2f}, 강도: {magnitude:.2f}"
                    )
                else:
                    st.info(
                        f"**중립적인 문장**입니다! 점수: {score:.2f}, 강도: {magnitude:.2f}"
                    )
