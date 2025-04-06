import pandas as pd
import subprocess

def run_script(script_path, job_title, job_description, cv_directory, email_test):
    # Run the script with the provided arguments
    command = ['python', script_path, '--job_title', job_title, '--job_description', job_description,
               '--cv_directory', cv_directory, '--email_test', str(email_test)]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

df = pd.read_csv('dataset/job_description.csv')
for i in range(len(df)):
    job_title = df['Job Title'][i]
    job_description = df['Job Description'][i]
    cv_directory = 'dataset'
    email_test = 0
    script_path = 'src/app.py'
    output = run_script(script_path, job_title, job_description, cv_directory, email_test)
    print(output)
    print("---------------------------------------------------------------------------------------")
    break

print("All candidates have been processed.")


    
    