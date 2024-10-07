import random
import string
import os
import yaml
from faker import Faker
import apprise
from datetime import datetime

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

def generate_dot_variations(username):
    variations = set()
    for i in range(1, len(username)):
        variations.add(username[:i] + '.' + username[i:])
    return variations

def generate_emails(base_email, name_types, add_numbers, total_count=10, plus_count=0, dot_variation_count=0, plus_dot_combination_count=0, domain="", plus_enabled=True, dot_enabled=True, plus_dot_combination_enabled=True):
    username, domain = base_email.split('@')
    plus_emails = set()
    dot_emails = set()
    plus_dot_emails = set()

    # Fallback to plus type if all counts are 0
    if total_count <= 10 or (plus_enabled and not plus_count and not dot_variation_count and not plus_dot_combination_count):
        plus_count = total_count

    # Generate Plus emails
    count = 0
    while count < plus_count and plus_enabled:
        plus_emails.add(f"{username}+{generate_name(name_types)}@{domain}")
        count += 1

    # Generate Dot Variation emails
    count = 0
    while count < dot_variation_count and dot_enabled:
        variation = generate_dot_variations(username)
        for var in variation:
            if count >= dot_variation_count:
                break
            dot_emails.add(f"{var}@{domain}")
            count += 1

    # Generate Plus Dot Combination emails
    count = 0
    while count < plus_dot_combination_count and plus_dot_combination_enabled:
        variation = generate_dot_variations(username)
        for var in variation:
            if count >= plus_dot_combination_count:
                break
            plus_dot_emails.add(f"{var}+{generate_name(name_types)}@{domain}")
            count += 1

    # Combine all emails
    emails = list(plus_emails) + list(dot_emails) + list(plus_dot_emails)
    return emails[:total_count]

def write_to_file(filename, emails):
    with open(filename, 'w') as f:
        for email in emails:
            f.write(f"{email}\n")

def send_to_discord(gmail_emails, outlook_emails, webhook_url):
    apobj = apprise.Apprise()
    apobj.add(webhook_url)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    gmail_plus = [email for email in gmail_emails if "+" in email and "." not in email]
    gmail_dot = [email for email in gmail_emails if "." in email and "+" not in email]
    gmail_plus_dot = [email for email in gmail_emails if "+" in email and "." in email]
    
    outlook_plus = [email for email in outlook_emails if "+" in email]

    message = (
        f"**Date and Time:** {timestamp}\n\n"
        "**Gmail Emails:**\n"
        "**Plus and Plus Dot Combination:**\n" + "\n".join(gmail_plus) + "\n\n" + "\n".join(gmail_plus_dot) + "\n\n"
        "**Dot Variation:**\n" + "\n".join(gmail_dot) + "\n\n"
        "**Outlook Emails:**\n"
        "**Plus:**\n" + "\n".join(outlook_plus)
    )

    apobj.notify(body=message, title="Generated Emails")

def main():
    control_config = load_config('config_control.yml')
    email_config = load_config('config_emails.yml')
    name_types = load_config('config_names.yml')['name_types']
    add_numbers = load_config('config_names.yml')['add_numbers']

    gmail_emails = []
    outlook_emails = []

    gmail_total_count = control_config['gmail']['count']
    outlook_total_count = control_config['outlook']['count']

    gmail_plus_count = control_config['gmail'].get('plus_count', 0)
    gmail_dot_variation_count = control_config['gmail'].get('dot_variation_count', 0)
    gmail_plus_dot_combination_count = control_config['gmail'].get('plus_dot_combination_count', 0)
    gmail_plus_enabled = control_config['gmail'].get('plus', False)
    gmail_dot_variation_enabled = control_config['gmail'].get('dot_variation', False)
    gmail_plus_dot_combination_enabled = control_config['gmail'].get('plus_dot_combination', False)

    outlook_plus_count = control_config['outlook'].get('plus_count', 0)
    outlook_dot_variation_count = control_config['outlook'].get('dot_variation_count', 0)
    outlook_plus_dot_combination_count = 0  # Outlook does not support dots
    outlook_plus_enabled = control_config['outlook'].get('plus', False)
    outlook_dot_variation_enabled = control_config['outlook'].get('dot_variation', False)
    outlook_plus_dot_combination_enabled = control_config['outlook'].get('plus_dot_combination', False)

    # Default to plus if total count is 10 or below
    if gmail_total_count <= 10:
        gmail_plus_count = gmail_total_count
        gmail_dot_variation_count = 0
        gmail_plus_dot_combination_count = 0

    if outlook_total_count <= 10:
        outlook_plus_count = outlook_total_count
        outlook_dot_variation_count = 0
        outlook_plus_dot_combination_count = 0

    if control_config['gmail']['enabled']:
        gmail_emails = generate_emails(email_config['gmail'], name_types, add_numbers, gmail_total_count, gmail_plus_count, gmail_dot_variation_count, gmail_plus_dot_combination_count, "gmail.com", gmail_plus_enabled, gmail_dot_variation_enabled, gmail_plus_dot_combination_enabled)
        write_to_file("gmail_emails.txt", gmail_emails)

    if control_config['outlook']['enabled']:
        outlook_emails = generate_emails(email_config['outlook'], name_types, add_numbers, outlook_total_count, outlook_plus_count, outlook_dot_variation_count, outlook_plus_dot_combination_count, "outlook.com", outlook_plus_enabled, outlook_dot_variation_enabled, outlook_plus_dot_combination_enabled)
        write_to_file("outlook_emails.txt", outlook_emails)

    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    send_to_discord(gmail_emails, outlook_emails, discord_webhook_url)

if __name__ == "__main__":
    main()
