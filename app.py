from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Message
from datetime import datetime
import os
import re
from config import config

# Create Flask app
app = Flask(__name__, static_folder='static')

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Create tables
with app.app_context():
    db.create_all()

def get_room_name(user1_id, user2_id):
    """Create a consistent room name for two users"""
    return f"room_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

def validate_username(username):
    """Validate username format"""
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username.strip()) > 20:
        return False, "Username must be less than 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username.strip()):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""

def validate_message(text):
    """Validate message content"""
    if not text or len(text.strip()) == 0:
        return False, "Message cannot be empty"
    if len(text.strip()) > 1000:
        return False, "Message must be less than 1000 characters"
    return True, ""

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    
    # Validate username
    is_valid, error_message = validate_username(username)
    if not is_valid:
        flash(error_message)
        return redirect(url_for('index'))
    
    try:
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # Create new user
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        
        # Store user in session
        session['user_id'] = user.id
        session['username'] = user.username
        
        return redirect(url_for('chat'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.')
        return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        current_user_id = session['user_id']
        
        # Get all other users
        other_users = User.query.filter(User.id != current_user_id).all()
        
        return render_template('chat.html', 
                             current_user=session['username'], 
                             users=other_users)
    except Exception as e:
        flash('An error occurred. Please try again.')
        return redirect(url_for('index'))

@app.route('/chat/<int:receiver_id>')
def private_chat(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        current_user_id = session['user_id']
        
        if current_user_id == receiver_id:
            return redirect(url_for('chat'))
        
        # Get receiver info
        receiver = User.query.get_or_404(receiver_id)
        
        # Get all messages between current user and receiver
        messages = Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == receiver_id)) |
            ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.timestamp).all()
        
        return render_template('private_chat.html', 
                             current_user=session['username'],
                             current_user_id=current_user_id,
                             receiver=receiver, 
                             messages=messages)
    except Exception as e:
        flash('An error occurred. Please try again.')
        return redirect(url_for('chat'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Socket.IO events
@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")
    # Don't check session here, let the client handle authentication

@socketio.on('disconnect')
def on_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_chat')
def on_join_chat(data):
    print(f"Join chat request: {data}")
    receiver_id = data.get('receiver_id')
    if not receiver_id:
        print("No receiver_id provided")
        return
    
    # Get user info from the client
    current_user_id = data.get('current_user_id')
    current_username = data.get('current_username')
    
    if not current_user_id or not current_username:
        print("Missing user info")
        return
    
    room = get_room_name(current_user_id, receiver_id)
    join_room(room)
    
    print(f"User {current_username} joined room {room}")

@socketio.on('leave_chat')
def on_leave_chat(data):
    print(f"Leave chat request: {data}")
    receiver_id = data.get('receiver_id')
    if not receiver_id:
        return
    
    current_user_id = data.get('current_user_id')
    if not current_user_id:
        return
    
    room = get_room_name(current_user_id, receiver_id)
    leave_room(room)
    
    print(f"User left room {room}")

@socketio.on('send_message')
def handle_message(data):
    print(f"Send message request: {data}")
    
    text = data.get('text', '').strip()
    receiver_id = data.get('receiver_id')
    current_user_id = data.get('current_user_id')
    current_username = data.get('current_username')
    
    # Validate message
    is_valid, error_message = validate_message(text)
    if not is_valid:
        emit('error', {'message': error_message})
        return
    
    if not receiver_id or not current_user_id or not current_username:
        emit('error', {'message': 'Missing required data'})
        return
    
    try:
        # Verify receiver exists
        receiver = User.query.get(receiver_id)
        if not receiver:
            emit('error', {'message': 'Receiver not found'})
            return
        
        # Save message to database
        message = Message(
            sender_id=current_user_id,
            receiver_id=receiver_id,
            text=text
        )
        db.session.add(message)
        db.session.commit()
        
        # Get room name
        room = get_room_name(current_user_id, receiver_id)
        
        # Emit message to room
        message_data = {
            'id': message.id,
            'sender_id': current_user_id,
            'sender_username': current_username,
            'receiver_id': receiver_id,
            'text': text,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"Emitting message to room {room}: {message_data}")
        socketio.emit('new_message', message_data, room=room)
        
    except Exception as e:
        db.session.rollback()
        print(f"Error sending message: {e}")
        emit('error', {'message': 'Failed to send message. Please try again.'})

@socketio.on('clear_chat')
def handle_clear_chat(data):
    print(f"Clear chat request: {data}")
    
    receiver_id = data.get('receiver_id')
    current_user_id = data.get('current_user_id')
    current_username = data.get('current_username')
    
    if not receiver_id or not current_user_id or not current_username:
        emit('error', {'message': 'Missing required data'})
        return
    
    try:
        # Verify receiver exists
        receiver = User.query.get(receiver_id)
        if not receiver:
            emit('error', {'message': 'Receiver not found'})
            return
        
        # Delete all messages between the two users
        deleted_count = Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == receiver_id)) |
            ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user_id))
        ).delete()
        
        db.session.commit()
        
        # Get room name
        room = get_room_name(current_user_id, receiver_id)
        
        # Emit clear chat event to room
        clear_data = {
            'cleared_by': current_username,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"Clearing chat in room {room}: {clear_data}")
        socketio.emit('chat_cleared', clear_data, room=room)
        
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing chat: {e}")
        emit('error', {'message': 'Failed to clear chat. Please try again.'})