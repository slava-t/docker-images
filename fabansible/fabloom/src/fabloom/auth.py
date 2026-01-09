import os
import json
import itertools
from getpass import getpass
from socket import gaierror
from typing import Generator, List, Dict

from fabric import Connection, Config

from invoke import Responder

from paramiko.ssh_exception import (
  AuthenticationException,
  NoValidConnectionsError,
  SSHException
)

class Tracker:
  def __init__(self):
    self.msg_map = {}

  def track(self, id, msg=None):
    if id is None:
      return
    if self.msg_map.get(id) is None:
      self.msg_map[id] = []
    self.msg_map[id].append(id)

  def get(self, id):
    return self.msg_map.get(id)

  def reset(self):
    self.msg_map = {}

class TrackedResponder(Responder):
  def __init__(self, pattern: str, response: str, id: str, tracker):
    super().__init__(pattern, response)
    self.id = id
    self.tracker = tracker

  def submit(self, stream: str) -> Generator[str, None, None]:
    result = iter(super().submit(stream))
    try:
      first_item = next(result)
      self.tracker.track(self.id)
      for item in itertools.chain([first_item], result):
        yield item
    except StopIteration:
      return

class Watchers:
  def __init__(self, responders: List[Dict[str, str]]):
    self.tracker = Tracker()
    self.responders = []
    for r in responders:
      id = r.get('id')
      if id is None:
        self.responders.append(Responder(r['pattern'], r['response']))
      else:
        self.responders.append(TrackedResponder(
          r['pattern'],
          r['response'],
          id,
          self.tracker
        ))

  def watchers(self):
    return list(self.responders)

  def reset(self):
    self.tracker.reset()

  def submissions(self, id):
    return self.tracker.get(id)

  def submitted(self, id):
    submissions = self.submissions(id)
    if submissions is None or len(submissions) < 1:
      return False
    return True

def enter_password_responses(password):
  return [{
      'pattern': 'Vault password: ',
      'response': '{}\n'.format(password)
    }, {
      'pattern': 'SSH password: ',
      'response': '{}\n'.format(password)
    }, {
      'pattern': 'BECOME password.*:',
      'response': '{}\n'.format(password)
    }, {
      'pattern': 'Enter passphrase for key.*:',
      'response': '{}\n'.format(password)
    }, {
      'pattern': 'Enter passphrase: ',
      'response': '{}\n'.format(password)
  }]

def change_password_responses(current_password, new_password):
  return [{
    'id': 'current',
    'pattern': 'Current password: ',
    'response': '{}\n'.format(current_password)
  }, {
    'id': 'current',
    'pattern': '(current) UNIX password: ',
    'response': '{}\n'.format(current_password)
  }, {
    'id': 'new',
    'pattern': 'New password: ',
    'response': '{}\n'.format(new_password)
  }, {
    'id': 'new',
    'pattern': 'Enter new UNIX password: ',
    'response': '{}\n'.format(new_password)
  }, {
    'id': 'retype',
    'pattern': 'Retype new password: ',
    'response': '{}\n'.format(new_password)
  }, {
    'id': 'retype',
    'pattern': 'Retype new UNIX password: ',
    'response': '{}\n'.format(new_password)
  }]

