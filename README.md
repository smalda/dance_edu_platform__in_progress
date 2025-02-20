# Dance Education Platform 🎭

A comprehensive platform facilitating dance education through homework assignments, submissions, and feedback, powered by FastAPI and Telegram Bot interface.

## Quick Overview 🚀

- **Purpose**: Streamlines communication between dance teachers and students
- **Core Features**: Homework management, submissions handling, feedback system
- **Tech Stack**: FastAPI, PostgreSQL, RabbitMQ, Telegram Bot API, Prometheus, Alembic, SQLAlchemy (as sqlmodel)

## Features & Interactions 🔄

### For Teachers 👨‍🏫
- Assign homework to individual or multiple students
- Review student submissions
- Provide detailed feedback
- Track student progress

### For Students 👨‍🎓
- Receive homework assignments
- Submit completed work
- Get notifications about feedback
- Track personal progress

### Key Interactions
1. Teacher assigns homework → Students receive notifications
2. Students submit work → Teachers get notified
3. Teachers provide feedback → Students receive updates

## Technical Implementation 🛠

### Architecture
- **Backend**: FastAPI-based REST API
- **Database**: PostgreSQL with SQLModel ORM
- **Message Queue**: RabbitMQ for async notifications
- **Interface**: Telegram Bot
- **Monitoring**: Prometheus metrics

### Components
1. **API Server**
   - RESTful endpoints
   - Database operations
   - Event publishing

2. **Message Queue Consumer**
   - Processes notifications
   - Handles Telegram message delivery
   - Manages message persistence

3. **Telegram Bot**
   - Command handling
   - Conversation management
   - User interaction flows

### Deployment
- Dockerized services
- docker-compose orchestration
- Prometheus monitoring
- CI/CD with GitHub Actions

## Getting Started 🏃‍♂️

```bash
# Clone repository
git clone [repository-url]

# Set up environment
cp .env.template .env
# Fill in required credentials

# Start services
docker-compose -f docker/docker-compose.yml up -d

# Access API documentation
http://localhost:8000/docs
```

### Environment Variables
```
DATABASE_URL=postgresql://username:password@host:port/database_name
RABBITMQ_HOST=host
RABBITMQ_PORT=port
RABBITMQ_USER=username
RABBITMQ_PASS=password
TELEGRAM_BOT_TOKEN=your_bot_token
```

## Testing 🧪

```bash
# Run tests with coverage
pytest --cov=app

# Run specific test categories
pytest tests/test_api  # API tests
pytest tests/test_bot  # Bot tests
...
```

## Monitoring 📊

- Prometheus metrics available at `/metrics` in FastAPI or via Prometheus UI at http://localhost:9090
- Track:
  - Request counts and latency
  - Queue message statistics
  - Database operations
