def get_service_to_deploy(yaml_path, service):
  service_name = ''
  if service != '--all':
    with open(yaml_path, 'r') as file:
      data = yaml.safe_load(file)
      services = data.get('services')
      if not isinstance(services, dict):
        print('There is no object named \'services\' in the yaml file \'{}\'.')
        raise SystemExit(1)
      if service not in services.keys():
        print(
          'There is no service named \'{}\' in the yaml file \'{}\'.'.format(
            service,
            yaml_path
          )
        )
        raise SystemExit(1)
      service_name = service
  return service_name

def dc_commands(service):
  up = 'docker compose up'
  down = 'docker compose down'
  if service:
    up += ' \'{}\''.format(service)
    down += ' \'{}\''.format(service)
  return {
    'up': up,
    'down': down
  }

def do_stop_service(remote, _unused_local, service=None, **_):
  dc = dc_commands(service)
  remote.run(
    (
      'bash -c \'if test -f ~/runner/docker-compose.yml; then '
      ' cd ~/runner && {}; fi\''
    ).format(dc.get('down')),
    hide=True,
    warn=True
  )

def do_restart_service(remote, local, service=None, **_):
  do_stop_service(remote, local, service=service)
  dc = dc_commands(service)
  remote.run(
    'bash -c \'cd ~/runner && {} -d --build\''.format(dc.get('up')),
    hide=True,
    warn=True
  )

def do_deploy_service(remote, local, service=None, **_):
  do_stop_service(remote, local, service=service)
  dc = dc_commands(service)
  local.run(
    'bash -c \'set -eu -o pipefail; '
    'cd /gitlab && rm -f /tmp/gitlab-runner.tar && '
    'tar -cf /tmp/gitlab-runner.tar runner\'',
    hide=True
  )
  remote.put('/tmp/gitlab-runner.tar', '/tmp/')
  local.run('rm -f /tmp/gitlab-runner.tar', hide=True)

  #rsync is used in order to make sure the directories
  #mapped as volumes in containers are not recreated
  remote.run(
    'bash -c \'cd /tmp && '
    'rm -rf runner && '
    'tar -xf gitlab-runner.tar && '
    'rsync -a --inplace --delete runner ~/ &&'
    'rm -rf runner && '
    'rm -f /tmp/gitlab-runner.tar\'',
    hide=True
  )
  remote.run(
    'bash -c \'cd ~/runner && {} -d --build\''.format(dc.get('up'))
  )

