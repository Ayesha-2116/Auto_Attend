import streamlit as st
def apply_custom_css():
    custom_css = """
    <style>
   
    #autoattend-tracker {
        margin-left: auto;
        color:DodgerBlue;
        padding: inherit;
      
    }
    .header-section {
        background-color: #f0f2f6;
        /*padding: 20px;*/
        border-radius: 10px;
        color: DodgerBlue;
        text-align: center;
        margin-bottom: 20px;
        font-size: 2.5em;
        font-weight: bold;
        position: fixed;
        top: 7%;
        left: 0;
        width: 100%;
        z-index: 1000;
        margin-left: auto;
        margin-right: auto;
        
    }
    .stButton button {
        background-color: DodgerBlue;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        transition: background-color 0.3s, color 0.3s;
    }
    .stButton button:hover {
        background-color: #1e90ff;
        color: white;
    }
    .stButton button:active {
        background-color: #104e8b;
        color: white;
    }
    .stButton button:focus {
        outline: none;
        color: white;
        box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.5);
    }
    .stButton button:hover,
    .stButton button:active,
    .stButton button:focus,
    .stButton button:visited {
        color: white;
    }
    
    
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
