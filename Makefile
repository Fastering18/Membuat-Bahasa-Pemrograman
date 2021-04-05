TEST_DIREKTORI = ./testing

test: $(TEST_DIREKTORI)/*
    nuitka gblk.py
    for file in $^ ; do \
        ./gblk.exe $${file} ; \
    done
