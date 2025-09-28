# RAG Example - Recipe Retrieval System

A containerized Retrieval-Augmented Generation (RAG) system for recipe search using PostgreSQL with pgvector, FastAPI embedding service, and Express.js API.

## 🏗️ Architecture

This project consists of 3 containerized microservices:

1. **Database Service** (`db-service`)
   - PostgreSQL 17 with pgvector extension
   - Stores recipe content and embeddings
   - Internal network access only

2. **Embedding Service** (`embedding-service`)
   - FastAPI service using sentence-transformers
   - E5-small-v2 model for text embeddings
   - Provides `/embedding` endpoint for text vectorization

3. **API Service** (`api`)
   - Express.js/TypeScript REST API
   - Handles search queries and vector similarity
   - Connects to both database and embedding services

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

2. **Data Loading Setup Required**: Additional wiring is needed to:
   - Parse the `recipes.csv` file from the dataset
   - Generate embeddings for recipe content
   - Insert data into the PostgreSQL database with vector embeddings

3. **Current State**: The `import.sql` file is empty and serves as a placeholder for your data loading script.

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

### Health Check
```bash
GET http://localhost:4000/health
```

### Embedding Search
```bash
POST http://localhost:4000/embedding
Content-Type: application/json

{
  "query": "chocolate chip cookies"
}
```

**Response:**
```json
{
    "data":{
        "question":"query: I need a chocolate recipe.",
        "context":[...],
        "answer":"Here are five recipes that include chocolate, though some may not be directly relevant to your request:\n\n1. **Chocolate Pfeffernusse**  \n   - Steps: 6  \n   - Ingredients: 14  \n\n2. **Modeling Chocolate**  \n   - Steps: 7  \n   - Ingredients: 6  \n\n3. **Modeling Chocolate** (Kid Friendly)  \n   - Steps: 8  \n   - Ingredients: 0 (no specific ingredients listed)  \n\n4. **Chocolate Biscotti (No Butter)**  \n   - Steps: 12  \n   - Ingredients: 6  \n\n5. **Chocolate Chocolate, Baby!**  \n   - Steps: 5  \n   - Ingredients: 2  \n\nPlease note that while all these recipes involve chocolate, the second and third recipes are more about creating a chocolate modeling dough rather than a traditional dessert."
    },
    "status":{...},
    "timestamp":{...}
}
```

### Embedding Service (Direct)
```bash
POST http://localhost:8000/embedding
Content-Type: application/json

{
  "question": "query: sample text to embed"
}
```

## 🛠️ Development

### Data Loading Process

To set up the recipe database with the Kaggle dataset:

1. **Download and Extract**: Get the Food.com dataset from Kaggle
2. **Python Environment Setup**: Create a virtual environment for Python scripts:
   ```bash
   cd 2_Embedding
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Data Processing Script Needed**: Create a script to:
   ```python
   # Example workflow (implementation needed)
   - Load recipes.csv file
   - Clean and process recipe text (name, description, ingredients, steps)
   - Generate embeddings using the embedding service
   - Batch insert into PostgreSQL with vectors
   ```
4. **Database Population**: The current `2_Embedding/import.py` may serve as a starting point, but additional development is required.

### Project Structure

```
RAG_Example/
├── 1_Database_Setup/          # PostgreSQL with pgvector
│   ├── docker-compose.yml
│   └── import.sql
├── 2_Embedding/               # Python FastAPI service
│   ├── embedding_service.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── logs/
├── 3_RAG/                     # Express.js API
│   ├── server.ts
│   ├── lib/
│   ├── handlers/
│   ├── schemas/
│   ├── Dockerfile
│   └── package.json
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

| Variable | Description | Default |
|----------|-------------|---------|
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

## 🔒 Security

- Database and embedding services are not exposed externally
- Only the API service has external port access
- Services communicate through internal Docker network
- Environment variables for sensitive configuration