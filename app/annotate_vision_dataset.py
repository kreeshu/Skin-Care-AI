"""Local Streamlit UI for creating gold multilabel cosmetic-concern annotations."""

import csv
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image


QUEUE = Path(os.environ.get("VISION_REVIEW_QUEUE", "data/vision/manifests/review_queue.csv"))
OUTPUT = Path(os.environ.get("VISION_ANNOTATION_OUTPUT", "data/vision/annotations/gold_labels.csv"))
CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")
OPTIONS = {"Unknown / cannot judge": -1, "Absent": 0, "Present": 1}


@st.cache_data
def load_queue():
    return pd.read_csv(QUEUE).fillna("")


def load_annotations():
    if not OUTPUT.exists():
        return {}
    with OUTPUT.open(newline="", encoding="utf-8") as handle:
        return {row["image_id"]: row for row in csv.DictReader(handle)}


def save_annotation(row):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    annotations = load_annotations()
    annotations[row["image_id"]] = row
    fields = ["image_id", "usable", "image_scope", *CONCERNS, "notes"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(annotations.values())


st.set_page_config(page_title="Skin Concern Annotation", layout="wide")
st.title("Cosmetic Concern Review")

if not QUEUE.exists():
    st.error(f"Missing review queue: {QUEUE}")
    st.stop()

queue = load_queue()
annotations = load_annotations()
pending = queue[~queue.image_id.astype(str).isin(annotations)]
st.progress(len(annotations) / len(queue), text=f"{len(annotations)} / {len(queue)} reviewed")

if pending.empty:
    st.success("All review images are annotated.")
    st.stop()

row = pending.iloc[0]
left, right = st.columns([3, 2])
with left:
    try:
        st.image(Image.open(row.original_path), use_container_width=True)
    except OSError as error:
        st.error(f"Cannot open image: {error}")
with right:
    st.caption(f"Image {len(annotations) + 1} of {len(queue)}")
    st.write(f"Source: `{row.source}`")
    st.write(f"Quality check: `{row.quality_status}`")
    with st.expander("Show source label"):
        st.write(row.original_label)

    with st.form(f"annotation_{row.image_id}"):
        usable = st.radio(
            "Usable facial skin image?", ["Yes", "No"], horizontal=True,
            key=f"usable_{row.image_id}",
        )
        scope = st.radio(
            "Image scope", ["Full face", "Facial close-up", "Not facial skin"], horizontal=True,
            key=f"scope_{row.image_id}",
        )
        labels = {
            concern: OPTIONS[st.selectbox(
                concern.replace("_", " ").title(), list(OPTIONS), key=f"{concern}_{row.image_id}"
            )]
            for concern in CONCERNS
        }
        notes = st.text_input("Notes (optional)", key=f"notes_{row.image_id}")
        if st.form_submit_button("Save and next", type="primary", use_container_width=True):
            save_annotation({
                "image_id": str(row.image_id),
                "usable": int(usable == "Yes"),
                "image_scope": {"Full face": "full_face", "Facial close-up": "facial_closeup", "Not facial skin": "not_facial"}[scope],
                **labels,
                "notes": notes,
            })
            st.rerun()
