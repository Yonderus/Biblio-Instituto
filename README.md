# 📚 Biblio-Instituto

> **Sistema inteligente de gestión de bibliotecas para instituciones educativas**  
> Construido con Odoo 18 + PostgreSQL en contenedores Docker

---

## 🎯 Visión General

**Biblio-Instituto** es una aplicación empresarial completa para administrar bibliotecas en institutos educativos. Automatiza préstamos, controla disponibilidad de libros, gestiona usuarios y genera reportes de forma eficiente.

### ✨ Características Principales

- 📖 **Catálogo Digital**: Gestión completa de libros con metadatos, ISBN, portadas y géneros
- 👥 **Gestión de Usuarios**: Alumnos, docentes y personal administrativo con límites de préstamos
- 🔄 **Sistema de Préstamos**: Automatización inteligente con control de retrasos y renovaciones
- 📊 **Reportes**: Generación de reportes de préstamos y disponibilidad
- 🛡️ **Control de Acceso**: Permisos granulares por rol de usuario
- 🎨 **Interfaz Intuitiva**: Vistas kanban, listas y formularios en Odoo

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│         ODOO 18 (Web Port: 8069)            │
│  ┌─────────────────────────────────────┐   │
│  │    Módulo: Library Instituto        │   │
│  │  ┌──────────────────────────────┐   │   │
│  │  │   Modelos ORM               │   │   │
│  │  │  • LibraryBook              │   │   │
│  │  │  • LibraryAuthor            │   │   │
│  │  │  • LibraryPublisher         │   │   │
│  │  │  • LibraryLoan              │   │   │
│  │  │  • ResPartner (extendido)   │   │   │
│  │  └──────────────────────────────┘   │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
              ▼ (Conexión TCP)
┌─────────────────────────────────────────────┐
│    PostgreSQL 15 (Base de Datos)            │
│  ┌─────────────────────────────────────┐   │
│  │  library_libro                      │   │
│  │  library_author                     │   │
│  │  library_publisher                  │   │
│  │  library_loan                       │   │
│  │  res_partner (usuarios)             │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🔑 Puntos Clave del Código

### 1️⃣ **Modelo de Libros** (`library.book`)

```python
# Representa cada libro del catálogo
title              → Título del libro
isbn               → ISBN-13 (identificador único)
total_copies       → Número de ejemplares físicos
genre              → Narrativa, Poesía, Teatro, etc.
state              → disponible | prestado | reparación | baja
cover_image        → Portada (max 300x400px)
available_copies   → CÁLCULO automático
active_loans_count → CÁLCULO automático
```

**Lógica importante:**
```python
available_copies = total_copies - (préstamos activos + vencidos)
# Se actualiza en TIEMPO REAL cuando:
# • Se crea un préstamo
# • Se devuelve un libro
# • Se renueva un préstamo
```

---

### 2️⃣ **Modelo de Préstamos** (`library.loan`)

```python
# Cada préstamo es un movimiento de libro
loan_date              → Fecha de préstamo
expected_return_date   → Fecha límite de devolución (+15 días)
real_return_date       → Cuándo realmente se devuelve
state                  → activo | devuelto | vencido
late_days              → Días de retraso (CÁLCULO automático)
renewed                → ¿Ha sido renovado?
```

**Estados automáticos:**
```
├─ Activo     → Libro prestado, dentro del plazo
├─ Vencido    → Pasó la fecha límite, no devuelto
└─ Devuelto   → Ya se devolvió el libro
```

**Validación clave:**
```python
# Previene que un usuario supere su límite de préstamos
def _check_loan_limit(self):
    active_loans = user.library_loan_ids.filtered(
        lambda item: item.state in ["activo", "vencido"]
    )
    if len(active_loans) >= user.library_max_loans:
        raise ValidationError("Límite de préstamos alcanzado")
```

---

### 3️⃣ **Modelo de Usuarios** (`res.partner` extendido)

```python
# Extensión de contactos con campos de biblioteca
library_card_number        → Nº de carnet único
library_max_loans          → Máximo préstamos simultáneos (defecto: 3)
library_active_loans       → CÁLCULO de préstamos en curso
library_user_type          → Alumno | Docente | Admin
library_course_group       → "2º ESO-A", "1º Bach-B", etc.
```

