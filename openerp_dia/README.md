# OpenERP-6.1 - openerp_dia
Licéncia GPL 3
>Problemas conocidos: No está contemplado el uso de una jerarquización de más de 2 niveles vacios:<br>
 ✓ MenuModulo/MenuVacio1/Clase1<br>
 X ~~MenuModulo/MenuVacio1/MenuVacio2/Clase1~~<br>
 
###codegen_openerp_61_v3.py
  >Retoques a la v2:
  Ahora los campos one2many y many2many por defecto son mostrados en la vista xml.<br>
  Eliminados en los nombres de los separadores los ' y espacios iniciales/finales

###codegen_openerp_61_v2.py
  >Basado en el generador <a href="https://code.launchpad.net/~openerp-commiter/openobject-addons/extra-6.0">OERP 6.0</a> (no permite jerarquía de menús 6.1).<br>
  >Esta versión construye por defecto el fichero de permisos
  
  <strong>Modificaciones:</strong><br>
<a href="https://github.com/jaumarar/OpenERP-6.1/blob/master/openerp_dia/codegen_openerp_61_v2.py#L310">Jerarquización de menús</a><br>
  <br><strong>Menú XML:</strong><br>
  ![MenuXML](http://i.imgur.com/QJkVHbK.jpg)
  <br><strong>Menú webclient:</strong><br>
  ![MenuWeb](http://i.imgur.com/5o4qh6I.jpg)

###codegen_openerp_61_v1.py
  >Basado en el generador usado en clase (OERP 5.0)(no permite jerarquía de menús 6.1)
  
  <strong>Modificaciones:</strong>
    <a href="https://github.com/jaumarar/OpenERP-6.1/blob/master/openerp_dia/codegen_openerp_61_v1.py#L236">Jerarquización de menús</a><br>
###TODO
  >Permitir más de 2 estereotipos vacios encadenados (mediante un for?)
