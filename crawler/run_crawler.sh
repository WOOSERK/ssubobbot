#!/bin/bash

PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/ec2-user/.local/bin:/home/ec2-user/bin

cd $(dirname $0)
cd ./crawler

scrapy crawl crawler -o result.jl
