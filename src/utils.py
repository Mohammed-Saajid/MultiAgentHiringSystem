from PyPDF2 import PdfReader
import sqlite3
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from agents import CandidateDataRetrieverAgent,HiringManagerAgent,JobDescriptionSummarizerAgent,CandidateExtractorAgent
# utils
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        str: Extracted text from the PDF file.
    """
    pdf = PdfReader(pdf_path)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def format_text(text: str) -> str:
    """Remove unwanted characters and format text.
    Args:
        text (str): Text to be formatted.
    Returns:
        str: Formatted text.
    """
    text = text.replace('*','')
    return text

def write_to_db(data: dict, db_path: str = "database\\candidates.db") -> None:
    """Write text to a sqlite db.
    Args:
        data (dict): Dictionary containing candidate data.
        db_path (str): Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    id = data.get('candidate_id', None)
    name = data.get('candidate_name', None)
    email = data.get('candidate_mail', None)
    job_title = data.get('job_title', None)
    # Check if all required fields are present
    if id is None or name is None or email is None or job_title is None:
        print(f"Data: {data}")
        print(f"ID: {id}, Name: {name}, Email: {email}, Job Title: {job_title}")
        raise ValueError("Missing required fields in data dictionary")
    # Create a Table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            job_title TEXT,
            invite_sent INTEGER DEFAULT 0
        )
    ''')
    # Insert or replace the candidate data
    cursor.execute('''
        INSERT OR REPLACE INTO candidates (id, name, email, job_title) VALUES (?, ?, ?, ?)
    ''', (id, name, email, job_title))
    conn.commit()
    conn.close()


def read_from_db(db_path: str = "database\\candidates.db") -> list:
    """Read text from a sqlite db.
    Args:
        db_path (str): Path to the SQLite database file.
    Returns:
        list: List of tuples containing candidate data.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Execute a query to select all rows from the candidates table
    cursor.execute('SELECT * FROM candidates WHERE invite_sent = 0')
    # Fetch all rows from the result set
    rows = cursor.fetchall()
    # Close the database connection
    conn.close()
    # Return the list of rows
    return rows

def update_db(id: str,db_path: str = "database\\candidates.db" ) -> None:
    """update invite_sent column in sqlite db.
    Args:
        id (str): Candidate ID to be updated.
        db_path (str): Path to the SQLite database file.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Execute a query to update the invite_sent column for the given candidate ID
    cursor.execute('UPDATE candidates SET invite_sent = 1 WHERE id = ?', (id,))
    # Commit the changes to the database
    conn.commit()
    # Close the database connection
    conn.close()


def send_email(recipient:str, subject:str, body:str, sender_email:str, sender_password:str, smtp_server:str='smtp.gmail.com', smtp_port:int=587):
    """
    Send an email using SMTP
    """
    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        
        # Login to server
        server.login(sender_email, sender_password)
        
        # Send email
        text = message.as_string()
        server.sendmail(sender_email, recipient, text)
        
        # Terminate the session
        server.quit()
        
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")


def send_invite(sender_email:str,sender_password:str,recipient:str,subject:str,body:str,smtp_server:str,smtp_port:int,test:bool=True) -> None:
    """Send invite to candidate.
    Args:
        sender_email (str): Email address of the candidate.
        sender_password (str): Sender email password.  
        recipient (str): Recipient email address.
        subject (str): Subject of the email.
        body (str): Body of the email.
        smtp_server (str): SMTP server address.
        smtp_port (int): SMTP server port.
        test (bool): If True, simulates sending a mail. Default is True.
    Returns:
        None
    """
    if test:
        # Simulate sending an invite email
        print(f"Sending invite to {sender_email}...")
        # we just print the email address
        print(f"Invite sent to {sender_email}")
        return
    send_email(recipient, subject, body, sender_email, sender_password, smtp_server, smtp_port)
    


def check_invited_status(candidate_id: str, db_path: str = "database\\candidates.db") -> bool:
    """Check if the candidate has already been invited.
    Args:
        candidate_id (str): Candidate ID to check.
        db_path (str): Path to the SQLite database file.
    Returns:
        bool: True if the candidate has already been invited, False otherwise.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Execute a query to check if the candidate has already been invited
    cursor.execute('SELECT invite_sent FROM candidates WHERE id = ?', (candidate_id,))
    result = cursor.fetchone()
    # Close the database connection
    conn.close()
    res = result[0] == 1 if result else False
    # Return True if the candidate has already been invited, False otherwise
    return res

def hiring(job_title:str,job_description:str,cvs_directory:str,summarized_job_description:str = None,email_test:bool=True) -> tuple[str, list[str]] :
    """Main function to manage the hiring process.
    Args:
        job_title (str): Job title for the position.
        job_description (str): Job description for the position.
        cvs_directory (str): Directory containing CV files.
        summarized_job_description (str): Summarized job description.
        email_test (bool): If True, simulates sending a mail. Default is True.
    Returns:
        tuple[str,list]: A tuple containing the summarized job description and a list of candidate IDs.
    """
    # Initialize agents
    jd_summarizer_agent = JobDescriptionSummarizerAgent()
    recruiting_agent = CandidateExtractorAgent()
    hiring_manager_agent = HiringManagerAgent()
    candidate_data_agent = CandidateDataRetrieverAgent()
    # if the email test is not true, get the email details from the user
    if not email_test:
        sender_email = input("Enter your email: \n")
        sender_password = input("Enter your password: \n")
        smtp_server = input("Enter your SMTP server: \n")
        smtp_port = int(input("Enter your SMTP port: \n"))
        recipient = input("Enter the recipient email: \n")
        subject = input("Enter the email subject: \n")
        body = input("Enter the email body: \n")
    else:
        sender_email = sender_password = smtp_server = smtp_port = recipient = subject = body = ""

    # Check if the job description has already been summarized
    if not summarized_job_description:
        summarized_job_description = jd_summarizer_agent.summarize(job_description)
    # Write the summarized job description to a file
    with open('text_files\\job_description_summary.txt', 'w') as f:
            f.write(summarized_job_description)
    # Create a list to store candidate ids
    candidates_list = []
    # Process each CV in the directory
    for filename in os.listdir(cvs_directory):
        # Check if the file is a PDF
        if filename.endswith('.pdf'):
            candidate_id = filename[0:-4]
            # Check if the candidate has already been invited
            with open('text_files\\not_selected_candidates.txt', 'r') as f:
                not_selected_candidates = f.read().split(',')
            if candidate_id in not_selected_candidates:
                print(f"Skipping already processed candidate: {candidate_id}")
                candidates_list.append(candidate_id)
                continue
            if check_invited_status(candidate_id):
                print(f"Candidate {candidate_id} has already been invited.")
                candidates_list.append(candidate_id)
                continue
            # Construct the full path to the CV file
            cv_path = os.path.join(cvs_directory, filename)
            # Extract text from the CV
            cv_text = extract_text_from_pdf(cv_path)
            # Format the text
            formatted_cv_text = format_text(cv_text)
            # Extract candidate data
            candidate_data = recruiting_agent.extract(formatted_cv_text)
            # Write the candidate data to a file
            with open('text_files\\candidate_data.txt', 'w') as f:
                f.write(candidate_data)
            # validate candidate data with job description
            hiring_manager_response = hiring_manager_agent.manage_hiring(summarized_job_description, candidate_data)
            # Write the hiring manager response to a file
            with open('text_files\\hiring_manager_response.txt', 'w') as f:
                f.write(hiring_manager_response)
            # if the candidate is a good fit, send an invite
            if 'yes' in hiring_manager_response:
                # Extract candidate data
                candidate_data = candidate_data_agent.retrieve(candidate_data)
                # load the candidate data as JSON
                json_data = json.loads(candidate_data)
                # add job title to the candidate data
                json_data['job_title'] = job_title
                # Write the candidate data to db
                write_to_db(json_data)
                # send invite to the candidate
                send_invite(sender_email=json_data.get('candidate_mail'),sender_password=sender_password,recipient=recipient,subject=subject,body=body,smtp_server=smtp_server,smtp_port=smtp_port,test=email_test)
                # Update the invite status in the database
                update_db(json_data.get('candidate_id'))
                # add candidate id to the list
                candidates_list.append(candidate_id)
            # if the candidate is not a good fit, write to not_selected_candidates.txt
            elif 'no' in hiring_manager_response:
                 print(f"Candidate {candidate_id} is not a good fit for the job.")
                 with open('text_files\\not_selected_candidates.txt', 'a') as f:
                    f.write(candidate_id+",")
                 candidates_list.append(candidate_id)
            else:
                print("Invalid response from hiring manager agent")
            
        else :
            print(f"Skipping non-pdf file: {filename}")
    return summarized_job_description,candidates_list