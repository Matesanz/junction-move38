"""Renderiza la página principal."""

import io
import json
from datetime import datetime

import fingerprinting
import numpy as np
import streamlit as st
from PIL import Image
from sqlitedict import SqliteDict

db = SqliteDict("traces.db", tablename="demo", autocommit=True)


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
        download_time = datetime.now()
        metadata = {
            "timestamp": download_time.timestamp(),
            "download_date": download_time.strftime("%D/%M/%Y, %H:%M:%S"),
            "parent_id": parent_id,
            "child_id": child_id,
            "security_level": level,
        }

        fingerprinted, fingerprint = fingerprinting.fingerprint_image(
            np.array(Image.open(image_file)), metadata
        )
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
