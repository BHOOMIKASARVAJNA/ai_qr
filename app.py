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


SUSPICIOUS_TERMS = ["bogus", "fake", "fraud", "test", "dummy", "xyz"]


def is_suspicious_text(text):
    text_lower = text.lower()
    return any(word in text_lower for word in SUSPICIOUS_TERMS)


def extract_upi(data):
    try:
        parsed = urlparse(data)
        params = parse_qs(parsed.query)
        return params.get("pa", ["Not found"])[0]
    except:
        return "Not found"


def validate_upi(data):
    try:
        parsed = urlparse(data)
        params = parse_qs(parsed.query)

        pa = params.get("pa", [""])[0]
        pn = params.get("pn", [""])[0]

        if not pa or "@" not in pa:
            return False

        if is_suspicious_text(pa) or is_suspicious_text(pn):
            return False

        if not re.match(r"^[a-zA-Z0-9.\-_]+@[a-zA-Z]+$", pa):
            return False

        return True

    except:
        return False


def analyze_qr(image):
    img = np.array(image)
    detector = cv2.QRCodeDetector()

    data, _, _ = detector.detectAndDecode(img)

    if not data:
        return "invalid", None, None

    upi_id = None

    if data.startswith("upi://"):
        upi_id = extract_upi(data)
        if validate_upi(data):
            return "valid", data, upi_id
        else:
            return "invalid", data, upi_id

    if len(data.strip()) < 5 or is_suspicious_text(data):
        return "invalid", data, None

    return "valid", data, None


if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded QR Code", use_column_width=True)

    status, data, upi_id = analyze_qr(image)

    st.write("---")

    if status == "valid":
        st.success("Valid QR Code")
        st.subheader("Decoded Content")
        st.code(data)

    else:
        st.error("Invalid QR Code")

        if upi_id:
            st.subheader("Extracted UPI ID")
            st.code(upi_id)

    st.write("---")
    st.caption("Validation is based on QR decoding, structure checks, and rule-based content filtering.")
