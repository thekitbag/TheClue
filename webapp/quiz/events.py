from webapp import socketio

@socketio.on('player_joined', namespace='/quiz')
def handle_player_joined(data):
    quiz_id = data['quiz_id']
    player_name = data['player_name']
    print(f"Received player_joined event for quiz ID: {quiz_id}, Player: {player_name}")
    socketio.emit('player_list_updated', {'quiz_id': quiz_id}, namespace='/quiz')