clean:
	rm -rf .venv dist
	rm -rf dist
	rm -rf data

clean_fetch:
	make clean
	poetry install
	make fetch
	sort -u data/icons.txt -o data/icons.txt	
	poetry run python -m dbd_tooling.fetch.icons
	rm -rf data/icons.txt

fetch:
	poetry run python -m dbd_tooling.fetch.perks
	poetry run python -m dbd_tooling.fetch.powers_addons
	poetry run python -m dbd_tooling.fetch.cleanup

	poetry run python -m dbd_tooling.aux.locale_gen
	poetry run python -m dbd_tooling.fetch.locales.fr
	poetry run python -m dbd_tooling.fetch.locales.de
	poetry run python -m dbd_tooling.features.gen_feature_flags
	cp -r static/. data/


