'''
filename: utils.py
functions: encode_features, load_model
creator: shashank.gupta
version: 1
'''

###############################################################################
# Import necessary modules
# ##############################################################################

import logging

from datetime import datetime

import pandas as pd
import numpy as np

import sqlite3
from sqlite3 import Error

import subprocess
import os

import mlflow
import mlflow.sklearn
import mlflow.pyfunc
from pycaret.classification import *
import functools

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from lead_scoring_inference_pipeline.constants import *
from optuna.distributions import IntDistribution


###############################################################################
# Define the function to train the model
# ##############################################################################


def encode_features():
    '''
    This function one hot encodes the categorical features present in our  
    training dataset. This encoding is needed for feeding categorical data 
    to many scikit-learn models.

    INPUTS
        db_file_name : Name of the database file 
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES : list of the features that needs to be there in the final encoded dataframe
        FEATURES_TO_ENCODE: list of features  from cleaned data that need to be one-hot encoded
        **NOTE : You can modify the encode_featues function used in heart disease's inference
        pipeline for this.

    OUTPUT
        1. Save the encoded features in a table - features

    SAMPLE USAGE
        encode_features()
    '''
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        query = f"SELECT * FROM {MODEL_INPUT_TABLE}"
        df = pd.read_sql_query(query, conn)
        encoded_df = pd.DataFrame(columns= ONE_HOT_ENCODED_FEATURES)
        placeholder_df = pd.DataFrame()
        
        # One-Hot Encoding using get_dummies for the specified categorical features
        for f in FEATURES_TO_ENCODE:
            if(f in df.columns):
                encoded = pd.get_dummies(df[f])
                encoded = encoded.add_prefix(f + '_')
                placeholder_df = pd.concat([placeholder_df, encoded], axis=1)
            else:
                print('Feature not found')
                
         # Implement these steps to prevent dimension mismatch during inference
        for feature in encoded_df.columns:
            if feature in df.columns:
                encoded_df[feature] = df[feature]
            if feature in placeholder_df.columns:
                encoded_df[feature] = placeholder_df[feature]
                
        # fill all null values
        encoded_df.fillna(0, inplace=True)
        print(encoded_df.columns)
        encoded_df.to_sql(FEATURES_TABLE, conn, if_exists='replace', index=False)
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except pd.errors.EmptyDataError:
        print(f"Table '{table_name}' is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

###############################################################################
# Define the function to load the model from mlflow model registry
# ##############################################################################

def get_models_prediction():
    '''
    This function loads the model which is in production from mlflow registry and 
    uses it to do prediction on the input dataset. Please note this function will the load
    the latest version of the model present in the production stage. 

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        model from mlflow model registry
        model name: name of the model to be loaded
        stage: stage from which the model needs to be loaded i.e. production


    OUTPUT
        Store the predicted values along with input data into a table

    SAMPLE USAGE
        load_model()
    '''
    conn = None
     # opening the conncetion for creating the sqlite db
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        
        # Format: "models:/<model_name>/<stage_or_version>"
        TRACKING_URI = "http://0.0.0.0:6006"
        mlflow.set_tracking_uri(TRACKING_URI)
        model_uri = f"models:/{MODEL_NAME}/{STAGE}"  # or "models:/LightGBM/1"

        # Load the model
        loaded_model = mlflow.pyfunc.load_model(model_uri)
        if loaded_model.metadata.signature and loaded_model.metadata.signature.inputs:
            columns = loaded_model.metadata.signature.inputs.input_names()
            print("Model was trained on columns:", columns)
        else:
            print("Model signature or input columns are not available.")


        query = f"SELECT * FROM {FEATURES_TABLE}"
        dataset = pd.read_sql_query(query, conn)
        #print(dataset.columns)
        #target_dataset = dataset[TARGET_VAR]
        #dataset = dataset.drop(columns=TARGET_VAR)

        # Make predictions
        predictions = loaded_model.predict(dataset)  # data = pandas DataFrame
        predictions_df = pd.DataFrame({PREDICTION: predictions})
        predictions_df.to_sql(PREDICTION, conn, if_exists='replace', index=False)
        dataset.to_sql(FEATURES_TABLE, conn, if_exists='replace', index=False)
        print(predictions_df.head())
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except pd.errors.EmptyDataError:
        print(f"Table '{FEATURES_TABLE}' is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
    
    

###############################################################################
# Define the function to check the distribution of output column
# ##############################################################################

def prediction_ratio_check():
    '''
    This function calculates the % of 1 and 0 predicted by the model and  
    and writes it to a file named 'prediction_distribution.txt'.This file 
    should be created in the ~/airflow/dags/Lead_scoring_inference_pipeline 
    folder. 
    This helps us to monitor if there is any drift observed in the predictions 
    from our model at an overall level. This would determine our decision on 
    when to retrain our model.
    

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be

    OUTPUT
        Write the output of the monitoring check in prediction_distribution.txt with 
        timestamp.

    SAMPLE USAGE
        prediction_col_check()
    '''
    conn = None
     # opening the conncetion for creating the sqlite db
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        query = f"SELECT * FROM {PREDICTION}"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print(f"No prediction data found in table: {PREDICTION}")
            return
        
        # Assume prediction column is named 'prediction'
        if 'predictions' not in df.columns:
            print("Column 'prediction' not found in prediction table.")
            return
        
        #calculate distribution
        total = len(df)
        percent_0 = (df[PREDICTION] == 0).sum() / total * 100
        percent_1 = (df[PREDICTION] == 1).sum() / total * 100
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} | Class0 : {percent_0: .2f}% | Class1: {percent_1:.2f}%\n"
        output_dir = os.path.expanduser(FILE_PATH)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, PREDICTION_DISTRIBUTION)

        # Write log
        with open(output_file, "a") as f:
            f.write(log_line)

        print("Prediction ratio logged successfully.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except pd.errors.EmptyDataError:
        print(f"Table '{PREDICTION_TABLE}' is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
###############################################################################
# Define the function to check the columns of input features
# ##############################################################################


def input_features_check():
    '''
    This function checks whether all the input columns are present in our new
    data. This ensures the prediction pipeline doesn't break because of change in
    columns in input data.

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES: List of all the features which need to be present
        in our input data.

    OUTPUT
        It writes the output in a log file based on whether all the columns are present
        or not.
        1. If all the input columns are present then it logs - 'All the models input are present'
        2. Else it logs 'Some of the models inputs are missing'

    SAMPLE USAGE
        input_col_check()
    '''
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)

        query = f"SELECT * FROM {FEATURES_TABLE}"
        dataset = pd.read_sql_query(query, conn)
        
        if functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q,sorted(dataset.columns),sorted(ONE_HOT_ENCODED_FEATURES)), True):       
            print('All the models input are present')
        else:
            print(sorted(dataset.columns))
            print(sorted(ONE_HOT_ENCODED_FEATURES))
            print('Some of the models inputs are missing')
        
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except pd.errors.EmptyDataError:
        print(f"Table '{FEATURES_TABLE}' is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            

    
   
