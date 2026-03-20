from pyinfra.operations import apt, server


APT_CACHE_TIME = 3600

# Locales

server.shell(
    name="Locales - Allow and generate only en_US and ru_RU locales",
    commands=[
        "echo 'en_US.UTF-8 UTF-8\nru_RU.UTF-8 UTF-8' > /etc/locale.gen",
        "locale-gen",
    ],
    _sudo=True,
)

# System packages

apt.packages(
    name="System packages - Install base packages",
    packages=[
        "apt-listchanges",
        "ca-certificates",
        "debsums",
        "locales",
        "unattended-upgrades",
    ],
    latest=True,
    no_recommends=True,
    present=True,
    update=True,
    cache_time=APT_CACHE_TIME,
    _sudo=True,
)
