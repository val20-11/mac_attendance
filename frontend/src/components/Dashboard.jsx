import { useAuth } from '../contexts/AuthContext'
import AdminPanel from './AdminPanel'
import AttendancePanel from './AttendancePanel'
import StudentPanel from './StudentPanel'

const Dashboard = () => {
    const { user, logout } = useAuth()

    const isAssistant = user.profile?.user_type === 'assistant'
    const isAdmin = user.is_staff || user.is_superuser

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6' }}>
            <nav style={{
                backgroundColor: 'white',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                borderBottom: '1px solid #e5e7eb'
            }}>
                <div style={{
                    maxWidth: '1200px',
                    margin: '0 auto',
                    padding: '0 1rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    height: '4rem'
                }}>
                    <h1 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827' }}>
                        Sistema MAC - {isAdmin ? 'Administrador' : isAssistant ? 'Asistente' : 'Estudiante'}
                    </h1>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span style={{ color: '#374151' }}>Hola, {user.profile?.full_name || user.first_name}</span>
                        <button
                            onClick={logout}
                            style={{
                                backgroundColor: '#dc2626',
                                color: 'white',
                                padding: '0.5rem 1rem',
                                borderRadius: '0.375rem',
                                border: 'none',
                                fontSize: '0.875rem',
                                cursor: 'pointer'
                            }}
                        >
                            Cerrar Sesión
                        </button>
                    </div>
                </div>
            </nav>

            {isAdmin ? (
                <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
                    <AdminPanel />
                </div>
            ) : isAssistant ? (
                <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
                    <AttendancePanel />
                </div>
            ) : (
                <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
                    <StudentPanel />
                </div>
            )}
        </div>
    )
}

export default Dashboard