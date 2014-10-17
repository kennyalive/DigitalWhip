import os
import shutil
import subprocess
import sys
import time

BUILD_DIR = 'build'
BENCHMARKS_DIR = 'benchmarks'
DATA_DIR = 'data'
BUILD_SCRIPT = 'build.py'

def get_exe_runnable(output_dir):
    return [os.path.join(output_dir, 'benchmark.exe')]

def get_python_runnable(output_dir):
    return ['pypy', os.path.join(output_dir, 'benchmark.py')]

LANGUAGES = [
    {
        'folder': 'lang_cpp',
        'runnable': get_exe_runnable
    },
    {
        'folder': 'lang_d',
        'runnable': get_exe_runnable
    },
    {
        'folder': 'lang_go',
        'runnable': get_exe_runnable
    },
    {
        'folder': 'lang_python',
        'runnable': get_python_runnable
    }
]

def build_benchmark(benchmark):
    build_config = []
    for language in LANGUAGES:
        language_folder = language['folder']
        build_script = os.path.join(BENCHMARKS_DIR, benchmark, language_folder, BUILD_SCRIPT)

        if os.path.exists(build_script):
            output_dir = os.path.join(BUILD_DIR, benchmark, language_folder)
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir)

            build_config.append({
                'build_script': build_script, 
                'output_dir': output_dir
            })

    os.environ['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))
    for config in build_config:
        subprocess.call(['python', config['build_script'], config['output_dir']])

def run_benchmark(benchmark, validate_results):
    data_dir = os.path.join(BENCHMARKS_DIR, benchmark, DATA_DIR)
    for language in LANGUAGES:
        language_folder = language['folder']
        output_dir = os.path.join(BUILD_DIR, benchmark, language_folder)
        if os.path.exists(output_dir):
            # prepare command line to launch benchmark executable
            runnable_command_line = language['runnable'](output_dir)
            runnable_command_line.append(data_dir)
            if validate_results:
                runnable_command_line.append('validate')
            # launch benchmark
            print(language_folder)
            start = time.clock()
            benchmark_result = subprocess.call(runnable_command_line)
            # print benchmark results
            if validate_results:
                print('Passed' if benchmark_result == 0 else 'Failed')
            else:
                elapsed_time_benchmark = benchmark_result / 1000.0
                elapsed_time_total = time.clock() - start
                print("benchmark {:.3f}".format(elapsed_time_benchmark))
                print("total {:.3f}\n".format(elapsed_time_total))

if __name__ == '__main__':
    validate_results = len(sys.argv) > 1 and sys.argv[1] == 'validate'

    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)

    benchmarks = os.listdir('benchmarks')
    for benchmark in benchmarks:
        build_benchmark(benchmark)

    print("")
    for benchmark in benchmarks:
        print('------ Running ' + benchmark + ' ------')
        run_benchmark(benchmark, validate_results)
