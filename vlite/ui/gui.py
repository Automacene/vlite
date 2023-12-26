from vlite.ui.utils import load_md_text, Settings
import streamlit as st


#---------------------------------#
#------------ Session ------------#
#---------------------------------#
is_open_toggles = [
    "settings",
    "about",
]

def set_session() -> None:
    """
    Set the session state.
    """
    st.set_page_config(
        page_title="EmbRaVec",
        page_icon=":fire:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session button toggle states
    toggle_all_other_toggles("all")

    # Initialize session settings
    st.session_state["settings"] = Settings()

def toggle_all_other_toggles(toggle_name: str) -> None:
    """
    Toggles all other toggles in the session state.

    parameters:
        toggle_name: str
            The name of the toggle to not toggle.
            "all" will toggle all toggles. (Works because there is no toggle named "all")
    """
    for toggle in is_open_toggles:
        temp_toggle_name = f"is_open_{toggle}"
        if temp_toggle_name != toggle_name:
            st.session_state[temp_toggle_name] = False

#---------------------------------#
#------------ Graphics -----------#
#---------------------------------#
def create_sidebar() -> None:
    """Create the sidebar."""
    sb = st.sidebar
    sb.title("EmbRaVec")
    sb.markdown(load_md_text("./resources/INTRO.md", __file__))
    
    #Toggles
    col1, col2 = sb.columns([1,3])
    if col1.button("About"):
        toggle_all_other_toggles("is_open_about")
        st.session_state.is_open_about = not st.session_state.is_open_about
    if col1.button("Settings"):
        toggle_all_other_toggles("is_open_settings")
        st.session_state.is_open_settings = not st.session_state.is_open_settings

    #Quick Helps
    col2.markdown("*About EmbRaVec and its creators.*")
    col2.markdown("*Path and AI settings.*")

    #Draws
    if st.session_state.is_open_about:
        sb.markdown(load_md_text("./resources/ABOUT.md", __file__))
    if st.session_state.is_open_settings:
        sb.text_input("Database Path")
        sb.button("Save")

def write_page() -> None:
    col1, col2, col3 = st.columns([1,10,1])
    with col2:
        st.markdown(load_md_text("./resources/README.md", __file__))


if __name__ == "__main__":
    set_session()
    create_sidebar()
    write_page()