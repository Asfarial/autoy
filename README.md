Django_Online_Shop<br>
HEROKU BRANCH

November, 2021<br>
Author: Vladyslav Zolotukhin <br>
xxxkova@gmail.com<br>

Educational Project - eCommerce <br>
"Autoy"<br>
Framework: Django 3.2.8 <br>
            &emsp;&emsp;visual block-scheme > block-scheme.odg <br>
Language: Python3.9 <br>
            &emsp;&emsp;modules > requirements.txt <br>
Additional Languages: HTML5, CSS, JS, Django Template Language <br>
Additional technologies: HTTP, git, GitKraken, ssh, openssh, python3.9-venv, pip3 <br>
Database: PostgreSQL <br>
            &emsp;&emsp;fixture > db.json <br>
            &emsp;&emsp;settings.DB_TRANSFER = True - before loaddata <br>
Email Server: SMTP gmail <br>
//Email Server Mailchimp Transactional - removed to file <br>

Website: autoyshop.pp.ua <br>
Host: Heroku <br>
SSL/TLS: CloudFlare <br>

https://github.com/Asfarial/Django_Online_Shop_pub


Functionalities:
    
    HOME:
    - Random model on Advert
    - Google maps iframe
    
    CATALOG:
    - built by class-based views
    - Categories
    - Filtering by Characteristics
    - Search
    - Rating
    - Dynamic Pagination
    - Template tag filter
    
    ACCOUNTS:
    - built by function-based views
    - used generic Accounts
    - Profile
        extended Profile to User model
        unique email verifications
    - Public agreement consent
    - Sign up
    - Activation email
    - Password Reset
    - Password Change
    - Orders history
    - Profile edit/delete
    - Email change
    - Email verifications on critical points
    - SHOW/HIDE password
    - "Manager" Group
    
    ADMIN:
    - Custom layouts, filters, searches
    - Permission control over some models
        i.e. cannot delete/change Orders
    
    GENERAL:
    - Following SOLID principles
    - Cart based on Sessions
        -Lock Database on checkout:
            with transaction.atomic():
                model.select_for_update
        -Verification on Product availability
    - Subsription to News Latters (MAILCHIMP MARKETING API)
    - Access control - redirects to last page
    - Signals processing
    
    DEBUG:
    -Django-silk
    -Middleware - request processing time; SQL count
    
    SETTINGS (dist):
    -Setup for HTTPS only
    -Secrets in Secrets.py


