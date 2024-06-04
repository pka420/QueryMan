#!/usr/bin/bash
source ~/.bashrc

echo "something"
current_dir=$(dirname "$0")
echo $current_dir

pushd $current_dir >/dev/null 2>&1
source env/bin/activate
echo "running python script" >> $3
echo "$curent_dir" >> $3
python main.py -n $1 -p $2 > $3
if [[ $? -ne 0 ]]; then
    echoerr "Python Selenium Script Failed" >> $3
    exit 1
fi
deactivate

sed -i 's/\\u....//g' trending_topics.json

mongoimport --db QueryMan --collection trending --file trending_topics.json >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Data import failed" >> $3
    exit 1
fi

popd >/dev/null 2>&1
exit 0
