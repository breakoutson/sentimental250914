# import streamlit as st
# from google.cloud import language_v1
# import os
# from dotenv import load_dotenv
# import json
# import re

# # .env 파일에서 환경 변수를 로드합니다.
# # .env 파일이 루트 폴더에 있으므로 경로를 따로 지정하지 않습니다.
# load_dotenv()


# def format_private_key(private_key):
#     """private_key를 올바른 형식으로 변환"""
#     # BEGIN과 END 사이의 키 데이터만 추출
#     key_data = (
#         private_key.replace("-----BEGIN PRIVATE KEY-----", "")
#         .replace("-----END PRIVATE KEY-----", "")
#         .strip()
#     )

#     # 64자씩 끊어서 개행 문자 추가
#     formatted_lines = []
#     for i in range(0, len(key_data), 64):
#         formatted_lines.append(key_data[i : i + 64])

#     # 올바른 형식으로 재조립
#     return (
#         "-----BEGIN PRIVATE KEY-----\n"
#         + "\n".join(formatted_lines)
#         + "\n-----END PRIVATE KEY-----\n"
#     )


# try:
#     # secrets에서 credentials 가져오기
#     credentials_raw = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
#     credentials_json = credentials_raw.strip()
#     credentials_json = re.sub(r"[\r\n\t]", "", credentials_json)
#     credentials_json = credentials_json.replace("\\n", "\n")
#     credentials_dict = json.loads(credentials_json)

#     # private_key 재포맷
#     credentials_dict["private_key"] = format_private_key(
#         credentials_dict["private_key"]
#     )

#     # 클라이언트 초기화 (한 번만!)
#     client = language_v1.LanguageServiceClient.from_service_account_info(
#         credentials_dict
#     )

#     st.success("Google Cloud API 클라이언트 초기화 성공!")

#     # 여기서 client를 사용해서 실제 작업 수행
#     # 예: 감정 분석
#     # document = language_v1.Document(content="Hello world", type_=language_v1.Document.Type.PLAIN_TEXT)
#     # response = client.analyze_sentiment(request={"document": document})

# except Exception as e:
#     st.error(f"오류: {e}")
#     st.stop()


# def analyze_sentiment(text_content):
#     """
#     구글 자연어 API를 사용해 텍스트의 감성을 분석하는 함수
#     """
#     try:
#         document = language_v1.Document(
#             content=text_content,
#             type_=language_v1.Document.Type.PLAIN_TEXT,
#             language="ko",
#         )
#         sentiment = client.analyze_sentiment(
#             request={"document": document}
#         ).document_sentiment
#         return sentiment.score, sentiment.magnitude
#     except Exception as e:
#         st.error(f"감성 분석 중 오류가 발생했습니다: {e}")
#         return None, None


# # --- Streamlit 웹 앱 UI 구성 ---
# st.set_page_config(page_title="감성 분석기", layout="wide")

# st.title("텍스트 감성 분석기")
# st.markdown(
#     """
#     자연어 처리를 사용하여 입력한 텍스트의 감성을 분석합니다. -breakoutson
#     """
# )

# # 사용자 입력
# text_input = st.text_area("여기에 감성 분석을 원하는 문장을 입력하세요:", height=150)

# if st.button("분석하기"):
#     if not text_input:
#         st.warning("분석할 텍스트를 입력해주세요.")
#     else:
#         with st.spinner("분석 중..."):
#             score, magnitude = analyze_sentiment(text_input)

#             if score is not None and magnitude is not None:
#                 st.subheader("분석 결과")

#                 # 감성 점수와 강도 표시
#                 col1, col2 = st.columns(2)

#                 with col1:
#                     st.metric("감성 점수 (Score)", f"{score:.2f}")

#                 with col2:
#                     st.metric("감정 강도 (Magnitude)", f"{magnitude:.2f}")

#                 st.markdown("---")

