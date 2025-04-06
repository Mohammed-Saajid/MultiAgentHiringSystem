@echo off
REM Run the Python script with predefined parameters

python src/app.py ^
--job_title "Quality Assurance Engineer" ^
--job_description "Ensure the quality and reliability of software applications by conducting manual and automated testing. Identify bugs, optimize testing processes, and collaborate with developers to improve software performance. Responsibilities: Develop and execute test plans, cases, and scripts. Identify and document software defects, ensuring timely resolution. Automate testing processes to improve efficiency. Collaborate with developers to enhance software quality. Conduct performance and security testing as needed. Qualifications: Bachelor's degree in Computer Science, Engineering, or related field. Experience with testing tools like Selenium, JUnit, or TestNG. Strong analytical and problem-solving skills. Knowledge of software development lifecycle (SDLC) and Agile methodologies. Ability to work independently and in a team environment." ^
--cv_directory "test" ^
--email_test 0

REM Pause to allow the user to see the output before closing the terminal
pause