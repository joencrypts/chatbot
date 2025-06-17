# Flask Chat Application

A real-time chat application built with Flask, SQLAlchemy, and Socket.IO.

## Features

- User registration and login
- Real-time private messaging
- Modern dark UI design
- Secure session management
- Input validation and error handling
- Clear chat functionality for both users

## Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables (optional but recommended):**
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Set the environment variable
   export SECRET_KEY=your-generated-secret-key
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Access the application:**
   Open your browser and go to `http://localhost:5000`

## Online Deployment

### Option 1: Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create a new Heroku app:**
   ```bash
   heroku create your-chat-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-generated-secret-key
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Open your app:**
   ```bash
   heroku open
   ```

### Option 2: Railway

1. **Connect your GitHub repository** to Railway
2. **Set environment variables** in Railway dashboard:
   - `SECRET_KEY`: Your generated secret key
   - `FLASK_ENV`: `production`
3. **Deploy automatically** from your repository

### Option 3: Render

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service**
3. **Set environment variables:**
   - `SECRET_KEY`: Your generated secret key
   - `FLASK_ENV`: `production`
4. **Set build command:** `pip install -r requirements.txt`
5. **Set start command:** `python wsgi.py`

### Option 4: PythonAnywhere

1. **Upload your files** to PythonAnywhere
2. **Create a virtual environment** and install requirements
3. **Configure WSGI file** to point to your app
4. **Set environment variables** in your WSGI file

## Environment Variables

- `SECRET_KEY`: Secret key for session management (required for production)
- `FLASK_ENV`: Environment mode (`development` or `production`)
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

## Recent Fixes

### Critical Bug Fixes:
- **Fixed `chat.html`**: The chat dashboard was showing a login form instead of the user list. Now properly displays all users and allows starting conversations.
- **Added input validation**: Usernames and messages are now properly validated with length and format restrictions.
- **Improved security**: Secret key now uses environment variables with a fallback for development.
- **Enhanced error handling**: Added try-catch blocks and proper error messages throughout the application.
- **Fixed Socket.IO messaging**: Real-time messaging now works properly between users.
- **Added clear chat functionality**: Users can clear chat history for both participants.

### Security Improvements:
- Username validation (3-20 characters, alphanumeric + underscores only)
- Message length limits (max 1000 characters)
- Environment variable for secret key
- Input sanitization and validation
- Database error handling with rollbacks

### User Experience Improvements:
- Better error messages displayed to users
- Improved UI with proper chat dashboard
- Real-time error handling in chat interface
- Responsive design improvements
- Clear chat button with confirmation dialog

## Project Structure

- `app.py` - Main Flask application with routes and Socket.IO handlers
- `models.py` - Database models for User and Message
- `config.py` - Configuration settings for different environments
- `wsgi.py` - WSGI entry point for production deployment
- `run.py` - Development server entry point
- `templates/` - HTML templates
  - `login.html` - User login/registration page
  - `chat.html` - Chat dashboard showing all users
  - `private_chat.html` - Individual chat interface
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment configuration
- `runtime.txt` - Python version specification

## Database

The application uses SQLite by default. The database file (`chat.db`) will be created automatically when you first run the application.

For production, consider using PostgreSQL or MySQL for better performance and scalability.

## Security Notes

- Change the default secret key in production
- Consider using a production database like PostgreSQL
- Implement rate limiting for production use
- Add HTTPS in production environments
- Regularly update dependencies for security patches

## Support

If you encounter any issues:
1. Check the browser console for JavaScript errors
2. Check the server logs for Python errors
3. Ensure all dependencies are installed correctly
4. Verify environment variables are set properly 