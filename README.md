# SMW Central ROM Archive

[![build status](https://git.cssnr.com/shane/smwc-web/badges/master/build.svg)](https://git.cssnr.com/shane/smwc-web/commits/master) [![coverage report](https://git.cssnr.com/shane/smwc-web/badges/master/coverage.svg)](https://git.cssnr.com/shane/smwc-web/commits/master)

This tool downloads all Super Mario World ROM's that are uploaded to www.smwcentral.net in the awaiting moderation section and archives them for download.

### Frameworks

- Django (2.1.2) https://www.djangoproject.com/
- Bootstrap (4.1.3) http://getbootstrap.com/
- Font Awesome (5.4.2) http://fontawesome.io/

# Development

### Deployment

To deploy this project on the development server:

```
git clone https://git.cssnr.com/shane/smwc-web.git
cd django-twitch
pyvenv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp settings.ini.example settings.ini
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata site-fixtures.json
python manage.py loaddata social-fixtures.json
python manage.py runserver 0.0.0.0:8000
```

*Note: Make sure to update the `settings.ini` with the necessary details...*

### Copying This Project

To clone a clean copy of this project int your repository:

```
git clone https://git.cssnr.com/shane/smwc-web.git
cd django-twitch
rm -rf .git
git init
git remote add origin https://github.com/your-org/your-repo.git
git push -u origin master
```

*Note: make sure to replace `your-org/your-repo.git` with your actual repository location...*
