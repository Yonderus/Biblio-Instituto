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
        "security/library_security_rules.xml",
        "views/library_author.xml",
        "views/library_book.xml",
        "views/library_publisher.xml",
        "views/library_loan.xml",
        "views/res_partner_library.xml",
        "views/library_menus.xml",
        "reports/report_loan.xml"
    ],
   
    # Indica si aparece como aplicacion en el menu principal.
    "application": True,
    "installable": True,
    # Datos de demo: solo se cargan en instancias con modo demo activado, no en producción.
    "demo": ["data/library_demo_clean.xml"],
}