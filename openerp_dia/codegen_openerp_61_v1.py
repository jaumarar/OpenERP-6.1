# -*- encoding: utf-8 -*-
##############################################################################
#
#    This file is based heavily on the addon provided by
#    OpenERP (<http://tiny.be>) by Tiny SPRL Copyright (C) 2004-2008
#    Copyright (C) 2015 Jaume Martí (<https://github.com/jaumarar>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import sys, dia, os
import zipfile

#
# This code is inspired by codegen.py
#
class Klass :
    def __init__ (self, name) :
        self.name = name
        self.attributes = []
        # a list, as java/c++ support multiple methods with the same name
        self.stereotype = ""
        self.operations = []
        self.comment = ""
        self.parents = []
        self.templates = []
        self.inheritance_type = ""
    def AddAttribute(self, name, type, visibility, value, comment) :
        self.attributes.append((name, (type, visibility, value, comment)))
    def AddOperation(self, name, type, visibility, params, inheritance_type, comment, class_scope) :
        self.operations.append((name,(type, visibility, params, inheritance_type, comment, class_scope)))
    def SetComment(self, s) :
        self.comment = s
    def AddParent(self, parent):
        self.parents.append(parent)
    def AddTemplate(self, template):
        self.templates.append(template)
    def SetInheritance_type(self, inheritance_type):
        self.inheritance_type = inheritance_type

class ObjRenderer :
    "Implements the Object Renderer Interface and transforms diagram into its internal representation"
    def __init__ (self) :
        # an empty dictionary of classes
        self.klasses = {}
        self.klass_names = []   # store class names to maintain order
        self.arrows = []
        self.filename = ""

    def begin_render (self, data, filename) :
        self.filename = filename
        for layer in data.layers :
            # for the moment ignore layer info. But we could use this to spread accross different files
            for o in layer.objects :
                if o.type.name == "UML - Class" :
                    #print o.properties["name"].value
                    k = Klass (o.properties["name"].value)
                    k.SetComment(o.properties["comment"].value)
                    k.stereotype = o.properties["stereotype"].value
                    if o.properties["abstract"].value:
                        k.SetInheritance_type("abstract")
                    if o.properties["template"].value:
                        k.SetInheritance_type("template")
                    for op in o.properties["operations"].value :
                        # op : a tuple with fixed placing, see: objects/UML/umloperations.c:umloperation_props
                        # (name, type, comment, stereotype, visibility, inheritance_type, class_scope, params)
                        params = []
                        for par in op[8] :
                            # par : again fixed placement, see objects/UML/umlparameter.c:umlparameter_props
                            params.append((par[0], par[1]))
                        k.AddOperation (op[0], op[1], op[4], params, op[5], op[2], op[7])
                    #print o.properties["attributes"].value
                    for attr in o.properties["attributes"].value :
                        # see objects/UML/umlattributes.c:umlattribute_props
                        #print "    ", attr[0], attr[1], attr[4]
                        k.AddAttribute(attr[0], attr[1], attr[4], attr[2], attr[3])
                    self.klasses[o.properties["name"].value] = k
                    self.klass_names += [o.properties["name"].value]
                    #Connections
                elif o.type.name == "UML - Association" :
                    # should already have got attributes relation by names
                    pass
                # other UML objects which may be interesting
                # UML - Note, UML - LargePackage, UML - SmallPackage, UML - Dependency, ...

        edges = {}
        for layer in data.layers :
            for o in layer.objects :
                for c in o.connections:
                    for n in c.connected:
                        if not n.type.name in ("UML - Generalization", "UML - Realizes"):
                            continue
                        if str(n) in edges:
                            continue
                        edges[str(n)] = None
                        if not (n.handles[0].connected_to and n.handles[1].connected_to):
                            continue
                        par = n.handles[0].connected_to.object
                        chi = n.handles[1].connected_to.object
                        if not par.type.name == "UML - Class" and chi.type.name == "UML - Class":
                            continue
                        par_name = par.properties["name"].value
                        chi_name = chi.properties["name"].value
                        if n.type.name == "UML - Generalization":
                            self.klasses[chi_name].AddParent(par_name)
                        else: self.klasses[chi_name].AddTemplate(par_name)

    def end_render(self) :
        # without this we would accumulate info from every pass
        self.attributes = []
        self.operations = {}


