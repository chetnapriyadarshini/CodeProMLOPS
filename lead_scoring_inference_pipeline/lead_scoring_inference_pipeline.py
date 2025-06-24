##############################################################################
# Import necessary modules
# #############################################################################

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import lead_scoring_inference_pipeline.utils


###############################################################################
# Define default arguments and create an instance of DAG
# ##############################################################################

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


Lead_scoring_inference_dag = DAG(
                dag_id = 'Lead_scoring_inference_pipeline',
                default_args = default_args,
                description = 'Inference pipeline of Lead Scoring system',
                schedule_interval = '@hourly',
                catchup = False
)

###############################################################################
# Create a task for encode_data_task() function with task_id 'encoding_categorical_variables'
# ##############################################################################
op_encoding_categorical_variables = PythonOperator(task_id='encoding_categorical_variables', 
                                python_callable=lead_scoring_inference_pipeline.utils.encode_features,
                              dag=Lead_scoring_inference_dag)


###############################################################################
# Create a task for load_model() function with task_id 'generating_models_prediction'
# ##############################################################################
op_model_prediction = PythonOperator(task_id='generating_models_prediction', 
                                python_callable=lead_scoring_inference_pipeline.utils.get_models_prediction,
                              dag=Lead_scoring_inference_dag)


###############################################################################
# Create a task for prediction_col_check() function with task_id 'checking_model_prediction_ratio'
# ##############################################################################
op_prediction_ratio_check = PythonOperator(task_id='checking_model_prediction_ratio', 
                                python_callable=lead_scoring_inference_pipeline.utils.prediction_ratio_check,
                              dag=Lead_scoring_inference_dag)


###############################################################################
# Create a task for input_features_check() function with task_id 'checking_input_features'
# ##############################################################################
op_input_features_check = PythonOperator(task_id='checking_input_features', 
                                python_callable=lead_scoring_inference_pipeline.utils.input_features_check,
                              dag=Lead_scoring_inference_dag)


###############################################################################
# Define relation between tasks
# ##############################################################################

op_encoding_categorical_variables >> op_input_features_check >> op_model_prediction >> op_prediction_ratio_check
