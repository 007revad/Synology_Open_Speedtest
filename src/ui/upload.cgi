#!/bin/bash
head -c "${CONTENT_LENGTH:-0}" > /dev/null
echo "Content-Type: text/plain"
echo "Access-Control-Allow-Origin: *"
echo "Access-Control-Allow-Methods: POST"
echo ""
echo "OK"
