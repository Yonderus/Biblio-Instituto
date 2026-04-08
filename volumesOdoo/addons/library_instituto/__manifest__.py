# -*- coding: utf-8 -*-
{
    # Nombre del modulo que se muestra en Odoo.
    "name": "Library Instituto",
    # Version del modulo.
    "version": "1.0",
    # Modulos requeridos para que este funcione.
    "depends": ["base"],
    # Autor del modulo.
    "author": "Javier Gisbert Talboom",
    "license": "LGPL-3",
    # Archivos XML/CSV que se cargan al instalar el modulo.
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/library_author.xml"
    ],
    # Indica si aparece como aplicacion en el menu principal.
    "application": True,
    "installable": True,
}