from slowapi import Limiter
from slowapi.util import get_remote_address

# The limiter is initialised here and imported into main.py and routers.
# get_remote_address uses the client's IP as the default key for guest users.
# For authenticated users, the router overrides the key with the user's ID.

limiter = Limiter(key_func=get_remote_address)