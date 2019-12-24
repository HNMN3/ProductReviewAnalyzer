# Imports the Google Cloud client library
import csv
import os
import sys
import time

from google.api_core.exceptions import ResourceExhausted
from google.cloud import language, storage

from config import Session
from database import Review, Entity

tmp_file = 'reviews.csv'


# This function calls the Google NLP API and stores the review entities
def analyze_review(client, review, session, msg):
    try:

        # The review text to analyze
        text = review.review_text

        # Calling Google NLP API
        document = language.types.Document(
            content=text,
            type='PLAIN_TEXT',
        )
        review_response = client.analyze_sentiment(
            document=document,
            encoding_type='UTF32',
        )
        review.review_sentiment_magnitude = review_response.document_sentiment.magnitude
        review.review_sentiment_score = review_response.document_sentiment.score

        entities_response = client.analyze_entity_sentiment(
            document=document,
            encoding_type='UTF32',
        )
        entities = entities_response.entities
        for entity in entities:
            entity_name = entity.name
            salience = entity.salience
            sentiment_score = entity.sentiment.score
            sentiment_magnitude = entity.sentiment.magnitude
            entity_obj = Entity(entity_name, salience, sentiment_score, sentiment_magnitude, review.id)
            session.add(entity_obj)
        return True
    except ResourceExhausted:
        print("Resource Quota Exhausted for the NLP API!!")
        print(msg)
        return False
    except:
        import traceback
        traceback.print_exc()
        print("Stopping the process!!")
        return False


# This function fetches file from GCS
def fetch_file_from_gcs(bucket_name, file_name):
    print("Fetching file from Google Cloud Storage")
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.download_to_filename(tmp_file)
        print("File Fetched!!")
    except:
        print("Unable to fetch file!! Please verify permissions!!")
        exit()


# This function takes the input and store it in reviews table
def process_input(header=True):
    csv_file = open(tmp_file, 'r', encoding='utf-8')
    try:
        csv_reader = list(csv.reader(csv_file, delimiter=','))
    except:
        print("Error in opening csv file. Please check the format/encoding!!")
        exit()
    line_no = 0
    if header:
        line_no += 1
        csv_reader = csv_reader[1:]
    session = Session()

    all_reviews = session.query(Review).all()
    reviews_set = {(review.product_id, str(review.review_text).lower()) for review in all_reviews}
    reviews_in_file = set()
    print("Processing input file..")
    for line in csv_reader:
        line_no += 1
        review_text = line[0]
        product_id = line[4]
        search_key = (product_id, str(review_text).lower())
        if search_key in reviews_set:
            print("Review at line: {} is already in db!!".format(line_no))
        elif search_key in reviews_in_file:
            print("Review at line: {} is duplicate in file!!".format(line_no))
        else:
            review_ob = Review(product_id, review_text)
            session.add(review_ob)
            reviews_in_file.add(search_key)

    print("Committing data...")
    session.commit()
    session.close()
    try:
        # Remove downloaded file
        os.remove(tmp_file)
    except:
        pass


# This function iterates the  reviews which are pending to analyze and analyzes them.
def process_reviews():
    session = Session()
    client = language.LanguageServiceClient()
    reviews_to_analyze = session.query(Review).filter_by(review_analyzed=False).all()
    total = len(reviews_to_analyze)
    processed = 0
    step = 1
    throttle_limit = 500
    print("Processing Reviews...")
    print("Processed {}/{} ".format(processed, total), end='\r')
    default_msg = 'Sleeping for 1 minute before retrying..'
    abort_message = 'Stopping the process!!'
    start_time = time.time()
    one_minute = 60
    for review in reviews_to_analyze:
        flag = (analyze_review(client, review, session, default_msg)
                or time.sleep(60)
                or analyze_review(client, review, session, abort_message))
        if not flag:
            break
        review.review_analyzed = True
        session.add(review)
        processed += 1
        if processed == 5:
            break

        if processed % step == 0:
            print("Processed {}/{} ".format(processed, total), end='\r')

        if processed % throttle_limit == 0:
            end_time = time.time()
            time_taken = end_time - start_time
            if time_taken < one_minute:
                time.sleep(one_minute - time_taken)
            start_time = time.time()

    print("Processed {}/{} ".format(processed, total))
    print("Committing data...")
    session.commit()
    session.close()

    print("Processed data stored successfully!!")


if __name__ == '__main__':
    args = sys.argv
    if len(args) != 3:
        print("Usage: python main.py bucket_name file_name")
        quit()
    try:
        bucket_name = args[1]
        file_name = args[2]
        header = input("Consider first line as header?(Y/n):") or "y"
        fetch_file_from_gcs(bucket_name, file_name)
        process_input(str(header).lower() == "y")
        process_reviews()
    except:
        # import traceback
        #
        # traceback.print_exc()
        print("Error in Processing data!! Aborting!!")
