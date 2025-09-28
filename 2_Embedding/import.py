import os
import csv
import psycopg
import json
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from pgvector.psycopg import register_vector
from dotenv import load_dotenv
from parsers import parse_images, parse_instructions, parse_metadata, parse_content
from tqdm import tqdm

load_dotenv()

BATCH_SIZE = 1000
CSV_LIMIT = 100000000

def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        filename='logs/import.log', 
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    try:
        logger.info("Starting embedding process...")
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, './data/recipes.csv')
        csv.field_size_limit(CSV_LIMIT)

        logger.info("Loading model...")
        model = SentenceTransformer("intfloat/e5-small-v2")
        process_csv(filename, model, logger)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e

def process_csv(filename: str, model: SentenceTransformer, logger: logging.Logger):
    """Process the CSV file and import the relevant recipes into the database."""
    logger.info("Connecting to database...")
    with psycopg.connect(f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')} password={os.getenv('DB_PASS')}") as conn:
        
        logger.info("Registering vector extension...")
        register_vector(conn)

        with conn.cursor() as cursor:

            logger.info("Importing recipes...")
            with open(filename, 'r') as f:
                total_lines = sum(1 for _ in f) - 1  # subtract header

            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                batch = []
                idx = 0

                for recipe in tqdm(reader, desc="Processing recipes...", total=total_lines):
                    images = parse_images(recipe["Images"], logger)
                    instructions = parse_instructions(recipe["RecipeInstructions"], logger)

                    #Ignore recipes with no images or instructions, it's less interesting when it's not clear what the recipe looks like
                    if (len(images)==0) :
                        logger.warning(f"Ignoring {recipe['Name']}, no Images...")
                        logger.warning(recipe["Images"])
                        continue

                    #Ignore recipes with no instructions
                    if (len(instructions)==0) :
                        logger.warning(f"Ignoring {recipe['Name']}, no Instructions...")
                        logger.warning(recipe["RecipeInstructions"])
                        continue
                   
                    #Create the metadata object to be stored in the database
                    metadata = parse_metadata(recipe, logger)

                    if not metadata.get("success", False):
                        logger.warning(f"Error while parsing metadata for {recipe['Name']}, skipping...")
                        continue

                    #Create the content string to be embedded
                    content = parse_content(recipe, logger)

                    if not content.get("success", False):
                        logger.warning(f"Error while parsing content for {recipe['Name']}, skipping...")
                        continue

                    embedding = np.array(model.encode("passage: " + content.get("data"), show_progress_bar = False))
                    batch.append((content.get("data"), embedding, json.dumps(metadata.get("data"))))
                    logger.info(f"Successfully processed {recipe['Name']}")
                    
                    #Commit the batch to the database every BATCH_SIZE recipes
                    if idx % BATCH_SIZE == 0:
                        cursor.executemany("INSERT INTO recipes (content, embedding, metadata) VALUES (%s, %s, %s)", batch)
                        conn.commit()
                        logger.info(f"Committed batch ending at record {idx}")
                        batch = []
                    idx += 1

                #Commit the final batch to the database
                if batch:
                    cursor.executemany("INSERT INTO recipes (content, embedding, metadata) VALUES (%s, %s, %s)", batch)
                    conn.commit()
                    logger.info("Committed final batch")
    logger.info("Finished importing recipes.")

if __name__ == "__main__":
    main()