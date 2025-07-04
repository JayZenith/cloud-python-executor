# Arbitrary Python Code Execution Service

This project implements an API service that takes a Python script as input via a POST request to the /execute endpoint. It executes the main() function within the provided script and returns its result along with any standard output generated during execution.

## Features
- Secure code execution using nsjail sandboxing (demonstrated locally)
- Support for common libraries (pandas, numpy, os)
- JSON-based API with error handling
- Lightweight Docker container


### Google Cloud Run Endpoint Example 1
```bash
curl -X POST https://cloud-python-executor-640759399043.us-central1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello from the cloud!\", \"status\": \"success\"}"
  }'
```
### Expected Output
```bash
-d {"result":{"message":"Hello from the cloud!","status":"success"},"stdout":""}
```

### Google Cloud Run Endpoint Example 2 (Error case: No main())

```bash
curl -X POST https://cloud-python-executor-640759399043.us-central1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def not_main(): pass"}'
```
### Expected Output
```bash
-d '{ "error": "No main() in user script" }'
```

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

### Security Considerations & nsjail
This assignment specifies use of nsjail for secure script execution and deployment to Google Cloud Run. This presents a critical conflict:
- nsjail requires low-level Linux kernel features (like namespaces and seccomp filters) that require priveleged operations on host system
- Google Cloud Run is a managed serverless platform where containers run in a highly secure, unprivileged environment. It does not allow the kind of privileged operations that nsjail requiers. Attempting to run nsjail on Cloud Run will result in permission errors and failure. 

Therefore, for deployment to Google Cloud Run, nsjail has been omitted. The app.py has the nsjail command logic commented out for the deployed version, and the Dockerfile does not include nsjail build steps, however, you can use the Dockerfile.nsjail for the nsjail implementation.

### Time Taken To Complete
Approximately 5-6 hours due to investiging the security issues

## Requirements
- Script must contain a `main()` function
- `main()` function must return a JSON-serializable object
- Maximum execution time: 5 seconds
- Available libraries: os, pandas, numpy, and Python standard library

