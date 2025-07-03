import sys, json, importlib.util, io, contextlib, os

def run_user_script(path):
    try:
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
        
        return {
            "stdout": stdout,
            "result": result
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: runner.py <script_path>"}))
        sys.exit(1)
    
    output = run_user_script(sys.argv[1])
    print(json.dumps(output))
    
    if "error" in output:
        sys.exit(1)

#==========================================================================================


# import sys, json, importlib.util, io, contextlib

# def run_user_script(path):
#     #import user scripts as python modules 
#     spec = importlib.util.spec_from_file_location("user_script", path)
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)

#     # Ensure scripts have main()
#     if not hasattr(module, "main"):
#         raise Exception("No main() in user script")

#     # stdout capture to redirect print stmts to buffer 
#     # capture return value and stdout separately
#     with io.StringIO() as buf, contextlib.redirect_stdout(buf):
#         result = module.main()
#         stdout = buf.getvalue()

#     # Ensure return value can be serialized to JSON
#     if not isinstance(result, (dict, list, str, int, float, bool, type(None))):
#         raise Exception("main() must return a JSON-serializable value")

#     return {
#         "stdout": stdout, 
#         "result": result
#     }

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print(json.dumps({"error": "Usage: runner.py <path>"}))
#         sys.exit(1)

#     try:
#         output = run_user_script(sys.argv[1])
#         print(json.dumps(run_user_script(sys.argv[1])))
#     except Exception as e:
#         print(json.dumps({"error": str(e)}))
#         sys.exit(1)


