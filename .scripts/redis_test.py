import redis

redis_client = redis.Redis(host='localhost', port=13706, decode_responses=True)

redis_client.set('test', 'YES, Redis works.') # hset(str, mapping={}) , hgetall
redis_client.expire('test', 5)

result = redis_client.get('test')
print(result or 'expired')

redis_client.close()