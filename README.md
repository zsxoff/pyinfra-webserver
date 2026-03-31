# Web server with pyinfra

## What's inside

| File                               | Description           |
| :--------------------------------- | :-------------------- |
| [./src/deploy.py](./src/deploy.py) | Setup base web server |

## Prerequisites

### In your device

Generate SSH key for running pyinfra commands:

```bash
ssh-keygen -t ed25519 -a 200 -C "infra" -f ~/.ssh/infra
```

### In your server

Create `infra` user with `sudo` capabilities:

```bash
sudo useradd -m -s /bin/bash -G sudo -U infra && sudo passwd infra
```

Add SSH key from your device to `authorized_keys` for `infra` user:

```bash
ssh-copy-id infra@<IP>
```

or edit file manually:

```bash
sudo -u infra mkdir -p -m 700 -v /home/infra/.ssh/
```

```bash
echo "<publickey>" | sudo -u infra tee -a "/home/infra/.ssh/authorized_keys"
```

```bash
sudo chmod 600 authorized_keys /home/infra/.ssh/authorized_keys
```

Change OpenSSH server daemon config in `/etc/ssh/sshd_config`:

```text
AllowUsers admin main infra
AuthenticationMethods publickey
PermitRootLogin no
PasswordAuthentication no

# Supported HostKey algorithms by order of preference
HostKey /etc/ssh/ssh_host_ed25519_key

# SSH File Transfer Protocol
Subsystem sftp /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO
```

Reload OpenSSH server daemon:

```bash
sudo systemctl restart sshd.service
```

## How to deploy this

### On local machine

```bash
pyinfra @local ./src/deploy.py
```

### On remote machine

```bash
pyinfra --ssh-user infra --ssh-key ~/.ssh/id_ed25519 192.168.0.100 ./src/deploy.py
```

### On many remote machines

Copy `inventory.py.example` to `inventory.py`, setup your hosts like official [Create a Deploy](https://docs.pyinfra.com/en/3.x/getting-started.html#create-a-deploy) docs and run:

```bash
pyinfra --ssh-user infra --ssh-key ~/.ssh/id_ed25519 inventory.py ./src/deploy.py
```

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)

This project is licensed under the terms of the [MIT](https://opensource.org/licenses/MIT) license (see [LICENSE](https://github.com/zsxoff/pyinfra-webserver/blob/main/LICENSE) file).
