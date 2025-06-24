##############################################################################
# Import necessary modules
# #############################################################################


from airflow import DAG
from airflow.operators.python import PythonOperator
import lead_scoring_data_pipeline.utils
import lead_scoring_data_pipeline.data_validation_checks
from datetime import datetime, timedelta


###############################################################################
# Define default arguments and DAG
# ##############################################################################

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


ML_data_cleaning_dag = DAG(
                dag_id = 'Lead_Scoring_Data_Engineering_Pipeline',
                default_args = default_args,
                description = 'DAG to run data pipeline for lead scoring',
                schedule_interval = '@daily',
                catchup = False
)

###############################################################################
# Create a task for build_dbs() function with task_id 'building_db'
# ##############################################################################
op_building_db = PythonOperator(task_id='building_db', 
                                python_callable=lead_scoring_data_pipeline.utils.build_dbs,
                              dag=ML_data_cleaning_dag)
###############################################################################
# Create a task for raw_data_schema_check() function with task_id 'checking_raw_data_schema'
# ##############################################################################
op_checking_raw_data_schema = PythonOperator(task_id='checking_raw_data_schema', 
                              python_callable=lead_scoring_data_pipeline.data_validation_checks.raw_data_schema_check,
                              dag=ML_data_cleaning_dag)

###############################################################################
# Create a task for load_data_into_db() function with task_id 'loading_data'
# #############################################################################
op_loading_data = PythonOperator(task_id='loading_data', 
                                python_callable=lead_scoring_data_pipeline.utils.load_data_into_db,
                              dag=ML_data_cleaning_dag)
###############################################################################
# Create a task for map_city_tier() function with task_id 'mapping_city_tier'
# ##############################################################################
op_mapping_city_tier = PythonOperator(task_id='mapping_city_tier', 
                                python_callable=lead_scoring_data_pipeline.utils.map_city_tier,
                              dag=ML_data_cleaning_dag)
###############################################################################
# Create a task for map_categorical_vars() function with task_id 'mapping_categorical_vars'
# ##############################################################################
op_mapping_categorical_vars = PythonOperator(task_id='mapping_categorical_vars', 
                                python_callable=lead_scoring_data_pipeline.utils.map_categorical_vars,
                              dag=ML_data_cleaning_dag)
###############################################################################
# Create a task for interactions_mapping() function with task_id 'mapping_interactions'
# ##############################################################################
op_mapping_interactions = PythonOperator(task_id='mapping_interactions', 
                                python_callable=lead_scoring_data_pipeline.utils.interactions_mapping,
                              dag=ML_data_cleaning_dag)
###############################################################################
# Create a task for model_input_schema_check() function with task_id 'checking_model_inputs_schema'
# ##############################################################################
op_checking_model_inputs_schema = PythonOperator(task_id='checking_model_inputs_schema', 
                        python_callable=lead_scoring_data_pipeline.data_validation_checks.model_input_schema_check,
                              dag=ML_data_cleaning_dag)
###############################################################################
# Define the relation between the tasks
# ##############################################################################


op_building_db >> op_checking_raw_data_schema >> op_loading_data >> op_mapping_city_tier >> op_mapping_categorical_vars >> op_mapping_interactions >> op_checking_model_inputs_schema
