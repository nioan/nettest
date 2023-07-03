#!/usr/bin/env python3
import os
from crontab import CronTab
from config import read_nettest_config


def setup_cron_job(script_name, cron_interval):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)

    # Get the user's crontab
    cron = CronTab(user=True)

    # Check if a cron job already exists for the script
    for job in cron:
        if job.command == f"python3 {script_path}":
            print("Cron job already set up.")
            return

    # Create a new cron job for the script
    job = cron.new(command=f"python3 {script_path}")
    job.setall(cron_interval)
    cron.write()
    print("Cron job successfully set up.")


def setup_cron_jobs(cron):
    for job, cron_interval in cron.items():
        script_name = f"{job}.py"
        setup_cron_job(script_name, cron_interval)


def main():
    config = read_nettest_config()
    setup_cron_jobs(config.get('cron', {}))


if __name__ == '__main__':
    main()
