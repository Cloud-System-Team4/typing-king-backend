import socket
import time
import mysql.connector

HOST = '172.20.34.67' # socket.gethostbyname(socket.gethostname()) #'SERVER_IP'  # 서버 IP 주소 입력
PORT = 9999  # 서버 포트 번호

# 서버와의 연결 설정
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def get_random_sentence(): # 데이터베이스에서 문장 가져옴
    connection = mysql.connector.connect(
        host="localhost",
        user="cloud4",
        password="qwerty",
        database="typeDB"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT sentence FROM sentences ORDER BY RAND() LIMIT 10;")
    sentences = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return sentences

def wait_for_match():
    '''대기상태로 돌아가 매칭신호 기다림'''
    print("Waiting for a match...")
    while True:
        message = client_socket.recv(1024).decode()
        if message == "START":
            print("Match found! Starting game...")
            break


def play_game():
    '''타이핑 게임 실행하고 결과 서버 전송'''
    sentences = get_random_sentence()
    player = client_socket.recv(1024).decode()
    print(f"Typing Game start! You are {player}.")

    start_time = time.time()  # 게임 시작 시간

    for i in range(3):  # 10회의 타이핑 게임 진행
        same = False
        while not same:
            compare = sentences[i]
            print(f"문장을 입력하세요: {compare}")
            from_user = input("입력: ")
            if from_user == compare:
                print("정답입니다!")
                same = True
                #client_socket.send(str(same).encode())
                break
            else:
                print("틀렸습니다. 다시 시도하세요.")
                #client_socket.send(str(same).encode())
    end_time = time.time()  # 게임 종료 시간
    elapsed_time = end_time - start_time
    print(f"총 소요 시간: {elapsed_time:.2f}초")

    # 서버로 결과 전송
    client_socket.send(str(elapsed_time).encode())

    # 서버에게 우승 결과 받기
    try:
        result = client_socket.recv(1024).decode()
        print(f"raw result from server: {result}")
        if result.startswith("RESULT"):
            _, player_time, opponent_time, winner = result.split("|")
            print(f"Your time: {player_time}")
            print(f"Opponent's time: {opponent_time}")
            print(f"Winner: {winner}")
    except Exception as e:
        print(f"Error receiving result: {e}")

while True:
    wait_for_match() # 매칭 대기 (서버가 하는 중)
    play_game()      # 게임 실행

    # 추가 게임 여부 확인
    more = input("Another round? (yes/no): ").strip().lower()
    client_socket.send(more.encode())
    if more != "yes":
        print("게임을 종료합니다.")
        break

# 소켓 닫기
client_socket.close()
