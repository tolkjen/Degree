import subprocess
from os.path import dirname

# Custom help message
Help("""
Type: 'scons' to build shared library,
      'scons test' to build and run unit tests.
""")

# Decider - MD5 mixed with timestamps
Decider('MD5-timestamp')

# Add SConscript 
(shared_lib, tests) = SConscript('libclassifier/SConscript')
Default(shared_lib)

# Custom builders
def run_tests(target, source, env):
	print """
+-------------------------------+
|      Running unit tests       |
+-------------------------------+
"""
	filepath = tests[0].abspath
	p = subprocess.Popen(filepath, cwd=dirname(filepath), shell=True)
	p.wait()

env = DefaultEnvironment()
env.Append(BUILDERS = {'RunTests' : Builder(action = run_tests)})
run_tests = env.RunTests('runtests', None)

# Aliases
Alias('test', run_tests)
AlwaysBuild(tests)

# Dependencies
Depends(run_tests, tests)
