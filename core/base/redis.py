import redis


class RedisClient:
    """
    Singleton class for managing a Redis connection.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """ """

        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self, host="localhost", port=6379, db=0):
        """
        Initialize Redis connection if not already initialized.
        """

        if not self._initialized:
            self._initialized = True
            self.connection = redis.StrictRedis(
                host=host, port=port, db=db, decode_responses=True
            )

    def get_connection(self):
        """
        Returns the Redis connection instance.
        """

        return self.connection

    def z_add(self, key: str, mapping: dict) -> int:
        """
        Adds one or more members to a sorted set or updates its score if it exists.
        """

        return self.connection.zadd(key, mapping)

    def z_range_by_score(self, key: str, min_score: int, max_score: int) -> list:
        """
        Retrieves members in a sorted set by score range.
        """

        return self.connection.zrangebyscore(key, min_score, max_score)

    def z_rem(self, key: str, member: str) -> int:
        """
        Removes a member from a sorted set.
        """

        return self.connection.zrem(key, member)
