#!/bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

EDITOR=vim
PASSWD=/etc/passwd
RED='\033[0;41;30m'
STD='\033[0;0;39m'

pause(){
    read -p "Press [Enter] key to continue..." fackEnterKey
}


one(){
    TOKEN=$(curl -s -X POST -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        --data '{"client_app": "CuroVindico", "access_key_id": "CuroVindico", "secret_acces_key": "CuroVindico" }' \
        http://localhost:6080/token | jq -r '.access_token')
        
    curl -i -F file=@${SCRIPTPATH}/test/zyZgQ7rRMaM.xlsx \
        -H "Authorization: Bearer ${TOKEN}" http://localhost:6080/api/files
    pause
}
 

two(){
    TOKEN=$(curl -s -X POST -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        --data '{"client_app": "CuroVindico", "access_key_id": "CuroVindico", "secret_acces_key": "CuroVindico" }' \
        http://localhost:6080/token | jq -r '.access_token')
        
    curl  -H "Authorization: Bearer ${TOKEN}" http://localhost:6080/api/files/zyZgQ7rRMaM.xlsx -o ${SCRIPTPATH}/test/downloded.xlsx
    pause
}


three(){
    TOKEN=$(curl -s -X POST -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        --data '{"client_app": "CuroVindico", "access_key_id": "CuroVindico", "secret_acces_key": "CuroVindico" }' \
        http://localhost:6080/token | jq -r '.access_token')
	 curl -X DELETE  -H "Authorization: Bearer ${TOKEN}" http://localhost:6080/api/files/zyZgQ7rRMaM.xlsx
    pause
}
 
# function to display menus
show_menus() {
    clear
    echo "~~~~~~~~~~~~~~~~~~~~~"	
    echo " M A I N - M E N U"
    echo "~~~~~~~~~~~~~~~~~~~~~"
    echo "1. Test Upload"
    echo "2. Test Download"
    echo "3. Test Delete"
    echo "4. Exit"
}
read_options(){
	local choice
	read -p "Enter choice [ 1 - 4 ] " choice
	case $choice in
		1) one ;;
		2) two ;;
		3) three;;
		4) exit 0;;
		*) echo -e "${RED}Error...${STD}" && sleep 2
	esac
}
trap '' SIGINT SIGQUIT SIGTSTP
while true
do
    show_menus
    read_options
done