#                 # 결과 해석
#                 if score > 0.2:
#                     st.success(
#                         f"**긍정적인 글**입니다! 점수: {score:.2f}, 강도: {magnitude:.2f}"
#                     )
#                 elif score < -0.2:
#                     st.error(
#                         f"**부정적인 글**입니다! 점수: {score:.2f}, 강도: {magnitude:.2f}"
#                     )
#                 else:
#                     st.info(
#                         f"**중립적인 글**입니다! 점수: {score:.2f}, 강도: {magnitude:.2f}"
#                     )


# import streamlit as st
# from google.cloud import language_v1
# import json
# import re
# import time
# from urllib.request import urlopen
# from bs4 import BeautifulSoup


# # Google Cloud API 클라이언트 초기화
# def format_private_key(private_key):
#     key_data = (
#         private_key.replace("-----BEGIN PRIVATE KEY-----", "")
#         .replace("-----END PRIVATE KEY-----", "")
#         .strip()
#     )
#     lines = [key_data[i : i + 64] for i in range(0, len(key_data), 64)]
#     return f"-----BEGIN PRIVATE KEY-----\n{chr(10).join(lines)}\n-----END PRIVATE KEY-----\n"


# try:
#     credentials_raw = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
#     credentials_json = re.sub(r"[\r\n\t]", "", credentials_raw.strip()).replace(
#         "\\n", "\n"
#     )
#     credentials_dict = json.loads(credentials_json)
#     credentials_dict["private_key"] = format_private_key(
#         credentials_dict["private_key"]
#     )

#     client = language_v1.LanguageServiceClient.from_service_account_info(
#         credentials_dict
#     )

# except Exception as e:
#     st.error(f"API 연결 오류: {e}")
#     st.stop()


# # 구글 API 감성 분석 함수
# def analyze_sentiment(text):
#     try:
#         document = language_v1.Document(
#             content=text, type_=language_v1.Document.Type.PLAIN_TEXT
#         )
#         response = client.analyze_sentiment(request={"document": document})
#         return response.document_sentiment.score, response.document_sentiment.magnitude
#     except Exception as e:
#         st.error(f"분석 오류: {e}")
#         return None, None


# # 텍스트 전처리 함수
# def preprocess_text(text):
#     # 불필요한 문자열 제거
#     remove_list = [
#         "\u200b",
#         "대표사진 삭제",
#         "사진 설명을 입력하세요.",
#         "출처 입력",
#         "사진 삭제",
#         "이미지 썸네일 삭제",
#         "동영상 정보 상세 보기",
#         "동영상 설명을 입력하세요.",
#         "blog.naver.com",
#     ]

#     for item in remove_list:
#         text = text.replace(item, "")

#     # 이모지 제거
#     emoji_pattern = re.compile(
#         "["
#         "\U0001f600-\U0001f64f"  # emoticons
#         "\U0001f300-\U0001f5ff"  # symbols & pictographs
#         "\U0001f680-\U0001f6ff"  # transport & map symbols
#         "\U0001f1e0-\U0001f1ff"  # flags (iOS)
#         "]+",
#         flags=re.UNICODE,
#     )
#     text = emoji_pattern.sub("", text)

#     # 공백과 줄바꿈 정리
#     text = re.sub("\n+| +", " ", text).strip()

#     return text


# # 네이버 블로그 크롤링 함수
# def crawl_naver_blog(url):
#     try:
#         if not "m.blog.naver.com" in url:
#             url = url.replace("blog.naver.com", "m.blog.naver.com")

#         code = urlopen(url)
#         soup = BeautifulSoup(code, "html.parser")
#         content_div = soup.select_one("div.se-main-container")

#         if content_div:
#             return content_div.text
#         else:
#             return None
#     except Exception as e:
#         st.error(f"블로그 크롤링 오류: {e}")
#         return None


# # Streamlit UI
# st.title("🎭 감성분석기")
# st.markdown("---")

