import socket
import time
import mysql.connector
import websockets
import asyncio
import json
import threading

HOST = '127.0.0.1'  # 서버 IP 주소 입력
PORT = 9999  # 서버 포트 번호
SERVER_URI = "ws://localhost:9998"  # 웹소켓 서버 URI

def get_random_sentence():  # 데이터베이스에서 문장 가져옴
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
    """대기상태로 돌아가 매칭신호 기다림"""
    print("Waiting for a match...")
    while True:
        message = client_socket.recv(1024).decode()
        if message == "START":
            print("Match found! Starting game...")
            return True

async def play_game(websocket, client_socket):
    """타이핑 게임 실행하고 결과 서버 전송"""
    sentences = get_random_sentence()  # DB 랜덤 값 채움.
    player = client_socket.recv(1024).decode()

    # 프론트에게 전달
    await send_message(websocket, {"type": "START", "role": player})
    start_time = time.time()  # 게임 시작 시간

    print(f"Typing Game start! You are {player}.")
    await send_message(websocket, {"type": "NEXT_SENTENCE", "sentence": sentences[0]})

    for i in range(1, 3):
        while True:  # 프런트로부터 답변이 올 때까지 기다림
            message = await get_message(websocket)
            if message and message["type"] == "ANSWER" and message["correct"]:
                await send_message(websocket, {"type": "NEXT_SENTENCE", "sentence": sentences[i]})
                break

    elapsed_time = time.time() - start_time
    client_socket.send(str(elapsed_time).encode())

    # 서버로부터 결과 수신
    result = client_socket.recv(1024).decode()
    if result.startswith("RESULT"):
        _, player_time, opponent_time, winner = result.split("|")
        await send_message(websocket, {
            "type": "RESULT",
            "total_time": player_time,
            "opponent_time": opponent_time,
            "winner": winner
        })
        print(f"Your time: {player_time}, Opponent time: {opponent_time}, Winner: {winner}")

async def asking(websocket, client_socket):
    """추가 게임 여부 확인"""
    message = await get_message(websocket)
    if message and message["type"] == "RETRY":
        continue_game = message["continue"]
        client_socket.send(str(continue_game).encode())
        return continue_game
    return False

async def starting(websocket):
    """웹소켓 시작"""
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("inside starting()")

        start_game = True
        while start_game:
            raw = await websocket.recv()
            message = json.loads(raw)
            if message and message["type"] == "START_GAME" and message["start"]:
                if await wait_for_match(client_socket):
                    await play_game(websocket, client_socket)

                start_game = await asking(websocket, client_socket)

        print("게임을 종료합니다.")
        client_socket.close()
        break

async def main():
    print("waiting for js")
    async with websockets.serve(starting, "localhost", 9998):
        await asyncio.Future()  # 서버 무한 실행

# 직접 실행될 때만 main() 실행
if __name__ == "__main__":
    asyncio.run(main())
