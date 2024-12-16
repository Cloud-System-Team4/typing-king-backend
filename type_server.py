import socket
from _thread import *
import threading
import websocket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server started on {HOST}:{PORT}")

lock = threading.Lock()
waiting_room = []  # 대기 중인 클라이언트 소켓 저장
matched_clients = []
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
                print("==========================================================")
                print(f"----- waiting_room: {[client.getpeername() for client in waiting_room]}")
                print(f"----- currently alive clients: {[client.getpeername() for client in client_sockets]}")
                print(f"----- currently matched clients: {[f'{client1.getpeername()} and {client2.getpeername()}' for client1, client2 in matched_clients]}")
                print("==========================================================")

                while waiting_room:
                    if waiting_room[0] != client_socket:
                        # 매칭 중인 클라이언트와 새 룸 생성
                        player1 = waiting_room.pop(0)
                        try: # 클라이언트 상태 검증
                            player1.send(b"PING")
                        except (socket.error, BrokenPipeError):
                            print(f"Client {player1.getpeername()} is unresponsive. Removing from waiting room.")
                            client_sockets.remove(player1)
                            player1.close()
                            continue
                        player2 = client_socket
                        room_id += 1
                        rooms[room_id] = (player1, player2)

                        matched_clients.append((player1, player2))

                        # 룸 참가자들에게 START 메시지 전송
                        player1.send("START".encode())
                        player2.send("START".encode())
                        print(f"Room {room_id} created with players {addr} and {player1.getpeername()}")

                        # 룸 내에서 게임 진행
                        start_new_thread(run_game, (room_id, player1, player2))
                        return
                
                if any(client_socket in (client1, client2) for client1, client2 in matched_clients):
                    print(f"{client_socket.getpeername()} is matched.")
                    print("==========================================================")
                    return
                
                if not waiting_room and not any(client_socket in (client1, client2) for client1, client2 in matched_clients):
                    # waiting_room 비어있을 때
                    waiting_room.append(client_socket)
                    print(f"Client {addr} added to waiting room. Waiting for another player...")
                    print("==========================================================")

            while client_socket in waiting_room:
                pass
    except Exception as e:
        print(f"Error with client {addr}: {e}")
        print("==========================================================")

def run_game(room_id, player1, player2): # 클라이언트와 통신하는 부분
    player1_time = None
    player2_time = None
    player1.send("Player 1".encode())
    player2.send("Player 2".encode())

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

                player1.send(f"RESULT|{player1_time:.2f}|{player2_time:.2f}|{winner}".encode())
                player2.send(f"RESULT|{player2_time:.2f}|{player1_time:.2f}|{winner}".encode())

                # 추가 게임 여부 확인
                player1_more = player1.recv(1024).decode().lower()
                player2_more = player2.recv(1024).decode().lower()

                with lock:
                    if player1_more == "yes":
                        waiting_room.append(player1)
                        print(f"Player 1 {player1.getpeername()} from Room {room_id} rejoining waiting room.")
                        print("==========================================================")
                    else:
                        if player1 in client_sockets:
                            client_sockets.remove(player1)
                            print(f"Player 1 {player1.getpeername()} from Room {room_id} disconnected. Current client count: {len(client_sockets)}")
                            print("==========================================================")
                with lock:
                    if player2_more == "yes":
                        waiting_room.append(player2)
                        print(f"Player 2 {player2.getpeername()} from Room {room_id} rejoining waiting room.")
                        print("==========================================================")
                    else:
                        if player2 in client_sockets:
                            client_sockets.remove(player2)
                            print(f"Player 2 {player2.getpeername()} from Room {room_id} disconnected. Current client count: {len(client_sockets)}")
                            print("==========================================================")
                    matched_clients.remove((player1, player2))
                    #print(f"----- currently matched clients: {[f'{client1.getpeername()} and {client2.getpeername()}' for client1, client2 in matched_clients]}")

                # 리소스 해제 - 위에 추가할 경우 '[WinError 10038] 소켓 이외의 개체에 작업을 시도했습니다' 난다.
                if player1_more == "no":
                    player1.close()
                if player2_more == "no":
                    player2.close()
                break
    except Exception as e:
        print(f"Error in room {room_id}: {e}")
        print("==========================================================")
    finally:
        # 클라이언트 종료 및 룸 제거
        with lock:
            if room_id in rooms:
                del rooms[room_id]
                print(f"Room {room_id} removed. Current active rooms: {len(rooms)}")
                print("==========================================================")

try:
    while True:
        print("Waiting for clients...")
        client_socket, addr = server_socket.accept()
        start_new_thread(handle_client, (client_socket, addr))
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    server_socket.close()