# # 입력 방식 선택
# input_type = st.radio("입력 방식을 선택하세요:", ["직접 입력", "네이버 블로그 URL"])

# if input_type == "직접 입력":
#     text_input = st.text_area(
#         "분석할 텍스트를 입력하세요:",
#         height=150,
#         placeholder="여기에 텍스트를 입력하세요...",
#     )
#     processed_text = text_input
# else:
#     url_input = st.text_input(
#         "네이버 블로그 URL을 입력하세요:", placeholder="https://blog.naver.com/..."
#     )
#     processed_text = ""

#     if url_input and "blog.naver.com" in url_input:
#         if st.button("블로그 내용 가져오기"):
#             with st.spinner("블로그 내용을 가져오는 중..."):
#                 crawled_text = crawl_naver_blog(url_input)
#                 if crawled_text:
#                     processed_text = preprocess_text(crawled_text)
#                     st.success("블로그 내용을 성공적으로 가져왔습니다!")

#                     # 가져온 텍스트 미리보기
#                     with st.expander("가져온 텍스트 미리보기"):
#                         st.text_area(
#                             "",
#                             (
#                                 processed_text[:500] + "..."
#                                 if len(processed_text) > 500
#                                 else processed_text
#                             ),
#                             height=100,
#                         )

# # 분석 버튼
# if st.button("🔍 감성 분석 시작"):
#     if not processed_text:
#         st.warning("분석할 텍스트를 입력하거나 블로그 URL에서 내용을 가져와주세요.")
#     else:
#         with st.spinner("분석 중..."):
#             # 텍스트 전처리 (직접 입력인 경우에도 적용)
#             if input_type == "직접 입력":
#                 processed_text = preprocess_text(processed_text)

#             # 프로그레스 바 애니메이션
#             progress_bar = st.progress(0)
#             for i in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(i + 1)

#             # 구글 API로 감성 분석
#             score, magnitude = analyze_sentiment(processed_text)

#             if score is not None and magnitude is not None:
#                 st.markdown("---")
#                 st.subheader("📊 분석 결과")

#                 # 감성 점수와 강도 표시
#                 col1, col2, col3 = st.columns(3)

#                 with col1:
#                     st.metric(
#                         "감성 점수",
#                         f"{score:.2f}",
#                         help="감성 점수 (-1: 매우 부정적, 0: 중립, +1: 매우 긍정적)",
#                     )

#                 with col2:
#                     st.metric(
#                         "감정 강도",
#                         f"{magnitude:.2f}",
#                         help="감정의 강도 (0: 감정없음, 4+: 매우 강한 감정)",
#                     )

#                 with col3:
#                     # 텍스트 길이 표시
#                     st.metric("텍스트 길이", f"{len(processed_text)} 자")

#                 st.markdown("---")

#                 # 결과 해석 및 이펙트
#                 if score > 0.2:
#                     confidence = min(abs(score) * 100, 100)
#                     st.success(f"🎉 **{confidence:.1f}%의 확률로 긍정적인 글입니다!**")
#                     st.markdown(
#                         f"**감성 점수:** {score:.2f} | **감정 강도:** {magnitude:.2f}"
#                     )
#                     st.balloons()

#                 elif score < -0.2:
#                     confidence = min(abs(score) * 100, 100)
#                     st.error(f"😢 **{confidence:.1f}%의 확률로 부정적인 글입니다.**")
#                     st.markdown(
#                         f"**감성 점수:** {score:.2f} | **감정 강도:** {magnitude:.2f}"
#                     )
#                     st.snow()

#                 else:
#                     st.info(f"😐 **중립적인 글입니다.**")
#                     st.markdown(
#                         f"**감성 점수:** {score:.2f} | **감정 강도:** {magnitude:.2f}"
#                     )

#                 # 분석된 텍스트 표시 (접을 수 있게)
#                 with st.expander("분석된 텍스트 보기"):
#                     st.text_area("", processed_text, height=200)