**Cálculo inteligente:**
```python
library_active_loans = contar préstamos con state in ["activo", "vencido"]
# Se actualiza automáticamente en los cambios
# Visible en el formulario como información readonly
```

---

### 4️⃣ **Wizard de Préstamos Múltiples** (`library.loan.wizard`)

```python
# Asistente para prestar varios libros a la vez
# Usa modelos transitorios (se borran solos)

user_id         → A quién se le prestan todos
line_ids        → Lista de libros a prestar

action_confirm():
    └─→ Recorre cada línea y crea un library.loan
    └─→ Reutiliza validaciones automáticas
```

**Uso típico:**
```
1. Alumno llega con 3 libros
2. Personal abre wizard
3. Selecciona alumno
4. Añade los 3 libros a las líneas
5. Pulsa "Confirmar"
6. ¡Se crean los 3 préstamos de golpe!
```

---

### 5️⃣ **Modelos Auxiliares**

| Modelo | Propósito | Restricciones |
|--------|-----------|--------------|
| `library.author` | Autores de libros | Nombre único |
| `library.publisher` | Editoriales | Nombre único, teléfono obligatorio |
| `library.book` | Catálogo de libros | ISBN + Título requeridos |

---

## 📋 Flujos de Negocio Principales

### Flujo: Prestar un Libro
```
1. Personal busca al usuario en Odoo
2. Abre el formulario del usuario
3. Ve "Préstamos activos" (computed)
4. Si no alcanzó límite → puede prestar
5. Crea loan manual o usa wizard
6. Sistema calcula automáticamente:
   ├─ expected_return_date (+15 días)
   ├─ available_copies del libro
   └─ library_active_loans del usuario
```

### Flujo: Devolver un Libro
```
1. Alumno devuelve libro
2. Personal abre el préstamo
3. Rellena real_return_date
4. Sistema calcula:
   ├─ state → "devuelto"
   ├─ late_days (si hay retraso)
   └─ available_copies aumenta
```

### Flujo: Detectar Retrasos
```
1. Cada día, el sistema chequea:
   └─ Si today > expected_return_date
   └─ Y real_return_date es vacío
   └─ Entonces state = "vencido"
   
2. Campo late_days = today - expected_return_date
3. Visible en reportes para sanciones
```

---

## 🚀 Instalación Rápida

### Requisitos
- Docker & Docker Compose
- (Opcional) Git

### Pasos

```bash
# 1. Clonar
git clone https://github.com/Yonderus/Biblio-Instituto.git
cd Biblio-Instituto

# 2. Iniciar servicios
docker-compose up -d

# 3. Esperar ~10 segundos a que Odoo inicie
# (Ver logs: docker-compose logs -f web)

# 4. Acceder
# http://localhost:8069
```

### Usuarios del sistema

| Correo | Contraseña | Rol Odoo | Grupo biblioteca |
|--------|-----------|----------|-----------------|
| `javigisbert05@gmail.com` | `biblioinstituto` | Administrador | Todos |
| `fonsi.biblio@biblio.com` | `fonsi` | Usuario interno | Bibliotecario |
| `benito.biblio@bibio.com` | `Benito` | Usuario interno | Usuario biblioteca |

---

## 📦 Servicios Docker

### Odoo 18 (Web)
```yaml
Puerto: 8069
Usuario BD: odoo
Contraseña: odoo
Volúmenes:
  ├─ ./volumesOdoo/addons      → Módulos personalizados
  ├─ odoo_filestore            → Adjuntos y documentos
  └─ odoo_sessions             → Sesiones de usuarios
```

### PostgreSQL 15 (Base de Datos)
```yaml
Host: db (interno en Docker)
Puerto: 5432
Usuario: odoo
Contraseña: odoo
BD: postgres
Volumen: postgres_data
```

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f web

# Solo BD
docker-compose logs -f db

# Reiniciar Odoo
docker-compose restart web

# Parar todo
docker-compose down

