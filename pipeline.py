import subprocess
import os
import tempfile
import sys
def run_pipeline(input_sequence):
    """
    Runs the complete pipeline: sequence -> CT file -> dot bracket -> CSV processing -> prediction
    """
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.seq', delete=False) as seq_file:
            seq_file.write(f">input_sequence\n{input_sequence}\n")
            seq_filename = seq_file.name
        # Compile C++ programs if needed
        if not os.path.exists("process1") or not os.path.exists("process2"):
            print("Compiling C++ programs...")
            subprocess.run(["g++", "-o", "process1", "process1.cpp"], check=True)
            subprocess.run(["g++", "-o", "process2", "process2.cpp"], check=True)
        try:
            # Step 1: Generate CT file using process1 (Fold)
            ct_filename = seq_filename.replace('.seq', '.ct')
            print(f"Step 1: Running Fold on {seq_filename} -> {ct_filename}")
            result1 = subprocess.run(["./process1", seq_filename, ct_filename], 
                                   capture_output=True, text=True, check=True)
            print("Step 1 completed: CT file generated")
            # Step 2: Generate dot bracket file using process2 (ct2dot)
            dot_filename = ct_filename.replace('.ct', '.dot')
            print(f"Step 2: Converting CT to dot bracket {ct_filename} -> {dot_filename}")
            result2 = subprocess.run(["./process2", ct_filename, "1", dot_filename], 
                                   capture_output=True, text=True, check=True)
            print("Step 2 completed: Dot bracket file generated")
            # Step 3: Process CT and dot files with process3.py
            print("Step 3: Processing CT and dot files for feature extraction")
            result3 = subprocess.run(["python3", "process3.py", ct_filename, dot_filename], 
                                   capture_output=True, text=True)
            if result3.returncode == 0:
                print("Step 3 completed: Feature extraction successful")
            else:
                print(f"Step 3 warning: {result3.stderr}")
            # Step 4: Run prediction with process4.py
            print("Step 4: Running model prediction")
            result4 = subprocess.run(["python3", "process4.py"], 
                                   capture_output=True, text=True)
            if result4.returncode == 0:
                print("Step 4 completed: Prediction successful")
                return result4.stdout.strip()
            else:
                print(f"Step 4 warning: {result4.stderr}")
                return f"Prediction completed with warnings: {result4.stderr}"
        finally:
            # Clean up temporary files
            for temp_file in [seq_filename, ct_filename, dot_filename]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    except subprocess.CalledProcessError as e:
        return f"Error in pipeline step: {e.stderr if e.stderr else str(e)}"
    except Exception as e:
        return f"Pipeline error: {str(e)}"
if name == "main":
    if len(sys.argv) > 1:
        input_seq = " ".join(sys.argv[1:])
        result = run_pipeline(input_seq)
        print(result)
    else:
        print("Usage: python3 pipeline.py <input_sequence>")
        print("Example: python3 pipeline.py AUGCUGCUGCUGAUC")
