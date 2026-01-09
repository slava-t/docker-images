def verify_ssh(ctx, host, port):
  command = 'ssh-keyscan -p {} "{}"'.format(port, host)
  result = ctx.run(
    command,
    hide=True,
    warn=True,
    pty=True
  )
  return result.return_code == 0

def choose_ssh_port(ctx, host, port, fallback_port):
  if verify_ssh(ctx, host, port):
    return port
  elif verify_ssh(ctx, host, fallback_port):
    return fallback_port
  return None

