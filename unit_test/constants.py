# You can create more variables according to your project. The following are the basic variables that have been provided to you
ROOT_FOLDER = "/home/"
ASSIGNMENT_FOLDER="Assignment/01_data_pipeline/scripts/unit_test/"
DB_PATH = ROOT_FOLDER+ASSIGNMENT_FOLDER
DB_FILE_NAME = 'utils_output.db'
UNIT_TEST_DB_FILE_NAME = 'unit_test_cases.db'
DATA_DIRECTORY = ROOT_FOLDER+ASSIGNMENT_FOLDER
DATA = "leadscoring_test.csv"
INITIAL_DATA_TABLE = 'loaded_data'
CITY_TIER_MAPPED_DATA_TABLE = 'city_tier_mapped'
CATEGORICAL_DATA_MAPPED_TABLE = 'categorical_variables_mapped'
INTERACTIONS_MAPPED_TABLE = "interactions_mapped"
MODEL_INPUT_TABLE="model_input"
INTERACTION_MAPPING = ROOT_FOLDER+ASSIGNMENT_FOLDER+'interaction_mapping.csv'
INDEX_COLUMNS_TRAINING = ['created_date', 'first_platform_c',
       'first_utm_medium_c', 'first_utm_source_c', 'total_leads_droppped', 'city_tier',
       'referred_lead', 'app_complete_flag']
INDEX_COLUMNS_INFERENCE = ['created_date', 'first_platform_c',
       'first_utm_medium_c', 'first_utm_source_c', 'total_leads_droppped', 'city_tier',
       'referred_lead']

NOT_FEATURES = [
'created_date',
'assistance_interaction',
'career_interaction',
'payment_interaction',
'social_interaction',
'syllabus_interaction',
"city_mapped",
"interaction_type",
"1_on_1_industry_mentorship",                              
"call_us_button_clicked",                                 
"career_assistance",                                    
"career_coach",                                         
"career_impact",                                              
"careers",                                             
"chat_clicked",                                                
"companies",                                              
"download_button_clicked",                                     
"download_syllabus",                                   
"emi_partner_click",                                         
"emi_plans_clicked",                                         
"fee_component_click",                                         
"hiring_partners",                                       
"homepage_upgrad_support_number_clicked",                      
"industry_projects_case_studies",                     
"live_chat_button_clicked",                            
"payment_amount_toggle_mover",                                 
"placement_support",                               
"placement_support_banner_tab_clicked",                        
"program_structure",                      
"programme_curriculum",                                        
"programme_faculty",                                      
"request_callback_on_instant_customer_support_cta_clicked",    
"shorts_entry_click",  
"social_referral_click",                                       
"specialisation_tab_clicked",                                  
"specializations",                                
"specilization_click",                                         
"syllabus",                                       
"syllabus_expand",                                             
"syllabus_submodule_expand",                                   
"tab_career_assistance",                                 
"tab_job_opportunities",                                     
"tab_student_support",                                     
"view_programs_page",                                       
"whatsapp_chat_click"
]




