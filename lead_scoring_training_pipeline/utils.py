'''
filename: utils.py
functions: encode_features, get_train_model
creator: shashank.gupta
version: 1
'''

###############################################################################
# Import necessary modules
# ##############################################################################

import pandas as pd
import numpy as np

import sqlite3
from sqlite3 import Error

import subprocess
import os

import mlflow
import mlflow.sklearn
from pycaret.classification import *
from mlflow.models.signature import infer_signature

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from lead_scoring_training_pipeline.constants import *
from optuna.distributions import IntDistribution


###############################################################################
# Define the function to encode features
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
       

    OUTPUT
        1. Save the encoded features in a table - features
        2. Save the target variable in a separate table - target


    SAMPLE USAGE
        encode_features()
        
    **NOTE : You can modify the encode_featues function used in heart disease's inference
        pipeline from the pre-requisite module for this.
    '''
    conn = None
    conn2 = None
    try:
        conn = sqlite3.connect(INPUT_DATA_FILE)
        conn2 = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        query = f"SELECT * FROM {MODEL_INPUT_TABLE}"
        df = pd.read_sql_query(query, conn)
        target_df = df[TARGET_VAR]
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
        encoded_df.to_sql(FEATURES_TABLE, conn2, if_exists='replace', index=False)
        target_df.to_sql(TARGET_TABLE, conn2, if_exists='replace', index=False)
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except pd.errors.EmptyDataError:
        print(f"Table '{MODEL_INPUT_TABLE}' is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close() 
        if conn2:
            conn2.close()


###############################################################################
# Define the function to train the model
# ##############################################################################

def get_trained_model():
    '''
    This function setups mlflow experiment to track the run of the training pipeline. It 
    also trains the model based on the features created in the previous function and 
    logs the train model into mlflow model registry for prediction. The input dataset is split
    into train and test data and the auc score calculated on the test data and
    recorded as a metric in mlflow run.   

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be


    OUTPUT
        Tracks the run in experiment named 'Lead_Scoring_Training_Pipeline'
        Logs the trained model into mlflow model registry with name 'LightGBM'
        Logs the metrics and parameters into mlflow run
        Calculate auc from the test data and log into mlflow run  

    SAMPLE USAGE
        get_trained_model()
    '''
    conn = None
     # opening the conncetion for creating the sqlite db
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        
        start_mlflow_server()
        
        mlflow.set_tracking_uri(TRACKING_URI)
        
        query = f"SELECT * FROM {FEATURES_TABLE}"
        dataset = pd.read_sql_query(query, conn)
        
        # Optional: downsample dataset for testing
        dataset = dataset.sample(frac=0.1, random_state=42)

        # Split into training and unseen data
        data_for_model, data_unseen = train_test_split(dataset, test_size=0.01, random_state=786)

        # Reset indexes
        data_for_model.reset_index(drop=True, inplace=True)
        data_unseen.reset_index(drop=True, inplace=True)
        
        Lead_Scoring_Training_Pipeline = setup(data = data_for_model, target = TARGET_VAR, 
                   session_id = 42,fix_imbalance=False,
                   n_jobs=-1,use_gpu=True,
                   log_experiment=True,experiment_name=EXPERIMENT,
                   log_plots=True, log_data=True,
                   silent=True, verbose=True,
                   normalize=False, transformation=False,
                   log_profile=False)
        
        lgbm  = create_model('lightgbm', fold = 5)
        custom_grid = {
    'actual_estimator__num_leaves': IntDistribution(10, 100)
        }

        tuned_lgbm_optuna,tuner_1 = tune_model(lgbm, 
                                            search_library='optuna',
                                            fold = 10,
                                            custom_grid=custom_grid,
                                            optimize = 'AUC',
                                            choose_better=True,
                                            return_tuner=True)
        # Finalize and log model
        final_model = finalize_model(tuned_lgbm_optuna)
        save_model(final_model, model_config)
       # mlflow.log_artifact('LightGBM.pkl')
        target_data = data_for_model[TARGET_VAR]
        data_for_model = data_for_model.drop(columns=[TARGET_VAR])
        signature = infer_signature(data_for_model, target_data)
        mlflow.sklearn.log_model(final_model, artifact_path="model", registered_model_name="LightGBM", signature=signature)
        
        predictions = predict_model(final_model, data=data_unseen)
        auc = roc_auc_score(predictions[TARGET_VAR], predictions['Score'])
        mlflow.log_metric("AUC", auc)
        
      #  data_unseen.to_sql(UNSEEN_DATA_TABLE, conn, if_exists='replace', index=False)
        
    # return an error if connection not established
    except Error as e:
        print(e)
     # closing the connection once the database is created
    finally:
        if conn:
            conn.close()

            
def start_mlflow_server():
    # Create folder for mlruns if it doesn't exist
    os.makedirs(ML_RUNS_PATH, exist_ok=True)
    
    # Change current working directory
    os.chdir(ML_RUNS_PATH)

    # Command to start MLflow server
    cmd = [
        "mlflow", "server",
        "--backend-store-uri", DB_FILE_MLFLOW,
        "--default-artifact-root", os.path.abspath(ML_RUNS_PATH),
        "--host", "0.0.0.0",
        "--port", "6006"
    ]

    # Start MLflow server
    subprocess.Popen(cmd)

    print("✅ MLflow Tracking Server started at http://0.0.0.0:6006")
   
