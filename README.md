# NLP_Review_Analyzer
- Download the private key for your account from GCP and put it in env variable as below:
    export GOOGLE_APPLICATION_CREDENTIALS="path_to_private_key.json"
- setup the DATABASE_URI as follow:
    export DATABASE_URI="postgres+psycopg2://USERNAME:PASSWORD@IP_ADDRESS:PORT/DATABASE_NAME"
- git clone https://github.com/HNMN3/NLP_Review_Analyzer.git
- Make sure that python 3.7 is installed
- Installed the required libraries via below command:
    pip install -r requirements.txt
- Run below command to create the db tables for the first time and whenever something changes in db tables
    python setup.py
- Run the python program as follows:
    python main.py bucket_name file_name
