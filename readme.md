
# Phish Buster CRON - Twitter API

This project consists of several components aimed at detecting fake Twitter profiles. It includes a CRON job, a data extractor for Twitter using the `tweeterpy` library, and an API for a Machine Learning model. The CRON job runs on an AWS Lambda, connects to the Twitter API, and stores specific information.

## Components

- **Data Extractor**: Located in `src.dataset_extractor`, this component uses the `tweeterpy` library to scrape Twitter data.
  
- **API for ML Model**: This API is situated in `src.api.api` and is responsible for analyzing Twitter profiles to determine their authenticity.
  
- **CRON Job**: This is the scheduled task that periodically triggers the data extraction and sends it to the ML model for analysis.

## Environment Setup

1. **Install Python**: If you haven't done so already, install Python on your machine. It is recommended to use Python 3.10 as newer versions seem not to work well with scraping libraries.

2. **Create a Virtual Environment**: In the root directory of your project, create a virtual environment by running:

    ```cmd
    python3 -m venv phishbusters
    ```

3. **Activate the Virtual Environment**: Depending on your operating system, activate the virtual environment with one of the following commands:

    ```cmd
    On Windows, run: .\phishbusters\Scripts\activate
    On Unix or MacOS, run: source phishbusters/bin/activate
    ```

4. **Install Dependencies**: Install the necessary dependencies by running:

    ```cmd
    pip install -r requirements.txt
    ```

5. **Environment Variables**: Copy and paste `.env.template` and rename it to `.env`. Fill in the required variables.

6. **Twitter Credentials**: To facilitate data extraction from Twitter, you can create a `login_twitter.csv` file in the root directory. In this file, you can list multiple Twitter accounts, separated by tabs as follows:

    ```txt
    username\tpassword\tlastLogin
    cuenta1\tpass1\t
    cuenta2\tpass2\t
    ```

This allows the program to switch between multiple accounts to circumvent Twitter's rate limiting.

## Running the Modules

To run the individual components, use the following commands:

- For the API:  

  ```cmd
  python -m src.api.api
  ```

- For the CRON job:

  ```cmd
  python -m src.cron.main
  ```

- For the Data Extractor:  

  ```cmd
  python -m src.main
  ```
