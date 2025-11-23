"""Test helper: log in as a user, send a chat message, then log in as admin and fetch messages.

Usage (PowerShell):
  .\env\Scripts\Activate.ps1; python scripts/send_test_message.py --user user@example.com --user-pass secret --admin admin@example.com --admin-pass AdminPass!23 --message "Hello from test"

This script is intended for local development only.
"""
import requests
import argparse


def login(session, base, email, password, admin=False):
    if admin:
        url = base + "/admin/login"
    else:
        url = base + "/login"
    r = session.post(url, data={"email": email, "password": password}, allow_redirects=True)
    return r


def send_user_message(session, base, message):
    url = base + "/chat/send"
    r = session.post(url, data={"body": message})
    return r


def fetch_admin_contacts(session, base):
    url = base + "/admin/chat/contacts"
    return session.get(url)


def fetch_admin_messages(session, base, user_id):
    url = f"{base}/admin/chat/messages/{user_id}"
    return session.get(url)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://127.0.0.1:5000", help="Base URL of running app")
    p.add_argument("--user", required=True)
    p.add_argument("--user-pass", required=True)
    p.add_argument("--admin", required=True)
    p.add_argument("--admin-pass", required=True)
    p.add_argument("--message", required=True)
    args = p.parse_args()

    base = args.base.rstrip("/")

    # Login as user and send message
    s_user = requests.Session()
    print("Logging in as user...")
    r = login(s_user, base, args.user, args.user_pass, admin=False)
    print("User login status:", r.status_code)
    print("Sending message...")
    r = send_user_message(s_user, base, args.message)
    print("Send status:", r.status_code, r.text)

    # Login as admin and fetch contacts/messages
    s_admin = requests.Session()
    print("Logging in as admin...")
    r = login(s_admin, base, args.admin, args.admin_pass, admin=True)
    print("Admin login status:", r.status_code)
    print("Fetching contacts...")
    r = fetch_admin_contacts(s_admin, base)
    print(r.status_code, r.text)

    # If contacts include the user, fetch messages for that user id
    try:
        data = r.json()
        contacts = data.get("contacts", [])
        target = next((c for c in contacts if c.get("name") and c.get("name") == args.user), None)
        if not target and contacts:
            # try matching by id of first
            target = contacts[0]
        if target:
            uid = target.get("id")
            print(f"Fetching messages for user id {uid}...")
            r2 = fetch_admin_messages(s_admin, base, uid)
            print(r2.status_code, r2.text)
    except Exception as e:
        print("Could not parse contacts response:", e)


if __name__ == "__main__":
    main()
