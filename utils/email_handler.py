from imap_tools import MailBox, AND
from datetime import timedelta

def search_emails(username, password, subject, sender, start_date_dt, end_date_dt):
    """
    Connects to a GMail account and searches for emails based on criteria.
    Returns the number of emails found or an error string.
    """
    try:
        with MailBox("imap.gmail.com").login(username, password, "Inbox") as mb:
            criteria = AND(
                from_=sender,
                subject=subject,
                date_gte=start_date_dt,
                date_lt=(end_date_dt + timedelta(days=1))
            )
            uids = mb.uids(criteria)
            return len(uids)
    except Exception as e:
        print(f"An error occurred during email search: {e}")
        return f"Error: {e}"