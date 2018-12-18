export PYTHONPATH = ../orgparser
tests = test_tree test_orgparser

all: $(tests)

$(patsubst %.py, %, $(tests)):
	python $@.py 2>&1 | tee $@.out

clean:
	rm *.out *.log
