#!/bin/bash
docker run --name moloch -p 8005:8005 -d --link es:elasticsearch --net enisanet --ip 10.34.1.4 enisa:moloch
