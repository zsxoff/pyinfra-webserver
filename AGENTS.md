# Web server with pyinfra Coding Rules

## Linux server rules

### Server Linux distribution

- The server has a Debian Linux or Ubuntu Linux distribution installed

### Server account for applying commands via pyinfra

- Account name: `infra`
- This account is a service account
- This account was created by the command `sudo useradd -m -s /bin/bash -G sudo -c "Service account for pyinfra" -U infra`
- This account has disabled password by command `sudo passwd -l infra`
- This account has `sudo` privileges
- This account is used for the pyinfra Python framework
- This account cannot be used for password-based login, SSH key login is required
- This account is already allowed in OpenSSH server daemon config for login as `AllowUsers infra`

### Server firewall

- This server uses ufw as a firewall
