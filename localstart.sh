#!/bin/sh


# ./odoo/odoo-bin.py -c odoo/config/local.conf
parse_yaml() {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
       -ne "s|^\($s\)\($w\)$s:$s'\(.*\)'$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

eval $(parse_yaml config/config.yml "config_")
# access yaml content

if [ $1 = "start" ]; then
    ./odoo/odoo-bin -c config/local.conf

elif [ $1 = "startwithport" ]; then
    ./odoo/odoo-bin -c config/server.conf --xmlrpc-port=$2

elif [ $1 = "upgradewithport" ]; then
    ./odoo/odoo-bin -c config/server.conf --xmlrpc-port=$config_common_modules,$2  -u $3 -d $4

elif [ $1 = "serverstart" ]; then
    ./odoo/odoo-bin -c config/server.conf

elif [ $1 = "--help" ]; then
    echo "=================================OPTIONS ============================"
    echo "      Run command line 'sh localstart.sh [option]' with options below:"
    echo "      [start]                                       Start Odoo with default port in file config."
    echo "      - Ex: sh localstart.sh start"
    echo "      [upgrade MODULE_NAME DB_NAME]                 Upgrade Odoo with module and database."
    echo "      - Ex: sh localstart.sh upgrade base db_demo"
    echo "      [startwithport PORT]                          Start Odoo with port define."
    echo "      - Ex: sh localstart.sh startwithport 8069"
    echo "      [upgradewithport PORT MODULE_NAME DB_NAME]    upgrade Odoo with port define."
    echo "      - Ex: sh localstart.sh upgradewithport 8069 base db_demo"
    echo "      [serverstart]    start Odoo on server."
    echo "      - Ex: sh localstart.sh serverstart"
    echo "      [--help]                                      Show more options."
    echo "================================ END ================================"

else [ $1 = "upgrade" ]
    echo "\033[1;37m - Upgrade modules: [$config_common_modules,$2]\033[0m"
    echo "\033[1;37m - On database $3\033[0m"
    ./odoo/odoo-bin -c config/local.conf -u $config_common_modules,$2 -d $3
fi
