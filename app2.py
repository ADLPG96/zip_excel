import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile

st.set_page_config(page_title="ZIP a Excel", layout="centered")

st.title("🗂️ Analiza Carpetas desde un ZIP")
st.write("Sube un archivo `.zip` que contenga carpetas. Se generará un Excel con la estructura.")

uploaded_file = st.file_uploader("📁 Sube tu archivo .zip", type=["zip"])

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "archivo.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        estructura_columnas = []
        estructura_niveles = []

        for carpeta_actual, subcarpetas, _ in os.walk(temp_dir):
            if '__MACOSX' in carpeta_actual:
                continue
            nivel = carpeta_actual.replace(temp_dir, '').count(os.sep)
            fila_columnas = [''] * nivel + [os.path.basename(carpeta_actual)]
            estructura_columnas.append(fila_columnas)
            estructura_niveles.append([nivel, os.path.basename(carpeta_actual)])

        max_cols = max(len(fila) for fila in estructura_columnas)
        estructura_columnas = [fila + [''] * (max_cols - len(fila)) for fila in estructura_columnas]

        excel_path = os.path.join(temp_dir, "estructura_folders.xlsx")
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            pd.DataFrame(estructura_columnas).to_excel(writer, sheet_name='Visual', index=False, header=False)
            pd.DataFrame(estructura_niveles, columns=['Nivel', 'Carpeta']).to_excel(writer, sheet_name='Por Nivel',
                                                                                    index=False)

        with open(excel_path, "rb") as f:
            st.success("✅ ¡Excel generado!")
            st.download_button("⬇️ Descargar Excel", f, file_name="estructura_folders.xlsx")