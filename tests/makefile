export PYTHONPATH = ../pdd
tests = test_core test_dl test_circuit test_blocks test_tools

all: $(tests)

$(patsubst %.py, %, $(tests)):
	echo '==================================================='
	python $@.py 2>&1 | tee $@.out

clean:
	rm -rf *.out *.log __pycache__
