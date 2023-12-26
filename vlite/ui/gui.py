from vlite.ui.utils import load_md_text, get_databases, create_new_database, Settings
from typing import List, Any
import streamlit as st
import re


#---------------------------------#
#------------ Session ------------#
#---------------------------------#
is_open_toggles = [
    "settings",
    "about",
]

name_cleaner = re.compile(r"[^a-zA-Z0-9_]")

def set_session() -> None:
    """
    Set the session state.
    """
    st.set_page_config(
        page_title="EMBRAVEC DB",
        page_icon=":fire:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session button toggle states
    for toggle in is_open_toggles:
        if f"is_open_{toggle}" not in st.session_state:
            st.session_state[f"is_open_{toggle}"] = False

    # Initialize session settings
    st.session_state["settings"] = Settings()
    st.session_state["selected_database"] = None

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

def set_and_save_settings(key: str, value: Any) -> None:
    """
    Set and save a setting.

    parameters:
        key: str
            The key of the setting to set.
        value: Any
            The value of the setting to set.
    """
    st.session_state.settings.set(key, value)
    st.session_state.settings.save_settings()

#---------------------------------#
#------------ Graphics -----------#
#---------------------------------#
def create_sidebar() -> None:
    """Create the sidebar."""
    sb = st.sidebar
    sb.title("EMBRAVEC DB")
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
    col2.markdown("*About EMBRAVEC DB and its creators.*")
    new_line(col2)
    col2.markdown("*Path and AI settings.*")
    new_line(col2)

    #Draws
    if st.session_state.is_open_about:
        sb.markdown(load_md_text("./resources/ABOUT.md", __file__))
    if st.session_state.is_open_settings:
        db_path = sb.text_input("Database Path", placeholder=st.session_state.settings.database_path)
        sb.button("Save", on_click=set_and_save_settings, args=("database_path", db_path))

def write_page() -> None:
    """Write the page."""
    st.markdown(load_md_text("./resources/README.md", __file__))
    search, edit = st.tabs(["Search", "Edit"])
    with search:
        write_database_selection_window()
    with edit:
        write_edit_window()


def write_database_selection_window() -> None:
    """
    Write the databases to the page.
    """
    #Build selection window
    col1, col2, col3 = st.columns([1,1,1])
    
    #Titles
    col1.markdown("#### Database Names")
    col2.markdown("#### Database Descriptions")
    col3.markdown("#### Selection Buttons")

    #Databases
    databases, descriptions = get_databases(st.session_state.settings.database_path)
    for database, description in zip(databases, descriptions):
        col1.markdown(database)
        col2.markdown(description)
        col3.checkbox(database)

def write_edit_window() -> None:
    """
    Write the edit window to the page.
    """
    if st.session_state.selected_database == None:
        st.markdown("No database selected, please select a database under the search tab or create a new one.")
        col1, col2 = st.columns([1,3])
        new_line(col1, 2)
        make_new_database = col1.button("Create New Database")
        db_name = col2.text_input("Database Name", placeholder="Enter database name here...")

        if make_new_database:
            temp_db_name = name_cleaner.sub("", db_name)
            if temp_db_name != db_name:
                st.error("Please only use letters, numbers, and underscores in the database name.")
            
            db_name = temp_db_name
            if db_name == "":
                st.error("Please enter a database name.")
            else:
                create_new_database(st.session_state.settings.database_path, db_name)
                st.session_state.selected_database = f"{db_name}.db"
                st.session_state.is_open_settings = True
            return

#---------------------------------#
#------------ Functions ----------#
#---------------------------------#
def new_line(container: Any = None, times: int = 1) -> None:
    """
    Add a new line to an element.

    parameters:
        container: Any
            Any item like a streamlit column or container.
            None will add a new line to the page.
        times: int
            The number of new lines to add.
    """
    if container == None:
        for _ in range(times):
            st.markdown(" ")
    else:
        for _ in range(times):
            container.markdown(" ")

if __name__ == "__main__":
    set_session()
    create_sidebar()
    write_page()