
import sys

try:
    with open(r'd:\Project\Doctor-Scheduling-System\backend\debug_output.txt', 'r', encoding='utf-16') as f:
        print(f.read())
except Exception as e:
    try:
         with open(r'd:\Project\Doctor-Scheduling-System\backend\debug_output.txt', 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as e2:
        print(f"Error reading file: {e}, {e2}")
