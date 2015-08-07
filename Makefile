check:
	nosetests -v -m "(?:^|[\b\./-])[Ss]elftest" \
	    --with-doctest --doctest-options=+NORMALIZE_WHITESPACE,+ELLIPSIS \
	    $$(git ls-files '**/*.py')
