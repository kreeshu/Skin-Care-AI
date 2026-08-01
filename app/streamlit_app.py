import streamlit as st
import pandas as pd
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.inference.predict import SkinAnalyzer
from src.recommendation.condition_rules import ConditionRules

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
MODEL_PATH = os.path.join(BASE_DIR, "models", "skin_classifier.keras")
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "enriched", "unified_products.csv")
MAPPINGS_DIR = os.path.join(BASE_DIR, "data", "mappings")
SKIN_DIR = os.path.join(BASE_DIR, "Skin_Conditions")

CONDITION_COLORS = {
    "Acne": "#FF6B6B",
    "Carcinoma": "#D32F2F",
    "Eczema": "#FF9800",
    "Keratosis": "#9C27B0",
    "Milia": "#2196F3",
    "Rosacea": "#E91E63",
}


@st.cache_resource
def load_analyzer():
    products_df = pd.read_csv(PRODUCTS_PATH)
    analyzer = SkinAnalyzer(MODEL_PATH, products_df, MAPPINGS_DIR)
    analyzer.set_class_names(ConditionRules.all_conditions())
    return analyzer


def get_sample_images():
    samples = {}
    for condition in sorted(os.listdir(SKIN_DIR)):
        cond_dir = os.path.join(SKIN_DIR, condition)
        if os.path.isdir(cond_dir):
            imgs = [f for f in os.listdir(cond_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            if imgs:
                samples[condition] = os.path.join(cond_dir, imgs[0])
    return samples


def format_price(price):
    if price is None or pd.isna(price):
        return "N/A"
    return f"Rs. {int(price):,}"


def main():
    st.set_page_config(
        page_title="SkinCare AI",
        page_icon="🧴",
        layout="wide",
    )

    st.title(" SkinCare AI")
    st.caption("AI-powered skin condition detection and product recommendations for Nepal")

    analyzer = load_analyzer()
    sample_images = get_sample_images()

    with st.sidebar:
        st.header("About")
        st.markdown("""
        **Model:** EfficientNetB0 (88.6% accuracy)

        **Detects 6 conditions:**
        - Acne
        - Carcinoma
        - Eczema
        - Keratosis
        - Milia
        - Rosacea

        **Product Sources:**
        - ForEveryNG
        - Jeevee
        - Oriflame
        """)

        st.divider()
        st.markdown("**How to use:**")
        st.markdown("1. Upload a skin image or pick a sample")
        st.markdown("2. Click **Analyze**")
        st.markdown("3. View detection + recommendations")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📷 Input Image")

        tab_upload, tab_sample = st.tabs(["Upload Image", "Sample Images"])

        uploaded_image = None
        selected_image_path = None

        with tab_upload:
            uploaded_file = st.file_uploader(
                "Upload a skin image",
                type=["jpg", "jpeg", "png"],
                help="Upload a close-up photo of the skin condition",
            )
            if uploaded_file:
                uploaded_image = Image.open(uploaded_file)
                st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

        with tab_sample:
            selected_condition = st.selectbox(
                "Pick a sample condition",
                options=list(sample_images.keys()),
                index=None,
                placeholder="Select a condition...",
            )
            if selected_condition:
                selected_image_path = sample_images[selected_condition]
                st.image(
                    selected_image_path,
                    caption=f"Sample: {selected_condition}",
                    use_container_width=True,
                )

        image_to_analyze = None
        if uploaded_image is not None:
            image_to_analyze = uploaded_image
        elif selected_image_path is not None:
            image_to_analyze = selected_image_path

        analyze_clicked = st.button(
            "🔍 Analyze",
            type="primary",
            use_container_width=True,
            disabled=image_to_analyze is None,
        )

    with col2:
        st.subheader("🔍 Analysis Results")

        if not analyze_clicked and "result" not in st.session_state:
            st.info("Upload an image or select a sample, then click **Analyze**.")
            return

        if analyze_clicked and image_to_analyze is not None:
            with st.spinner("Analyzing..."):
                result = analyzer.analyze(image_to_analyze)
            st.session_state["result"] = result

        if "result" not in st.session_state:
            st.info("Upload an image or select a sample, then click **Analyze**.")
            return

        result = st.session_state["result"]
        condition = result["detected_condition"]
        confidence = result["model_confidence"]
        color = CONDITION_COLORS.get(condition, "#666666")

        st.markdown(
            f'<div style="background-color:{color}20; border-left:4px solid {color}; '
            f'padding:16px; border-radius:4px; margin-bottom:16px;">'
            f'<h3 style="color:{color}; margin:0;">{condition}</h3>'
            f'<p style="margin:4px 0;">Confidence: <strong>{confidence:.1%}</strong></p>'
            f'<p style="margin:4px 0;">{result["title"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(f"**{result['description']}**")

        if result["is_medical"] and condition == "Carcinoma":
            st.error(
                "⚠️ This may indicate a serious skin condition. "
                "Please consult a dermatologist immediately."
            )
            st.stop()

        st.divider()
        st.subheader("🛒 Recommended Products")

        if result["recommendations"]:
            for category, recs in result["recommendations"].items():
                with st.expander(f"**{category.upper()}** ({len(recs)} products)", expanded=True):
                    for rec in recs[:3]:
                        ingredients_text = ", ".join(rec["matching_ingredients"]) if rec["matching_ingredients"] else "N/A"
                        price = format_price(rec["discounted_price"] or rec["price"])
                        rating = f"⭐ {rec['rating']:.1f}" if rec["rating"] else "No rating"

                        st.markdown(
                            f'<div style="padding:8px 0; border-bottom:1px solid #eee;">'
                            f'<strong>{rec["name"][:60]}</strong>'
                            f'<br/><span style="color:#666;">{rec["brand"]} | {price} | {rating} | Score: {rec["score"]:.3f}</span>'
                            f'<br/><span style="color:#888; font-size:0.85em;">Ingredients: {ingredients_text}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
        else:
            st.warning("No product recommendations available for this condition.")

        st.divider()
        st.subheader("📋 Suggested Routine")
        for i, step in enumerate(result["routine_suggestion"], 1):
            st.markdown(f"**{i}.** {step}")

        st.divider()
        st.caption(
            "⚕️ These are cosmetic recommendations only and do not constitute medical advice. "
            "Please consult a dermatologist for medical concerns."
        )


if __name__ == "__main__":
    main()
