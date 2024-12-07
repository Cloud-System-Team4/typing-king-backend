import socket
from _thread import *
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server started on {HOST}:{PORT}")

lock = threading.Lock()
waiting_room = []  # 대기 중인 클라이언트 소켓 저장
rooms = {}  # 룸 ID와 클라이언트 소켓 매칭
room_id = 0

client_sockets = []  # 모든 클라이언트 소켓 관리

def handle_client(client_socket, addr):
    global room_id
    print(f"Connected by {addr}")

    with lock:
        client_sockets.append(client_socket)

    try:
        while True:
            with lock:
                if waiting_room and waiting_room[0] != client_socket:
                    # 매칭 중인 클라이언트와 새 룸 생성
                    player1 = waiting_room.pop(0)
                    player2 = client_socket
                    room_id += 1
                    rooms[room_id] = (player1, player2)

                    # 룸 참가자들에게 START 메시지 전송
                    player1.send("START".encode())
                    player2.send("START".encode())
                    print(f"Room {room_id} created with players {addr} and {player1.getpeername()}")

                    # 룸 내에서 게임 진행
                    start_new_thread(run_game, (room_id, player1, player2))
                    return
                else:
                    waiting_room.append(client_socket)
                    print(f"Client {addr} added to waiting room. Waiting for another player...")

            while client_socket in waiting_room:
                pass
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    # finally:
    #     with lock:
    #         if client_socket in waiting_room:
    #             waiting_room.remove(client_socket)
    #         if client_socket in client_sockets:
    #             client_sockets.remove(client_socket)
    #             print(f"Client {addr} disconnected. Current client count: {len(client_sockets)}")
    #     client_socket.close()

def run_game(room_id, player1, player2): # 클라이언트와 통신하는 부분
    player1_time = None
    player2_time = None

    try:
        while True:
            if player1_time is None:
                player1_time = float(player1.recv(1024).decode())
            if player2_time is None:
                player2_time = float(player2.recv(1024).decode())

            if player1_time is not None and player2_time is not None:
                # 결과 비교 및 전송
                if player1_time < player2_time:
                    winner = "Player 1"
                elif player1_time > player2_time:
                    winner = "Player 2"
                else:
                    winner = "Draw"

                player1.send(f"RESULT|{player1_time}|{player2_time}|{winner}".encode())
                player2.send(f"RESULT|{player2_time}|{player1_time}|{winner}".encode())

                # 추가 게임 여부 확인
                player1_more = player1.recv(1024).decode().lower()
                player2_more = player2.recv(1024).decode().lower()

                with lock:
                    if player1_more == "yes":
                        waiting_room.append(player1)
                        print(f"Player 1 from Room {room_id} rejoining waiting room.")
                    else:
                        if player1 in client_sockets:
                            client_sockets.remove(player1)
                            print(f"Player 1 from Room {room_id} disconnected. Current client count: {len(client_sockets)}")

                    if player2_more == "yes":
                        waiting_room.append(player2)
                        print(f"Player 2 from Room {room_id} rejoining waiting room.")
                    else:
                        if player2 in client_sockets:
                            client_sockets.remove(player2)
                            print(f"Player 2 from Room {room_id} disconnected. Current client count: {len(client_sockets)}")

                break
    except Exception as e:
        print(f"Error in room {room_id}: {e}")
    finally:
        # 클라이언트 종료 및 룸 제거
        with lock:
            if room_id in rooms:
                del rooms[room_id]
                print(f"Room {room_id} removed. Current active rooms: {len(rooms)}")
        player1.close()
        player2.close()

try:
    while True:
        print("Waiting for clients...")
        client_socket, addr = server_socket.accept()
        start_new_thread(handle_client, (client_socket, addr))
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    server_socket.close()
