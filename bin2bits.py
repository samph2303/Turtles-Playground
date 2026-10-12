import sys
import time

if len(sys.argv) !=2:
    print("try again")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file,"rb") as file:
        data = file.read()

    bits = ''.join(format(byte, '08b') for byte in data)

    for bit in bits:
        
        print(bit, end='', flush=True)
        time.sleep(0.001)
    
    print(f"\nTotal bits: {len(bits)}")

except FileNotFoundError:
    print("file not found")

except OSError as e:
    print(f"file error: {e}")