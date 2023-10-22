"""Renderiza la página principal."""

import io
import json
import tempfile
from datetime import datetime

import cv2
import fingerprinting
import insightface
import numpy as np
import streamlit as st
import transform
from insightface.app import FaceAnalysis
from insightface.data import get_image
from PIL import Image
from sqlitedict import SqliteDict

db = SqliteDict("traces.db", tablename="demo", autocommit=True)


def _render_lockfile():
    app = FaceAnalysis(
        name="buffalo_s", providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )
    app.prepare(ctx_id=0, det_size=(640, 640))

    level = st.selectbox(
        "Nivel",
        [
            "Nivel 1 (no compartir con nadie)",
            "Nivel 2 (compartir conmigo)",
            "Nivel 3 (compartir con autorizados)",
            "Nivel 4 (compartir con todos)",
        ],
    )

    parent_id = st.text_input("ID del padre")

    child_id = st.text_input("ID del hijo")

    image_file = st.file_uploader("¡Sube tu imagen!", key="lockfile")

    if image_file is not None:
        _, tp = tempfile.mkstemp(suffix=".jpg")
        Image.open(image_file).save(tp)
        det_img = get_image(tp.replace(".jpg", ""))
        faces = app.get(det_img)
        boxes = [np.array([int(k) for k in face["bbox"]]) for face in faces]
        for face in faces:
            x1, y1, x2, y2 = face["bbox"]
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            cv2.rectangle(det_img, (x1, y1), (x2, y2), (255, 0, 0), 5)
        det_img = cv2.cvtColor(det_img, cv2.COLOR_BGR2RGB)
        image_file = transform.apply_transform(det_img, boxes, transform.blur_transformation)
        st.image(image_file)
        download_time = datetime.now()
        metadata = {
            "timestamp": download_time.timestamp(),
            "download_date": download_time.strftime("%D/%M/%Y, %H:%M:%S"),
            "parent_id": parent_id,
            "child_id": child_id,
            "security_level": level,
        }

        fingerprinted, fingerprint = fingerprinting.fingerprint_image(image_file, metadata)
        db[fingerprint] = json.dumps(metadata)
        fingerprinted_buffer = io.BytesIO()
        Image.fromarray(fingerprinted).save(fingerprinted_buffer, format="PNG")

        st.download_button(
            label=":lock: ¡Descarga tu imagen protegida!",
            data=fingerprinted_buffer.getvalue(),
            file_name="fingerprinted.png",
        )


def _render_unlockfile():
    image_file = st.file_uploader("¡Sube tu imagen!", key="unlockfile")

    if image_file is not None:
        st.image(image_file)

        # TODO: llama a la función de Rubén uwu
        with st.status("Buscando huella digital...", state="running") as status:
            fingerprint = fingerprinting.extract(np.array(Image.open(image_file)))
            if fingerprint is not None:
                status.update(label="Huella digital encontrada!", expanded=True, state="complete")
                st.success(fingerprint)
                # TODO: Buscar en bbdd
                metadata = db[fingerprint]
                st.json(metadata)
            if fingerprint is None:
                status.status(label="No se encontro ninguna huella ¯\_(ツ)_/¯", state="error")


def render_main():
    """Renderiza la página principal."""
    st.title("Move38 Junction")
    tab1, tab2 = st.tabs(["Proteger imagen", "Descifrar imagen"])

    with tab1:
        _render_lockfile()
    with tab2:
        _render_unlockfile()


if __name__ == "__main__":
    render_main()
