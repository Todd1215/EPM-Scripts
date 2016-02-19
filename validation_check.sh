#!/bin/bash
# validate_epm.sh $regfile
# Pass in the registry file for the EPM environment that you want to run URL validation against.


validation_check () {
# parse _registry.html file for required values

  
  then
  regfile=$EPM_ORACLE_INSTANCE/diagnostics/reports/registry.html
  host=$(hostname)
  port=19000
  
  printf "response time | http status code | URL\n"
  
  for url in $(cat "${regfile}" | grep validationContext | cut -d'>' -f5 | cut -d'<' -f1|sed 's/\ /%20/g')
  do
	check_url "${host}" "${port}" "${url}"
  done
}

check_url () {
local red='\e[31m'
local yellow='\e[33m'
local green='\e[32m'
local reset='\e[0m'
local host=$1
local port=$2
local url=$3

  stats=$(curl -fL ${host}:${port}/$url -w '%{time_total}|%{http_code}|%{url_effective}' -so /dev/null)
  totaltime=$(echo ${stats} | cut -d'|' -f1)
  ttcompare=$(echo $totaltime | cut -d'.' -f1)
  httpcode=$(echo ${stats} | cut -d'|' -f2 | cut -d'|' -f1)
  fullurl=$(echo ${stats} | cut -d'|' -f3)
  
  if [ "${httpcode}" -ne "200" ]
  then
	echo -e "${totaltime} | ${red}${httpcode}${reset} | ${fullurl}"
  else
	if [ "${ttcompare}" -lt "10" ]
	then
	  echo -e "${green}${totaltime}${reset} | ${httpcode} | ${fullurl}"
	elif [ "${ttcompare}" -ge "10" ] && [ "${ttcompare}" -lt "30" ]
	then
	  echo -e "${yellow}${totaltime}${reset} | ${httpcode} | ${fullurl}"
	elif [ "${ttcompare}" -ge "30" ]
	then
	  echo -e "${red}${totaltime}${reset} | ${httpcode} | ${fullurl}"
	fi
  fi
}

main () {
	validation_check
}

# start code execution
main