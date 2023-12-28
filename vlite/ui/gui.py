from vlite.ui.utils import load_md_text, get_databases, create_new_database, \
                           load_database, Settings, create_entry, retrieve_entries_by_id, \
                           retrieve_entries_by_query, retrieive_entries_by_hyde
from automacene.processor.backends.multimodal.vertexAI import VertexAIGenerativeModel
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
    if "select_entry_by_id" not in st.session_state:
        st.session_state["select_entry_by_id"] = False
    if "selecte_entry_by_hyde" not in st.session_state:
        st.session_state["selecte_entry_by_hyde"] = False
    if "retrieved_table" not in st.session_state:
        st.session_state["retrieved_table"] = []


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

def toggle_retrieve_by_method(method:str) -> None:
    """
    Toggle the retrieve by id or hyde methods.

    parameters:
        method: str
            The method to toggle.
            "id" will toggle the id method.
            "hyde" will toggle the hyde method.
            Anything else will toggle both off and default to the vanilla query method.
    """
    if method == "id":
        st.session_state.select_entry_by_id = not st.session_state.select_entry_by_id
        st.session_state.selecte_entry_by_hyde = False
    elif method == "hyde":
        st.session_state.select_entry_by_id = False
        st.session_state.selecte_entry_by_hyde = not st.session_state.selecte_entry_by_hyde
    else:
        st.session_state.select_entry_by_id = False
        st.session_state.selecte_entry_by_hyde = False


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
    table = [{"id": "ID", "data": "Data"}]
    if st.session_state.retrieved_table == []:
        table += retrieve_entries_by_id(database)
    else:
        table += st.session_state.retrieved_table
    draw_table(table)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1,1,4])
    #Retrieve Entry
    new_line(col1, 1)
    new_line(col2, 1)
    do_retrieve_entries = col1.button("Retrieve Entry")
    query_help = "Select a method on the side, if none are selected, just ask a question or enter data related to the information you'd like to find."
    query_placeholder = "If 'By ID' is checked, this is the ID. If 'By HyDE' is checked, add content from a source. Otherwise, this is the query."
    query = col3.text_area("Query", placeholder=query_placeholder, key="query", help=query_help)
    id_help = "Retrieve entries by their ID. It will only retrieve 1 or 0 entries if none are found."
    col2.checkbox("By ID", key="retrieve_by_id", on_change=toggle_retrieve_by_method, args=("id",), help=id_help)
    hyde_help = "HyDE stands for Hypothetical Document Embeddings. "
    hyde_help += "Our version of HyDE generates a content from one source of content, and then uses it to generate a question for another source of content. "
    hyde_help += "Then the question is used to generate a hypothetical answer for the data in the database. "
    hyde_help += "An example would be submitting laws for New Jersey, generating a question about the law but from the perspective of Maryland, and then generating a hypothetical answer for the law from the perspective of Maryland. "
    hyde_help += "This is then used to find laws in Maryland that are close to the generated hypothetical answer. "
    col2.checkbox("By Hyde", key="retrieve_by_hyde", on_change=toggle_retrieve_by_method, args=("hyde",), help=hyde_help)
    
    #Create Entry
    new_line(col1, 11)
    new_line(col2, 7)
    new_line(col3, 4)
    create_new_entry = col1.button("Create Entry")
    entry_id = col2.text_input("Creation ID", placeholder="Enter ID here...", key="create_id")
    entry_data = col3.text_area("Data", placeholder="Enter data here...")
    
    #Metadata for Create Entry
    new_line(col1, 1)
    new_line(col2, 1)
    new_line(col3, 4)
    with col3.form("Metadata"):
        col2.markdown("#### Metadata")
        metadata_id = col2.text_input("Metadata ID", placeholder="Enter ID here...", key="metadata_id")
        metadata_source = col2.text_input("Source", placeholder="Enter source here...", key="metadata_source")
        metadata_description = col2.text_area("Description", placeholder="Enter description here...", key="metadata_description")

    #Delete Entry
    new_line(col1, 27)
    new_line(col2, 2)
    do_delete = col1.button("Delete Entry")
    delete_id = col2.text_input("Deletion ID", placeholder="Enter ID here...", key="delete_id")

    #Read all buttons
    #Create Button
    if create_new_entry:
        #Conformity checks
        #TODO: This is hella ugly, fix it. Maybe separate function or pass checks from create_entry?
        temp_entry_id = name_cleaner.sub("", entry_id)
        if temp_entry_id != entry_id:
            st.error("Please only use letters, numbers, and underscores in the entry id.")
            return
        temp_entry_id = temp_entry_id.strip()
        temp_entry_id = None if temp_entry_id == "" else temp_entry_id
        
        temp_metadata_id = name_cleaner.sub("", metadata_id)
        if temp_metadata_id != metadata_id:
            st.error("Please only use letters, numbers, and underscores in the metadata id.")
            return
        temp_metadata_id = temp_metadata_id.strip()
        temp_metadata_id = None if temp_metadata_id == "" else temp_metadata_id

        temp_metadata_source = source_cleaner.sub("", metadata_source)
        if temp_metadata_source != metadata_source:
            st.error("Please only use letters, numbers, and underscores in the metadata source. This should be a web address or file path.")
            return
        temp_metadata_source = temp_metadata_source.strip()
        temp_metadata_source = None if temp_metadata_source == "" else temp_metadata_source

        temp_metadata_description = description_cleaner.sub("", metadata_description)
        if temp_metadata_description != metadata_description:
            st.error("Please only use letters, numbers, and punctuation (.,!?;:-) in the metadata description.")
            return
        temp_metadata_description = temp_metadata_description.strip()
        temp_metadata_description = None if temp_metadata_description == "" else temp_metadata_description

        #Empty checks
        entry_data = entry_data.strip()
        if entry_data == "":
            st.error("Please enter an entry data.")
            return
        
        metadata = {
            "id": temp_metadata_id,
            "source": temp_metadata_source,
            "description": temp_metadata_description
        }
        create_entry(database, entry_data, id=entry_id, metadata=metadata)
    
    #Retrieve Button
    if do_retrieve_entries:
        #Conformity checks
        if st.session_state.select_entry_by_id:
            temp_query = name_cleaner.sub("", query)
            if temp_query != query:
                st.error("Please only use letters, numbers, and underscores in the query.")
                return
            temp_query = temp_query.strip()
            temp_query = None if temp_query == "" else temp_query
            query = temp_query
        
        #Empty checks
        query = query.strip()
        if query == "":
            st.error("Please enter a query.")
            return

        #Retrieve
        if st.session_state.select_entry_by_id:
            retrieved_table = retrieve_entries_by_id(database, ids=[query])
            st.session_state.retrieved_table = retrieved_table
        elif st.session_state.selecte_entry_by_hyde:
            retrieved_table = retrieive_entries_by_hyde(database, query, "./access_key.json")
            st.session_state.retrieved_table = retrieved_table
        else:
            retrieved_table = retrieve_entries_by_query(database, query)
            st.session_state.retrieved_table = retrieved_table
    
    #Delete Button
    if do_delete:
        #Conformity checks
        temp_delete_id = name_cleaner.sub("", delete_id)
        if temp_delete_id != delete_id:
            st.error("Please only use letters, numbers, and underscores in the delete id.")
            return
        temp_delete_id = temp_delete_id.strip()
        temp_delete_id = None if temp_delete_id == "" else temp_delete_id

        #Empty checks
        delete_id = delete_id.strip()
        if delete_id == "":
            st.error("Please enter a delete id.")
            return
        
        #Delete
        try:
            database.forget(id=delete_id)
        except Exception as e:
            st.error(f"Could not delete entry: {e}")


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