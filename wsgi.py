import os
from app import app, socketio

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app with allow_unsafe_werkzeug=True for production
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True) 