import random
import string
import os
import yaml
from faker import Faker
import apprise

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
    positions = range(len(username) - 1)
    variations = set()
    
    for i in positions:
        for j in positions:
            if i < j:
                variation = username[:i+1] + '.' + username[i+1:j+1] + '.' + username[j+1:]
                variations.add(variation)
    return variations

def generate_emails(base_email, name_types, add_numbers, count=10, plus=True, dot=False, plus_dot_combination=False, domain=""):
    username, domain = base_email.split('@')
    emails = set()
    
    while len(emails) < count:
        name = generate_name(name_types)
        if add_numbers['enabled']:
            number_suffix = ''.join(random.choices(string.digits, k=add_numbers['digits']))
            name += number_suffix
        
        if domain == "gmail.com":
            if plus_dot_combination and len(emails) < count // 2:
                dot_variations = generate_dot_variations(username)
                for variation in dot_variations:
                    emails.add(f"{variation}+{name}@{domain}")
            elif plus:
                emails.add(f"{username}+{name}@{domain}")
            elif dot:
                dot_variations = generate_dot_variations(username)
                for variation in dot_variations:
                    emails.add(f"{variation}@{domain}")
        elif domain == "outlook.com" and dot:
            print("Error: Outlook does not support dots. Skipping dot-based email generation.")
        else:
            emails.add(f"{username}+{name}@{domain}")
    
    return list(emails)[:count]

def write_to_file(filename, emails):
    with open(filename, 'w') as f:
        for email in emails:
            f.write(f"{email}\n")

def send_to_discord(gmail_emails, outlook_emails, webhook_url):
    apobj = apprise.Apprise()
    apobj.add(webhook_url)
    message = "**Gmail Emails:**\n" + "\n".join(gmail_emails) + "\n\n**Outlook Emails:**\n" + "\n".join(outlook_emails)
    apobj.notify(body=message, title="Generated Emails")

def main():
    control_config = load_config('config_control.yml')
    email_config = load_config('config_emails.yml')
    name_types = load_config('config_names.yml')['name_types']
    add_numbers = load_config('config_names.yml')['add_numbers']

    gmail_emails = []
    outlook_emails = []

    if control_config['gmail']['enabled']:
        gmail_emails = generate_emails(email_config['gmail'], name_types, add_numbers, control_config['gmail']['count'], control_config['gmail']['plus'], control_config['gmail']['dot_variation'], control_config['gmail']['plus_dot_combination'], "gmail.com")
        write_to_file("gmail_emails.txt", gmail_emails)

    if control_config['outlook']['enabled']:
        outlook_emails = generate_emails(email_config['outlook'], name_types, add_numbers, control_config['outlook']['count'], control_config['outlook']['plus'], control_config['outlook']['dot'], "outlook.com")
        write_to_file("outlook_emails.txt", outlook_emails)

    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    send_to_discord(gmail_emails, outlook_emails, discord_webhook_url)

if __name__ == "__main__":
    main()
