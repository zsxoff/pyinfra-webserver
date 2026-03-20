from pyinfra.operations import apt, server, systemd


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
    name="APT - Install base system packages",
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

# UFW

apt.packages(
    name="APT - Install UFW",
    packages=["ufw"],
    latest=True,
    no_recommends=True,
    present=True,
    update=True,
    cache_time=APT_CACHE_TIME,
    _sudo=True,
)

server.shell(
    name="UFW - Allow SSH",
    commands=["ufw allow ssh"],
    _sudo=True,
)

server.shell(
    name="UFW - Default deny incoming",
    commands=["ufw default deny incoming"],
    _sudo=True,
)

server.shell(
    name="UFW - Default allow outgoing",
    commands=["ufw default allow outgoing"],
    _sudo=True,
)

server.shell(
    name="UFW - Force enable",
    commands=["ufw --force enable"],
    _sudo=True,
)

systemd.service(
    name="Systemd - Enable UFW",
    service="ufw.service",
    running=True,
    enabled=True,
    _sudo=True,
)

# Fail2ban

apt.packages(
    name="APT - Install Fail2ban",
    packages=["fail2ban"],
    latest=True,
    no_recommends=True,
    present=True,
    update=True,
    cache_time=APT_CACHE_TIME,
    _sudo=True,
)

systemd.service(
    name="Systemd - Enable Fail2ban",
    service="fail2ban.service",
    running=True,
    enabled=True,
    _sudo=True,
)

# TODO(zsxoff): Copy /etc/fail2ban/jail.conf to jail.local.

# Logrotate

apt.packages(
    name="APT - Install Logrotate",
    packages=["logrotate"],
    latest=True,
    no_recommends=True,
    present=True,
    update=True,
    cache_time=APT_CACHE_TIME,
    _sudo=True,
)

systemd.service(
    name="Systemd - Enable Logrotate",
    service="logrotate.timer",
    running=True,
    enabled=True,
    _sudo=True,
)
