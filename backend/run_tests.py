import subprocess
import sys

def run_tests():
    with open("test_results.txt", "w", encoding='utf-8') as f:
        # Run auth tests
        f.write("=== AUTH TESTS ===\n")
        subprocess.run([sys.executable, "-m", "pytest", "tests/test_auth.py", "-v"], stdout=f, stderr=f)
        
        # Run schedule tests
        f.write("\n=== SCHEDULE TESTS ===\n")
        subprocess.run([sys.executable, "-m", "pytest", "tests/test_schedules.py", "-v"], stdout=f, stderr=f)

if __name__ == "__main__":
    run_tests()
