# RAG Example - Recipe Retrieval System

A containerized Retrieval-Augmented Generation (RAG) system for recipe search using PostgreSQL with pgvector, FastAPI embedding service, and Express.js API with LangChain integration.

## 🏗️ Architecture

This project consists of 3 containerized microservices:

1. **Database Service** (`db-service`)
   - PostgreSQL 17 with pgvector extension
   - Stores recipe content and embeddings with HNSW indexing
   - Internal network access only
   - Health checks and automatic restart

2. **Embedding Service** (`embedding-service`)
   - FastAPI service using sentence-transformers
   - E5-small-v2 model for text embeddings (384 dimensions)
   - Provides `/embedding` endpoint for text vectorization
   - Includes health checks and logging

3. **API Service** (`api`)
   - Express.js/TypeScript REST API with LangChain integration
   - Handles search queries using LangGraph for RAG workflows
   - Connects to both database and embedding services
   - Includes rate limiting and error handling

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 23+ (for local development)
- Python 3.11+ (for local development)

### Environment Setup

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_USER=your_db_user
DB_PASS=your_secure_password_here
DB_NAME=fooddb
DB_PORT=5432

# API Configuration
PORT=4000

# Embedding Service
EMBEDDING_SERVICE_PORT=8000

# OpenAI (optional)
OPENAI_API_KEY=your_openai_key_here
```

### Data Setup

**Important**: This repository doesn't include the initial database dump due to size constraints. To populate the database with recipe data:

1. **Download the dataset** from [Kaggle - Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/data)

2. **Prerequisites for Data Import**:
   - **PostgreSQL Instance**: You need a running PostgreSQL instance to create the database dump
   - **Database Setup**: Create the database and run the schema:
     ```bash
     # Start PostgreSQL (if using Docker)
     docker run --name temp-postgres -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=fooddb -p 5432:5432 -d postgres:17
     ```

3. **Data Loading Process**: The system includes a complete data loading pipeline:
   - Place the `recipes.csv` file in `2_Embedding/data/` directory
   - Set up your `.env` file with database connection details
   - The `import.py` script processes the CSV file and:
     - Parses recipe images, instructions, and metadata
     - Filters recipes with valid images and instructions
     - Generates embeddings using the E5-small-v2 model
     - Batch inserts data into PostgreSQL with vector embeddings
   - Run the import script: `python 2_Embedding/import.py`

4. **Create Database Dump**: After successful import, create the dump for Docker:
   ```bash
   # Create the dump file that docker-compose will use
   pg_dump -h localhost -U your_user -d fooddb > 1_Database_Setup/import.sql
   ```

### Running with Docker

1. **Start all services:**
   ```bash
   docker-compose up --build -d
   ```

2. **Check service health:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

## 📡 API Endpoints

### Main API Service (Port 4000)

#### Health Check
```bash
GET http://localhost:4000/health
```

#### Recipe Search (RAG)
```bash
POST http://localhost:4000/retrieve
Content-Type: application/json

