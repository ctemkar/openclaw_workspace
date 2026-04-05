#!/bin/zsh

get_external_nonce() {
 local ext_time=$(curl -s http://worldtimeapi.org/api/timezone/Asia/Bangkok | grep -oE '"unix_time":[0-9]+' | cut -d: -f2)
 local nano_suffix=$(date +%N)
 echo "${ext_time}${nano_suffix}"
}

run_gemini_call() {
 local payload=$1
 local current_nonce=$(get_external_nonce)
 
 echo "Syncing with external time... Nonce: $current_nonce" >&2
 
 # Replace this line with your actual API execution command
 # Use $current_nonce as your 'nonce' parameter
 
 echo "Cooling down for 35 seconds..." >&2
 sleep 35
}

run_gemini_call "$1"