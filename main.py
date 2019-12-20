# Imports the Google Cloud client library
import csv
import os
import sys

from google.cloud import language

from config import Session
from database import Review, Entity

last_line_is_progress_bar = False


# This function calls the Google NLP API and stores the review entities
def analyze_review(review, session):
    # Instantiates a client
    client = language.LanguageServiceClient()

    # The review text to analyze
    text = review.review_text

    # Calling Google NLP API
    document = language.types.Document(
        content=text,
        type='PLAIN_TEXT',
    )
    response = client.analyze_entity_sentiment(
        document=document,
        encoding_type='UTF32',
    )
    entities = response.entities
    for entity in entities:
        entity_name = entity.name
        salience = entity.salience
        sentiment_score = entity.sentiment.score
        entity_obj = Entity(entity_name, salience, sentiment_score, review.id)
        session.add(entity_obj)


# This function takes the input and store it in reviews table
def process_input(input_file, header=True):
    global last_line_is_progress_bar
    csv_file = open(input_file, 'r')
    csv_reader = list(csv.reader(csv_file, delimiter=','))
    total = len(csv_reader)
    line_no = 0
    if header:
        line_no += 1
        csv_reader = csv_reader[1:]
    session = Session()

    all_reviews = session.query(Review).all()
    reviews_set = {(review.product_id, str(review.review_text).lower()) for review in all_reviews}
    reviews_in_file = set()
    print("Processing input file..")
    last_line_is_progress_bar = False
    step = 10
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
    last_line_is_progress_bar = False
    session.commit()
    session.close()


# This function iterates the  reviews which are pending to analyze and analyzes them.
def process_reviews():
    global last_line_is_progress_bar
    session = Session()
    reviews_to_analyze = session.query(Review).filter_by(review_analyzed=False).all()
    total = len(reviews_to_analyze)
    processed = 0
    step = 1
    print("Processing Reviews...")
    print("Processed {}/{} ".format(processed, total), end='\r')
    for review in reviews_to_analyze:
        analyze_review(review, session)
        review.review_analyzed = True
        session.add(review)
        processed += 1
        if processed % step == 0:
            print("Processed {}/{} ".format(processed, total), end='\r')

    print("Processed {}/{} ".format(processed, total))
    print("Committing data...")
    session.commit()
    session.close()
    print("All reviews processed")


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print("Usage: python main.py path_to_input_file.csv")
        quit()
    file_path = args[1]
    if not os.path.exists(file_path):
        print("No file found at path: {}".format(file_path))
        quit()
    header = input("Consider first line as header?(Y/n):") or "y"
    process_input(file_path, str(header).lower() == "y")
    process_reviews()
