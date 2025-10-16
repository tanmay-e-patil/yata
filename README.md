# Yata - Todo App

A simple todo application built with Python FastAPI backend, React TypeScript frontend, and Google OAuth authentication.

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript, managed by Bun
- **Database**: PostgreSQL for data persistence
- **Cache/Session**: Redis for session management
- **Authentication**: Google OAuth 2.0
- **Development Environment**: Docker Compose

## Prerequisites

- Docker and Docker Compose
- Google OAuth Client ID and Secret

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd yata
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Fill in your Google OAuth credentials in the `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

3. **Start the development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Google OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:3000/auth/callback`
6. Copy the Client ID and Client Secret to your `.env` file

## Project Structure

```
yata/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile.dev
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript types
│   │   ├── utils/        # Utility functions
│   │   └── App.tsx       # Main React component
│   ├── package.json
│   └── Dockerfile.dev
├── docker-compose.dev.yml
└── README.md
```

## API Endpoints

### Authentication
- `GET /api/v1/auth/google/login` - Redirect to Google OAuth
- `GET /api/v1/auth/google/callback` - OAuth callback handler
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user info

### Todos
- `GET /api/v1/todos` - Get all todos for authenticated user
- `POST /api/v1/todos` - Create new todo
- `GET /api/v1/todos/{id}` - Get specific todo
- `PUT /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo

## Development

### Backend Development
- The backend runs on port 8000 with hot reload enabled
- Database migrations are handled automatically on startup
- API documentation is available at `/docs`

### Frontend Development
- The frontend runs on port 3000 with hot reload enabled
- TypeScript is configured for strict type checking
- Tailwind CSS is used for styling

### Database Management
- PostgreSQL data is persisted in a Docker volume
- Redis is used for session management
- Database schema is created automatically on startup

## Production Deployment

For production deployment, you'll need to:

1. Use production Dockerfiles (not the `.dev` versions)
2. Set up proper environment variables
3. Configure HTTPS
4. Set up a proper database and Redis instance
5. Configure proper CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.