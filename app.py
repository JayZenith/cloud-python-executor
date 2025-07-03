from flask import Flask, request, jsonify
import subprocess, os, json, uuid

app = Flask(__name__)

NSJAIL_PATH = "/nsjail/nsjail"
PYTHON_BIN = "/usr/bin/python3"
RUNNER_PATH = "/app/runner.py"
SANDBOX_DIR = "/tmp/sandbox"  # mounted inside container


def run_script_with_nsjail(script_code: str):
    script_path = os.path.join(SANDBOX_DIR, f"user_{uuid.uuid4().hex}.py")
    with open(script_path, "w") as f:
        f.write(script_code)

    cmd = [
        NSJAIL_PATH,
        "-Mo",
        "--time_limit=5",
        "--cwd", SANDBOX_DIR,
        "--bindmount_ro", "/usr",
        "--bindmount_ro", "/lib",
        "--bindmount_ro", "/lib64",
        "--bindmount_ro", "/app",              
        "--bindmount", SANDBOX_DIR,
        "--",
        PYTHON_BIN,
        RUNNER_PATH,
        script_path
    ]


    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(script_path)
    return result



@app.route("/execute", methods=["POST"])
def execute():
    # Check content type
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    # Parse JSON with error handling
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400
    
    # Validate required field exists
    if not data or "script" not in data:
        return jsonify({"error": "Missing 'script' field"}), 400
    
    # Validate script is a string
    if not isinstance(data["script"], str):
        return jsonify({"error": "'script' must be a string"}), 400

    proc = run_script_with_nsjail(data["script"])
    if proc.returncode != 0:
        return jsonify({"error": proc.stderr.strip()}), 500

    try:
        output = json.loads(proc.stdout)
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": f"Output not valid JSON: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
