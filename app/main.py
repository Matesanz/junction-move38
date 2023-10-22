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

    st.markdown("Sube la foto, elige los datos, anonimiza, encripta, y descarga.")
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
            "download_date": download_time.strftime("%d/%m/%Y, %H:%M:%S"),
            "parent_id": parent_id,
            "child_id": child_id,
            "security_level": level,
        }

        fingerprinted, fingerprint = fingerprinting.fingerprint_image(image_file, metadata)
        Image.fromarray(fingerprinted - np.resize(image_file, fingerprinted.shape)).save("diff.png")
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
                try:
                    metadata = db[fingerprint]
                    st.json(metadata)
                except Exception:
                    st.error("La entrada no esta en la base de datos!")
            if fingerprint is None:
                status.status(label="No se encontro ninguna huella ¯\_(ツ)_/¯", state="error")


def _render_about():
    st.markdown("### ¿Qué es SnapGuard?")
    st.markdown("SnapGuard es un pequeño guardian que protege a los más pequeños en una foto. Este pequeño guardian permite a padres y tutores elegir el nivel de privacidad de la foto a compartir, y permite trazar el origen de usos incorrectos.")

    st.markdown("### ¿Cómo funciona?")
    st.markdown("Sube una foto, elige un nivel de permisos, y descarga tu foto anonimizada y firmada. Posteriormente podrás subir una imagen firmada para recuperar la firma y la información de traza.")

    st.markdown("### ¿Cómo lo hacemos?")
    st.markdown("Usamos criptografía e inteligencia artificial generativa para anonimizar y trazar imágenes. Nuestro método es resistente a recortes y ciertas modificaciones.")


def render_main():
    """Renderiza la página principal."""
    st.set_page_config(
        page_title="SNAPGUARD",
        page_icon="./app/assets/logo.png",
        layout="centered",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    st.image("./app/assets/banner.png")
    tab1, tab2, tab3 = st.tabs(["Proteger imagen", "Descifrar imagen", "Información"])

    with tab1:
        _render_lockfile()
    with tab2:
        _render_unlockfile()
    with tab3:
        _render_about()


if __name__ == "__main__":
    render_main()
