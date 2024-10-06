import random
import string
import requests
import os

def generate_random_string(length=5):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_emails(base_email, domain, count=10):
    emails = [f"{base_email}+{generate_random_string()}@{domain}" for _ in range(count)]
    return emails

def write_to_file(filename, emails):
    with open(filename, 'w') as f:
        for email in emails:
            f.write(f"{email}\n")

def send_to_discord(emails, webhook_url):
    data = {"content": "\n".join(emails)}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send emails to Discord: {response.status_code}")

def main(generate_gmail=True, generate_outlook=True):
    gmail_base = "kishorkumar@gmail.com"
    outlook_base = "kishorkumar@outlook.com"

    gmail_emails = []
    outlook_emails = []

    if generate_gmail:
        gmail_emails = generate_emails(gmail_base, "gmail.com")
        write_to_file("gmail_emails.txt", gmail_emails)

    if generate_outlook:
        outlook_emails = generate_emails(outlook_base, "outlook.com")
        write_to_file("outlook_emails.txt", outlook_emails)

    all_emails = gmail_emails + outlook_emails
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    send_to_discord(all_emails, discord_webhook_url)

if __name__ == "__main__":
    main(generate_gmail=True, generate_outlook=True)
