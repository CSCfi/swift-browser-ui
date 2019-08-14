# Makefile for creating the dark theme, since rehosting the whole bulma and
# buefy repos would be unnecessary.
# Build script assumes that sass cli is instlled and accessible from bash
build:
	wget https://github.com/jgthms/bulma/releases/download/0.7.5/bulma-0.7.5.zip && 7z x bulma-0.7.5.zip &&\
	rm bulma-0.7.5.zip &&\
	sass --no-source-map sass/darktheme.scss:./darktheme.css && cp ./darktheme.css ../bulma-custom.css

clean:
	rm ../bulma-custom.css; rm ./darktheme.css

clean-deps:
	rm -rf ./bulma-0.7.5
