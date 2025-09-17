import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2

st.title("Proctored Final Assessment")
st.write("Your webcam will be used for proctoring. Please keep your face visible at all times.")

class HeadPoseDetector(VideoTransformerBase):
    def __init__(self):
        self.warning = False

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            self.warning = True
            cv2.putText(img, "WARNING: Face not detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        else:
            self.warning = False

        return img

ctx = webrtc_streamer(
    key="proctoring",
    video_transformer_factory=HeadPoseDetector,
    media_stream_constraints={"video": True, "audio": False},
    async_transform=True,
)

if ctx.video_transformer:
    if ctx.video_transformer.warning:
        st.warning("Please keep your face visible to the camera!")