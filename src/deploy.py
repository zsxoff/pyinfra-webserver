from pathlib import Path

from pyinfra.operations import apt, files, server, systemd


STATIC_FILES = Path(".") / "static"

APT_CACHE_TIME = 3600
ROOT_USER = "root"
ROOT_GROUP = "root"

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
    user=ROOT_USER,
    group=ROOT_GROUP,
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
        "nftables",
        "openssh-server",
        "unattended-upgrades",
    ],
    latest=True,
    no_recommends=True,
    present=True,
    update=True,
    cache_time=APT_CACHE_TIME,
    _sudo=True,
)

# Firewall

server.shell(
    name="Firewall - Configure nftables rules",
    commands=[
        "nft delete table inet filter 2>/dev/null || true",
        "nft add table inet filter",
        "nft add chain inet filter input '{type filter hook input priority 0;}'",
        "nft add chain inet filter forward '{type filter hook forward priority 0;}'",
        "nft add chain inet filter output '{type filter hook output priority 0;}'",
        "nft add rule inet filter input ct state established,related accept",
        "nft add rule inet filter input iif lo accept",
        "nft add rule inet filter input tcp dport 22 accept",
        "nft add rule inet filter input tcp dport 443 accept",
        "nft add rule inet filter input udp dport 443 accept",
        "nft chain inet filter input '{policy drop;}'",
        "nft chain inet filter forward '{policy drop;}'",
        "nft chain inet filter output '{policy accept;}'",
    ],
    _sudo=True,
)

server.shell(
    name="Firewall - Save nftables rules",
    commands=[
        "nft list ruleset > /etc/nftables.conf",
    ],
    _sudo=True,
)

systemd.service(
    name="Systemd - Enable nftables",
    service="nftables.service",
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

files.put(
    name="Files - Put fail2ban jail.local config",
    src=(STATIC_FILES / "jail.local").as_posix(),
    dest="/etc/fail2ban/jail.local",
    user=ROOT_USER,
    group=ROOT_GROUP,
    mode="644",
    _sudo=True,
)

systemd.service(
    name="Systemd - Restart Fail2Ban after config change",
    service="fail2ban",
    running=True,
    enabled=True,
    _sudo=True,
)

# Logrotate

systemd.service(
    name="Systemd - Enable Logrotate",
    service="logrotate.timer",
    running=True,
    enabled=True,
    _sudo=True,
)

# Sysctl

hardening_sysctls = [
    ("net.ipv4.ip_forward", 0),
    ("net.ipv4.conf.all.send_redirects", 0),
    ("net.ipv4.conf.all.accept_source_route", 0),
    ("net.ipv4.tcp_syncookies", 1),
    ("net.ipv4.icmp_echo_ignore_all", 1),
]

for sysctl_key, sysctl_value in hardening_sysctls:  # noqa: WPS481
    server.sysctl(
        name=f"sysctl - Set {sysctl_key}",
        key=sysctl_key,
        value=sysctl_value,
        persist=True,
        _sudo=True,
    )
