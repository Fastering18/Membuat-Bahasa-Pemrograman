TEST_DIREKTORI = ./testing

test: $(TEST_DIREKTORI)/*
	for file in $^ ; do \
		python gblk.py $${file} ; \
	done