{
  "question": "chocolate chip cookies"
}
```

**Response:**
```json
{
    "data": {
        "question": "chocolate chip cookies",
        "context": [
            {
                "content": "Recipe content...",
                "metadata": {
                    "name": "Chocolate Chip Cookies",
                    "ingredients": 12,
                    "steps": 8,
                    "rating": 4.5
                }
            }
        ],
        "answer": "Here are some chocolate chip cookie recipes that match your search..."
    },
    "status": "ok",
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Embedding Service (Port 8000)

#### Service Information
```bash
GET http://localhost:8000/
```

#### Health Check
```bash
GET http://localhost:8000/health
```

#### Generate Embedding
```bash
POST http://localhost:8000/embedding
Content-Type: application/json

{
  "text": "chocolate chip cookies recipe"
}
```

**Response:**
```json
{
    "embedding": [0.1, -0.2, 0.3, ...],
    "processing_time": 0.05
}
```

#### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Development

### Data Loading Process

The system includes a complete data loading pipeline:

1. **Download Dataset**: Get the Food.com dataset from Kaggle
2. **Setup Data Directory**: Create `2_Embedding/data/` and place `recipes.csv` there
3. **Run Import Script**: 
   ```bash
   cd 2_Embedding
   python import.py
   ```

The import script automatically:
- Parses recipe images, instructions, and metadata using `parsers.py`
- Filters recipes with valid images and instructions
- Generates embeddings using the E5-small-v2 model
- Batch inserts data into PostgreSQL with vector embeddings
- Logs progress to `logs/import.log`

### Project Structure

```
RAG_Example/
├── 1_Database_Setup/          # PostgreSQL with pgvector
│   ├── create.sql            # Database schema and indexes
│   └── import.sql            # Database initialization
├── 2_Embedding/               # Python FastAPI service
│   ├── embedding_service.py  # FastAPI application
│   ├── import.py            # Data loading script
│   ├── parsers.py           # Recipe parsing utilities
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Container configuration
│   └── logs/               # Service logs
├── 3_RAG/                     # Express.js API with LangChain
│   ├── server.ts           # Main application server
│   ├── handlers/           # API route handlers
│   │   ├── health.ts
│   │   ├── retrieve.ts
│   │   └── ...
│   ├── lib/                # Core libraries
│   │   ├── vectorStore.ts  # Vector store integration
│   │   ├── langchain.ts    # LangChain configuration
│   │   └── ...
│   ├── schemas/            # Request/response schemas
│   ├── middlewares/        # Express middlewares
│   ├── types/              # TypeScript type definitions
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Container configuration
├── docker-compose.yml         # Multi-service orchestration
└── README.md
```

## 🔧 Configuration

### Database Schema

The system uses a `recipes` table with the following structure:

```sql
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),           -- E5-small-v2 embeddings (384 dimensions)
    metadata JSONB                   
);

CREATE INDEX ON recipes USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON recipes USING gin (metadata);
```

**Note**: The database starts empty. You'll need to populate it with recipe data from the Kaggle dataset using a custom data loading script.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_HOST` | Database hostname 
| `DB_PORT` | Database port
| `DB_USER` | Database username
| `DB_PASS` | Database password
| `DB_NAME` | Database name
| `PORT` | API service port
| `EMBEDDING_SERVICE_URL` | Embedding service URL

## 📊 Performance

- **Embedding Model:** E5-small-v2 (384 dimensions)
- **Vector Search:** HNSW index for fast similarity search
- **Database:** PostgreSQL with pgvector extension

## ✨ Features

- **Vector Search**: Fast similarity search using HNSW indexing
- **RAG Pipeline**: LangChain integration with LangGraph for intelligent recipe retrieval
- **Scalable Architecture**: Microservices with health checks and auto-restart
- **Rate Limiting**: Built-in API rate limiting for production use
- **Comprehensive Logging**: Detailed logging across all services
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Data Validation**: Zod schema validation for all API inputs
- **Error Handling**: Graceful error handling and shutdown procedures

## 🔒 Security

- Database and embedding services are not exposed externally
- Only the API service has external port access
- Services communicate through internal Docker network
- Environment variables for sensitive configuration
- Rate limiting to prevent abuse
- Input validation and sanitization

## 🐛 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check service status
docker-compose ps

# View logs for specific service
docker-compose logs db-service
docker-compose logs embedding-service
docker-compose logs api
```

#### Database Connection Issues
- Ensure PostgreSQL is healthy: `docker-compose logs db-service`
- Check environment variables in `.env` file
- Verify database credentials and network connectivity

#### Embedding Service Issues
- Check if model is loading: `curl http://localhost:8000/health`
- View embedding service logs: `docker-compose logs embedding-service`
- Ensure sufficient memory for the E5-small-v2 model

#### API Service Issues
- Check API health: `curl http://localhost:4000/health`
- Verify all environment variables are set
- Check rate limiting if getting 429 errors

### Performance Optimization

- **Memory**: Ensure at least 4GB RAM for embedding service
- **Storage**: SSD recommended for vector database performance
- **Batch Size**: Adjust `BATCH_SIZE` in `import.py` based on available memory
- **Index Tuning**: Modify HNSW parameters in `create.sql` for your use case

### Data Import Issues

- Ensure `recipes.csv` is in `2_Embedding/data/` directory
- Check CSV file format and encoding
- Monitor import logs: `tail -f 2_Embedding/logs/import.log`
- Verify database has sufficient storage space
- **Database Connection**: Ensure PostgreSQL is running and accessible
- **Environment Variables**: Verify `.env` file has correct database credentials
- **Database Dump**: After import, ensure `pg_dump` creates the `import.sql` file successfully
- **Docker Volume**: The `import.sql` file will be mounted as `/docker-entrypoint-initdb.d/init.sql` in the container

## 📚 Additional Resources

- [PostgreSQL pgvector Documentation](https://github.com/pgvector/pgvector)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [E5 Embedding Model](https://huggingface.co/intfloat/e5-small-v2)

## 🙏 Acknowledgments

- [Food.com Recipes and Reviews Dataset](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews) on Kaggle
- [E5 Embedding Model](https://huggingface.co/intfloat/e5-small-v2) by Microsoft
- [LangChain](https://github.com/langchain-ai/langchain) for RAG framework
- [pgvector](https://github.com/pgvector/pgvector) for PostgreSQL vector support