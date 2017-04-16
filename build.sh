#!/usr/bin/env bash

mkdir -p out
cd src
zip -r -q ../out/templie.zip .
cd ..
echo '#!/usr/bin/env python3' | cat - out/templie.zip > out/templie
chmod +x out/templie
rm out/templie.zip
