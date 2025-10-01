import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import AdminPanel from './AdminPanel'
import AttendancePanel from './AttendancePanel'
import StudentPanel from './StudentPanel'

const Dashboard = () => {
    const { user, logout } = useAuth()
    const [activePanel, setActivePanel] = useState('admin')

    const isAssistant = user.profile?.user_type === 'assistant'

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
                        Sistema MAC - {isAssistant ? 'Asistente' : 'Estudiante'}
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

            {isAssistant ? (
                <div style={{ display: 'flex' }}>
                    <div style={{ width: '250px', backgroundColor: 'white', minHeight: 'calc(100vh - 4rem)', boxShadow: '1px 0 3px 0 rgba(0, 0, 0, 0.1)' }}>
                        <nav style={{ padding: '1rem 0' }}>
                            <button
                                onClick={() => setActivePanel('admin')}
                                style={{
                                    width: '100%',
                                    textAlign: 'left',
                                    padding: '0.75rem 1rem',
                                    border: 'none',
                                    backgroundColor: activePanel === 'admin' ? '#dbeafe' : 'transparent',
                                    color: activePanel === 'admin' ? '#1e40af' : '#6b7280',
                                    fontSize: '0.875rem',
                                    fontWeight: '500',
                                    cursor: 'pointer'
                                }}
                            >
                                📊 Administración
                            </button>
                            <button
                                onClick={() => setActivePanel('attendance')}
                                style={{
                                    width: '100%',
                                    textAlign: 'left',
                                    padding: '0.75rem 1rem',
                                    border: 'none',
                                    backgroundColor: activePanel === 'attendance' ? '#dbeafe' : 'transparent',
                                    color: activePanel === 'attendance' ? '#1e40af' : '#6b7280',
                                    fontSize: '0.875rem',
                                    fontWeight: '500',
                                    cursor: 'pointer'
                                }}
                            >
                                📝 Registro de Asistencia
                            </button>
                        </nav>
                    </div>

                    <div style={{ flex: 1, padding: '2rem' }}>
                        {activePanel === 'admin' && <AdminPanel />}
                        {activePanel === 'attendance' && <AttendancePanel />}
                    </div>
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