def try_root_auth(host, port, password):
  user = 'root'
  root_password = getpass(prompt='Root password:')
  run_watchers = Watchers(
    enter_password_responses(root_password) +
    change_password_responses(root_password, password)
  )
  connect_kwargs = {
    'password': root_password,
    'look_for_keys': False,
    'allow_agent': False
  }
  try:
    with Connection(
      host,
      user=user,
      port=int(port),
      connect_kwargs=connect_kwargs,
    ) as c:
      c.run(
        'echo "Trying root password login"',
        pty=True,
        watchers=run_watchers.watchers()
      )
  except AuthenticationException as e:
    return {
      'success': False,
      'error': 'Root password authentication failed'
    }
  except NoValidConnectionsError as e:
    return {
      'success': False,
      'error': 'Could not connect to {}:{}. Error: {}'.format(host, port, e)
    }
  except gaierror as e:
    return {
      'success': False,
      'error': 'Could not resolve the host \'{}\'. Error: {}'.format(host, e)
    }
  except Exception as e:
    return {
      'success': False,
      'error': (
        'An exception has been raised in the first root authentication step. '
        'Exception: {} {}'
      ).format(type(e), e)
    }
  try:
    with Connection(
      host,
      user=user,
      port=int(port),
      connect_kwargs=connect_kwargs,
    ) as c:
      c.run(
        'passwd',
        pty=True,
        watchers=run_watchers.watchers()
      )
  except AuthenticationException as e:
    #it means that the password has been changed in the previous step
    pass
  except Exception as e:
    return {
      'success': False,
      'error': (
        'An exception has been raised in the second root authentication step. '
        'Error: {}'
      ).format(e)
    }
  return {
    'success': True
  }

def try_connect(user, host, port, password, key_filename):
  print('Trying to ssh {}@{} -p {}'.format(user, host, port))
  is_root = user == 'root'
  pass_auth = not key_filename
  pubkey_auth = not pass_auth
  root_auth = is_root and pass_auth
  ssh_no_pubkey_auth = '' if pubkey_auth else '-o PubkeyAuthentication=no '

  ssh_extra_args = ''
  if ssh_no_pubkey_auth:
    ssh_extra_args += ssh_no_pubkey_auth

  if ssh_extra_args:
    ssh_extra_args = '--ssh-extra-args="{}" '.format(ssh_extra_args)

  ask_password_arg = '' if key_filename else '-k '
  become_arg = '' if is_root else '-K '
  private_key_arg = '' if not key_filename else '--private-key \'{}\' '.format(
    key_filename
  )
  ansible_args = '-u {} {}{}{}{}'.format(
    user,
    ssh_extra_args,
    ask_password_arg,
    become_arg,
    private_key_arg
  )
  watchers = Watchers(
    enter_password_responses(password)
  )
  run_watchers = Watchers([])
  connect_kwargs = {
    'password': password,
    'look_for_keys': False,
    'allow_agent': False
  }
  if root_auth:
    result = try_root_auth(host, port, password)
    if not result.get('success'):
      return {
        'success': False,
        'error': 'Trying root authentication failed. Error: {}'.format(
          result.get('error')
        )
      }
  if key_filename:
    connect_kwargs = {
      'key_filename': key_filename,
      'passphrase': password,
      'look_for_keys': False,
      'allow_agent': False
    }

  config = {}

  if not is_root:
    config['sudo'] = {
      'password': password
    }
  test_command = (
    'bash -c \''
    'set -eu;'
    '. /etc/os-release; '
    'echo "{ \\"id\\": \\"$ID\\", \\"version\\": \\"$VERSION_ID\\" }"'
    '\''
  )
  error_msg = 'Unknown error'
  fatal = True
  try:
    with Connection(
      host,
      user=user,
      port=int(port),
      connect_kwargs=connect_kwargs,
      config=Config(overrides=config)
    ) as c:
      result = c.run(
        test_command,
        watchers=run_watchers.watchers()
      ) if is_root else c.sudo(test_command)
      if not result.ok:
        return {
          'success': False,
          'error': 'Command [{}] exited with code {}'.format(
            test_command,
            result.return_code
          ),
          'stdout': result.stdout,
          'stderr': result.stderr
        }
      os_info = json.loads(result.stdout)
      return {
        'success': True,
        'os': os_info,
        'host': host,
        'user': user,
        'port': port,
        'ansible_args': ansible_args,
        'watchers': watchers.watchers()
      }
  except AuthenticationException as e:
    fatal = False
    error_msg = (
      'Authentication of user \'{}\' to host \'{}\' with port {} '
      'using {} authentication  failed'
    ).format(user, host, port, 'public key' if pubkey_auth else 'password')
  except SSHException as e:
    if e.args[0] == 'encountered RSA key, expected OPENSSH key':
      fatal = False
      error_msg = (
        'Authentication of user \'{}\' to host \'{}\' with port {} '
        'using {} authentication failed'
      ).format(user, host, port, 'public key' if pubkey_auth else 'password')
    else:
      error_msg = 'An SSH exception has been raised. Exception: {}'.format(e)
  except NoValidConnectionsError as e:
    error_msg = 'Could not connect to {}:{}. Error: {}'.format(host, port, e)
  except gaierror as e:
    error_msg = 'Could not resolve the host \'{}\'. Error: {}'.format(host, e)
  except Exception as e:
    error_msg = 'An exception has been raised. Exception:{} {}'.format(
      type(e),
      e
    )
  return {
    'success': False,
    'error': error_msg,
    'fatal': fatal
  }

