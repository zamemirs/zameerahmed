import json
import os
import subprocess
import sys
from datetime import datetime


def run_program(filename, input_data=None, output_filename=None):
    python_command = sys.executable

    result = subprocess.run(
        [python_command, filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=input_data,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error running {filename}: {result.stderr}")

    output_lines = result.stdout.strip().split('\n')

    for line in output_lines:
        if line.startswith("RESULT:"):
            value = line.split(":")[1].strip()
            return value


def get_absolute_path(relative_path):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(BASE_DIR, relative_path)


def load_input_json(relative_path):
    absolute_path = get_absolute_path(relative_path)
    with open(absolute_path, 'r') as f:
        return json.load(f)


def main():
    start_time = datetime.now()
    print(f"Start Time : {start_time}")
    print("Starting WebScraping...")

    web_scrapper_config = get_absolute_path('web_scrapping_program/WebScrapperConfigurable.py')
    web_scrapper_map_data = get_absolute_path('web_scrapping_program/WebScrapperMapData.py')
    validation_random_select = get_absolute_path('web_scrapping_program/validation_randomselect.py')

    folder_name = run_program(web_scrapper_config)
    print(f"Scraping Complete {datetime.now()}")
    print(f"Data Modeling... start time {datetime.now()}")

    run_program(web_scrapper_map_data, folder_name)
    print(f"Data Validation... start time {datetime.now()}")
    run_program(validation_random_select, folder_name)

    end_time = datetime.now()
    print(f"End Time : {end_time}")
    total_time = end_time - start_time
    minutes, seconds = divmod(total_time.seconds, 60)
    print(f"Total Time: {minutes} minutes {seconds} seconds")
    return folder_name


if __name__ == "__main__":
    lookup_table_data = [
        {"Provider": ["Provider", "Provider Name"]},
        {"Estimate/ShareClass": ["Share Class", "Class"]}
    ]

    input_json_data = load_input_json('web_scrapping_program/input.json')

    timestr = '20231017120050'  # input("Folder Name: ")
    output_filename = f"data_map_{timestr}.csv"

    main()
