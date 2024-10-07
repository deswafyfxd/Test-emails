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
    positions = range(len(username))
    variations = set()

    for i in positions:
        variation = username[:i] + '.' + username[i:]
        variations.add(variation)
    return variations

def generate_emails(base_email, name_types, add_numbers, total_count=10, plus_count=0, dot_variation_count=0, plus_dot_combination_count=0, domain="", plus_enabled=True, dot_enabled=True, plus_dot_combination_enabled=True):
    username, domain = base_email.split('@')
    emails = set()

    # Fallback to plus type if all counts are 0
    if total_count > 10 and plus_count == 0 and dot_variation_count == 0 and plus_dot_combination_count == 0:
        plus_count = total_count

    while len(emails) < total_count:
        name = generate_name(name_types)
        if add_numbers['enabled']:
            number_suffix = ''.join(random.choices(string.digits, k=add_numbers['digits']))
            name += number_suffix

        if domain == "gmail.com":
            if plus_dot_combination_enabled and plus_dot_combination_count > 0 and len(emails) < plus_dot_combination_count:
                dot_variations = generate_dot_variations(username)
                for variation in dot_variations:
                    emails.add(f"{variation}+{name}@{domain}")
            elif plus_enabled and plus_count > 0 and len(emails) < plus_count + plus_dot_combination_count:
                emails.add(f"{username}+{name}@{domain}")
            elif dot_enabled and dot_variation_count > 0:
                dot_variations = generate_dot_variations(username)
                for variation in dot_variations:
                    emails.add(f"{variation}@{domain}")
        elif domain == "outlook.com" and dot_enabled:
            print("Error: Outlook does not support dots. Skipping dot-based email generation.")
        else:
            emails.add(f"{username}+{name}@{domain}")

    return list(emails)[:total_count]

def write_to_file(filename, emails):
    with open(filename, 'w') as f:
        for email in emails:
            f.write(f"{email}\n")

def send_to_discord(gmail_emails, outlook_emails, webhook_url):
    apobj = apprise.Apprise()
    apobj.add(webhook_url)
    
    gmail_plus = "\n".join([email for email in gmail_emails if "+" in email and "." not in email])
    gmail_dot = "\n".join([email for email in gmail_emails if "." in email and "+" not in email])
    gmail_plus_dot = "\n".join([email for email in gmail_emails if "+" in email and "." in email])
    
    outlook_plus = "\n".join([email for email in outlook_emails if "+" in email])
    
    message = (
        f"**Gmail Emails:**\n"
        f"**Plus:**\n{gmail_plus}\n\n"
        f"**Dot Variation:**\n{gmail_dot}\n\n"
        f"**Plus Dot Combination:**\n{gmail_plus_dot}\n\n"
        f"**Outlook Emails:**\n"
        f"**Plus:**\n{outlook_plus}"
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
