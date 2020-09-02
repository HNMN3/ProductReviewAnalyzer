# Product Review Analyzer
## Requirements
- python 3.7
- Google Cloud Project and private_key.json file

## Steps to follow
- Download the private key for your account from GCP and put it in env variable as below:
```
export GOOGLE_APPLICATION_CREDENTIALS="path_to_private_key.json"
```
- setup the DATABASE_URI as follow:
```
export DATABASE_URI="postgres+psycopg2://USERNAME:PASSWORD@IP_ADDRESS:PORT/DATABASE_NAME"
```
- Clone the project and cd into it
```
git clone https://github.com/HNMN3/ProductReviewAnalyzer.git
cd ProductReviewAnalyzer
```
- Installed the required libraries via below command:
```
pip install -r requirements.txt
```
- Run below command to create the db tables for the first time and whenever something changes in db tables
```
python setup.py
```
- Run the python program as follows:
```
python main.py bucket_name file_name
```
