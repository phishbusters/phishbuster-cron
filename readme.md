# Phish buster CRON - Twitter API

This project is a CRON job running on an AWS Lambda, connecting to the Twitter API, and storing certain information.

## Environment Setup

1. **Install Python**: If you haven't done so already, install Python on your machine.
2. **Create a virtual environment**: In the root directory of your project, run the following command in your terminal to create a virtual environment:

```cmd
    python3 -m venv phishbusters
```

3. **Activate the virtual environment**: To activate the virtual environment, use one of the following commands depending on your operating system:

```cmd
    On Windows, run: `.\phishbusters\Scripts\activate`
    On Unix or MacOS, run: `source phishbusters/bin/activate`
```

4. **Install dependencies**: In the root directory of your project, run the following command in your terminal to install the necessary dependencies:

```cmd
    pip install -r requirements.txt
```

## Twitter API Setup

1. Get your API keys: Visit <https://developer.twitter.com/> and follow the instructions to get your API keys and access tokens.

2. Set up your environment variables: Create a .env file in the root directory of your project and add the following lines, replacing your_value with the API keys and tokens you obtained in the previous step:

```cmd
TWITTER_API_KEY=your_value
TWITTER_API_SECRET_KEY=your_value
TWITTER_ACCESS_TOKEN=your_value
TWITTER_ACCESS_TOKEN_SECRET=your_value
```

## Running

Run the CRON job: To run the CRON job, use the following command in your terminal:

```py
    python cron_job/main.py
```
