import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='A user interface for vlite CRUD operations and management.')
    parser.add_argument('--interface', action='store_true', help='Launch the interface')

    args = parser.parse_args()

    if args.interface:
        subprocess.run(["streamlit", "run", "vlite/ui/gui.py"])

if __name__ == "__main__":
    main()