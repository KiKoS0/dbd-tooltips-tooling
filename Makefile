.PHONY: clean
clean:
	rm -rf .venv dist
	rm -rf dist
	rm -rf data

.PHONY: clean_fetch
clean_fetch:
	make clean fetch
	sort -u data/icons.txt -o data/icons.txt	
	uv run python -m dbd_tooling.fetch.icons
	rm -rf data/icons.txt

.PHONY: fetch
fetch:
	uv run python -m dbd_tooling.fetch.perks
	uv run python -m dbd_tooling.fetch.powers_addons
	uv run python -m dbd_tooling.fetch.cleanup

	uv run python -m dbd_tooling.aux.locale_gen
	uv run python -m dbd_tooling.fetch.locales.fr
	uv run python -m dbd_tooling.fetch.locales.de
	uv run python -m dbd_tooling.features.gen_feature_flags
	cp -r static/. data/


