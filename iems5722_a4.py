from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iems5722'
socketio = SocketIO(app)

@app.route("/api/a4/broadcast_room", methods=["POST"])
def broadcast_room():
    #json = request.form.get('json')
    chatroom_id = request.json.get('chatroom_id')
    message = request.json.get('message')
    #print(message, chatroom_id)
    socketio.emit('broadcast', {'chatroom_id': chatroom_id, 'message': message}, broadcast=True, room='room'+str(chatroom_id))
    #...

#@socketio.on('my event')
#def my_event_handler(data):
    #emit(...)


@socketio.on('join')
def on_join(data):
    room = 'room'+str(data['chatroom_id'])
    join_room(room)
    #print(room)
    s = 'entered chatroom(id '+str(data['chatroom_id'])+')'
    #send('entered chatroom(id '+room+')', room=room)
    emit('join', { 'chatroom_id' : s } , broadcast=True, room=room)
    #join_room(chatroom_id)

@socketio.on('leave')
def on_leave(data):
    room = 'room'+str(data['chatroom_id'])
    print(room)
    s = 'left chatroom(id '+str(data['chatroom_id'])+')'
    leave_room(room)
    emit('leave', { 'chatroom_id' : s } , broadcast=True, room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8001)