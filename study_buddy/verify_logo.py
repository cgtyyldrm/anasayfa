import base64
import os

try:
    if not os.path.exists("logo.png"):
        print("Error: logo.png not found")
        exit(1)
        
    with open("logo.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    print(f"Success! Length: {len(encoded_string)}")
    print(f"Start: {encoded_string[:50]}...")
except Exception as e:
    print(f"Error: {e}")