class OpenERPRenderer(ObjRenderer) :
    def __init__(self) :
        ObjRenderer.__init__(self)

    def data_get(self):
        return {
            'file': self.filename,
            'module': os.path.basename(self.filename).split('.')[-2]
        }

    def terp_get(self):
        terp = """{
        "name" : "%(module)s",
        "version" : "0.1",
        "author" : "Unknow",
        "website" : "http://openerp.com",
        "category" : "Unknown",
        "description": \"\"\"  \"\"\",
        "depends" : ['base'],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "update_xml" : ['%(module)s_view.xml'],
        "installable": True
}""" % self.data_get()
        return terp

    def init_get(self):
        return '#\n# Generated by the OpenERP plugin for Dia !\n#\n\nimport %(module)s' % self.data_get()

    def view_class_get(self, cn, cd):
        data = self.data_get()
        i = 1
        fields_form = fields_tree = ""
        cols = {}
        for sa,attr in cd.attributes:
            cols[sa] = True
            attrs = ''
            if attr[0] in ('one2many', 'many2many', 'text'):
                attrs='colspan="4" '
            fields_form += ("                <field name=\"%s\" "+attrs+"select=\"%d\"/>\n") % (sa,i)
            if attr[0] not in ('one2many', 'many2many'):
                fields_tree += "                <field name=\"%s\"/>\n" % (sa,)
            if (i==2) or not i:
                i=-1
            i += 1
        data['form']= fields_form
        data['tree']= fields_tree
        data['name_id']= cn.replace('.','_')
        if not cd.stereotype:
            data['menu']= 'Unknown/'+cn.replace('.','_')
        else:
            data['menu']= cd.stereotype
        data['name']= cn
        data['name_en']= data['menu'].split('/')[-1]
        data['mode'] = 'tree,form'
        if 'date' in cols:
            data['mode']='tree,form,calendar'
        result = """
    <record model="ir.ui.view" id="view_%(name_id)s_form">
        <field name="name">%(name)s.form</field>
        <field name="model">%(name)s</field>
        <field name="type">form</field>
        <field name="arch" type="xml">
            <form string="%(name)s">
%(form)s
            </form>
        </field>
    </record>
    <record model="ir.ui.view" id="view_%(name_id)s_tree">
        <field name="name">%(name)s.tree</field>
        <field name="model">%(name)s</field>
        <field name="type">tree</field>
        <field name="arch" type="xml">
            <tree string="%(name)s">
%(tree)s
            </tree>
        </field>
    </record>
    <record model="ir.actions.act_window" id="action_%(name_id)s">
        <field name="name">%(name_en)s</field>
        <field name="res_model">%(name)s</field>
        <field name="view_type">form</field>
        <field name="view_mode">%(mode)s</field>
    </record>
    <!-- <menuitem name="%(menu)s" id="menu_%(name_id)s" action="action_%(name_id)s"/> -->

        """ % data
        return result

    def view_get(self):
        result = """<?xml version="1.0"?>
<openerp>
<data>
"""
        for sk in self.klass_names:
            result += self.view_class_get(sk, self.klasses[sk])
        ########################################################################
        result += "<!-- ## MENUS ###################################################### -->"
        # arrayGlobal al que ir añadiendo el nombre y el id de cada uno de los menus que encontremos, así como el base del módulo
        self.arrayGlobal = { 'module_menu_id' : None,'module_menu_name':None, 'menuitems':{}}
        # Recorremos todas las clases del diagrama para generaremos los menus
        for sk in self.klass_names:
            result += self.menu_class_get(sk, self.klasses[sk])
        result += "<!-- ############################################################### -->"
        ########################################################################
        result += """
</data>
</openerp>"""
        return result

    ### INICIO MENUS ###################################################################################################################################
    def menu_class_get(self, className, classData):
        # Iniciar la cadena de texto que devolveremos con todos los menus
        menus = ""
        data = self.data_get() # contiene 'file' : self.filename Y 'module' : os.path.basename(self.filename).split('.')[-2]
        data['module_menu_id'] = "menu_%s" % className.split('.')[0] # school.*

        data['name_id'] = className.replace('.','_')
        data['menu'] = classData.stereotype
        data['name'] = className
        data['menu_name'] = data['menu'].split('/')[-1]
        data['menu_id'] = "menu_%s" % data['name_id']    # menu_school_*
        data['menu_action'] = "action_%s" % data['name_id']

        # Comprobar si el menu base del modulo esta creado
        if data['module_menu_id'] not in str( self.arrayGlobal['module_menu_id'] ):
            # Añadir el nombre del menuitem base
            data['module_menu_name'] = data['menu'].split('/')[0] # Course
            self.arrayGlobal['module_menu_name'] = data['module_menu_name']
            # Añadir la id del menuitem base
            self.arrayGlobal['module_menu_id'] = data['module_menu_id']
            # Se añade también a los menus normales
            self.arrayGlobal['menuitems'][data['module_menu_name']] = {'menu_name': data['module_menu_name'], 'menu_id':data['module_menu_id']}
            # Añadir <menuitem>
            menus += """<menuitem name="%(module_menu_name)s" id="%(module_menu_id)s"/>""" % data

        # Añadir el actual al registro
        if data['menu_name'] not in self.arrayGlobal['menuitems']:
            self.arrayGlobal['menuitems'][data['menu_name']] = {'menu_name': data['menu_name'], 'menu_id':data['menu_id']}

        # Determinar si el elemento actual tiene un padre
        data['padre_name'] = None
        data['padre_id'] = None
        if len( data['menu'].split('/') ) > 1:
            # Padre el elemento actual
            data['padre_name'] = data['menu'].split('/')[-2]
            # Si el padre no se había registrado (es un menú vacio) agregarlo
            if data['padre_name'] not in self.arrayGlobal['menuitems']:
                # Añadirlo
                data['padre_id'] = "%s_" % data['module_menu_id']
                data['padre_id'] += data['padre_name'].lower().replace(' ','_')
                self.arrayGlobal['menuitems'][data['padre_name']] = {'menu_name': data['padre_name'], 'menu_id':data['padre_id']}
                # Añadir <menuitem>
                menus += """<menuitem name="%(padre_name)s" id="%(padre_id)s" parent="%(module_menu_id)s"/>""" % data
            # Buscar al padre (que ya habrá sido creado) y asignarlo
            data['padre_id'] = self.arrayGlobal['menuitems'][data['padre_name']]['menu_id']

        # Segun tenga padre o no...
        if data['padre_name'] is not None:
            menus += """<menuitem name="%(menu_name)s" id="%(menu_id)s" action="%(menu_action)s" parent="%(padre_id)s"/>""" % data
        else:
            menus += """<menuitem name="%(menu_name)s" id="%(menu_id)s" action="%(menu_action)s"/>""" % data
        return menus
