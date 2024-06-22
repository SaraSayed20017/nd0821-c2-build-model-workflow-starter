#!/usr/bin/env python
"""
Performs basic cleaning on the data and saves the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info("Downloading input artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    # Read the data
    logger.info("Reading the data from the artifact")
    df = pd.read_csv(artifact_local_path)

    # Drop outliers
    logger.info(f"Dropping rows with price not between {args.min_price} and {args.max_price}")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    logger.info("Converting last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Save cleaned data to a new CSV file
    cleaned_artifact_path = "clean_sample.csv"
    logger.info(f"Saving cleaned data to {cleaned_artifact_path}")
    df.to_csv(cleaned_artifact_path, index=False)

    # Log the cleaned data as an artifact
    logger.info("Logging cleaned data as an artifact")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(cleaned_artifact_path)
    run.log_artifact(artifact)

    logger.info("Cleaning process finished")
    run.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This step cleans the data")

    parser.add_argument(
        "--input_artifact", 
        type=str, 
        help="Fully-qualified name for the input artifact", 
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str, 
        help="Name for the output artifact", 
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str, 
        help="Type for the output artifact", 
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str, 
        help="Description for the output artifact", 
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float, 
        help="Minimum price to filter the dataset", 
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float, 
        help="Maximum price to filter the dataset", 
        required=True
    )

    args = parser.parse_args()

    go(args)
