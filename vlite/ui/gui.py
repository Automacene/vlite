from vlite.ui.utils import load_md_text, get_databases, create_new_database, load_database, Settings
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
description_cleaner = re.compile(r"[^a-zA-Z0-9_ .,!?;:-]")
source_cleaner = re.compile(r"[^a-zA-Z0-9_/:.]")

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
    if "selected_database" not in st.session_state:
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

def toggle_selected_database(database: str) -> None:
    """
    Select a database.

    parameters:
        database: str
            The name of the database to select.
    """
    if st.session_state.selected_database == database:
        st.session_state.selected_database = None
    else:
        st.session_state.selected_database = database

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
    search, edit, create = st.tabs(["Search", "Edit", "Create"])
    with search:
        write_database_selection_window()
    with edit:
        write_edit_window()
    with create:
        write_create_window()


def write_database_selection_window() -> None:
    """
    Write the databases to the page.
    """
    #Build selection window
    col1, col2, col3 = st.columns([1,4,1])
    
    #Titles
    col1.markdown("#### Database Names")
    col2.markdown("#### Database Descriptions")
    col3.markdown("#### Selection Buttons")

    #Databases
    databases, descriptions = get_databases(st.session_state.settings.database_path)
    for database, description in zip(databases, descriptions):
        col1.markdown(database)
        col2.markdown(description)
        checked = st.session_state.selected_database == database
        col3.checkbox(f"-- Select {database} --", value=checked, on_change=toggle_selected_database, args=(database,))


def write_edit_window() -> None:
    """
    Write the edit window to the page.
    """
    if st.session_state.selected_database == None:
        st.markdown("No database selected, please select a database under the **'Search'** tab or create a new one under the **'Create'** tab.")
        return

    database = load_database(st.session_state.settings.database_path, st.session_state.selected_database)
    #Entry View
    keys = database._vector_key_store
    table = [{"id": "ID", "data": "Data"}]
    for key in keys:
        data, _, _ = database.remember(id=key)
        entry = {"id": key, "data": data}
        table.append(entry)
    draw_table(table)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1,1,4])
    #Retrieve Entry
    new_line(col1, 1)
    new_line(col2, 1)
    col1.button("Retrieve Entry")
    col2.checkbox("By ID", key="retrieve_by_id")
    col3.text_area("Query", placeholder="Enter query here. If 'By ID' is checked, this is the ID. Otherwise, this is the data.")
    
    #Create Entry
    new_line(col1, 11)
    new_line(col2, 10)
    new_line(col3, 4)
    col1.button("Create Entry")
    col2.text_input("ID", placeholder="Enter ID here...", key="create_id")
    col3.text_area("Data", placeholder="Enter data here...")
    
    #Delete Entry
    new_line(col1, 6)
    new_line(col2, 4)
    new_line(col3, 4)
    col1.button("Delete Entry")
    col2.text_input("ID", placeholder="Enter ID here...", key="delete_id")

def write_create_window() -> None:
    """
    Write the create window to the page.
    """
    col1, col2 = st.columns([1,3])
    new_line(col1, 2)
    make_new_database = col1.button("Create New Database")
    db_name = col2.text_input("Database Name", placeholder="Enter database name here...")
    db_description = col2.text_input("Database Description", placeholder="Enter database description here...")
    db_source = col2.text_input("Database Source", placeholder="Enter database source here...")

    if make_new_database:
        #Conformity checks
        temp_db_name = name_cleaner.sub("", db_name)
        if temp_db_name != db_name:
            st.error("Please only use letters, numbers, and underscores in the database name.")
            return
        
        temp_db_source = source_cleaner.sub("", db_source)
        if temp_db_source != db_source:
            st.error("Please only use letters, numbers, and underscores in the database source. This should be a web address or file path.")
            return
        
        temp_db_description = description_cleaner.sub("", db_description)
        print(temp_db_description, db_description)
        if temp_db_description != db_description:
            st.error("Please only use letters, numbers, and punctuation (.,!?;:-) in the database description.")
            st.error(temp_db_description)
            st.error(db_description)
            return

        #Empty checks
        db_name = temp_db_name
        if db_name == "":
            st.error("Please enter a database name.")
            return
        
        db_source = temp_db_source
        if db_source == "":
            st.error("Please enter a database source.")
            return
        
        db_description = temp_db_description
        if db_description == "":
            st.error("Please enter a database description.")
            return
        
        create_new_database(st.session_state.settings.database_path, db_name, db_description, db_source)
        toggle_selected_database(db_name)


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


def draw_table(table: List[dict], container: Any = None) -> None:
    """
    A markdown table.

    parameters:
        table: List[dict]
            The table to draw with a key and value for each column in the table for every row.
            The first row is the header row, the values are the formatted column names.
        container: Any
            Any item like a streamlit column or container.
            None will add a new line to the page.
    """
    #Check for empty table
    if len(table) == 1:
        if container == None:
            st.markdown("No data to display.")
        else:
            container.markdown("No data to display.")
        return
    
    #Create table string
    table_string = "|"
    for key in table[0]:
        table_string += f" {table[0][key]} |"
    table_string += "\n|"
    for _ in table[0]:
        table_string += " --- |"
    table_string += "\n"
    for row in table[1:]:
        table_string += "|"
        for key in row:
            table_string += f" {row[key]} |"
        table_string += "\n"
    
    #Draw table
    if container == None:
        st.markdown(table_string)
    else:
        container.markdown(table_string)


if __name__ == "__main__":
    set_session()
    create_sidebar()
    write_page()