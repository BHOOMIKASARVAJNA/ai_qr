import streamlit as st
from PIL import Image
import numpy as np
import cv2
import re
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="QR Code Integrity Checker", layout="centered")

st.title("QR Code Integrity Checker")
st.write("Detect whether a QR code is valid or potentially tampered using structural and content validation.")

uploaded_file = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])


# Suspicious keywords list
SUSPICIOUS_TERMS = ["bogus", "fake", "fraud", "test", "dummy", "xyz"]


def is_suspicious_text(text):
    text_lower = text.lower()
    for word in SUSPICIOUS_TERMS:
        if word in text_lower:
            return True
    return False


def validate_upi(data):
    try:
        parsed = urlparse(data)
        params = parse_qs(parsed.query)

        pa = params.get("pa", [""])[0]  # UPI ID
        pn = params.get("pn", [""])[0]  # Name

        # Basic structure validation
        if not pa or "@" not in pa:
            return False, "Invalid UPI ID structure"

        # Check suspicious words
        if is_suspicious_text(pa) or is_suspicious_text(pn):
            return False, "Suspicious keywords detected"

        # Basic format check
        if not re.match(r"^[a-zA-Z0-9.\-_]+@[a-zA-Z]+$", pa):
            return False, "Malformed UPI ID"

        return True, data

    except Exception:
        return False, "Parsing error"


def analyze_qr(image):
    img = np.array(image)
    detector = cv2.QRCodeDetector()

    data, points, _ = detector.detectAndDecode(img)

    if not data:
        return "tampered", "QR not readable"

    # Check if it's a UPI QR
    if data.startswith("upi://"):
        is_valid, message = validate_upi(data)
        if is_valid:
            return "valid", data
        else:
            return "tampered", message

    # Generic QR validation
    if len(data.strip()) < 5:
        return "tampered", "Data too short"

    if is_suspicious_text(data):
        return "tampered", "Suspicious content detected"

    return "valid", data


if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded QR Code", use_column_width=True)

    status, result = analyze_qr(image)

    st.write("---")

    if status == "valid":
        st.success("Valid QR Code")
        st.subheader("Decoded Content")
        st.code(result)
    else:
        st.error("Potentially Tampered or Invalid QR Code")
        st.subheader("Reason")
        st.write(result)

    st.write("---")
    st.caption("Validation is based on QR decoding, structure checks, and rule-based content filtering.")
