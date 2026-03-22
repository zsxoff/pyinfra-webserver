from pathlib import Path

from pyinfra.operations import apt, files, server, systemd


STATIC_FILES = Path(".") / "static"

APT_CACHE_TIME = 3600

# Locales

server.locale(
    name="Locales - Ensure en_US.UTF-8 locale is present",
    locale="en_US.UTF-8",
    _sudo=True,
)

server.locale(
    name="Locales - Ensure ru_RU.UTF-8 locale is present",
    locale="ru_RU.UTF-8",
    _sudo=True,
)

# Timezone

server.timezone(
    name="Timezone - Set the timezone to UTC",
    timezone="UTC",
    _sudo=True,
)

# SSH

files.put(
    name="Files - Put OpenSSH server daemon config",
    src=(STATIC_FILES / "sshd_config").as_posix(),
    dest="/etc/ssh/sshd_config",
    user="root",
    group="root",
    mode="644",
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
    name="UFW - Allow 443/TCP",
    commands=["ufw allow 443/tcp"],
    _sudo=True,
)

server.shell(
    name="UFW - Allow 443/UDP",
    commands=["ufw allow 443/udp"],
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

# Sysctl

server.sysctl(
    name="sysctl - Set net.ipv4.icmp_echo_ignore_all",
    key="net.ipv4.icmp_echo_ignore_all",
    value=1,
    persist=True,
    _sudo=True,
)
