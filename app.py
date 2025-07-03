from flask import Flask, request, jsonify
import subprocess, os, json, uuid


app = Flask(__name__)

NSJAIL_PATH = "/nsjail/nsjail"
PYTHON_BIN = "/usr/bin/python3"
RUNNER_PATH = "/app/runner.py"
SANDBOX_DIR = "/tmp/sandbox"  # mounted inside container


def run_script_with_nsjail(script_code: str):
    #create unique filename for each script to prevent race conditions
    script_path = os.path.join(SANDBOX_DIR, f"user_{uuid.uuid4().hex}.py")
    #write user code to temporary file
    with open(script_path, "w") as f:
        f.write(script_code)

    #nsjail cmd construction
    cmd = [
        NSJAIL_PATH,
        "-Mo",                      # Mount mode, no network (prevent external comm)
        "--time_limit=5",           # 5s timeout (prevent infinite loops)
        "--cwd", SANDBOX_DIR,       
        "--bindmount_ro", "/usr",   # Read-only access to system libs
        "--bindmount_ro", "/lib",   
        "--bindmount_ro", "/lib64",
        "--bindmount_ro", "/app",              
        "--bindmount", SANDBOX_DIR, # Read-write access to sandbox 
        "--",
        PYTHON_BIN,
        RUNNER_PATH,
        script_path
    ]

    # execute sandboxed command and clean up temp file
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

    # Execute script 
    proc = run_script_with_nsjail(data["script"])
    if proc.returncode != 0:
        # return jsonify({"error": proc.stderr.strip()}), 500
        # error_message = proc.stderr.strip().splitlines()[-1] if proc.stderr else "Unknown error"
        # return jsonify({"error": error_message}), 500
        try:
            # Try to parse the last line of stderr as JSON (from runner.py)
            last_line = proc.stdout.strip().splitlines()[-1]
            parsed = json.loads(last_line)
            return jsonify({"error": parsed.get("error", "Unknown error")}), 500
        except Exception:
            return jsonify({"error": "Execution failed"}), 500


    # parse JSON output from runner 
    try:
        output = json.loads(proc.stdout)
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": f"Output not valid JSON: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)