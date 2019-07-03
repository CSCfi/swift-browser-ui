#!/bin/bash

echo 'Build documentation'
cd docs
make html
echo 'Run HTTP python server documentation'
cd build/html
exec python -m http.server 8080
