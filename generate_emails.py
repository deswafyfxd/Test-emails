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

def generate_name(name_types):
    if name_types['personal_given_names']:
        return fake.first_name().lower()
    if name_types['surnames']:
        return fake.last_name().lower()
    if name_types['nicknames']:
        # Faker does not have direct nicknames; could use first names as a proxy
        return fake.first_name().lower()
    if name_types['brand_names']:
        return fake.company().lower().replace(' ', '')
    if name_types['place_names']:
        return fake.city().lower()
    if name_types['pen_names']:
        return f"{fake.first_name().lower()}_{fake.last_name().lower()}"
    if name_types['stage_names']:
        return f"{fake.first_name().lower()}_{fake.last_name().lower()}"
    if name_types['usernames']:
        return fake.user_name().lower()
    if name_types['scientific_names']:
        # Faker does not have scientific names; creating a placeholder
        return f"species_{fake.word()}".lower()
    return fake.first_name().lower()  # Default to personal names if all false

def generate_emails(base_email, name_types, count=10):
    username, domain = base_email.split('@')
    emails = [f"{username}+{generate_name(name_types)}@{domain}" for _ in range(count)]
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
    name_types = load_config('config_names.yml')['name_types']

    gmail_emails = []
    outlook_emails = []

    if control_config['gmail']['enabled']:
        gmail_emails = generate_emails(email_config['gmail'], name_types, control_config['gmail']['count'])
        write_to_file("gmail_emails.txt", gmail_emails)

    if control_config['outlook']['enabled']:
        outlook_emails = generate_emails(email_config['outlook'], name_types, control_config['outlook']['count'])
        write_to_file("outlook_emails.txt", outlook_emails)

    all_emails = gmail_emails + outlook_emails
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    send_to_discord(all_emails, discord_webhook_url)

if __name__ == "__main__":
    main()
