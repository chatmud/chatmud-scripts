# ChatMUD Scripts

This repository contains various scripts used in the production environment for ChatMUD. ChatCore may or may not rely on these files for things such as:

- Running backups
- Curl requests
- Identifying total connections since start

## Directory Layout

- Executables: Files executed by a MOO with the `exec()` builtin.
- Maintenance: Scripts designed for ongoing maintenance of a MOO, including routine backups for the MOO database/SQLite and a restart script.
- Misc: Convenience scripts developed along the way that have no other home

## Contributing

Unfortunaetly, contributions to these scripts beyond critical security exploits or bugs will not be accepted. Please consider forking the repository and adding your own changes.

## Reporting Bugs

If you've identified a bug or security exploit with any of these scripts, please responsibly disclose it by emailing [mailto:opensource@chatmud.com](opensource@chatmud.com). If the bug is of a non-urgent matter, open an issue in this repository.