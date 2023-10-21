"""Renderiza la página principal."""

import streamlit as st


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

        st.download_button(
            label=":lock: ¡Descarga tu imagen protegida!",
            data=image_file,
            file_name=image_file.name,
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
