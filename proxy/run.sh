#!/bin/sh

# make sure the shell scrip fails if any of the subsequent cmd fails
set -e

# pipe in or insert the /etc/nginx/default.conf.tpl
# passing config values to the engine x server, copy our
#  conf.tpl file to docker image
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

# start engine x with the configuration set up
nginx -g 'daemon off;'