# Parar Y borrar volúmenes (⚠️ BORRA DATOS)
docker-compose down -v

# Reconstruir imágenes
docker-compose up -d --build
```

---

## 📊 Estructura de Directorios

```
Biblio-Instituto/
├── docker-compose.yml                    ← Configuración de servicios
├── .gitignore                            ← Archivos ignorados
└── volumesOdoo/
    ├── addons/
    │   └── library_instituto/            ← MÓDULO PRINCIPAL
    │       ├── __manifest__.py           ← Metadatos del módulo
    │       ├── __init__.py               ← Carga de modelos
    │       ├── models/
    │       │   ├── library_book.py       ← Modelo de libros
    │       │   ├── library_author.py     ← Modelo de autores
    │       │   ├── library_publisher.py  ← Modelo de editoriales
    │       │   ├── library_loan.py       ← Modelo de préstamos
    │       │   ├── library_loan_wizard.py← Wizard múltiple
    │       │   └── res_partner.py        ← Extensión de usuarios
    │       ├── views/
    │       │   ├── library_book.xml      ← Formularios y listas
    │       │   ├── library_loan.xml
    │       │   └── ... (más vistas)
    │       ├── security/                 ← Control de acceso
    │       ├── data/                     ← Datos de demo
    │       └── reports/                  ← Reportes PDF
    ├── dataPostgreSQL/                   ← BD persistente (git-ignored)
    └── odoo-data/                        ← Datos de Odoo (git-ignored)
```

---

## 🔐 Configuración en Producción

⚠️ **IMPORTANTE:** La configuración actual es para desarrollo.

Para producción, cambia en `docker-compose.yml`:

```yaml
# ❌ ACTUAL (desarrollo)
environment:
  - PASSWORD=odoo

# ✅ PRODUCCIÓN
environment:
  - PASSWORD=TuContraseñaSegura2024!
```

**También:**
- Usa volúmenes con backup automático
- Configura SSL/TLS en Odoo
- Cambia el usuario root por odoo en el contenedor
- Activa autenticación LDAP/SAML si es necesario

---

## 📈 Funcionalidades Avanzadas

### ✅ Cálculos Automáticos
- Ejemplares disponibles se actualizan en tiempo real
- Estados de préstamos cambian automáticamente
- Días de retraso se calculan dinámicamente

### ✅ Validaciones Integradas
- ISBN único por libro
- Carnet de biblioteca único
- Límite de préstamos por usuario
- Restricción de devoluciones (no se pueden borrar)

### ✅ Permisos Granulares
- Control de acceso por rol (`security/`)
- Reglas de seguridad específicas (`security/library_security_rules.xml`)

### ✅ Reportes
- Reporte de préstamos (PDF)
- Listados de morosos
- Disponibilidad de catálogo

---

## 👨‍💻 Desarrollo

### Estructura del módulo

El módulo `library_instituto` sigue la convención ORM de Odoo:

1. **Models** → Lógica de negocio (ORM)
2. **Views** → Interfaz (XML)
3. **Security** → Permisos (CSV + XML)
4. **Reports** → Reportes (XML)
5. **Data** → Datos de demo/iniciales

### Extensiones recomendadas

- Notificaciones por email a usuarios con retrasos
- Integración con escáner de códigos de barras
- Multas automáticas por retrasos
- Reservas de libros
- Estadísticas de uso por género/autor

---

## 📧 Contacto & Créditos

**Autor:** Javier Gisbert Talboom  
**Licencia:** LGPL-3  
**Repositorio:** [github.com/Yonderus/Biblio-Instituto](https://github.com/Yonderus/Biblio-Instituto)

---

## 📝 Notas Finales

Este proyecto demuestra:
- ✅ Diseño ORM avanzado en Odoo
- ✅ Cálculos automáticos con `@depends`
- ✅ Validaciones con constraints
- ✅ Wizards transitorios para operaciones complejas
- ✅ Containerización con Docker
- ✅ Buenas prácticas de seguridad

**¿Necesitas ayuda?** Abre un issue en el repositorio 👉 [Issues](https://github.com/Yonderus/Biblio-Instituto/issues)

---

*Última actualización: Junio 2026*