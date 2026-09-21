"""NeoHealth AI - FastAPI backend for the React frontend."""

import base64
import sys
import tempfile
from pathlib import Path

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------
# Project path
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# NeoHealth AI imports
# ---------------------------------------------------------

from src.config import CLASS_NAMES
from src.inference import load_model, predict_image
from src.gradcam import generate_gradcam, save_gradcam_overlay


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="NeoHealth AI API",
    description="Backend API for NeoHealth AI infant skin-condition screening.",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Model loading
# ---------------------------------------------------------

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

MODEL, DEVICE = load_model(device=DEVICE)


# ---------------------------------------------------------
# Helper: convert image file to base64 data URL
# ---------------------------------------------------------

def image_to_data_url(image_path: Path) -> str:
    """Convert an image file into a browser-compatible data URL."""

    image_bytes = image_path.read_bytes()

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    suffix = image_path.suffix.lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }

    mime_type = mime_types.get(
        suffix,
        "image/png",
    )

    return f"data:{mime_type};base64,{encoded}"


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    """Check whether the NeoHealth AI backend is running."""

    return {
        "status": "ok",
        "model": "EfficientNet-B0",
        "classes": CLASS_NAMES,
        "device": str(DEVICE),
    }


# ---------------------------------------------------------
# Prediction endpoint
# ---------------------------------------------------------

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    body_site: str = Form("Face / Cheeks"),
    patient_notes: str = Form(""),
):
    """
    Run NeoHealth AI screening on an uploaded image.

    Returns:
        prediction
        confidence
        class probabilities
        uncertainty status
        Grad-CAM visualization
    """

    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No image file was provided.",
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
    }

    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG and PNG images are supported.",
        )

    # -----------------------------------------------------
    # Save uploaded image temporarily
    # -----------------------------------------------------

    temporary_input = None
    temporary_gradcam = None

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(file_bytes)
            temporary_input = Path(temp_file.name)

        # -------------------------------------------------
        # Run EfficientNet prediction
        # -------------------------------------------------

        prediction_result = predict_image(
            temporary_input,
            model=MODEL,
            device=DEVICE,
        )

        # -------------------------------------------------
        # Generate Grad-CAM
        # -------------------------------------------------

        (
            original,
            predicted_index,
            gradcam_confidence,
            cam,
        ) = generate_gradcam(
            temporary_input,
            MODEL,
            DEVICE,
        )

        # -------------------------------------------------
        # Save Grad-CAM overlay
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".png",
        ) as temp_gradcam:

            temporary_gradcam = Path(
                temp_gradcam.name
            )

        save_gradcam_overlay(
            original,
            cam,
            temporary_gradcam,
        )

        # -------------------------------------------------
        # Convert images to browser-readable data URLs
        # -------------------------------------------------

        original_data_url = (
            f"data:{file.content_type or 'image/png'};"
            f"base64,"
            f"{base64.b64encode(file_bytes).decode('utf-8')}"
        )

        gradcam_data_url = image_to_data_url(
            temporary_gradcam
        )

        # -------------------------------------------------
        # Convert probabilities
        # -------------------------------------------------

        probabilities = prediction_result[
            "probabilities"
        ]

        probability_list = [
            {
                "label": class_name,
                "probability": float(
                    probabilities[class_name] * 100.0
                ),
            }
            for class_name in CLASS_NAMES
        ]

        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        return {
            "prediction": prediction_result["prediction"],
            "confidence": prediction_result["confidence"],
            "confidence_percent": prediction_result[
                "confidence_percent"
            ],
            "is_confident": prediction_result[
                "is_confident"
            ],
            "status": prediction_result["status"],
            "probabilities": probability_list,
            "gradcam": {
                "original_image": original_data_url,
                "heatmap_overlay": gradcam_data_url,
            },
            "body_site": body_site,
            "patient_notes": patient_notes,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"NeoHealth AI processing failed: {exc}",
        ) from exc

    finally:
        # -------------------------------------------------
        # Remove temporary files
        # -------------------------------------------------

        if temporary_input is not None:
            try:
                temporary_input.unlink(
                    missing_ok=True
                )
            except Exception:
                pass

        if temporary_gradcam is not None:
            try:
                temporary_gradcam.unlink(
                    missing_ok=True
                )
            except Exception:
                pass