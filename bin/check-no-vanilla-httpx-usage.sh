#!/bin/bash

for file in $@; do
  if grep --exclude=app/httpx.py -r "\(^\s*import httpx\)\|\(^\s*from httpx import\)" $file ; then
    exit 1
  fi
done || exit $?

