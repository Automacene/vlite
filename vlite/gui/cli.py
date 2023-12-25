import argparse

def main():
    parser = argparse.ArgumentParser(description='Your package CLI')
    parser.add_argument('--interface', action='store_true', help='Launch the interface')

    args = parser.parse_args()

    if args.interface:
        print("This is a test.")

if __name__ == "__main__":
    main()