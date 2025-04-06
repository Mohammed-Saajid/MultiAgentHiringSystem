from ollama import chat, ChatResponse


# Agents
class JobDescriptionSummarizerAgent:
    def __init__(self, model_name: str = "gemma3"):
        self.model_name = model_name
        self.system_message = (
            "You are a job description summarizer agent. Your task is to summarize the job description provided to you.\n"
        )
        self.required_output = (
            "Please summarize the job description into the following sections:\n"
            "1. Job Title\n"
            "2. Job Description\n"
            "3. Responsibilities\n"
            "4. Requirements\n"
            "5. Skills\n"
            "6. Experience\n"
            "7. Education\n"
            "other relevant information\n"
            "Please provide the output in a structured format.\n"
            "Do not include any other information.\n"
        )


    def summarize(self, job_description: str) -> str:
        response: ChatResponse = chat(
            model=self.model_name,
            messages=[{"role": "user", "content": self.system_message+job_description+self.required_output}],
            options={"temperature": 0.7},
            format='json'
        )
        return response['message']['content']
    
class CandidateExtractorAgent:
    def __init__(self, model_name: str = "gemma3"):
        self.model_name = model_name
        self.system_message = (
            "You are a candidate extractor agent. Your task is to extract candidate information from the CV provided to you.\n"
        )
        self.required_output = (
            "Please extract the following information from the CV:\n"
            "1. Name\n"
            "2. Contact Information\n"
            "3. Education\n"
            "4. Work Experience\n"
            "5. Skills\n"
            "6. Certifications\n"
            "7. Candidate ID\n"
            "other relevant information\n"
            "Please provide the output in a structured format.\n"
            "Do not include any other information.\n"
        )

    def extract(self, cv_text: str) -> str:
        response: ChatResponse = chat(
            model=self.model_name,
            messages=[{"role": "user", "content": self.system_message+cv_text+self.required_output}],
            options={"temperature": 0.7},
            format='json'
        )
        return response['message']['content']


class HiringManagerAgent:
    def __init__(self, model_name: str = "gemma3"):
        self.model_name = model_name
        self.system_message = (
            "You are a hiring manager agent. Your task is to manage the hiring process based on the job description and CV provided to you.\n"
            "Do not select fake CVs with invalid content and time conflicts\n"
            "If the candidate is a good fit that is the candidate should have an 80% match score with the job description, provide the response in the following format:\n"
            "yes along with the response"
            "\nIf the candidate is not a good fit, provide the response in the following format:\n" 
            "no along with the response\n"
            "Do not include any other information.\n"

        )

    def manage_hiring(self, job_description: str, cv_text: str) -> str:
        response: ChatResponse = chat(
            model=self.model_name,
            messages=[{"role": "user", "content": self.system_message+"\nJob Description:\n"+job_description+"\nCandidate Info:\n"+cv_text}],
            options={"temperature": 0.7}
        )
        return response['message']['content']

class CandidateDataRetrieverAgent:
    def __init__(self, model_name: str = "gemma3"):
        self.model_name = model_name
        self.system_message = (
            "You are a candidate data retriever agent. Your task is to summarise only the necessary information from the candidate data\n"
            "Please provide the candidate data in the following format as a json:\n"
            "candidate_id: str\n"
            "candidate_name: str\n"
            "candidate_mail: str\n"
            "Please provide the output in a structured format.\n"
            "Do not include any other information.\n"
            "Candidate data:\n"
        )
    def retrieve(self, candidate_data: str) -> str:
        response: ChatResponse = chat(
            model=self.model_name,
            messages=[{"role": "user", "content": self.system_message+candidate_data}],
            options={"temperature": 0.7},
            format='json'
        )
        return response['message']['content']
    
