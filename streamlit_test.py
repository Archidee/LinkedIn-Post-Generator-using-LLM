import streamlit as st

def main():
    st.title("Streamlit App")
    st.write("Hello, World!")
    selected_tag = st.selectbox("Title", options=["Option 1", "Option 2", "Option 3"])

if __name__ == "__main__":
    main()