import cv2
import json
import os

# TODO: Change video display on screen every x seconds, for each urls in list

if __name__ == "__main__":
    # Load rtsp urls from data.json but first check existance of file and exit the program is not found
    # Also check for data format and exit the program if not in the correct format
    if not os.path.isfile("data.json"):
        print(f"Missing data.json file!")
        exit(1)

    with open("data.json", 'r') as f:
        data = json.load(f)
    
    if "rtsp_urls" not in data:
        print(f"Missing 'rtsp_urls' from data.json file!")
        exit(1)
    
    urls = data["rtsp_urls"]
    if not isinstance(urls, list):
        print(f"'rtsp_urls' not a list!")
        exit(1)
    
    if len(urls) <= 0:
        print(f"'rtsp_urls' is empty!")
        exit(1)

    # Assign the variables use for this app
    # And create the capture variable for looping
    video_path = urls[0]
    window_name = "window"
    interframe_wait_ms = 30

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit(2)

    # Set cv2 imshow to auto fullscreen
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Application main loop
    # Read image from video capture and display on screen
    # Auto exit the loop on end of video or when pressing 'q'
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Reached end of video, exiting.")
            break

        cv2.imshow(window_name, frame)
        if cv2.waitKey(interframe_wait_ms) & 0x7F == ord('q'):
            print("Exit requested.")
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()