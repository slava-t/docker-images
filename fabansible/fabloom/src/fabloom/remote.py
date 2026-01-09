from fabric import Connection, Config

from fabloom.auth import (
  get_key_password
)

def run(
  ctx,
  fn,
  user,
  host,
  port,
  key_path,
  password=None,
  **kwargs
):
  password = get_key_password(ctx, password, key_path)
  config = Config(overrides={
    'sudo': {
      'password': password
    }
  })
  with Connection(
    host,
    user=user,
    port=int(port),
    connect_kwargs={
      'key_filename': key_path,
      'passphrase': password
    },
    config=config
  ) as rctx:
    return fn(rctx, ctx, password=password, **kwargs)