# # 사이드바에 도움말 추가
# with st.sidebar:
#     st.markdown("### 📖 사용법")
#     st.markdown(
#         """
#     1. **직접 입력**: 분석하고 싶은 텍스트를 직접 입력
#     2. **블로그 URL**: 네이버 블로그 URL을 입력해서 자동으로 내용 추출

#     ### 📈 점수 해석
#     - **감성 점수**: -1(부정) ~ +1(긍정)
#     - **감정 강도**: 0(무감정) ~ 4+(강한 감정)

#     ### ✨ 특징
#     - 이모지 자동 제거
#     - 불필요한 텍스트 정리
#     - 시각적 결과 표시
#     """
#     )

import streamlit as st
from google.cloud import language_v1
import json
import re
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup


# Google Cloud API 클라이언트 초기화
def format_private_key(private_key):
    key_data = (
        private_key.replace("-----BEGIN PRIVATE KEY-----", "")
        .replace("-----END PRIVATE KEY-----", "")
        .strip()
    )
    lines = [key_data[i : i + 64] for i in range(0, len(key_data), 64)]
    return f"-----BEGIN PRIVATE KEY-----\n{chr(10).join(lines)}\n-----END PRIVATE KEY-----\n"


try:
    credentials_raw = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
    credentials_json = re.sub(r"[\r\n\t]", "", credentials_raw.strip()).replace(
        "\\n", "\n"
    )
    credentials_dict = json.loads(credentials_json)
    credentials_dict["private_key"] = format_private_key(
        credentials_dict["private_key"]
    )

    client = language_v1.LanguageServiceClient.from_service_account_info(
        credentials_dict
    )

except Exception as e:
    st.error(f"API 연결 오류: {e}")
    st.stop()


# 구글 API 감성 분석 함수
def analyze_sentiment(text):
    try:
        document = language_v1.Document(
            content=text, type_=language_v1.Document.Type.PLAIN_TEXT
        )
        response = client.analyze_sentiment(request={"document": document})
        return response.document_sentiment.score, response.document_sentiment.magnitude
    except Exception as e:
        st.error(f"분석 오류: {e}")
        return None, None


# 텍스트 전처리 함수
def preprocess_text(text):
    # 불필요한 문자열 제거
    remove_list = [
        "\u200b",
        "대표사진 삭제",
        "사진 설명을 입력하세요.",
        "출처 입력",
        "사진 삭제",
        "이미지 썸네일 삭제",
        "동영상 정보 상세 보기",
        "동영상 설명을 입력하세요.",
        "blog.naver.com",
    ]

    for item in remove_list:
        text = text.replace(item, "")

    # 이모지 제거
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)

    # 공백과 줄바꿈 정리
    text = re.sub("\n+| +", " ", text).strip()

    return text


# 네이버 블로그 크롤링 함수
def crawl_naver_blog(url):
    try:
        if not "m.blog.naver.com" in url:
            url = url.replace("blog.naver.com", "m.blog.naver.com")

        code = urlopen(url)
        soup = BeautifulSoup(code, "html.parser")
        content_div = soup.select_one("div.se-main-container")

        if content_div:
            return content_div.text
        else:
            return None
    except Exception as e:
        st.error(f"블로그 크롤링 오류: {e}")
        return None


# Streamlit UI
st.title("🎭 감성분석기")
st.markdown("---")

# 입력 방식 선택
input_type = st.radio("입력 방식을 선택하세요:", ["직접 입력", "네이버 블로그 URL"])

if input_type == "직접 입력":
    text_input = st.text_area(
        "분석할 텍스트를 입력하세요:",
        height=150,
        placeholder="여기에 텍스트를 입력하세요...",
    )
    processed_text = text_input
