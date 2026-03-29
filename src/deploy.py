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
        "fail2ban",
        "locales",
        "logrotate",
        "openssh-server",
        "ufw",
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

server.shell(
    name="UFW - Configure firewall rules in one shot",
    commands=[
        "ufw reset",
        "ufw allow ssh",
        "ufw allow 443/tcp",
        "ufw allow 443/udp",
        "ufw default deny incoming",
        "ufw default allow outgoing",
        "ufw logging on",
        "ufw --force enable",
    ],
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

systemd.service(
    name="Systemd - Enable Fail2ban",
    service="fail2ban.service",
    running=True,
    enabled=True,
    _sudo=True,
)

# TODO(zsxoff): Copy /etc/fail2ban/jail.conf to jail.local.

# Logrotate

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
