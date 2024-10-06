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
    if name_types['personal_given_names']['indian']:
        fake = Faker('en_IN')
        return fake.first_name().lower()
    if name_types['personal_given_names']['western']:
        fake = Faker('en_US')
        return fake.first_name().lower()
    if name_types['personal_given_names']['japanese']:
        fake = Faker('en_US')
        return fake.first_name().lower()
    if name_types['personal_given_names']['chinese']:
        fake = Faker('en_US')
        return fake.first_name().lower()
    if name_types['personal_given_names']['other']:
        fake = Faker('en_US')
        return fake.first_name().lower()
    if name_types['surnames']:
        return fake.last_name().lower()
    if name_types['nicknames']:
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
        return f"species_{fake.word()}".lower()
    return fake.first_name().lower()  # Default to personal names if all false

def generate_emails(base_email, name_types, add_numbers, count=10, plus=True, dot=False):
    username, domain = base_email.split('@')
    emails = []
    for _ in range(count):
        name = generate_name(name_types)
        if add_numbers['enabled']:
            number_suffix = ''.join(random.choices(string.digits, k=add_numbers['digits']))
            name += number_suffix
        if plus:
            emails.append(f"{username}+{name}@{domain}")
        elif dot:
            emails.append(f"{username}.{name}@{domain}")
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
    add_numbers = load_config('config_names.yml')['add_numbers']

    gmail_emails = []
    outlook_emails = []

    if control_config['gmail']['enabled']:
        gmail_emails = generate_emails(email_config['gmail'], name_types, add_numbers, control_config['gmail']['count'], control_config['gmail']['plus'], control_config['gmail']['dot'])
        write_to_file("gmail_emails.txt", gmail_emails)

    if control_config['outlook']['enabled']:
        outlook_emails = generate_emails(email_config['outlook'], name_types, add_numbers, control_config['outlook']['count'], control_config['outlook']['plus'], control_config['outlook']['dot'])
        write_to_file("outlook_emails.txt", outlook_emails)

    all_emails = gmail_emails + outlook_emails
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    send_to_discord(all_emails, discord_webhook_url)

if __name__ == "__main__":
    main()
