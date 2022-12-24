import streamlit as st
from main import analyze_zip


def main_page():
    st.write('Welcome')


def compare_zips():
    st.write('Compare Zips...')
    with st.spinner('Loading...'):
        fig = analyze_zip(90210)
        st.plotly_chart(fig)


if __name__ == '__main__':
    page_names_to_funcs = {
        #"Main Page": main_page,
        "Compare Zips": compare_zips,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
