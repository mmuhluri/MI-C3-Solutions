# Timestamp Difference Service

## Features
- Web interface for easy input
- REST API endpoint (/compute)
- Load balanced between multiple nodes
- Docker containerization

## Running the Application

1. Build and start containers:
```bash
docker-compose up --build -d

for command line 
curl -X POST --data-binary @input.txt http://localhost:8080/compute



This implementation provides:
1. User-friendly web interface with form input
2. Maintains existing API functionality
3. Shows which container handled the request
4. Load balancing through Nginx
5. Responsive design with CSS styling
6. Error handling and input validation

The frontend and backend share the same input processing logic, ensuring consistent results between the web interface and API endpoints.