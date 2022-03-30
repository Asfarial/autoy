#!/usr/bin/bash
echo -e '\033[1;92m1. Activating venv'
source ../venv/bin/activate
echo '2. Installing pip3 packages'
pip3 install -r ../requirements.txt > /dev/null
echo '3. Setting DB_TRANSFER = True'
sed -i 's%^.*DB_TRANSFER.*$%DB_TRANSFER = True%' ../Django_Online_Shop/settings.py
echo '4. Making migrations'
python3 ../manage.py migrate
echo -e '\033[1;92m5. Deleting ContentTypes'
python3 ../manage.py shell < del_content_types.py
echo -e '6. Loading database fixture\033[0m'
python3 ../manage.py loaddata db.json
echo -e '\033[1;92m7. Setting DB_TRANSFER = False'
sed -i 's%^.*DB_TRANSFER.*$%DB_TRANSFER = False%' ../Django_Online_Shop/settings.py
echo -e '\033[1;92m8. Deactivating venv'
deactivate

