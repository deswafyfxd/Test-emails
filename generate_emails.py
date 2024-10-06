import random
import string
import requests
import os
import yaml
from faker import Faker

fake = Faker()

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def generate_emails(base_email, domain, count=10):
    emails = [f"{base_email}+{fake.first_name().lower()}@{domain}" for _ in range(count)]
    return emails

def write_to_file(filename, emails):
    with open(filename, 'w') as f:
        for email in emails:
            f.write(f"{email}\n")

def send_to_discord(emails, webhook_url):
    if not webhook_url.startswith("http"):
        print("Invalid webhook URL: No scheme supplied")
        return
    data = {"content": "\n".join(emails)}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send emails to Discord: {response.status_code}")

def main():
    control_config = load_config('config_control.yml')
    email_config = load_config('config_emails.yml')

    gmail_emails = []
    outlook_emails = []

    if control_config['gmail']['enabled']:
        gmail_emails = generate_emails(email_config['gmail'], "gmail.com", control_config['gmail']['count'])
        write_to_file("gmail_emails.txt", gmail_emails)

    if control_config['outlook']['enabled']:
        outlook_emails = generate_emails(email_config['outlook'], "outlook.com", control_config['outlook']['count'])
        write_to_file("outlook_emails.txt", outlook_emails)

    all_emails = gmail_emails + outlook_emails
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    send_to_discord(all_emails, discord_webhook_url)

if __name__ == "__main__":
    main()
