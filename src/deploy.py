from pyinfra.operations import apt, server


# Locales

server.shell(
    name="Locales - Allow and generate only en_US and ru_RU locales",
    commands=[
        "echo -e 'en_US.UTF-8 UTF-8\nru_RU.UTF-8 UTF-8' > /etc/locale.gen",
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
    _sudo=True,
)
