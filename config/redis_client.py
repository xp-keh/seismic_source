import redis
from dotenv import load_dotenv
from config.utils import get_env_value

load_dotenv()

REDIS_HOST = get_env_value('REDIS_HOST')
REDIS_PORT = get_env_value('REDIS_PORT')

class RedisSingleton:
    _instance = None

    def __new__(cls, db=0):
        if cls._instance is None:
            cls._instance = super(RedisSingleton, cls).__new__(cls)
            cls._instance.r = redis.Redis( # type: ignore
                host=REDIS_HOST, # type: ignore
                port=int(REDIS_PORT), # type: ignore
                db=db,
                decode_responses=True,
            )
        return cls._instance
