import streamlit as st

st.set_page_config(
    page_title="Geoex AI: Seu assistente virtual baseado em IA",
    page_icon="🧠",
)

css_path = 'styles/style.css'
with open(css_path) as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


st.write("# Bem vindo ao Geoex AI 🧠")

st.sidebar.success("Selecione qual ferramenta de IA quer utilizar!")

st.markdown(
    """
    ### Em apenas um clique
    
    O Geoex AI é um assistente virtual baseado em IA que te da insights rapidos e precisos sobre dados presentes no sistema do Geoex
    
    No menu lateral você pode escolher entre as seguintes ferramentas:
    
    - **Projetos e Carteiras**: Consulte informações sobre Projetos e Carteiras de obras
    - **Coming Soon**: Novas ferramentas de IA em breve!
    
    Esse projeto é uma iniciativa do time do Geoex para facilitar o acesso a informações de forma rapida, eficiente e descomplicada ;)
"""
)
