import socket
import time
import mysql.connector
import websockets
import asyncio
import json

HOST = '172.20.4.31' #'SERVER_IP'  # 서버 IP 주소 입력
PORT = 9999  # 서버 포트 번호
SERVER_URI = "ws://localhost:9999" # 웹소켓 서버 URI

# 1. 시작하기 버튼 누르면 (페이지 이동) 큐에 들어가는 과정.
    ## 자스 웹소켓으로 받아서 
# 2. 매치가 되기 전까지 문장 안뜸

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

# 웹소켓 프런트에게 전달하는 함수
async def send_message(websocket, message):
    await websocket.send(json.dumps(message))

# 웹소켓 프런트에게 받는 함수
async def get_message(websocket):
    raw = await websocket.recv()
    try:
        message = json.loads(raw)
        return message
    except json.JSONDecodeError:
        print(f"Invalid JSON: {raw}")
        return None

async def wait_for_match(client_socket):
    '''대기상태로 돌아가 매칭신호 기다림'''
    print("Waiting for a match...")
    while True:
        message = client_socket.recv(1024).decode()
        if message == "START":
            print("Match found! Starting game...")
            return True

async def play_game(websocket, client_socket):
    '''타이핑 게임 실행하고 결과 서버 전송'''
    sentences = get_random_sentence() # DB 랜던값 채움.
    player = client_socket.recv(1024).decode()

    # 프론트에게 전달
    await send_message(websocket, {
        "type": "START",
        "role": player
    })
    start_time = time.time()  # 게임 시작 시간

    print(f"Typing Game start! You are {player}.")
    await send_message(websocket, {
                    "type":"NEXT_SENTENCE",
                    "sentence": sentences[0]
                })
    ## 프런트에게 sentence를 보내면 그쪽에서 동일 여부 판단.
    for i in range(1,3): # 변수화
        while True: # 자스로부터 True 받을 때에만 next sentence 보냄.
            message = await get_message(websocket)
            if message["type"]=="ANSWER" and message["correct"]:
                await send_message(websocket, {
                    "type":"NEXT_SENTENCE",
                    "sentence": sentences[i]
                })
                break
    elapsed_time = time.time() - start_time
    # print(f"총 소요 시간: {elapsed_time:.2f}초")
    # 서버로 결과 전송
    client_socket.send(str(elapsed_time).encode())

    # 서버에게 우승 결과 받기
    result = client_socket.recv(1024).decode()
    # print(f"raw result from server: {result}")
    
    if result.startswith("RESULT"):
        _, player_time, opponent_time, winner = result.split("|")
        # 프론트
        await send_message(websocket, {
            "type":"RESULT",
            "total_time":player_time,
            "opponent_time":opponent_time,
            "winner":winner
        })
        print(f"Your time: {player_time}, Opponent time: {opponent_time}, Winner: {winner}")

async def asking(websocket, client_socket):
    # 추가 게임 여부 확인을 프런트에서 받음
    message = await get_message(websocket)
    if message and message["type"]=="RETRY":
        continue_game = message["continue"] #input("Another round? (yes/no): ").strip().lower()
        client_socket.send(str(continue_game).encode())
        return continue_game
    return False
    
async def starting():
    while True:
        async with websockets.connect("ws://localhost:9999") as websocket:
            # 서버와의 연결 설정
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((HOST, PORT))
            
            start_game = True
            while start_game:
                # 자스에서 start 한다면 starting을 시작.
                message = await get_message(websocket)
                if message and message["type"]=="START_GAME" and message["start"]:
                    if await wait_for_match(client_socket): # 매칭 대기 (서버가 하는 중)
                        await play_game(websocket, client_socket)   # 게임 실행
                    
                    start_game = await asking(websocket, client_socket)
            print("게임을 종료합니다.")
            client_socket.close()
            break

# asyncio 실행
asyncio.run(starting())