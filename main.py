import os
import subprocess
import sys

def run_pipeline():
    """
    Executes the pipeline of Python scripts sequentially.
    This method is cross-platform.
    """
    print("Starting the pipeline...")

    # Define the sequence of scripts to be executed
    scripts = [
        'create_env.py', # Usually a one-time setup
        'stage_1.py',
        'merge_sessions.py',
        'create_folders.py',
        'stage_2.py'
    ]

    try:
        # Execute each script in the list
        for script in scripts:
            print(f"--- Running {script} ---")
            
            # Use sys.executable to ensure we use the same Python interpreter
            # that is running this main script. This is best practice.
            subprocess.run([sys.executable, script], check=True)
            
            print(f"--- Finished {script} ---\n")
        
        print("✅ Pipeline completed successfully!")

    except FileNotFoundError as e:
        # This error occurs if a script in the list doesn't exist
        print(f"\n❌ Error: Script not found: {e.filename}")
        print("Please ensure all script files are in the correct directory.")
        sys.exit(1)
        
    except subprocess.CalledProcessError as e:
        # This error occurs if any script returns a non-zero exit code (i.e., it fails)
        print(f"\n❌ Error: A script failed with exit code {e.returncode}.")
        # The failing script's output/errors should be visible above
        sys.exit(1)

if __name__ == '__main__':
    run_pipeline()
