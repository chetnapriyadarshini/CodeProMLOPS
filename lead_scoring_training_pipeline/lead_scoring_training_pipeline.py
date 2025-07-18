##############################################################################
# Import necessary modules
# #############################################################################
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta
import lead_scoring_training_pipeline.utils

###############################################################################
# Define default arguments and DAG
# ##############################################################################
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


ML_training_dag = DAG(
                dag_id = 'Lead_scoring_training_pipeline',
                default_args = default_args,
                description = 'Training pipeline for Lead Scoring System',
                schedule_interval = '@monthly',
                catchup = False
)

###############################################################################
# Create a task for encode_features() function with task_id 'encoding_categorical_variables'
# ##############################################################################
op_encoding_categorical_variables = PythonOperator(task_id='encoding_categorical_variables', 
                                python_callable=lead_scoring_training_pipeline.utils.encode_features,
                              dag=ML_training_dag)
###############################################################################
# Create a task for get_trained_model() function with task_id 'training_model'
# ##############################################################################

op_training_model = PythonOperator(task_id='training_model', 
                                python_callable=lead_scoring_training_pipeline.utils.get_trained_model,
                              dag=ML_training_dag)
###############################################################################
# Define relations between tasks
# ##############################################################################

op_encoding_categorical_variables >> op_training_model
