#!/bin/bash
# Detecta, descarga e instalar (con sus dependencias OpenERP 6.1.20140804)
######################################################################################
# Copyright (c) 2015 Jaume Martí <http://github.com/jaumarar>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
######################################################################################
B='\033[0m';
R='\033[31m';
V='\033[32m';
A='\033[33m';

if [ "$(whoami)" != "root" ]; then
	echo -e "["$R"Ubuntu"$B"] Necesita ejecutarse como sudo";
	exit 1;
fi;

# Version Ubuntu
RES=`lsb_release -r -s | egrep -o [0-9]{2} | head -1`;

if [ $RES -eq 12 ]; then
	echo -e "["$V"Ubuntu"$B"] Versión correcta";
else
	echo -e "["$R"Ubuntu"$B"] Versión no recomendada";
	exit 1;
fi;

echo -e "["$V"Ubuntu"$B"] Actualizando paquetes...";
apt-get update > /dev/null

PSQLUSER="postgres";
PSQLPASS="iocioc";

# Ficheros
ORPURL="http://nightly.odoo.com/old/openerp-6.1/6.1.20140804/";

ORPSERVERFICH="openerp_6.1-20140804-233536-1_all.deb";
ORPCLIENTEFICH="openerp-client-6.1-20140804-233536.tar.gz";

ORPSERVERURL="$ORPURL$ORPSERVERFICH";
ORPCLIENTEURL="$ORPURL$ORPCLIENTEFICH";

ORPUSER="openerp";
ORPPASS="iocioc";
ORPCFG="/etc/openerp/openerp-server.conf";

echo -e "["$V"OpenERP"$B"] Instalando dependencias...";
echo "" > exito.log; echo "" > error.log
echo "###################################################" | tee -a exito.log error.log > /dev/null
echo "####### [OpenERP][Dependencias][Inicio] ###########" | tee -a exito.log error.log > /dev/null
echo "###################################################" | tee -a exito.log error.log > /dev/null
apt-get install -y python-dateutil python-feedparser python-gdata python-ldap python-libxslt1 python-lxml python-mako python-openid python-psycopg2 python-pybabel python-pychart python-pydot python-pyparsing python-reportlab python-simplejson python-tz python-vatnumber python-vobject python-webdav python-xlwt python-yaml python-zsi python-werkzeug >> exito.log 2>> error.log
echo "###################################################" | tee -a exito.log error.log > /dev/null
echo "####### [OpenERP][Dependencias][Fin] ##############" | tee -a exito.log error.log > /dev/null
echo "###################################################" | tee -a exito.log error.log > /dev/null
echo -e "["$V"OpenERP"$B"] Dependencias instaladas.";
echo -e "["$A"Ubuntu"$B"] Esperando apt...";
sleep 10s

echo -e "["$V"PostgreSQL"$B"] Instalando...";
apt-get install -y postgresql-client-common postgresql-client-8.4 postgresql-common postgresql-8.4
echo -e "["$V"PostgreSQL"$B"] Instalado";

echo -e "["$A"Ubuntu"$B"] Esperando apt...";
sleep 10s

echo -e "["$V"cURL"$B"] Instalado...";
apt-get install -y curl > /dev/null
echo -e "["$V"cURL"$B"] Instalado";

if [ -f $ORPSERVERFICH ];then
    echo -e "["$V"OpenERP"$B"] Instalador servidor encontrado";
else
    echo -e "["$A"OpenERP"$B"] Instalador servidor, descargando...";
    curl -# $ORPSERVERURL -o $ORPSERVERFICH;
fi;

echo -e "["$V"PostgreSQL"$B"] Añadiendo usuario gestor de OpenERP { $ORPUSER:$PSQLPASS }";
echo -e "		1. "$R"USAR COMANDO"$B": createuser -U $PSQLUSER -d -R -S -P $ORPUSER";
echo -e "		2. "$R"PONER DE CONTRASEÑA"$B": $PSQLPASS";
echo -e "		3. "$R"USAR COMANDO"$B": exit";
echo -e "	Usar exit si ya ha sido creado el usuario anteriormente";
su $PSQLUSER 
echo -e "["$V"PostgreSQL"$B"] Usuario añadido";

echo -e "["$V"OpenERP"$B"] Instalando desde paquete deb..."
echo "###################################################" | tee -a exito.log error.log > /dev/null
echo "####### [OpenERP][Instalación][Inicio] ###########" | tee -a exito.log error.log > /dev/null
echo "###################################################" | tee -a exito.log error.log > /dev/null
dpkg -i $ORPSERVERFICH >> exito.log 2>> error.log
echo "###################################################" | tee -a exito.log error.log > /dev/null
echo "####### [OpenERP][Instalación][Fin] ##############" | tee -a exito.log error.log > /dev/null
echo "###################################################" | tee -a exito.log error.log > /dev/null
echo -e "["$V"OpenERP"$B"] Instalado"

echo -e "["$A"Ubuntu"$B"] Esperando apt...";
sleep 10s

echo -e "["$V"OpenERP"$B"] Configurando..";
echo "[options]" > $ORPCFG
echo "dbhost = localhost" >> $ORPCFG
echo "; This is the password that allows database operations:" >> $ORPCFG
echo "; admin_passwd = admin" >> $ORPCFG
echo "db_host = localhost" >> $ORPCFG
echo "db_port = 5432" >> $ORPCFG
echo "db_user = $ORPUSER" >> $ORPCFG
echo "db_password = $ORPPASS" >> $ORPCFG

echo -e "["$V"OpenERP"$B"] Comprobando servicio...";
ORPCHECKWEB=`netstat -ano | egrep -o "(8069)|(8070)" | wc -l`;
ORPCHECKSRV=`ps aux | egrep -o openerp | wc -l`;

if [ $ORPCHECKSRV -gt 2 ];then
	echo -e "["$V"OpenERP"$B"] Servicio correcto";
else
	echo -e "["$R"OpenERP"$B"] Servicio incorrecto";
fi;


if [ $ORPCHECKWEB -eq 2 ];then
	echo -e "["$V"OpenERP"$B"] Servicio web correcto";
else
	echo -e "["$R"OpenERP"$B"] Servicio web incorrecto";
fi;



echo -e "["$V"OpenERP"$B"] Reiniciando configuración...";
service openerp restart

echo -e "["$V"OpenERP"$B"] Iniciando navegador en 10...\n["$A"****** PUEDE QUE EL SERVICIO NO ESTE AÚN INICIADO ******"$B"]";
sleep 10s
firefox http://localhost:8069 &






# JMA , 7N - 2015/10
