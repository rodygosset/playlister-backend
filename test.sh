cd ..
for test_file in backend/tests/test_*; do
    pytest $test_file
    rm test.db
done