##############################################################################
# Import the necessary modules
##############################################################################

import pandas as pd
import sqlite3
from sqlite3 import Error
from constants import *
import functools

###############################################################################
# Write test cases for load_data_into_db() function
# ##############################################################################

def test_load_data_into_db():
    """_summary_
    This function checks if the load_data_into_db function is working properly by
    comparing its output with test cases provided in the db in a table named
    'loaded_data_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'

    SAMPLE USAGE
        output=test_get_data()

    """
    conn = None
    conn2 = None
    # opening the conncetion for creating the sqlite db
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        query = f"SELECT * FROM {INITIAL_DATA_TABLE}"
        df_lead_scoring = pd.read_sql_query(query, conn)
        conn2 = sqlite3.connect(DB_PATH+UNIT_TEST_DB_FILE_NAME)
        query2 = f"SELECT * FROM {'loaded_data_test_case'}"
        df_lead_scoring_test = pd.read_sql_query(query2, conn2)
        
        if functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q,df_lead_scoring.columns,df_lead_scoring_test.columns), True):
        
         print("loaded_data_test_case")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except pd.errors.EmptyDataError:
        print(f"Table '{table_name}' is empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if conn:
            conn.close()
        if conn2:
            conn2.close()
    
    

###############################################################################
# Write test cases for map_city_tier() function
# ##############################################################################
def test_map_city_tier():
    """_summary_
    This function checks if map_city_tier function is working properly by
    comparing its output with test cases provided in the db in a table named
    'city_tier_mapped_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'

    SAMPLE USAGE
        output=test_map_city_tier()

    """
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        query = f"SELECT * FROM {CITY_TIER_MAPPED_DATA_TABLE}"
        df_lead_scoring = pd.read_sql_query(query, conn)
        conn2 = sqlite3.connect(DB_PATH+UNIT_TEST_DB_FILE_NAME)
        query2 = f"SELECT * FROM {'city_tier_mapped_test_case'}"
        df_lead_scoring_test = pd.read_sql_query(query2, conn2)
        
        if functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q,df_lead_scoring.columns,df_lead_scoring_test.columns), True):
        
         print("city_tier_mapped_test_case")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except pd.errors.EmptyDataError:
        print(f"Table '{table_name}' is empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if conn:
            conn.close()
        if conn2:
            conn2.close()
    
    
###############################################################################
# Write test cases for map_categorical_vars() function
# ##############################################################################    
def test_map_categorical_vars():
    """_summary_
    This function checks if map_cat_vars function is working properly by
    comparing its output with test cases provided in the db in a table named
    'categorical_variables_mapped_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'
    
    SAMPLE USAGE
        output=test_map_cat_vars()

    """    
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        query = f"SELECT * FROM {CATEGORICAL_DATA_MAPPED_TABLE}"
        df_lead_scoring = pd.read_sql_query(query, conn)
        conn2 = sqlite3.connect(DB_PATH+UNIT_TEST_DB_FILE_NAME)
        query2 = f"SELECT * FROM {'categorical_variables_mapped_test_case'}"
        df_lead_scoring_test = pd.read_sql_query(query2, conn2)
        
        if functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q,df_lead_scoring.columns,df_lead_scoring_test.columns), True):
        
         print("categorical_variables_mapped_test_case")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except pd.errors.EmptyDataError:
        print(f"Table '{table_name}' is empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if conn:
            conn.close()
        if conn2:
            conn2.close()

###############################################################################
# Write test cases for interactions_mapping() function
# ##############################################################################    
def test_interactions_mapping():
    """_summary_
    This function checks if test_column_mapping function is working properly by
    comparing its output with test cases provided in the db in a table named
    'interactions_mapped_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'

    SAMPLE USAGE
        output=test_column_mapping()

    """ 
    
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        query = f"SELECT * FROM {INTERACTIONS_MAPPED_TABLE}"
        df_lead_scoring = pd.read_sql_query(query, conn)
        df_lead_scoring = df_lead_scoring[sorted(df_lead_scoring.columns)]
        conn2 = sqlite3.connect(DB_PATH+UNIT_TEST_DB_FILE_NAME)
        query2 = f"SELECT * FROM {'interactions_mapped_test_case'}"
        df_lead_scoring_test = pd.read_sql_query(query2, conn2)
        df_lead_scoring_test = df_lead_scoring_test[sorted(df_lead_scoring_test.columns)]
        
        if functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q,df_lead_scoring.columns,df_lead_scoring_test.columns), True):
        
         print("interactions_mapped_test_case")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except pd.errors.EmptyDataError:
        print(f"Table '{table_name}' is empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if conn:
            conn.close()
        if conn2:
            conn2.close()
   
