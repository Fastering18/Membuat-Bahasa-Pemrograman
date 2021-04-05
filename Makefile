TEST_DIREKTORI = ./testing

test: $(TEST_DIREKTORI)/*
	@echo "MEMULAI TESTS"
	for file in $^ ; do \
		python gblk.py $${file} ; \
	done
	
