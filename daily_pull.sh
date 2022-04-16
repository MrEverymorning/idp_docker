#!/bin/bash

#cd ../
#cd ballpark && git pull && cd ../
#cd python3-packages && git pull && cd ../
#cd tvclient && git pull && cd ../
#cd python-packages && git pull && cd ../
#cd tvcommon && git pull && cd ../
#cd tvwebapp && git pull && cd ../
#cd mfgtest && git pull && cd ../
#cd tvapi && git pull && cd ../
#cd tvnotebook && git pull && cd ../
#cd tvproxbox && git pull && cd ../
#cd tvplatform && git pull && cd ../
#cd tvsalt && git pull && cd ../
#cd tvpillar-dev && git pull && cd ../
#cd dev-setup && git pull && cd ../

#!/bin/bash

for d in ~/recon/tv/*
do
    echo
    echo
    echo 'updating:' $d
    cd $d
    git pull
    git status
done
