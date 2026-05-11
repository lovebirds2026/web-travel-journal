import pytest
import uuid
from redis import Redis

from instance.config import Config

# can be skipped with pytest -m "not integration"
@pytest.mark.integration
@pytest.mark.skipif(not hasattr(Config, 'REDIS_PORT'), reason='No Redis setup detected')
def test_redis():
    redis_client = Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )
    assert redis_client.ping()

    test_key = str(uuid.uuid4()) # ~ c303282d-f2e6-46ca-a04a-35d3d873712d

    try:
        redis_client.set(test_key, 'YES, Redis works.') # hset(str, mapping={}) , hgetall
        redis_client.expire(test_key, 5)
        assert redis_client.get(test_key) == 'YES, Redis works.'
    finally:
        redis_client.delete(test_key)
        redis_client.close()