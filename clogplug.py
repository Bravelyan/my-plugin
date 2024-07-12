from octoprint.plugin import StartupPlugin, EventHandlerPlugin
import logging
import cv2
import numpy as np
import time
from threading import Thread


class PrintClogDetectionPlugin(StartupPlugin, EventHandlerPlugin):
    def __init__(self):
        self.monitoring = False
        self.check_interval = 10  # Check every 10 seconds
        self.camera_url = "http://localhost:8080/?action=stream"  # URL kamera
        self.clogging_threshold = 10  # Threshold deteksi clog

    def on_startup(self, host, port):
        self._logger.setLevel(logging.INFO)
        self._logger.info("PrintClogDetectionPlugin is starting up!")

    def on_event(self, event, payload):
        if event == "PrintStarted":
            self._logger.info("Print started, beginning clog detection...")
            self.monitoring = True
            Thread(target=self.monitor_camera).start()

        if event == "PrintDone" or event == "PrintFailed" or event == "PrintCancelled":
            self._logger.info("Print finished or cancelled, stopping clog detection.")
            self.monitoring = False

    def monitor_camera(self):
        cap = cv2.VideoCapture(self.camera_url)
        if not cap.isOpened():
            self._logger.error("Unable to open camera")
            self.monitoring = False
            return

        clogging_counter = 0

        while self.monitoring:
            ret, frame = cap.read()
            if not ret:
                self._logger.error("Failed to grab frame")
                self.monitoring = False
                break

            # Process the frame for clogging detection
            clogging_detected = self.detect_clogging(frame)
            if clogging_detected:
                clogging_counter += 1
            else:
                clogging_counter = 0

            if clogging_counter >= self.clogging_threshold:
                self._logger.error("Clogging detected, cancelling print!")
                self._printer.cancel_print()
                self.monitoring = False
                break

            time.sleep(self.check_interval)

        cap.release()

    def detect_clogging(self, frame):
        # Convert frame ke grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)

        # Threshold the image to get the foreground
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

        # Count the number of white pixels
        white_pixels = np.sum(thresh == 255) #800

        # Define a threshold for detecting clogging (adjust as needed)
        clogging_detected = white_pixels < 1000  # Example threshold

        return clogging_detected


__plugin_name__ = "PrintClogDetectionPlugin"
__plugin_pythoncompat__ = ">=3,<4"
__plugin_implementation__ = PrintClogDetectionPlugin()
