from flask import Flask, request, jsonify
import subprocess, os, json, tempfile, signal, sys

app = Flask(__name__)

def timeout_handler(signum, frame):
    raise TimeoutError("Script execution timed out")

def run_script_safe(script_code: str):
    """Run script with basic safety measures"""
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_code)
        script_path = f.name
    
    try:
        # Create runner script content
        runner_content = f'''
import sys, json, importlib.util, io, contextlib, signal, os

def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")

def run_user_script(path):
    try:
        # Set timeout alarm
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout
        
        # Import the script
        spec = importlib.util.spec_from_file_location("user_script", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for main function
        if not hasattr(module, "main"):
            raise Exception("Script must contain a 'def main():' function")

        # Capture stdout and run main
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            result = module.main()
            stdout = buf.getvalue()

        # Validate result is JSON serializable
        json.dumps(result)
        
        signal.alarm(0)  # Cancel alarm
        
        return {{
            "stdout": stdout,
            "result": result
        }}
    except TimeoutError:
        return {{"error": "Script execution timed out"}}
    except Exception as e:
        return {{"error": str(e)}}
    finally:
        signal.alarm(0)  # Make sure alarm is cancelled

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({{"error": "Usage: runner.py <script_path>"}}))
        sys.exit(1)
    
    output = run_user_script(sys.argv[1])
    print(json.dumps(output))
    
    if "error" in output:
        sys.exit(1)
'''
        
        # Write runner to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as runner_f:
            runner_f.write(runner_content)
            runner_path = runner_f.name
        
        try:
            # Run with subprocess timeout as backup
            result = subprocess.run(
                [sys.executable, runner_path, script_path], 
                capture_output=True, 
                text=True, 
                timeout=10  # 10 second hard timeout
            )
            return result
        finally:
            os.unlink(runner_path)
            
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            [], 1, stdout='{"error": "Script execution timed out"}', stderr=""
        )
    except Exception as e:
        return subprocess.CompletedProcess(
            [], 1, stdout=f'{{"error": "Execution failed: {str(e)}"}}', stderr=""
        )
    finally:
        if os.path.exists(script_path):
            os.unlink(script_path)

@app.route("/execute", methods=["POST"])
def execute():
    # Input validation
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data or "script" not in data:
        return jsonify({"error": "Missing 'script' field"}), 400
    
    if not isinstance(data["script"], str):
        return jsonify({"error": "'script' must be a string"}), 400

    if "def main(" not in data["script"]:
        return jsonify({"error": "Script must contain a 'def main():' function"}), 400

    # Execute script
    proc = run_script_safe(data["script"])
    
    if proc.returncode != 0:
        try:
            error_data = json.loads(proc.stdout)
            return jsonify({"error": error_data.get("error", "Execution failed")}), 500
        except:
            return jsonify({"error": "Execution failed"}), 500
    
    try:
        output = json.loads(proc.stdout)
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON output: {e}"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "Python Code Executor",
        "note": "nsjail sandboxing temporarily disabled for Cloud Run compatibility",
        "endpoints": {
            "POST /execute": "Execute Python code",
            "GET /health": "Health check"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

#===================================================================

# from flask import Flask, request, jsonify
# import subprocess, os, json, uuid


# app = Flask(__name__)

# NSJAIL_PATH = "/nsjail/nsjail"
# PYTHON_BIN = "/usr/bin/python3"
# RUNNER_PATH = "/app/runner.py"
# SANDBOX_DIR = "/tmp/sandbox"  # mounted inside container


# def run_script_with_nsjail(script_code: str):
#     #create unique filename for each script to prevent race conditions
#     script_path = os.path.join(SANDBOX_DIR, f"user_{uuid.uuid4().hex}.py")
#     #write user code to temporary file
#     with open(script_path, "w") as f:
#         f.write(script_code)

#     #nsjail cmd construction
#     cmd = [
#         NSJAIL_PATH,
#         "-Mo",                      # Mount mode, no network (prevent external comm)
#         "--time_limit=5",           # 5s timeout (prevent infinite loops)
#         "--cwd", SANDBOX_DIR,       
#         "--bindmount_ro", "/usr",   # Read-only access to system libs
#         "--bindmount_ro", "/lib",   
#         "--bindmount_ro", "/lib64",
#         "--bindmount_ro", "/app",              
#         "--bindmount", SANDBOX_DIR, # Read-write access to sandbox 
#         "--",
#         PYTHON_BIN,
#         RUNNER_PATH,
#         script_path
#     ]

#     # execute sandboxed command and clean up temp file
#     result = subprocess.run(cmd, capture_output=True, text=True)
#     os.remove(script_path)
#     return result



# @app.route("/execute", methods=["POST"])
# def execute():
#     # Check content type
#     if not request.is_json:
#         return jsonify({"error": "Content-Type must be application/json"}), 400
    
#     # Parse JSON with error handling
#     try:
#         data = request.get_json()
#     except Exception:
#         return jsonify({"error": "Invalid JSON"}), 400
    
#     # Validate required field exists
#     if not data or "script" not in data:
#         return jsonify({"error": "Missing 'script' field"}), 400
    
#     # Validate script is a string
#     if not isinstance(data["script"], str):
#         return jsonify({"error": "'script' must be a string"}), 400

#     # Execute script 
#     proc = run_script_with_nsjail(data["script"])
#     if proc.returncode != 0:
#         # return jsonify({"error": proc.stderr.strip()}), 500
#         # error_message = proc.stderr.strip().splitlines()[-1] if proc.stderr else "Unknown error"
#         # return jsonify({"error": error_message}), 500
#         try:
#             # Try to parse the last line of stderr as JSON (from runner.py)
#             last_line = proc.stdout.strip().splitlines()[-1]
#             parsed = json.loads(last_line)
#             return jsonify({"error": parsed.get("error", "Unknown error")}), 500
#         except Exception:
#             return jsonify({"error": "Execution failed"}), 500


#     # parse JSON output from runner 
#     try:
#         output = json.loads(proc.stdout)
#         return jsonify(output)
#     except Exception as e:
#         return jsonify({"error": f"Output not valid JSON: {e}"}), 500

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)



