import os
import sys
import subprocess
import platform

def build_c_library():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    is_windows = platform.system() == "Windows"
    lib_name = "libstudyc.dll" if is_windows else "libstudyc.so"
    output_path = os.path.join(current_dir, lib_name)
    src_files = [
        os.path.join(current_dir, "fast_index.c"),
        os.path.join(current_dir, "image_preprocess.c")
    ]
    cmd = ["gcc", "-O3", "-shared", "-o", output_path] + src_files + ["-lm"]
    print(f"Building C Core: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Build succeeded: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e.stderr}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("GCC not found, using pure-Python fallback", file=sys.stderr)
        return None

if __name__ == "__main__":
    build_c_library()