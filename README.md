# Python Code Execution Service

A secure API service that executes arbitrary Python code in a sandboxed environment using nsjail.

## Features

- Secure code execution using nsjail sandboxing
- Support for common libraries (pandas, numpy, os)
- JSON-based API with error handling
- Lightweight Docker container

## Local Development

### Build and Run
```bash
docker build -t python-executor .
docker run -p 8080:8080 python-executor
```

### Test Local Endpoint
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import pandas as pd\n\ndef main():\n    df = pd.DataFrame({\"a\": [1, 2, 3]})\n    print(\"DataFrame created\")\n    return {\"sum\": df[\"a\"].sum(), \"shape\": df.shape}"
  }'
```


### Google Cloud Run Endpoint
```bash
curl -X POST https://your-service-url.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello from the cloud!\", \"status\": \"success\"}"
  }'
```

## Requirements

- Script must contain a `main()` function
- `main()` function must return a JSON-serializable object
- Maximum execution time: 5 seconds
- Available libraries: os, pandas, numpy, and Python standard library

