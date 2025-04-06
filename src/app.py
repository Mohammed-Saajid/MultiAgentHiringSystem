import os
from utils import hiring
import argparse


if __name__ == "__main__":
    # Get user input
    parser = argparse.ArgumentParser(description="Automate input parameters.")
    parser.add_argument("--job_title", required=True, help="Job title")
    parser.add_argument("--job_description", required=True, help="Job description")
    parser.add_argument("--cv_directory", required=True, help="Directory containing CVs")
    parser.add_argument("--email_test", required=True, default=False, help="Test email sending (True:1/False:0)")
    args = parser.parse_args()

    job_title = args.job_title
    job_description = args.job_description
    cvs_directory = args.cv_directory
    email_test = int(args.email_test)

    email_test = False if email_test == 1 else True

    # Initialize variable
    summarized_job_description : str = None
    
    cvs_directory_list = os.listdir(cvs_directory)
    cvs = [x[:-4] for x in cvs_directory_list if x.endswith('.pdf')]

    max_attempts = 3
    i = 0
    while len(cvs) != 0 and i < max_attempts:
        summarized_job_description,candidates_id = hiring(job_title, job_description, cvs_directory, summarized_job_description,email_test=email_test)
        cvs = [x for x in cvs if x not in candidates_id]
        print(f"Candidates invited: {candidates_id}")
        i += 1
    if len(cvs) == 0:
        print("All candidates have been processed.")
    else:
        print("Some candidates are still left to be processed:")
        for candidate in cvs:
            print(candidate)

            








