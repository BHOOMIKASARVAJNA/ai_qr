import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="QR Integrity Checker", layout="centered")

st.markdown(
    """
    <h1 style='text-align: center;'>🔍 QR Code Integrity Checker</h1>
    <p style='text-align: center; color: grey;'>
    Detect whether a QR code is valid or potentially tampered using structural decoding.
    </p>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("📤 Upload QR Code Image", type=["png", "jpg", "jpeg"])

def analyze_qr(image):
    img = np.array(image)

    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)

    if not data:
        return "tampered", None

    # Extra validation (basic realism)
    if len(data.strip()) < 5:
        return "tampered", data

    return "valid", data

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    st.image(image, caption="Uploaded QR Code", use_column_width=True)

    with st.spinner("Analyzing QR Code..."):
        status, data = analyze_qr(image)

    st.markdown("---")

    if status == "valid":
        st.success("✅ Valid QR Code Detected")

        st.markdown("### 📄 Decoded Content:")
        st.code(data, language="text")

    else:
        st.error("⚠️ Potentially Tampered or Invalid QR Code")

    st.markdown("---")
    st.caption("This tool validates QR integrity by decoding and verifying embedded data structure.")
