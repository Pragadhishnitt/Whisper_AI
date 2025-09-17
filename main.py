import os
import subprocess
import sys

def run_pipeline():
    """
    Executes the pipeline of Python scripts based on the operating system.
    """
    if os.name == 'posix':  # Linux and macOS
        print("Running on a Unix-like system (Ubuntu/macOS)...")
        try:
            # The shell script path
            script_path = 'pipeline.sh'
            
            # Make sure the script is executable
            # You can also do this once in your terminal: chmod +x pipeline.sh
            if not os.access(script_path, os.X_OK):
                os.chmod(script_path, 0o755)

            # Execute the shell script
            subprocess.run([script_path], check=True, shell=True)
            print("Pipeline completed successfully!")
        except FileNotFoundError:
            print(f"Error: {script_path} not found. Please ensure it's in the correct directory.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error: The shell script failed with an error. Exit code: {e.returncode}")
            sys.exit(1)
    
    elif os.name == 'nt':  # Windows
        print("Running on Windows...")
        try:
            # List of Python scripts to run
            scripts = [
                'create_env.py',
                'stage_1.py',
                'merge_sessions.py',
                'create_folders.py',
                'stage_2.py'
            ]
            
            # Execute each script sequentially
            for script in scripts:
                print(f"Running {script} ...")
                # Use sys.executable to ensure the correct python interpreter is used
                subprocess.run([sys.executable, script], check=True)
            
            print("Pipeline completed successfully!")
        except FileNotFoundError:
            print(f"Error: A required Python script was not found. Please check your files.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error: A Python script failed with an error. Exit code: {e.returncode}")
            sys.exit(1)
            
    else:
        print(f"Unsupported OS: {os.name}. This script is designed for Windows, Ubuntu, and macOS.")
        sys.exit(1)

if __name__ == '__main__':
    run_pipeline()
