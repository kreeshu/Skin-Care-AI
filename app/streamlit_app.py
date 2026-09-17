import streamlit as st
import pandas as pd
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.inference.predict import SkinAnalyzer
from backend.config import MODEL_EVALUATION_PATH, MODEL_METADATA_PATH, MODEL_PATH

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "enriched", "unified_products.csv")
MAPPINGS_DIR = os.path.join(BASE_DIR, "data", "mappings")


@st.cache_resource
def load_analyzer(use_slm: bool = False):
    products_df = pd.read_csv(PRODUCTS_PATH)
    analyzer = SkinAnalyzer(
        MODEL_PATH,
        products_df,
        MAPPINGS_DIR,
        metadata_path=MODEL_METADATA_PATH,
        evaluation_path=MODEL_EVALUATION_PATH,
        use_slm=use_slm,
    )
    return analyzer


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
    st.caption("Cosmetic skin-concern observations and grounded product recommendations for Nepal")

    use_slm = st.sidebar.checkbox(
        "AI explanations (local SLM)",
        value=False,
        help="Enable the backend-hosted local model to explain recommendations and build a routine.",
    )

    analyzer = load_analyzer(use_slm)
    skin_type = st.sidebar.selectbox(
        "Your skin type (optional)",
        [None, "dry", "normal", "oily", "combination", "sensitive"],
    )

    with st.sidebar:
        st.header("About")
        st.markdown("""
        **Model:** EfficientNetB0 multi-label pilot

        **Visible cosmetic concerns:**
        - Blemishes
        - Dark spots
        - Redness
        - Visible pores
        - Fine lines

        Skin type is user-provided, never inferred from a photo.

        **Product Sources:**
        - ForEveryNG
        - Jeevee
        - Oriflame
        """)

        st.divider()
        st.markdown("**How to use:**")
        st.markdown("1. Upload a clear facial image")
        st.markdown("2. Click **Analyze**")
        st.markdown("3. View detection + recommendations")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📷 Input Image")

        uploaded_image = None
        uploaded_file = st.file_uploader("Upload a facial image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            uploaded_image = Image.open(uploaded_file)
            st.image(uploaded_image, caption="Uploaded Image", width="stretch")
        image_to_analyze = uploaded_image

        analyze_clicked = st.button(
            "🔍 Analyze",
            type="primary",
            width="stretch",
            disabled=image_to_analyze is None,
        )

    with col2:
        st.subheader("🔍 Analysis Results")

        if not analyze_clicked and "result" not in st.session_state:
            st.info("Upload an image or select a sample, then click **Analyze**.")
            return

        if analyze_clicked and image_to_analyze is not None:
            with st.spinner("Analyzing..."):
                result = analyzer.analyze(image_to_analyze, skin_type=skin_type)
            st.session_state["result"] = result

        if "result" not in st.session_state:
            st.info("Upload an image or select a sample, then click **Analyze**.")
            return

        result = st.session_state["result"]
        st.markdown(f"### {result['title']}")
        for concern in result["concerns"]:
            st.progress(concern["score"], text=f"{concern['name'].replace('_', ' ').title()}: {concern['status']} ({concern['score']:.1%} model score)")

        st.markdown(f"**{result['description']}**")

        if result.get("skin_type"):
            st.info(
                f"Your stated skin type: **{result['skin_type']}**"
            )

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
            st.warning("No personalized products available for this result.")

        slm = result.get("slm")
        if slm:
            st.divider()
            st.subheader("🤖 AI Explanations")
            for item in slm.get("chosen", []):
                st.markdown(
                    f"- **{item['name']}** ({item['category']}): {item['reason']}"
                )
            routine = slm.get("routine", {})
            if routine.get("am") or routine.get("pm"):
                st.markdown("**Your routine:**")
                col_am, col_pm = st.columns(2)
                with col_am:
                    st.markdown("**AM**")
                    for step in routine["am"]:
                        st.markdown(f"- {step}")
                with col_pm:
                    st.markdown("**PM**")
                    for step in routine["pm"]:
                        st.markdown(f"- {step}")

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
