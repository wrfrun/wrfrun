install_dir_path = py3.get_install_dir()

gen_init = custom_target(
  'generate_resource_init',
  input: 'generate_init.py',
  output: '__init__.py',
  command: [python3, '@INPUT@', '--output', '@OUTPUT@'],
  depend_files: files('generate_init.py'),
  install: true,
  install_dir: join_paths(install_dir_path, 'wrfrun', 'res')
)

py3.install_sources(
    [
        '__init__.py',
        'config.yaml.template',
        'run.sh.template',
    ],
    subdir: 'wrfrun/res'
)

subdir('extension')
subdir('namelist')
subdir('job_scheduler')
