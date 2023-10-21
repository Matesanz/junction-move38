"""Renderiza la página principal."""

import streamlit as st
import fingerprinting
import numpy as np
from PIL import Image
from datetime import datetime
import io


def _render_lockfile():

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
        st.image(image_file)
        # TODO: Llamada función Rubén uwu
        metadata = {
            "timestamp": datetime.now().timestamp(),
            "parent_id": parent_id,
            "child_id": child_id,
            "security_level": level
        }

        fingerprinted, fingerprint, metadata = fingerprinting.fingerprint_image(
            np.array(Image.open(image_file)), metadata)
        fingerprinted_buffer = io.BytesIO()
        Image.fromarray(fingerprinted).save(fingerprinted_buffer, format='PNG')
        # TODO: Añadir a bbdd

        st.download_button(
            label=":lock: ¡Descarga tu imagen protegida!",
            data=fingerprinted_buffer.getvalue(),
            file_name='fingerprinted.png',
        )


def _render_unlockfile():
    image_file = st.file_uploader("¡Sube tu imagen!", key="unlockfile")

    if image_file is not None:
        st.image(image_file)

        # TODO: llama a la función de Rubén uwu

        st.json(
            {
                "parent_id": "123456789",
                "child_id": "987654321",
                "level": "Nivel 1 (no compartir con nadie)",
            }
        )


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
