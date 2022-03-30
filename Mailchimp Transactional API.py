"""
The setup for MAILCHIMP TRANSACTIONAL API
Prepared for educational purpose
In test mode emails are allowed to OWN VERIFIED DOMAIN ONLY
Therefore removed from project
"""

# Test email
# test_email.html
{% autoescape off %}
Hi {{ user.username }},
This is test email through MAILCHIMP TRANSACTIONAL API
http://{{ domain }}
{% endautoescape %}

#function
def send_test_email(request, user, email, email_type, order_details=None):
    if not email_type == "test":
        return
    import mailchimp_transactional as MailchimpTransactional
    from mailchimp_transactional.api_client import ApiClientError
    try:
        from Django_Online_Shop import secrets
        mailchimp = MailchimpTransactional.Client(secrets.EMAIL_HOST_PASSWORD)
        mail_subject = 'AUTOY SHOP - test email'
        mail_template = 'accounts/test_email.html'
        current_site = get_current_site(request)
        content = render_to_string(mail_template, {'user': user, 'domain': current_site.domain})
        message = {"html": content, "subject": mail_subject, "from_email": "admin@autoyshop.pp.ua", "to": [{'email': email,
                                                                                                            'name': user.username,
                           'type': 'to'}]}
        response = mailchimp.messages.send(
            {"message": message})
        print(response)
    except ApiClientError as error:
        print("An exception occurred: {}".format(error.text))

        #try returns [{'email': 'myemail@gmail.com', 'status': 'rejected', '_id': '6b2cc03240724c46a6f9a834407aeee1', 'reject_reason': 'recipient-domain-mismatch'}]


#settings
EMAIL_USE_TLS = False
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_HOST_USER = 'Educational Purpose'
EMAIL_HOST_PASSWORD = 'aUueIS2V9KYLrZF_ylJJEQ'
EMAIL_PORT = 587

#DNS records

#MX for inbound - MAILCHIMP transfers the email with POST
#Emails shall be redirected to website and read there...
MX  autoyshop.pp.ua         31282999.in2.mandrillapp.com    TTL 20
MX  autoyshop.pp.ua         31282999.in1.mandrillapp.com    TTL 10

TXT _dmarc.autoyshop.pp.ua  v=DMARC1; p=reject; rua=mailto:postmaster@autoyshop.pp.ua, mailto:dmarc@autoyshop.pp.ua; pct=100; adkim=s; aspf=s

TXT mandrill._domainkey.autoyshop.pp.ua v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCrLHiExVd55zd/IQ/J/mRwSRMAocV/hMB3jXwaHH36d9NaVynQFYV8NaWi69c1veUtRzGt7yAioXqLj7Z4TeEUoOLgrKsn8YnckGs9i3B3tVFB+Ch/4mPhXWiNfNdynHWBcPcbJ8kjEQ2U8y78dHZj1YeRXXVvWob2OaKynO8/lQIDAQAB;

TXT autoyshop.pp.ua v=spf1 include:spf.mandrillapp.com ?all

TXT autoyshop.pp.ua mandrill_verify.9Rb48V6D5LgLPhM4AatPmA
