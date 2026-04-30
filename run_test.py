import sys
import os

# Create a small script to test main.py non-interactively
def main():
    print("Testing MCQ Extractor with finallytesting.jpg...")
    # Overwrite the input() function to automatically return "finallytesting.jpg"
    import builtins
    original_input = builtins.input
    def mock_input(prompt=""):
        if "Enter path" in prompt:
            print(prompt + "finallytesting.jpg")
            return "finallytesting.jpg"
        return original_input(prompt)
    builtins.input = mock_input
    
    import main
    main.main()

if __name__ == "__main__":
    main()
