import sys
from pathlib import Path

import streamlit as st
from PIL import Image

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLASS_NAMES
from src.inference import load_model, predict_image
from src.gradcam import generate_gradcam


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="NeoHealth AI",
    page_icon="🩺",
    layout="wide",
)


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .result-box {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-top: 10px;
    }

    .confidence {
        font-size: 32px;
        font-weight: 700;
    }

    .disclaimer {
        font-size: 13px;
        color: #666;
        padding-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">NeoHealth AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Infant Skin Condition Screening using Deep Learning"
    "</div>",
    unsafe_allow_html=True,
)

st.info(
    "Upload an infant skin image to obtain an AI-based screening result "
    "and visual explanation."
)


# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------

@st.cache_resource
def get_model():
    return load_model()


try:
    model, device = get_model()
except Exception as exc:
    st.error(f"Unable to load the trained model: {exc}")
    st.stop()


# ---------------------------------------------------------
# Upload image
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload an infant skin image",
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, JPEG and PNG.",
)


if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    st.divider()

    # -----------------------------------------------------
    # Display uploaded image
    # -----------------------------------------------------

    left, right = st.columns(2)

    with left:
        st.subheader("Uploaded Image")
        st.image(
            image,
            caption=uploaded_file.name,
            use_container_width=True,
        )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    with st.spinner("Analyzing image..."):

       # Save uploaded image temporarily so the inference pipeline
# can process it using its expected image-path interface.
temp_image_path = PROJECT_ROOT / "temp_uploaded_image.png"
image.save(temp_image_path)

result = predict_image(
    temp_image_path,
    model=model,
    device=device,
)
        

    with right:

        st.subheader("Screening Result")

        prediction = result["prediction"]
        confidence = result["confidence_percent"]
        status = result["status"]

        st.markdown(
            f'<div class="result-box">'
            f"<h2>{prediction}</h2>"
            f'<div class="confidence">{confidence:.2f}%</div>'
            f"<p>Model confidence</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if result["is_confident"]:
            st.success("High-confidence screening result")
        else:
            st.warning(
                "Uncertain result — review by a qualified healthcare "
                "professional is recommended."
            )

    # -----------------------------------------------------
    # Probability distribution
    # -----------------------------------------------------

    st.divider()

    st.subheader("Class Probabilities")

    probabilities = result["probabilities"]

    for class_name in CLASS_NAMES:

        probability = probabilities[class_name]

        st.write(
            f"**{class_name}** — {probability * 100:.2f}%"
        )

        st.progress(
            float(probability)
        )

    # -----------------------------------------------------
    # Grad-CAM
    # -----------------------------------------------------

    st.divider()

    st.subheader("Explainable AI — Grad-CAM")

    st.write(
        "Grad-CAM highlights image regions that contributed to the "
        "model's prediction."
    )

    try:

        gradcam_image = generate_gradcam(
            image=image,
            model=model,
            device=device,
        )

        st.image(
            gradcam_image,
            caption="Grad-CAM visualization",
            use_container_width=True,
        )

    except Exception as exc:

        st.warning(
            f"Grad-CAM visualization could not be generated: {exc}"
        )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="disclaimer">'
    "<b>Important:</b> NeoHealth AI is a research and screening "
    "prototype. Model predictions and confidence values are not "
    "medical diagnoses and should not replace professional "
    "clinical evaluation."
    "</div>",
    unsafe_allow_html=True,
)