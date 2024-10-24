import os


current_script_path = os.path.dirname(os.path.abspath(__file__))
Base_directory = current_script_path + os.path.sep
output_directory = f"{Base_directory}../glassdoor-scrap-jobs-data/"
output_file_link = f"{output_directory}job_listings_glassdoor.json"
acceptedTitle = ["data & analytics", "bi developer", "insight analyst", "data scientist", "insights analyst", "technical project manager", "business intelligence", "bi analyst", "data engineer", "bi engineer", "data analyst"]
notAcceptedTitle = ["senior"]
new_jobs_lookback = 6
pages_url = [{"url": "https://www.glassdoor.fr/Emploi/bruxelles-belgique-data-analyst-emplois-SRCH_IL.0,18_IS3845_KO19,31.htm", "seo" : "bruxelles-belgique-data-analyst-emplois", "url_input" : "IL.0,18_IS3845_KO19,31", "location_id": 3845, "location_type": "STATE", "key_word": "data-analyst"},
             {"url": "https://www.glassdoor.fr/Emploi/bruxelles-business-intelligence-emplois-SRCH_IL.0,9_IS3845_KO10,31.htm", "seo" : "bruxelles-business-intelligence-emplois", "url_input" : "IL.0,9_IS3845_KO10,31", "location_id": 3845, "location_type": "STATE", "key_word": "business-intelligence"},
             {"url": "https://www.glassdoor.fr/Emploi/munich-bayern-allemagne-data-analyst-emplois-SRCH_IL.0,23_IC4990924_KO24,36.htm", "seo" : "munich-bayern-allemagne-data-analyst", "url_input" : "IL.0,23_IC4990924_KO24,36", "location_id": 4990924, "location_type": "CITY", "key_word": "data-analyst"},
             {"url": "https://www.glassdoor.fr/Emploi/singapour-data-analyst-emplois-SRCH_IL.0,9_IN217_KO10,22.htm", "seo" : "singapour-data-analyst-emplois", "url_input" : "IL.0,9_IN217_KO10,22", "location_id": 217, "location_type": "COUNTRY", "key_word": "data-analyst"},
             {"url": "https://www.glassdoor.fr/Emploi/paris-france-data-analyst-emplois-SRCH_IL.0,12_IS4540_KO13,25.htm", "seo" : "paris-france-data-analyst-emplois", "url_input" : "IL.0,12_IS4540_KO13,25", "location_id": 4540, "location_type": "STATE", "key_word": "data-analyst"},
             {"url": "https://www.glassdoor.fr/Emploi/berlin-allemagne-data-analyst-emplois-SRCH_IL.0,16_IC2622109_KO17,29.htm", "seo" : "berlin-allemagne-data-analyst-emplois", "url_input" : "IL.0,16_IC2622109_KO17,29", "location_id": 2622109, "location_type": "CITY", "key_word": "data-analyst"},
             {"url": "https://www.glassdoor.fr/Emploi/dublin-dublin-business-intelligence-emplois-SRCH_IL.0,13_IC2739035_KO14,35.htm", "seo" : "dublin-dublin-business-intelligence-emplois", "url_input" : "IL.0,13_IC2739035_KO14,35", "location_id": 2739035, "location_type": "CITY", "key_word": "business-intelligence"},
             {"url": "https://www.glassdoor.fr/Emploi/dublin-irlande-data-analyst-emplois-SRCH_IL.0,14_IC2739035_KO15,27.htm", "seo" : "dublin-irlande-data-analyst-emplois", "url_input" : "IL.0,14_IC2739035_KO15,27", "location_id": 2739035, "location_type": "CITY", "key_word": "data-analyst"},
             {"url": "https://www.glassdoor.fr/Emploi/frankfurt-am-main-data-analyst-emplois-SRCH_IL.0,17_IC2632180_KO18,30.htm", "seo" : "frankfurt-am-main-data-analyst-emplois", "url_input" : "IL.0,17_IC2632180_KO18,30", "location_id": 2632180, "location_type": "CITY", "key_word": "data-analyst"},
             {"url": "https://www.glassdoor.fr/Emploi/frankfurt-am-main-allemagne-business-intelligence-emplois-SRCH_IL.0,27_IC2632180_KO28,49.htm", "seo" : "frankfurt-am-main-allemagne-business-intelligence-emplois", "url_input" : "IL.0,27_IC2632180_KO28,49", "location_id": 2632180, "location_type": "CITY", "key_word": "business-intelligence"},
             {"url": "https://www.glassdoor.fr/Emploi/munich-bayern-allemagne-business-intelligence-emplois-SRCH_IL.0,23_IC4990924_KO24,45.htm", "seo" : "munich-bayern-allemagne-business-intelligence-emplois", "url_input" : "IL.0,23_IC4990924_KO24,45", "location_id": 4990924, "location_type": "CITY", "key_word": "business-intelligence"},
             {"url": "https://www.glassdoor.fr/Emploi/berlin-allemagne-business-intelligence-emplois-SRCH_IL.0,16_IC2622109_KO17,38.htm", "seo" : "berlin-allemagne-business-intelligence-emplois", "url_input" : "IL.0,16_IC2622109_KO17,38", "location_id": 2622109, "location_type": "CITY", "key_word": "business-intelligence"}]

if not os.path.exists(output_directory):
    os.makedirs(output_directory, exist_ok=True)
