#!/usr/bin/env bash

ROOT=$(readlink -m .)

DEPLOY="$ROOT/out" # deploy location

rm -rf $DEPLOY
mkdir $DEPLOY

# Link all the files in uploadList
while IFS='' read -r f || [[ -n "$f" ]]; do
  # Skip lines starting with # or blank
  if [[ "${f:0:1}" != "#" ]] && [[ "$f" != "" ]]
  then
      echo "Linking:  $ROOT/$f -> $DEPLOY/$f"
      mkdir -p $(dirname $(readlink -m $DEPLOY/$f))
      ln -s $ROOT/$f $DEPLOY/$f
  fi
done < "uploadList"

echo "========="
echo "Exported:"
echo "========="
pushd $DEPLOY > /dev/null
find -L * -type f
popd > /dev/null

echo "==========="
echo "App server:"
echo "==========="
dev_appserver.py $DEPLOY  --host 0.0.0.0 2>&1 | grep -v "\" 200 "

# appcfg.py -A snail-1045 update out
# to publish
