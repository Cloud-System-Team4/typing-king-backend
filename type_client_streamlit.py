import streamlit as st
import socket
import time
from type_client import get_random_sentence

# 서버 연결 정보
HOST = '172.20.4.31'
PORT = 9999

# 문장 가져오기 및 출력
def fetch_sentences_ui():
    """DB에서 랜덤 문장 가져오기 및 UI 출력"""
    st.subheader("주어진 문장")
    try:
        sentences = get_random_sentence()
        for i, sentence in enumerate(sentences, 1):
            st.write(f"{i}. {sentence}")
        return sentences
    except Exception as e:
        st.error(f"문장을 가져오는 중 오류 발생: {e}")
        return []

# 상태 업데이트용 함수
def update_status(status_placeholder, status: str):
    """게임 상태 업데이트"""
    status_placeholder.text(status)

# 서버와 통신하는 함수
def connect_to_server(status_placeholder):
    """서버에 연결하고 게임을 실행"""
    try:
        # 클라이언트 소켓 생성 및 연결
        update_status(status_placeholder, "서버에 연결 중...")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        update_status(status_placeholder, "서버에 연결되었습니다. 매칭 대기 중...")

        # 매칭 상태를 확인하는 시뮬레이션
        with st.spinner("매칭 중입니다... 잠시만 기다려주세요!"):
            time.sleep(2)
        
        update_status(status_placeholder, "매칭 완료! 게임을 시작합니다.")

        # 게임 로직 대신 랜덤 문장 UI에 표시
        fetch_sentences_ui()

        # 게임 종료
        client_socket.close()
        update_status(status_placeholder, "게임이 종료되었습니다.")

    except Exception as e:
        update_status(status_placeholder, f"오류 발생: {e}")

# Streamlit UI 메인 함수
def game_ui():
    st.title("내일은 타자왕")
    st.sidebar.title("게임 설정")
    start_game = st.sidebar.button("게임 시작")

    # 상태 메시지 출력용 공간
    status_placeholder = st.empty()

    if start_game:
        # 서버 연결 및 게임 실행 (메인 스레드에서 실행)
        connect_to_server(status_placeholder)

# Streamlit 애플리케이션 실행
if __name__ == "__main__":
    game_ui()
