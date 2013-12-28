import subprocess
import psycopg2
import platform
from os.path import dirname, abspath
from termcolor import cprint

# Custom help message
Help("""
Type: 'scons' or 'scons server' to start HTTP server,
      'scons db' to setup database,
      'scons lib' to build shared library,
      'scons tests' to build and run unit tests.
""")

# Add SConscript 
shared_lib = SConscript('libclassifier/SConscript')

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
		print "failed!"
		return False
	print "success!"
	return True

# Colored printing
print_cyan = lambda x: cprint(x, 'cyan')

# Shell operations
def run_in_shell(filepath, directory=None):
	if directory == None:
		directory = dirname(filepath)
	else:
		directory = '{0}/{1}'.format(Dir('.').abspath, directory)
	p = subprocess.Popen(filepath, cwd=directory, shell=True)
	return p.wait()

def run_ut_classifier_func(target, source, env):
	print_cyan('Running classifier unit tests...')
	run_in_shell('python tests.py', 'libclassifier/unittests')
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
	run_in_shell('python manage.py test med.SeleniumTests --liveserver=localhost:8100', 'Django')
	print ''

def run_server_func(target, source, env):
	print_cyan("Running Django server...")
	run_in_shell('python manage.py runserver', 'Django')
	print ''

def setup_database_func(target, source, env):
	print_cyan("Setting up the database...")
	successes = 0
	print_cyan('Creating database...')
	if run_postgres_query('CREATE DATABASE skeleton_base;'):
		successes = successes + 1
	print_cyan('Adding user...')
	if run_postgres_query("CREATE USER skeleton WITH PASSWORD 'skeleton'"):
		successes = successes + 1
	print_cyan('Granting privileges...')
	if run_postgres_query("GRANT ALL PRIVILEGES ON DATABASE skeleton_base to skeleton;"):
		successes = successes + 1
	if run_postgres_query("ALTER USER skeleton CREATEDB;"):
		successes = successes + 1

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
run_ut_classifier_obj = env.RunUTClassifier('Classifier unit tests', None)
run_ut_utility_obj = env.RunUTUtility('Web app utility unit tests', None)
run_ut_webapp_obj = env.RunUTWebApp('Web app unit tests', None)
run_ut_webui_obj = env.RunUTWebUI('Web app ui tests', None)
setup_database_obj = env.SetupDatabase('database', None)
run_server_obj = env.RunServer('server', None)

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

# Dependencies
Depends(run_server_obj, shared_lib)
Depends(run_ut_classifier_obj, shared_lib)

# Copy boost dll to libclassifier unittests directory
if platform.system() == "Windows":
	ut_dll = Command(
		'#libclassifier/unittests/boost_python-vc110-mt-1_53.dll', 
		'#libclassifier/import/boost_python-vc110-mt-1_53.dll', 
		Copy("$TARGET", "$SOURCE")
	)
	Depends([run_ut_webapp_obj, run_ut_webui_obj, run_ut_classifier_obj], ut_dll)