### FIN MENUS ###################################################################################################################################

    def code_get(self):
        result = """##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields

"""
        for sk in self.klass_names:
            cname = sk.replace('.','_')
            result += "class %s(osv.osv):\n" % (cname,)
            if self.klasses[sk].comment:
                result += "    "+'"""'+self.klasses[sk].comment+'"""\n'
            result += "    _name = '%s'\n" % (sk,)


            parents = self.klasses[sk].parents
            if parents:
                result += "    _inherit = '"+parents[0]+"'\n"
            templates = self.klasses[sk].templates
            if templates:
                result += "    _inherits = {'"+templates[0]+"':'"+templates[0]+"'}\n"


            default = {}
            result += "    _columns = {\n"
            for sa,attr in self.klasses[sk].attributes :
                value = attr[2]
                if attr[3]:
                    value += ", help='%s'" % (attr[3].replace("'"," "),)
                attr_type = attr[0]
                result += "        '%s': fields.%s(%s),\n" % (sa, attr_type, value)
            result += "    }\n"

            if default:
                result += '    _defaults = {'
                for d in default:
                    result += "        '%s':lambda *args: '%s'\n" % (d, default[d])
                result += '    }'

            for so, op in self.klasses[sk].operations :
                pars = "self, cr, uid, ids"
                for p in op[2] :
                    pars = pars + ", " + p[0]
                result+="    def %s (%s) :\n" % (so, pars)
                if op[4]: result+="        \"\"\" %s \"\"\"\n" % op[4]
                result+="        # returns %s\n" % (op[0], )
            result += cname+"()\n\n"
        return result

    def end_render(self) :
        module = self.data_get()['module']
        zip = zipfile.ZipFile(self.filename, 'w')
        filewrite = {
                '__init__.py':self.init_get(),
                '__terp__.py':self.terp_get(),
                module+'.py': self.code_get(),
                module+'_view.xml': self.view_get()
        }
        for name,datastr in filewrite.items():
            info = zipfile.ZipInfo(module+'/'+name)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 2175008768
            zip.writestr(info, datastr)
        zip.close()
        ObjRenderer.end_render(self)


# dia-python keeps a reference to the renderer class and uses it on demand
dia.register_export ("PyDia Code Generation (OpenERP 6.1 v1)", "zip", OpenERPRenderer())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

