# StockSphere

StockSphere is a stock market analysis platform featuring a React frontend, a FastAPI backend, and MongoDB for database management.

## Getting Started

These instructions will get your copy of the StockSphere project up and running on your local machine for development and testing purposes. 

### Prerequisites

Before you begin, ensure you have the following installed:
- Git
- Docker
- Node.js
- npm or yarn

### Installation

First, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/StockSphere.git
cd StockSphere
```

### Docker Setup

To build and run the entire application using Docker, you can use the following commands:

```bash
# Build Docker images
docker-compose build

# Run Docker containers
docker-compose up
```

### Running Locally Without Docker

If you prefer to run the services individually without Docker, follow these steps:

### FastAPI Backend
Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

To run the FastAPI server:

```bash
uvicorn app.main:app --reload
```

This will start the backend server on http://localhost:8000.


To check all the API using swagger

```bash
[Swagger-Check-All-API](http://localhost:8000/docs#/)
```
### React Frontend

Navigate to the frontend directory and install dependencies:

```bash
cd ../frontend
npm install
```

To start the React development server:

```bash
npm start
```

### MongoDB

Ensure that MongoDB is running either as a Docker container or as a local/remote service.

### Getting Started

You can find the project file structure at tree.txt.

The main components are as below:

1) backend.app.collections : Contains all the json files for collections
[View Collections](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/collections)

2) backend.app.database : Script which connects to mongodb
[View DB scripts](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/database)

3) backend.app.ML : ML implementation and models
[View ML scripts and models](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/ML)

4) backend.app.routes: Contains all the routes and complex queries
[View routes](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/routes)
[View Complex Queries](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/routes/queries.py)

5) backend.app.scripts: Synthetic data generation for customers, agents and Transactions. (Used Faker component)
[Generate Customers, Agents & Stock Data](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/scripts/generate_data.py)
[Generate Customers, Agents & Crypto Data](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/scripts/generate_data_crypto.py)
[Save Collection Data](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/scripts/collections-save.py)

6) backend.app.tests: Test scripts to test queries, ML models and recommendation system implementation (recommendation system was an attempt) 
[Test Scripts](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/tests)

7) backend.app.utils: Script to populate data for stocks, stock_history, cryptocurrencies and crypto_history. Script to load the json files.
[Load Stock Data](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/utils/yahoo_finance.py)
[Load Crypto Data](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/utils/yahoo_finance_crypto.py)
[Load All Collections Data](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/utils/insert_collections_data.py)

8) backend.app.main.py : Connection to database and application backend startup.
[Main Startup](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/main.py)

9) backend.app.models.py : Schema structure for all collections
[Schema](https://github.com/abhishekjallawaram/StockSphere/tree/main/backend/app/models.py)

To load all the data into to collections navigate to /backend/app/utils and run the script insert_collections_data.py

```bash
cd /backend/app/utils
python insert_collections_data.py
```

