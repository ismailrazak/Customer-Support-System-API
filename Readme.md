# Customer Support API

An API built with Django REST Framework and Django Channels to enable real-time communication between customers and customer support representatives. The system implements a queue-based approach using Redis to manage customer support requests efficiently and dynamically.

## Features

- Real-time chat functionality using WebSocket connections
- Queue-based system for managing customer support requests
- Authentication using JWT tokens
- Automatic assignment of customer support representatives
- Capacity management for support representatives
- Persistent chat history
- Containerized deployment with Docker

## Technical Stack

- Django & Django REST Framework
- Django Channels for WebSocket support
- Redis for queue management
- JWT for authentication
- Docker & Docker Compose
## Queue System

The system implements a queue using Redis with the following features:

- Automatic assignment of available customer support representatives
- Queue management for customers when all representatives are busy
- Dynamic capacity management for support representatives
- Automatic reassignment when a chat is closed

## Quick Start with Docker

1. Clone the repository
```bash
git clone https://github.com/ismailrazak/Customer-Support-System-API.git
cd Customer-Support-System-API
```



2.Build and start the services:
```bash
# Build the images
docker-compose build

# Start the services in background
docker-compose up -d

# View logs
docker-compose logs -f
```

3.Run initial migrations:
```bash
docker-compose exec web python manage.py migrate
```



## API Endpoints

### Authentication
- `POST /auth/token/` - Obtain JWT token pair
- `POST /auth/token/refresh/` - Refresh JWT token
- `GET /auth/` - Authentication views (DRF built-in)

### User Registration
- `POST /api/register_customer/` - Register a new customer
- `POST /api/register_customer_rep/` - Register a new customer support representative

### Conversations
- `GET /api/conversations/` - List all conversations
- `GET /api/conversations/<str:pk>/` - Get specific conversation details

## WebSocket Connection

Connect to the WebSocket endpoint using postman:
```
ws://127.0.0.1:8000/ws/customer_support/0ef6966e-d9c2-4994-9071-bdae4649f37c/
```

### WebSocket Message Format

Messages should be sent as JSON objects:

```json
{
    "message": "Your message here"
}
```

For customer support representatives to close a chat:
```json
{
    "message": "Closing chat",
    "close_chat": true
}
```




