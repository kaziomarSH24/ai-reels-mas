import sys

def main():
    # This is a test script to check if Laravel can communicate with Python
    if len(sys.argv) < 2:
        print("Error: No arguments provided from Laravel.")
        return
    
    movie_name = sys.argv[1]
    word = sys.argv[2]
    
    print(f"Success! Python received data from Laravel. Movie: {movie_name}, Word: {word}")
    print("Next step: We will use MoviePy to cut the video here!")

if __name__ == "__main__":
    main()
