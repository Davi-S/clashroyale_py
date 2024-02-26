import abc
import json
import sqlite3
from datetime import datetime, timedelta


class CacheStorage(abc.ABC):
    """
    Abstract base class for cache storage, defining the CRUD interface.

    Subclasses must implement the abstract methods to provide concrete
    implementations for different storage mechanisms.
    """
    @abc.abstractproperty
    def expiration_time(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, key: str, value: dict, timestamp: datetime) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, key: str) -> tuple[dict, datetime]:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, key: str, value: dict, timestamp: datetime) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, key) -> None:
        raise NotImplementedError


class SqliteCacheStorage(CacheStorage):
    """
    Cache storage implementation using SQLite3.
    """
    
    def __init__(self, db_path="cache.db", expiration_time_in_minutes: int = 1):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, timestamp FLOAT)"
        )
        self.connection.commit()
        self.expiration_time = timedelta(minutes=expiration_time_in_minutes)

    @property
    def expiration_time(self):
        """
        Returns the current expiration time for cached values.
        """
        return self._expiration_time

    @expiration_time.setter
    def expiration_time(self, value: timedelta):
        self._expiration_time = value

    def create(self, key: str, value: dict, timestamp: datetime) -> None:
        """
        Creates a new key-value pair in the cache.
        """
        value_json = json.dumps(value)
        self.cursor.execute(
            "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
            (key, value_json, timestamp.timestamp()),
        )
        self.connection.commit()

    def read(self, key: str) -> tuple[dict, datetime]:
        """
        Reads the value and timestamp associated with a key from the cache.
        """
        self.cursor.execute("SELECT value, timestamp FROM cache WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        if row:
            # Check for expiration
            if (datetime.fromtimestamp(row[1]) + self.expiration_time) > datetime.utcnow():  
                value = json.loads(row[0])
                timestamp = datetime.fromtimestamp(row[1])
                return value, timestamp
            else:
                # Delete expired value
                self.delete(key)  
                raise KeyError(f"Key '{key}' expired in cache")
        else:
            raise KeyError(f"Key '{key}' not found in cache")

    def update(self, key: str, value: dict, timestamp: datetime) -> None:
        """
        Updates the value and timestamp associated with a key in the cache.
        """
        value_json = json.dumps(value)
        self.cursor.execute(
            "UPDATE cache SET value = ?, timestamp = ? WHERE key = ?",
            (value_json, timestamp.timestamp(), key),
        )
        self.connection.commit()

    def delete(self, key: str) -> None:
        """
        Deletes the key-value pair from the cache.
        """
        self.cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        self.connection.commit()

    def clear(self) -> None:
        """
        Clears all cached data.
        """
        self.cursor.execute("DELETE FROM cache")
        self.connection.commit()

    def __del__(self):
        """
        Closes the database connection upon object deletion.
        """
        self.connection.close()