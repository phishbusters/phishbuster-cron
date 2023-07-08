from cron_job.main import run_cron_job

def lambda_handler(event, context):
    run_cron_job()
    return {
        'statusCode': 200,
        'body': 'Cron job successfully run'
    }
