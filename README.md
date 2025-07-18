# 🤖 AI Chatbot with FastAPI

A professional-grade AI chatbot built with FastAPI, SQLAlchemy, SQLite, and OpenAI's API. This is a complete backend API that you can use to build chatbot applications.

## ✨ Features

- 🔐 **User Authentication** - JWT-based authentication system
- 💬 **AI Chat** - Powered by OpenAI's GPT models
- 📝 **Conversation Management** - Store and manage chat history
- 🗄️ **SQLite Database** - Lightweight database with SQLAlchemy ORM
- 📚 **Auto-Generated Documentation** - Interactive API docs with Swagger UI
- 🔒 **Secure** - Password hashing and JWT tokens
- 🚀 **Production Ready** - Well-structured, documented code

## 🏗️ Project Structure

```
chat_bot/
├── app/
│   ├── __init__.py           # Package initializer
│   ├── main.py              # FastAPI application and endpoints
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session management
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic models for validation
│   ├── crud.py              # Database operations (Create, Read, Update, Delete)
│   ├── auth.py              # Authentication utilities and JWT handling
│   └── chatbot_service.py   # OpenAI integration and chat logic
├── requirements.txt         # Python dependencies
├── run.py                  # Application startup script
├── env.example             # Environment variables template
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**
   
   Copy the environment template:
   ```bash
   copy env.example .env
   ```
   
   Edit `.env` file and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your-very-secret-key-change-this-in-production
   ```

3. **Run the Application**
   ```bash
   python run.py
   ```

That's it! Your chatbot API will be running at `http://localhost:8000`

## 📖 API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

The app uses environment variables for configuration. Here are the key settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `SECRET_KEY` | JWT secret key | Change in production |
| `DATABASE_URL` | Database connection string | `sqlite:///./chatbot.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |

## 🔄 How to Use the API

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpassword"
     }'
```

### 2. Login and Get Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpassword"
```

### 3. Send a Chat Message
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, how are you?"
     }'
```

### 4. Get All Conversations
```bash
curl -X GET "http://localhost:8000/conversations" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🏢 Understanding the Code

### Database Models (`models.py`)
- **User**: Stores user information and authentication data
- **Conversation**: Represents chat sessions between users and the bot
- **Message**: Individual messages within conversations

### API Endpoints (`main.py`)
- **Authentication**: `/auth/register`, `/auth/login`
- **Chat**: `/chat` - Main endpoint for chatting with the bot
- **Conversations**: CRUD operations for managing conversations
- **Users**: User profile management

### AI Integration (`chatbot_service.py`)
- Handles communication with OpenAI's API
- Manages conversation context and history
- Generates conversation titles automatically

### Security (`auth.py`)
- JWT token creation and validation
- Password hashing with bcrypt
- Authentication dependency injection for protected endpoints

## 🗄️ Database

The application uses SQLite by default, which creates a `chatbot.db` file in your project directory. The database schema includes:

- **users** table: User accounts and authentication
- **conversations** table: Chat sessions
- **messages** table: Individual chat messages

## 🔐 Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **CORS Support**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic models ensure data integrity

## 🚀 Production Deployment

For production deployment:

1. **Change the secret key** in your `.env` file
2. **Use a production database** like PostgreSQL
3. **Set up proper CORS origins** in `main.py`
4. **Use environment variables** for all sensitive data
5. **Consider using a reverse proxy** like Nginx

Example production startup:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🛠️ Development

To contribute or modify the code:

1. **Code Structure**: Each file has a specific purpose - keep it organized
2. **Database Changes**: Update models in `models.py` and run migrations
3. **New Endpoints**: Add them in `main.py` with proper authentication
4. **Testing**: Test your endpoints using the interactive docs at `/docs`

## 📚 Learning Resources

Since this is your first time with these technologies:

- **FastAPI**: https://fastapi.tiangolo.com/tutorial/
- **SQLAlchemy**: https://docs.sqlalchemy.org/en/20/tutorial/
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **JWT Authentication**: https://jwt.io/introduction/

## ❓ Common Issues

1. **"OpenAI API key not found"**: Make sure you've set `OPENAI_API_KEY` in your `.env` file
2. **"Could not validate credentials"**: Check that you're sending the JWT token in the Authorization header
3. **Database errors**: The database is created automatically on first run
4. **Module not found**: Make sure you've installed all requirements with `pip install -r requirements.txt`

## 🤝 Next Steps

Now that you have a working chatbot API, you can:

1. **Build a frontend** using React, Vue, or any framework
2. **Add more features** like file uploads, voice messages, etc.
3. **Integrate with other AI models** or services
4. **Deploy to cloud platforms** like AWS, Google Cloud, or Heroku
5. **Add real-time features** with WebSockets

Happy coding! 🎉
