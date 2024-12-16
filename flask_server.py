from flask import Flask, request, jsonify
import time
import mysql.connector

app = Flask(__name__)

# MySQL 연결 설정
def get_random_sentence():
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

@app.route('/wait_for_match', methods=['GET'])
def wait_for_match():
    """매칭 신호를 기다립니다."""
    # 여기서는 간단히 매칭이 즉시 성공했다고 가정합니다.
    return jsonify({"message": "Match found! Starting game..."})

@app.route('/play_game', methods=['POST'])
def play_game():
    """타이핑 게임 실행."""
    data = request.get_json()
    player = data.get("player", "Player 1")
    sentences = get_random_sentence()

    start_time = time.time()
    results = []

    for i in range(3):  # 3회의 타이핑 게임 진행
        compare = sentences[i]
        from_user = data.get(f"sentence_{i}", "")
        if from_user == compare:
            results.append({"sentence": compare, "result": "Correct"})
        else:
            results.append({"sentence": compare, "result": "Incorrect"})

    end_time = time.time()
    elapsed_time = end_time - start_time

    # 결과를 반환합니다.
    return jsonify({
        "player": player,
        "results": results,
        "elapsed_time": elapsed_time
    })

@app.route('/send_result', methods=['POST'])
def send_result():
    """게임 결과를 처리."""
    data = request.get_json()
    player_time = data.get("player_time")
    opponent_time = data.get("opponent_time")

    if float(player_time) < float(opponent_time):
        winner = "Player"
    else:
        winner = "Opponent"

    return jsonify({
        "player_time": player_time,
        "opponent_time": opponent_time,
        "winner": winner
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)