import mlflow
import tempfile
import os
import wandb
import hydra
from omegaconf import DictConfig
import json

# Define the steps to be executed
_steps = [
    "download",
    "basic_cleaning",
    "data_check",
    "data_split",
    "train_random_forest",
    # "test_regression_model" is not included in _steps as per your note
]

@hydra.main(config_name='config')
def go(config: DictConfig):
    # Setup W&B experiment
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    # Steps to execute
    steps_par = config['main']['steps']
    active_steps = steps_par.split(",") if steps_par != "all" else _steps

    with tempfile.TemporaryDirectory() as tmp_dir:
        for step in active_steps:
            print(f"Running step: {step}")
            try:
                if step == "download":
                    # Download file and load in W&B
                    mlflow.run(
                        f"{config['main']['components_repository']}/get_data",
                        "main",
                        parameters={
                            "sample": config["etl"]["sample"],
                            "artifact_name": "sample.csv",
                            "artifact_type": "raw_data",
                            "artifact_description": "Raw file as downloaded"
                        },
                    )
                elif step == "basic_cleaning":
                    # Perform basic data cleaning
                    mlflow.run(
                        os.path.join(hydra.utils.get_original_cwd(), "src", "basic_cleaning"),
                        "main",
                        parameters={
                            "input_artifact": "sample.csv:latest",
                            "output_artifact": "clean_sample.csv",
                            "output_type": "clean_sample",
                            "output_description": "Data with outliers and null values removed",
                            "min_price": config['etl']['min_price'],
                            "max_price": config['etl']['max_price']
                        },
                    )
                elif step == "data_check":
                    # Implement data checking code here
                    pass
                # Add more steps as needed

            except Exception as e:
                print(f"Error occurred in step {step}: {e}")
                # Handle the error as needed

if __name__ == "__main__":
    go()
