# -*- coding: utf-8 -*-
{
    # Nombre del modulo que se muestra en Odoo.
    "name": "Library Instituto",
    "summary": "Gestión de biblioteca para centros educativos",
    "description": "Módulo Odoo para digitalizar la gestión de préstamos, catálogo de libros y usuarios de la biblioteca de un instituto. Incluye control de disponibilidad, renovaciones, vencimientos y generación de comprobantes PDF.",
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
        "data/library_demo_clean.xml",
        "views/library_loan.xml",
        "views/library_loan_wizard.xml",
        "views/res_partner_library.xml",
        "views/library_menus.xml",
        "reports/report_loan.xml"
    ],
   
    # Indica si aparece como aplicacion en el menu principal.
    "application": True,
    "installable": True,
}