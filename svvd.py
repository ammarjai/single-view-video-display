import cv2
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

# TODO: Change video display on screen every x seconds, for each urls in list


class CircularBuffer:
    def __init__(self, size):
        self.buffer = []
        self.index = -1
        self.size = size

    def insert(self, item):
        if len(self.buffer) < self.size:
            self.buffer.append(item)
            self.index = len(self.buffer) - 1
        else:
            self.index = (self.index + 1) % self.size
            self.buffer[self.index] = item

    def empty(self):
        self.buffer.clear()
        return len(self.buffer)

    def get_latest(self):
        return self.buffer[self.index], self.index

    def is_empty(self):
        return True if len(self.buffer) == 0 else False


def fetch_loop(running: bool, capture, buffer: CircularBuffer):
    while running:
        ret, frame = capture.read()
        if not ret:
            print("Reached end of video, exiting.")
            break

        if not running:
            break

        buffer.insert(frame)

    print('fetch_loop stopped!')


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
    interframe_wait_ms = 1
    buffer = CircularBuffer(20)
    executor = ThreadPoolExecutor(1)
    thread_run = True

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit(2)

    # Set cv2 imshow to auto fullscreen
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.resizeWindow(window_name, 800, 480)

    future_1 = executor.submit(fetch_loop, thread_run, cap, buffer)

    # Application main loop
    # Read image from video capture and display on screen
    # Auto exit the loop on end of video or when pressing 'q'
    try:
        while True:
            start = time.perf_counter()

            if future_1.done():
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print("Error: Could not open video.")
                    exit(2)
                future_1 = executor.submit(fetch_loop, thread_run, cap, buffer)

            try:
                frame, _ = buffer.get_latest()
            except IndexError:
                continue

            cv2.imshow(window_name, frame)
            if cv2.waitKey(interframe_wait_ms) & 0x7F == ord('q'):
                print("Exit requested.")
                break

            total = time.perf_counter() - start
            sleep = 0.05 - total
            if sleep > 0:
                time.sleep(sleep)

    except KeyboardInterrupt:
        pass

    finally:
        # Cleanup
        thread_run = False
        executor.shutdown(wait=False, cancel_futures=True)
        cap.release()
        cv2.destroyAllWindows()
