import crypt

from socket import gethostbyname

from fabloom.auth import (
  get_key_password,
  find_connectable,
  try_connect
)

FABLIB_DIR='/fablib'
PLAYBOOK_DIR=FABLIB_DIR
INITIAL_PLAYBOOK='{}/initial.playbook.yaml'.format(PLAYBOOK_DIR)

def create_playbook_command(running_details, playbook_path, vars):
  var_args = ''
  for var_name in list((vars or {}).keys()):
    if var_args:
      var_args += ' '
    var_args += '-e \'{}={}\''.format(var_name, vars[var_name])
  playbook_command = (
    'ANSIBLE_HOST_KEY_CHECKING=False '
    'ansible-playbook -i \'{}:{},\' {} {} {}'
  ).format(
    running_details['host'],
    running_details['port'],
    running_details['ansible_args'],
    var_args,
    playbook_path
  )
  return playbook_command

def do_provision(
  ctx,
  user,
  fallback_user,
  host,
  port,
  private_key_file,
  **kwargs
):
  check_host_ip=kwargs.get('check_host_ip', False)
  vars = kwargs.get('vars', {})
  roles = kwargs.get('roles', [])
  password = get_key_password(ctx, kwargs.get('password'), private_key_file)
  running_details = find_connectable(
    user,
    fallback_user,
    host,
    port,
    password,
    private_key_file
  )

  shaddow_password = crypt.crypt(
    password, crypt.mksalt(crypt.METHOD_SHA512)
  )
  playbook_vars = {
    'ssh_user': user,
    'ssh_host': host,
    'ssh_port': port,
    'user_password': shaddow_password,
    'public_ssh_file': '{}.pub'.format(private_key_file),
  }
  playbook_vars.update(vars)
  if check_host_ip:
    playbook_vars['host_ip'] = gethostbyname(host)

  playbook_command = create_playbook_command(
    running_details,
    INITIAL_PLAYBOOK,
    playbook_vars
  )
  provision_result = ctx.run(
    playbook_command,
    watchers=running_details.get('watchers') or [],
    warn=True,
    pty=True
  )
  if provision_result.return_code == 0:
    print('Initial provisioning succeeded.')
  else:
    print('Initial provisioning failed. Return code: {}.'.format(
      provision_result.return_code
    ))
    raise SystemExit(1)
  running_details = try_connect(
    user,
    host,
    port,
    password,
    private_key_file
  )
  if not running_details.get('success'):
    print('Connecting after basic provisioning failed. Error: {}'.format(
      running_details.get('error')
    ))
    raise SystemExit(1)
  for role in roles:
    effective_vars = playbook_vars.copy()
    role_info = {}
    if isinstance(role, str):
      role_info['name'] = role
    else:
      role_info = role or {}
    rolename = role_info['name']
    if rolename is None:
      print('Invalid or missing role name')
      raise SystemExit(1)
    effective_vars.update(role_info.get('vars', {}))
    playbook = '{}/{}.playbook.yaml'.format(PLAYBOOK_DIR, rolename)
    playbook_command = create_playbook_command(
      running_details,
      playbook,
      effective_vars
    )
    provision_result = ctx.run(
      playbook_command,
      watchers=running_details.get('watchers') or [],
      warn=True,
      pty=True
    )
    if provision_result.return_code == 0:
      print(
        'Provisioning the \'{}\' role to host \'{}\' succeeded'.format(
          rolename,
          host
        )
      )
    else:
      print(
        'Provisioning the \'{}\' role to host \'{}\' failed'.format(
          rolename,
          host
        )
      )
      raise SystemExit(1)
