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
    # Archivos XML/CSV que se cargan al instalar el modulo.
    "data": [
        "views/library_author_views.xml",
        "views/library_book_views.xml",
        "views/library_publisher_views.xml",
        "security/ir.model.access.csv",
        "security/security.xml"
    ],
    # Indica si aparece como aplicacion en el menu principal.
    "application": True,
}