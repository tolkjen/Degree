import subprocess
import psycopg2
from os.path import dirname, abspath

# Custom help message
Help("""
Type: 'scons' or 'scons server' to start HTTP server,
      'scons db' to setup database,
      'scons lib' to build shared library,
      'scons tests' to build and run unit tests.
""")

# Decider - MD5 mixed with timestamps
Decider('MD5-timestamp')

# Add SConscript 
(shared_lib, tests) = SConscript('libclassifier/SConscript')

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

# Shell operations
def run_in_shell(filepath):
	p = subprocess.Popen(filepath, cwd=dirname(filepath), shell=True)
	return p.wait()

# Custom builders
def run_tests_func(target, source, env):
	print """
+-------------------------------+
|           Unit tests          |
+-------------------------------+
"""
	run_in_shell(tests[0].abspath)

def run_server_func(target, source, env):
	print """
+-------------------------------+
|         Django server         |
+-------------------------------+
"""
	command = '{0}/Django/manage.py runserver'.format(Dir('.').abspath)
	run_in_shell(command)

def setup_database_func(target, source, env):
	print """
+-------------------------------+
|         Database setup        |
+-------------------------------+
"""
	successes = 0
	print 'Creating database...',
	if run_postgres_query('CREATE DATABASE skeleton_base;'):
		successes = successes + 1
	print 'Adding user...',
	if run_postgres_query("CREATE USER skeleton WITH PASSWORD 'skeleton'"):
		successes = successes + 1
	print 'Granting privileges...',
	if run_postgres_query("GRANT ALL PRIVILEGES ON DATABASE skeleton_base to skeleton;"):
		successes = successes + 1

	print 'Creating tables in database...',
	command = '{0}/Django/manage.py syncdb'.format(Dir('.').abspath)
	if run_in_shell(command) == 0:
		successes = successes + 1
		print 'success!'
	else:
		print 'failure!'

	if successes == 4:
		print "Database setup completed!"
	else:
		print 'Problems during database setup.'

env = DefaultEnvironment()
env.Append(BUILDERS = {'RunTests' : Builder(action = run_tests_func)})
env.Append(BUILDERS = {'SetupDatabase' : Builder(action = setup_database_func)})
env.Append(BUILDERS = {'RunServer' : Builder(action = run_server_func)})
run_tests_obj = env.RunTests('runtests', None)
setup_database_obj = env.SetupDatabase('database', None)
run_server_obj = env.RunServer('server', None)

# Try to run server by default
Default(run_server_obj)

# Aliases
Alias(['test', 'tests', 'unittest', 'unittests'], run_tests_obj)
Alias(['setupdb', 'db', 'postgres'], setup_database_obj)
Alias(['server', 'runserver', 'django'], run_server_obj)
AlwaysBuild(tests)

# Dependencies
Depends(run_tests_obj, tests)
Depends(run_server_obj, shared_lib)
