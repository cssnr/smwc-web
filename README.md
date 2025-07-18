[![CI](https://img.shields.io/github/actions/workflow/status/cssnr/smwc-web/ci.yaml?logo=github&label=ci)](https://github.com/cssnr/smwc-web/actions/workflows/ci.yaml)
[![Lint](https://img.shields.io/github/actions/workflow/status/cssnr/smwc-web/lint.yaml?logo=github&label=lint)](https://github.com/cssnr/smwc-web/actions/workflows/lint.yaml)
[![Codecov](https://codecov.io/gh/cssnr/smwc-web/graph/badge.svg?token=6YSWJ1E6BJ)](https://codecov.io/gh/cssnr/smwc-web)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/cssnr/smwc-web?logo=github&label=updated)](https://github.com/cssnr/smwc-web/graphs/commit-activity)
[![GitHub Top Language](https://img.shields.io/github/languages/top/cssnr/smwc-web?logo=htmx&logoColor=white)](https://github.com/cssnr/smwc-web)
[![GitHub Org Stars](https://img.shields.io/github/stars/cssnr?style=flat&logo=github&label=org%20stars)](https://cssnr.github.io/)
[![Discord](https://img.shields.io/discord/899171661457293343?logo=discord&logoColor=white&label=cssnr%20discord&color=7289da)](https://discord.gg/wXy6m2X8wY)
[![Discord](https://img.shields.io/discord/111645911091814400?logo=discord&logoColor=white&label=smwc%20discord&color=7289da)](https://discord.gg/ZrRbfdE6kz)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-72a5f2?logo=kofi&label=support)](https://ko-fi.com/cssnr)
[![](https://repository-images.githubusercontent.com/443952841/5d9d45ca-7bf2-4773-969e-302f2ecd6903)](https://smwc.world/)

# SMW Central ROM Archive

This tool downloads all Super Mario World ROM's that are uploaded to www.smwcentral.net in the awaiting moderation section and archives them for download.

> [!TIP]  
> You can now Patch and Play ROM's Online with the click of a button using the SMWC Web Extension!  
> Download from: [Google](https://chromewebstore.google.com/detail/smwc-web-extension/foalfafgmnglcgpgkhhmcfhjgmdcjide) | [Mozilla](https://addons.mozilla.org/addon/smwc-web-extension) | [GitHub](https://github.com/cssnr/smwc-web-extension)

## Development

### Deployment

> [!WARNING]  
> These docs are out-of-date but serve as a general guide.

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

_Note: Make sure to update the `settings.env` with the necessary details..._

# Contributing

Please consider making a donation to support the development of this project
and [additional](https://cssnr.com/) open source projects.

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cssnr)

For a full list of current projects visit: [https://cssnr.github.io/](https://cssnr.github.io/)
