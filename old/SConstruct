import subprocess
import psycopg2
import platform
import psutil
import re
import os

from os.path import dirname, basename, abspath
from termcolor import cprint

# Custom help message
Help("""
Type: 'scons' or 'scons server' to start HTTP server,
      'scons db' to setup database,
      'scons lib' to build shared library,
      'scons ut' to build and run all unit tests,
      'scons ut-classifier' to build and run classifier unit tests,
      'scons ut-utility' to build and run utility unit tests,
      'scons ut-webapp' to build and run webapp unit tests,
      'scons ut-webui' to build and run webui unit tests,
""")

# Add SConscript 
shared_lib, shared_lib_tests = SConscript('libclassifier/SConscript')

# Database management
def run_postgres_query(query):
	try:
		conn = psycopg2.connect("user=postgres")
		try:
			conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
			cur = conn.cursor()
			cur.execute(query)
			conn.commit()
		finally:
			conn.close()
	except Exception, e:
		return False
	return True

# Colored printing
def print_cyan(text):
	if platform.system() == "Linux":
		cprint(text, "cyan")
	else:
		print text

# Printing data in table format
def print_in_columns(data, headers):
	def print_rows(data, lengths):
		for row in data:
			print ''.join(word.ljust(lengths[i]) for i, word in enumerate(row))

	lengths = []
	for i in range(len(data[0])):
		lengths.append(max(len(row[i]) for row in data) + 2)

	separator = '-' * (sum(lengths)-2)
	print_rows([headers], lengths)
	print separator
	print_rows(data, lengths)
	print separator

# Shell operations
def kill_all(process_name):
	running_process_pid = os.getpid()
	for process in psutil.process_iter():
		try:
			if process.name() == process_name and process.pid != running_process_pid:
				process.terminate()
		except:
			pass

def run_in_shell(filepath, directory=None):
	if directory == None:
		directory = dirname(filepath)
	else:
		directory = '{0}/{1}'.format(Dir('.').abspath, directory)

	p = subprocess.Popen(filepath, cwd=directory, shell=True)
	return p.wait()

def run_in_shell_get_stdout(filepath, directory=None):
	if directory == None:
		directory = dirname(filepath)
	else:
		directory = '{0}/{1}'.format(Dir('.').abspath, directory)

	p = subprocess.Popen(filepath, cwd=directory, shell=True, stdout=subprocess.PIPE)
	output, errors = p.communicate()
	return (p.returncode, output)

def run_ut_classifier_func(target, source, env):
	print_cyan('Running classifier unit tests...')
	run_in_shell('python tests.py', 'libclassifier/unittests')

	if platform.system() == "Linux":
		code, output = run_in_shell_get_stdout('gcov -rn classifier.gcda', 'libclassifier/bin/unittests')
		matches = re.findall('^File \'(.*?)\'.*?:(.*?)$', output, re.MULTILINE | re.DOTALL)
		sources = [x.name for x in Glob('libclassifier/src/lib/*.*pp')]
		true_matches = filter(lambda (path, r): basename(path) in sources, matches)

		print ''
		print_in_columns(true_matches, ['Name', 'Stmts'])
		print ''

def run_ut_utility_func(target, source, env):
	print_cyan('Running web app utility unit tests...')
	if run_in_shell('coverage run --source=med.utility -m med.unittests.tests', 'Django') == 0:
		print ''
		run_in_shell('coverage report', 'Django')
		print ''

def run_ut_webapp_func(target, source, env):
	print_cyan('Running web app tests...')
	omitted_dirs = ','.join(['med/utility/*', 'med/unittests/*'])
	run_in_shell('coverage run --source=med --omit=%s manage.py test med.ValidationViewTests' % (omitted_dirs), 'Django')
	print ''
	run_in_shell('coverage report', 'Django')
	print ''

def run_ut_webui_func(target, source, env):
	print_cyan('Running web UI tests...')
	run_in_shell('python manage.py test med.SeleniumTests --liveserver=127.0.0.1:8100', 'Django')
	print ''

def run_server_func(target, source, env):
	print_cyan("Running Django server...")
	run_in_shell('python manage.py runserver', 'Django')
	print ''

def kill_django_func(target, source, env):
	kill_all("python.exe")
	kill_all("python")
	print ''

def setup_database_func(target, source, env):
	print_cyan("Setting up the database...")

	run_postgres_query('DROP DATABASE skeleton_base;')
	run_postgres_query('DROP USER skeleton')

	successes = 0
	if run_postgres_query('CREATE DATABASE skeleton_base;'):
		successes = successes + 1
	if run_postgres_query("CREATE USER skeleton WITH PASSWORD 'skeleton'"):
		successes = successes + 1
	if run_postgres_query("GRANT ALL PRIVILEGES ON DATABASE skeleton_base to skeleton;"):
		successes = successes + 1
	if run_postgres_query("ALTER USER skeleton CREATEDB;"):
		successes = successes + 1

	if successes == 4:
		print "Success!"
	else:
		print "Failure!"
		return

	print_cyan('Creating tables in database...')
	if run_in_shell('python manage.py syncdb', 'Django') == 0:
		successes = successes + 1
		print 'Creating tables in database was successful!'
	else:
		print 'Creating tables in database failed!'

	if successes == 5:
		print "Database setup completed!"
	else:
		print 'Problems during database setup.'

env = DefaultEnvironment()
env.Append(BUILDERS = {'RunUTClassifier' : Builder(action = run_ut_classifier_func)})
env.Append(BUILDERS = {'RunUTUtility' : Builder(action = run_ut_utility_func)})
env.Append(BUILDERS = {'RunUTWebApp' : Builder(action = run_ut_webapp_func)})
env.Append(BUILDERS = {'RunUTWebUI' : Builder(action = run_ut_webui_func)})
env.Append(BUILDERS = {'SetupDatabase' : Builder(action = setup_database_func)})
env.Append(BUILDERS = {'RunServer' : Builder(action = run_server_func)})
env.Append(BUILDERS = {'KillDjango' : Builder(action = kill_django_func)})
run_ut_classifier_obj = env.RunUTClassifier('Classifier unit tests', None)
run_ut_utility_obj = env.RunUTUtility('Web app utility unit tests', None)
run_ut_webapp_obj = env.RunUTWebApp('Web app unit tests', None)
run_ut_webui_obj = env.RunUTWebUI('Web app ui tests', None)
setup_database_obj = env.SetupDatabase('database', None)
run_server_obj = env.RunServer('server', None)
kill_django_obj = env.KillDjango('kill django', None)

# Try to run server by default
Default(run_server_obj)

# Aliases
Alias(['ut-classifier'], run_ut_classifier_obj)
Alias(['ut-utility'], run_ut_utility_obj)
Alias(['ut-webapp'], run_ut_webapp_obj)
Alias(['ut-webui'], run_ut_webui_obj)
Alias(['ut', 'tests'], [run_ut_classifier_obj, run_ut_utility_obj, run_ut_webapp_obj,
	run_ut_webui_obj])
Alias(['setupdb', 'db', 'postgres', 'database'], setup_database_obj)
Alias(['server', 'runserver', 'django', 'webapp', 'app'], run_server_obj)
Alias(['stop'], kill_django_obj)
Alias(['all'], [run_ut_classifier_obj, run_ut_utility_obj, run_ut_webapp_obj,
	run_ut_webui_obj, shared_lib])

# Dependencies
Depends(run_server_obj, shared_lib)
Depends(run_ut_classifier_obj, shared_lib_tests)
Depends([run_ut_utility_obj, run_ut_webapp_obj, run_ut_webui_obj], shared_lib)