else:
    url_input = st.text_input(
        "네이버 블로그 URL을 입력하세요:", placeholder="https://blog.naver.com/..."
    )
    processed_text = ""

    if url_input and "blog.naver.com" in url_input:
        if st.button("블로그 내용 가져오기"):
            with st.spinner("블로그 내용을 가져오는 중..."):
                crawled_text = crawl_naver_blog(url_input)
                if crawled_text:
                    st.session_state.processed_text = preprocess_text(crawled_text)
                    st.success("블로그 내용을 성공적으로 가져왔습니다!")

                    # 가져온 텍스트 미리보기
                    with st.expander("가져온 텍스트 미리보기"):
                        st.text_area(
                            "",
                            (
                                st.session_state.processed_text[:500] + "..."
                                if len(st.session_state.processed_text) > 500
                                else st.session_state.processed_text
                            ),
                            height=100,
                        )

# 분석 버튼
if st.button("🔍 감성 분석 시작"):
    # 디버깅 정보
    st.write(
        f"DEBUG - processed_text 길이: {len(processed_text) if processed_text else 0}"
    )
    st.write(f"DEBUG - processed_text 타입: {type(processed_text)}")

    if not st.session_state.processed_text:
        st.warning("분석할 텍스트를 입력하거나 블로그 URL에서 내용을 가져와주세요.")
    else:
        with st.spinner("분석 중..."):
            # 텍스트 전처리 (직접 입력인 경우에도 적용)
            if input_type == "직접 입력":
                processed_text = preprocess_text(processed_text)

            # 프로그레스 바 애니메이션
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

            # 구글 API로 감성 분석
            score, magnitude = analyze_sentiment(st.session_state.processed_text)

            if score is not None and magnitude is not None:
                st.markdown("---")
                st.subheader("📊 분석 결과")

                # 감성 점수와 강도 표시
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "감성 점수",
                        f"{score:.2f}",
                        help="감성 점수 (-1: 매우 부정적, 0: 중립, +1: 매우 긍정적)",
                    )

                with col2:
                    st.metric(
                        "감정 강도",
                        f"{magnitude:.2f}",
                        help="감정의 강도 (0: 감정없음, 4+: 매우 강한 감정)",
                    )

                with col3:
                    # 텍스트 길이 표시
                    st.metric("텍스트 길이", f"{len(processed_text)} 자")

                st.markdown("---")

                # 결과 해석 및 이펙트
                if score > 0.2:
                    confidence = min(abs(score) * 100, 100)
                    st.success(f"🎉 **{confidence:.1f}%의 확률로 긍정적인 글입니다!**")
                    st.markdown(
                        f"**감성 점수:** {score:.2f} | **감정 강도:** {magnitude:.2f}"
                    )
                    st.balloons()

                elif score < -0.2:
                    confidence = min(abs(score) * 100, 100)
                    st.error(f"😢 **{confidence:.1f}%의 확률로 부정적인 글입니다.**")
                    st.markdown(
                        f"**감성 점수:** {score:.2f} | **감정 강도:** {magnitude:.2f}"
                    )
                    st.snow()

                else:
                    st.info(f"😐 **중립적인 글입니다.**")
                    st.markdown(
                        f"**감성 점수:** {score:.2f} | **감정 강도:** {magnitude:.2f}"
                    )

                # 분석된 텍스트 표시 (접을 수 있게)
                with st.expander("분석된 텍스트 보기"):
                    st.text_area("", processed_text, height=200)

# 사이드바에 도움말 추가
with st.sidebar:
    st.markdown("### 📖 사용법")
    st.markdown(
        """
    1. **직접 입력**: 분석하고 싶은 텍스트를 직접 입력
    2. **블로그 URL**: 네이버 블로그 URL을 입력해서 자동으로 내용 추출
    
    ### 📈 점수 해석
    - **감성 점수**: -1(부정) ~ +1(긍정)
    - **감정 강도**: 0(무감정) ~ 4+(강한 감정)
    
    ### ✨ 특징
    - 이모지 자동 제거
    - 불필요한 텍스트 정리
    - 시각적 결과 표시
    """
    )
