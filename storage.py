from datetime import datetime
import json
from pathlib import Path
from typing import TypedDict, Protocol
import sqlite3

from client_asic import AsicSystemInfo
import config

class AsicStorage(Protocol):
    """ Interface for any storage saving asic health """
    def save(self, health: AsicSystemInfo) -> None:
        raise NotImplementedError

class AsicSystemInfoRecord(TypedDict):
    """ Asic System Info Record """
    id: int
    ipaddress: str
    macaddr: str
    asictype: str

class SQLiteStorage:
    """ Store in SQLiteDB """
    def __init__(self, sqlitefiledb: Path):
        self._sqlitefiledb = sqlitefiledb
        self._init_storage()

    def save(self, weather: AsicSystemInfo) -> None:
        self._write(history)

    def _init_storage(self) -> None:
        if not self._sqlitefiledb.exists():
            _conn = sqlite3.connect(config.SQLITE3_DB_PATH)
            _cursor = _conn.cursor()
            _cursor.execute("CREATE TABLE IF NOT EXISTS asic (id INTEGER PRIMARY KEY AUTOINCREMENT, ipaddress VARCHAR, macaddr VARCHAR, asictype VARCHAR)")
            _conn.close()

    def _readAll(self) -> list[AsicSystemInfoRecord]:
        _conn = sqlite3.connect(config.SQLITE3_DB_PATH)
        _cursor = _conn.cursor()
        _list=[]
        for AsicSystemInfoRecord in _cursor.execute("SELECT id, ipaddress, macaddr, asictype FROM asic"):
            _list.append(AsicSystemInfoRecord)
        _conn.commit()
        return _list

    def _insert(self, items: list[HistoryRecord]) -> None:
        _conn = sqlite3.connect(config.SQLITE3_DB_PATH)
        _cursor = _conn.cursor()
        for item in items:
            _cursor.execute("INSERT INTO asic (ipaddress, macaddr, asictype) VALUES(?,?,?)", item.ipaddress, item.macaddr, item.asictype)
            _conn.commit()
        _conn.close()

    def _update(self, items: AsicSystemInfoRecord) -> None:
        _conn = sqlite3.connect(config.SQLITE3_DB_PATH)
        _cursor = _conn.cursor()
        for item in items:
            _cursor.execute("UPDATE asic SET ipaddress=?, macaddr=?, asictype=? WHERE id=?", item.ipaddress, item.macaddr, item.asictype, item.id)
            _conn.commit()
        _conn.close()

def save_asic(asic: AsicSystemInfo, storage: AsicStorage) -> None:
    """ Saves ASIC in the storage """
    storage.save(asic)
