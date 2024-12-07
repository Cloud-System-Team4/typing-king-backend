import socket
import time

HOST = '172.30.1.23' # socket.gethostbyname(socket.gethostname()) #'SERVER_IP'  # 서버 IP 주소 입력
PORT = 9999  # 서버 포트 번호

# 서버와의 연결 설정
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 데이터베이스에서 가져온 문장 목록
from_db = [
    "가","나","다","라","마","바","사","아","자","차","카","타","파","하"
    # "체다치즈를 최고 많이 먹은 최다연이 체다치즈 먹기 대회 최다 우승자이다.",
    # "정희수가 희희낙락하게 희끄무리한 흰머리를 뽑으며",
    # "이수지가 저수지에 갔는데 이 수지가 저수지에 간 걸까 저 수지가 저수지에 간걸까",
    # "그 수지가 저수지에 간 걸까 하며 이수지는 고민했는데 고민 끝에 이수의 마이웨이를 부르며 불쾌지수가 올라가며",
    # "저수지를 떠나 경기도 수지구의 한 학원으로 달려가더니 지수함수를 배워서 잘 사용하여 주식 수지를 맞아",
    # "'나 이수지, 바로 고단수지! 수지맞았다!'하며 행복해했다.",
    # "내가 그린 기린 그림은 잘 그린 기린 그림이고 네가 그린 기린 그림은 못 그린 기린 그림이다.",
    # "내가 그린 기린 그림은 목이 긴 기린 그린 그림이고, 네가 그린 기린 그림은 목이 안 긴 기린 그린 그림이다",
    # "내가 그린 구름그림은 새털구름 그린 구름그림이고, 네가 그린 구름그림은 깃털구름 그린 구름그림이다.",
    # "저기 계신 저 분이 박 법학박사이시고 여기 계신 이 분이 백 법학박사이시다."
]

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
    print("Typing Game start!")

    start_time = time.time()  # 게임 시작 시간

    for i in range(10):  # 10회의 타이핑 게임 진행
        same = False
        while not same:
            compare = from_db[i]
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
