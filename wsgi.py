import os
from app import app, socketio

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    socketio.run(app, host='0.0.0.0', port=port) 