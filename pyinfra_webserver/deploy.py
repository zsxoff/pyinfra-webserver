from pathlib import Path

from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, server, systemd


STATIC_FILES = Path(".") / "static"
APT_CACHE_TIME = 3600
ROOT_USER = "root"
ROOT_GROUP = "root"
ROOT_FILES_DEFAULT_MODE = "644"


@deploy("Setup locales")
def setup_locales() -> None:
    server.locale(name="Locale - Ensure en_US.UTF-8 locale is present", locale="en_US.UTF-8", _sudo=True)
    server.locale(name="Locale - Ensure ru_RU.UTF-8 locale is present", locale="ru_RU.UTF-8", _sudo=True)


@deploy("Setup timezone")
def setup_timezone() -> None:
    server.timezone(name="Timezone - Set the timezone to UTC", timezone="UTC", _sudo=True)


@deploy("Setup SSH daemon (sshd)")
def setup_sshd() -> None:
    files.put(
        name="Files - Put OpenSSH server daemon config",
        src=(STATIC_FILES / "sshd_config").as_posix(),
        dest="/etc/ssh/sshd_config",
        user=ROOT_USER,
        group=ROOT_GROUP,
        mode=ROOT_FILES_DEFAULT_MODE,
        _sudo=True,
    )


@deploy("Install packages")
def install_packages() -> None:
    apt.packages(
        name="APT - Install base system packages",
        packages=[
            "apt-listchanges",
            "auditd",
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


@deploy("Setup auto upgrades")
def setup_auto_upgrades() -> None:
    files.put(
        name="Files - Put APT periodic config",
        src=(STATIC_FILES / "20auto-upgrades").as_posix(),
        dest="/etc/apt/apt.conf.d/20auto-upgrades",
        user=ROOT_USER,
        group=ROOT_GROUP,
        mode=ROOT_FILES_DEFAULT_MODE,
        _sudo=True,
    )
    files.put(
        name="Files - Put unattended-upgrades config",
        src=(STATIC_FILES / "50unattended-upgrades").as_posix(),
        dest="/etc/apt/apt.conf.d/50unattended-upgrades",
        user=ROOT_USER,
        group=ROOT_GROUP,
        mode=ROOT_FILES_DEFAULT_MODE,
        _sudo=True,
    )


@deploy("Setup Auditd")
def setup_auditd() -> None:
    files.put(
        name="Files - Put auditd rules",
        src=(STATIC_FILES / "audit.rules").as_posix(),
        dest="/etc/audit/rules.d/audit.rules",
        user=ROOT_USER,
        group=ROOT_GROUP,
        mode=ROOT_FILES_DEFAULT_MODE,
        _sudo=True,
    )
    server.shell(
        name="Auditd - Reload audit rules",
        commands=[
            "auditctl -R /etc/audit/rules.d/audit.rules",
        ],
        _sudo=True,
    )
    systemd.service(
        name="Systemd - Enable Auditd",
        service="auditd.service",
        running=True,
        enabled=True,
        _sudo=True,
    )


@deploy("Setup nftables")
def setup_nftables() -> None:
    server.shell(
        name="nftables - Configure rules",
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
        name="nftables - Save rules",
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


@deploy("Setup Fail2ban")
def setup_fail2ban() -> None:
    systemd.service(
        name="Systemd - Enable Fail2ban",
        service="fail2ban.service",
        running=True,
        enabled=True,
        _sudo=True,
    )
    files.put(
        name="Files - Put Fail2ban jail.local config",
        src=(STATIC_FILES / "jail.local").as_posix(),
        dest="/etc/fail2ban/jail.local",
        user=ROOT_USER,
        group=ROOT_GROUP,
        mode=ROOT_FILES_DEFAULT_MODE,
        _sudo=True,
    )
    systemd.service(
        name="Systemd - Restart Fail2Ban after config change",
        service="fail2ban",
        running=True,
        enabled=True,
        _sudo=True,
    )


@deploy("Setup Logrotate")
def setup_logrotate() -> None:
    systemd.service(
        name="Systemd - Enable Logrotate",
        service="logrotate.timer",
        running=True,
        enabled=True,
        _sudo=True,
    )


@deploy("Setup sysctl")
def setup_sysctl() -> None:
    hardening_sysctls = [
        ("net.ipv4.ip_forward", 0),
        ("net.ipv4.conf.all.send_redirects", 0),
        ("net.ipv4.conf.all.accept_source_route", 0),
        ("net.ipv4.tcp_syncookies", 1),
        ("net.ipv4.icmp_echo_ignore_all", 1),
    ]
    for sysctl_key, sysctl_value in hardening_sysctls:
        server.sysctl(
            name=f"sysctl - Set {sysctl_key}",
            key=sysctl_key,
            value=sysctl_value,
            persist=True,
            _sudo=True,
        )


def deploy_server():
    tools = [
        install_packages,
        setup_locales,
        setup_timezone,
        setup_sshd,
        setup_auto_upgrades,
        setup_auditd,
        setup_nftables,
        setup_fail2ban,
        setup_logrotate,
        setup_sysctl,
    ]

    for tool in tools:
        tool()
