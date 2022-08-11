"""
config

Returns:
    ASIC_USERNAME: User Login API
    ASIC_PASSWD: User Passwd API
"""
import sys
from os import getenv

SQLITE3_DB_PATH = "local_db.db"

def open_secrets(env_var: str) -> str:
    """ Open Secrets file """
    path_to_file=getenv(env_var)
    if path_to_file is None:
        sys.exit(1)
    with open(path_to_file, encoding="utf-8") as file:
        secret_string = [word.strip() for word in file]
        return ''.join(secret_string)

ASIC_USERNAME = open_secrets('ASIC_USERNAME_FILE')
ASIC_PASSWD   = open_secrets('ASIC_PASSWD_FILE')
