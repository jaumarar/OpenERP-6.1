#!/bin/bash
# Detecta, descarga e instalar (con sus dependencias) OpenERP Client 6.1.20140804)
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

# Ficheros
ORPURL="http://nightly.odoo.com/old/openerp-6.1/6.1.20140804/";

ORPCLIENTEFICH="openerp-client-6.1-20140804-233536";

ORPCLIENTEURL="$ORPURL$ORPCLIENTEFICH";

ORPUSER="admin";
ORPPASS="iocioc";
ORPDIR="/opt/openerp-client";

echo -e "["$V"cURL"$B"] Instalado...";
apt-get install -y curl > /dev/null
echo -e "["$V"cURL"$B"] Instalado";

if [ -f $ORPCLIENTEFICH.tar.gz ];then
    echo -e "["$V"OpenERP"$B"] Source cliente encontrado";
else
    echo -e "["$A"OpenERP"$B"] Source cliente, descargando...";
    curl -# $ORPCLIENTEURL -o $ORPCLIENTEFICH;
fi;

echo -e "["$V"OpenERP"$B"] Extrayendo sources...";
tar -xzf $ORPCLIENTEFICH.tar.gz

echo -e "["$V"OpenERP"$B"] Moviendo a '$ORPDIR'";
mkdir $ORPDIR
mv $ORPCLIENTEFICH/* $ORPDIR
rm -R $ORPCLIENTEFICH

echo -e "["$V"OpenERP"$B"] Ejecutar mediante: $ORPDIR/bin/openerp-client.py";
$ORPDIR/bin/openerp-client.py
