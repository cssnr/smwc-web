[![Discord](https://img.shields.io/discord/111645911091814400?color=7289da&label=discord&logo=discord&logoColor=white&style=plastic)](https://discord.gg/ZrRbfdE6kz)
[![](https://repository-images.githubusercontent.com/443952841/5d9d45ca-7bf2-4773-969e-302f2ecd6903)](https://smwc.world/)
# SMW Central ROM Archive

[![build status](https://git.cssnr.com/shane/smwc-web/badges/master/build.svg)](https://git.cssnr.com/shane/smwc-web/commits/master) [![coverage report](https://git.cssnr.com/shane/smwc-web/badges/master/coverage.svg)](https://git.cssnr.com/shane/smwc-web/commits/master)

This tool downloads all Super Mario World ROM's that are uploaded to www.smwcentral.net in the awaiting moderation section and archives them for download.

### Frameworks

- Django 4 https://www.djangoproject.com/
- Bootstrap 4 http://getbootstrap.com/
- Font Awesome 5 http://fontawesome.io/

## Development

### Deployment

To deploy this project on your local server:

1. Create Discord App: [discord.com/developers/applications](https://discord.com/developers/applications)
1. Create Bitly Access Token: [dev.bitly.com/docs/getting-started...](https://dev.bitly.com/docs/getting-started/authentication/)
1. Create MySQL Database
1. Install Docker with Compose

```
git clone https://git.cssnr.com/shane/smwc-web.git
cd smwc-web
cp settings.env.example settings.env

mkdir -p \
    /data/docker/smwc-web/bin \
    /data/docker/smwc-web/tmp \
    /data/docker/smwc-web/roms \
    /data/docker/smwc-web/media \
    /data/docker/smwc-web/static
chown 1000:1000 -R /data/docker/smwc-web

docker compose up --build -d --remove-orphans
docker compose logs -f
```

*Note: Make sure to update the `settings.env` with the necessary details...*

### Copying This Project

Use the Fork button, or to clone a clean copy of this project into your repository:

```
git clone https://git.cssnr.com/shane/smwc-web.git
cd smwc-web
rm -rf .git
git init
git remote add origin https://github.com/your-org/your-repo.git
git push -u origin master
```

*Note: make sure to replace `your-org/your-repo.git` with your actual repository location...*
