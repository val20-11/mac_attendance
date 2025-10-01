# Sistema de Asistencia MAC - FES Acatlán

Sistema de gestión de asistencia para ponencias y eventos académicos de la Maestría en Arquitectura de Cómputo (MAC).

## 🚀 Características

- **Gestión de Eventos**: Crear y administrar ponencias, talleres, seminarios
- **Registro de Asistencia**: Manual, por código de barras o usuarios externos
- **Panel de Estudiantes**: Consulta de estadísticas y eventos disponibles
- **Panel de Asistentes**: Administración completa y registro de asistencias
- **Usuarios Externos**: Sistema de aprobación para asistentes externos
- **Estadísticas**: Seguimiento de porcentaje de asistencia por estudiante
- **Seguridad Avanzada**: JWT, rate limiting, auditoría completa
- **Sistema de Auditoría**: Registro automático de eventos de seguridad

## 📋 Requisitos Previos

- Python 3.10+
- Node.js 18+
- npm o yarn

## 🛠️ Instalación

### Backend (Django)

1. Crear entorno virtual:
```bash
cd backend
python -m venv venv
```

2. Activar entorno virtual:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Ejecutar migraciones:
```bash
python manage.py migrate
```

6. Crear superusuario (opcional):
```bash
python manage.py createsuperuser
```

7. Ejecutar servidor:
```bash
python manage.py runserver
```

El backend estará disponible en `http://127.0.0.1:8000`

### Frontend (React + Vite)

1. Instalar dependencias:
```bash
cd frontend
npm install
```

2. Ejecutar servidor de desarrollo:
```bash
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 📁 Estructura del Proyecto

```
mac_attendance/
├── backend/
│   ├── attendance/          # App de registro de asistencias
│   ├── authentication/      # App de autenticación y auditoría
│   ├── events/             # App de eventos y usuarios externos
│   ├── mac_attendance/     # Configuración principal y middleware
│   ├── scripts/            # Scripts de utilidad
│   │   ├── check_production.py   # Verificar config de producción
│   │   └── test_ratelimit.py     # Probar rate limiting
│   ├── static/             # Archivos estáticos
│   ├── media/              # Archivos subidos
│   ├── logs/               # Archivos de log (no trackeados)
│   ├── requirements.txt    # Dependencias Python
│   └── .env.example       # Ejemplo de variables de entorno
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── contexts/      # Contextos (AuthContext)
│   │   └── services/      # Servicios API
│   └── package.json       # Dependencias Node
├── docs/                   # Documentación del proyecto
│   ├── SECURITY.md         # Guía de seguridad completa
│   ├── RATE_LIMITING.md    # Documentación rate limiting
│   └── AUDIT.md            # Sistema de auditoría
└── README.md
```

## 🔐 Credenciales de Acceso

### Panel de Administración Django
- URL: `http://127.0.0.1:8000/admin/`
- Usuario: [crear con createsuperuser]

### Aplicación Web
- **Asistentes**: Número de cuenta + contraseña
- **Estudiantes**: Número de cuenta + contraseña
- **Externos**: Registro desde el formulario público

## 📊 Modelos Principales

### UserProfile
- Tipo de usuario (estudiante/asistente)
- Número de cuenta (7 dígitos)
- Información personal

### Event
- Título, descripción, ponente
- Fecha, hora de inicio/fin
- Modalidad (presencial/online/híbrido)
- Capacidad máxima

### Attendance
- Estudiante o usuario externo
- Evento asociado
- Método de registro (manual/barcode/external)
- Registrado por (asistente)

### ExternalUser
- Usuarios externos pendientes de aprobación
- Información de institución y motivo
- ID temporal único

## 🔧 Configuración Adicional

### Variables de Entorno (.env)
```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### CORS
El backend está configurado para aceptar peticiones desde:
- `http://localhost:5173` (desarrollo)
- `http://127.0.0.1:5173` (desarrollo)

## 🔒 Seguridad

Este proyecto implementa múltiples capas de seguridad:

### Autenticación y Autorización
- ✅ **JWT (JSON Web Tokens)** para autenticación stateless
- ✅ **Control de acceso basado en roles** (estudiante/asistente)
- ✅ **Tokens de corta duración** (1 hora) con refresh tokens (7 días)

### Protección contra Ataques
- ✅ **Rate Limiting**: Límites en todos los endpoints críticos
  - Login: 5 intentos/minuto por IP
  - Registro externo: 3/hora por IP
  - Ver `docs/RATE_LIMITING.md` para detalles
- ✅ **Headers de seguridad** HTTP (HSTS, X-Frame-Options, etc.)
- ✅ **Sanitización automática** de datos sensibles en logs

### Sistema de Auditoría
- ✅ **Registro automático** de eventos de seguridad
- ✅ **Trazabilidad completa**: IP, user agent, timestamp
- ✅ **Logs inmutables** consultables desde Django Admin
- ✅ Ver `docs/AUDIT.md` para documentación completa

### Documentación de Seguridad
- 📄 `docs/SECURITY.md` - Guía de seguridad y checklist de producción
- 📄 `docs/RATE_LIMITING.md` - Configuración de rate limiting
- 📄 `docs/AUDIT.md` - Sistema de auditoría

## 🚧 Mejoras Futuras

- [x] Implementar JWT para autenticación
- [ ] Agregar exportación de reportes (CSV/PDF)
- [ ] Implementar lector de códigos de barras
- [ ] Notificaciones por email
- [ ] Panel de estadísticas avanzadas
- [ ] Tests unitarios y de integración
- [ ] Dockerización del proyecto

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, contacta a: [tu-email@ejemplo.com]