def verify_key_password(ctx, key_path, password):
  command = 'ssh-keygen -y -f "{}"'.format(key_path)
  watchers = Watchers(enter_password_responses(password))
  result = ctx.run(
    command,
    watchers=watchers.watchers(),
    hide=True,
    warn=True,
    pty=True
  )
  return result.return_code == 0

def find_connectable(user, fallback_user, host, port, password, key_path):
  print('Testing if user \'{}\' is connectable with public key'.format(user))
  result = try_connect(user, host, port, password, key_path)
  if not result.get('success'):
    if result.get('fatal'):
      print(
        (
          'Fatal error while testing if user \'{}\' is '
          'connectable with public key. Error: {}'
        ).format(user, result.get('error'))
      )
      raise SystemExit(1)
    print(
      (
        'Testing if user \'{}\' is '
        'connectable with the provided password'
      ).format(user)
    )
    result = try_connect(user, host, port, password, None)
  if not result.get('success'):
    if result.get('fatal'):
      print(
        (
          'Fatal error while testing if user \'{}\' is '
          'connectable with the provided password. Error: {}'
        ).format(user, result.get('error'))
      )
      raise SystemExit(1)
    print(
      (
        'Testing if fallback user \'{}\' is '
        'connectable with the public key'
      ).format(fallback_user)
    )
    result = try_connect(
      fallback_user,
      host,
      port,
      password,
      key_path
    )
  if not result.get('success'):
    if result.get('fatal'):
      print(
        (
          'Fatal error while testing if user \'{}\' is '
          'connectable with the public key. Error: {}'
        ).format(fallback_user, result.get('error'))
      )
      raise SystemExit(1)
    print(
      (
        'Testing if fallback user \'{}\' is '
        'connectable with the provided password'
      ).format(fallback_user)
    )
    result = try_connect(
      fallback_user,
      host,
      port,
      password,
      None
    )
  if not result.get('success'):
    if result.get('fatal'):
      print(
        (
          'Fatal error while testing if user \'{}\' is '
          'connectable with the provided password. Error: {}'
        ).format(fallback_user, result.get('error'))
      )
      raise SystemExit(1)
    print('All connection tries failed')
    raise SystemExit(1)
  return result

def get_key_password(ctx, ret_pass, private_key_file):
  if ret_pass is not None:
    return ret_pass
  if not os.path.exists(private_key_file):
    print('The ssh private key file \'{}\' doesn\'t exist.'.format(
      private_key_file
    ))
    raise SystemExit(1)
  os.chmod(private_key_file, 0o600)
  if private_key_file is None:
    print('No private key provided')
    raise SystemExit(1)
  head, tail = os.path.split(private_key_file)
  keyname = tail or os.path.basename(head)
  password = getpass(prompt='Password for {}:'.format(keyname))
  while not verify_key_password(ctx, private_key_file, password):
    print('Incorrect password')
    password = getpass(prompt='Password for {}:'.format(keyname))
  return password

