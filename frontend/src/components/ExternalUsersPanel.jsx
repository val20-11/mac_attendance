import { useState, useEffect } from 'react'
import { apiRequest } from '../services/api'

const ExternalUsersPanel = () => {
    const [pendingUsers, setPendingUsers] = useState([])
    const [approvedUsers, setApprovedUsers] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('pending')

    useEffect(() => {
        fetchExternalUsers()
    }, [])

    const fetchExternalUsers = async () => {
        try {
            const response = await apiRequest('/events/external/list/')
            const users = response || []

            setPendingUsers(users.filter(u => u.status === 'pending'))
            setApprovedUsers(users.filter(u => u.status === 'approved'))
        } catch (error) {
            console.error('Error fetching external users:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleApprove = async (userId) => {
        try {
            await apiRequest(`/events/external/${userId}/approve/`, {
                method: 'POST',
                body: { action: 'approve' }
            })
            alert('Usuario aprobado exitosamente')
            fetchExternalUsers()
        } catch (error) {
            alert('Error al aprobar usuario')
        }
    }

    const handleReject = async (userId) => {
        const reason = prompt('Motivo del rechazo (opcional):')
        try {
            await apiRequest(`/events/external/${userId}/approve/`, {
                method: 'POST',
                body: { action: 'reject', reason: reason || '' }
            })
            alert('Usuario rechazado')
            fetchExternalUsers()
        } catch (error) {
            alert('Error al rechazar usuario')
        }
    }

    if (loading) return <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando...</div>

    return (
        <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem' }}>
                Gestión de Usuarios Externos
            </h2>

            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                <button
                    onClick={() => setActiveTab('pending')}
                    style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        border: 'none',
                        backgroundColor: activeTab === 'pending' ? '#2563eb' : '#e5e7eb',
                        color: activeTab === 'pending' ? 'white' : '#374151',
                        cursor: 'pointer',
                        fontWeight: '500'
                    }}
                >
                    Pendientes ({pendingUsers.length})
                </button>
                <button
                    onClick={() => setActiveTab('approved')}
                    style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        border: 'none',
                        backgroundColor: activeTab === 'approved' ? '#2563eb' : '#e5e7eb',
                        color: activeTab === 'approved' ? 'white' : '#374151',
                        cursor: 'pointer',
                        fontWeight: '500'
                    }}
                >
                    Aprobados ({approvedUsers.length})
                </button>
            </div>

            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', overflow: 'hidden', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                {activeTab === 'pending' && (
                    pendingUsers.length > 0 ? (
                        pendingUsers.map((user) => (
                            <div key={user.id} style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{user.full_name}</h3>
                                        <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                                            <strong>Email:</strong> {user.email}
                                        </p>
                                        <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                                            <strong>Institución:</strong> {user.institution}
                                        </p>
                                        {user.position && (
                                            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                                                <strong>Cargo:</strong> {user.position}
                                            </p>
                                        )}
                                        <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
                                            <strong>Motivo:</strong> {user.reason}
                                        </p>
                                        <p style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.5rem' }}>
                                            ID Temporal: {user.temporary_id}
                                        </p>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', justifyContent: 'center' }}>
                                        <button
                                            onClick={() => handleApprove(user.id)}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                backgroundColor: '#059669',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '0.375rem',
                                                cursor: 'pointer',
                                                fontWeight: '500'
                                            }}
                                        >
                                            Aprobar
                                        </button>
                                        <button
                                            onClick={() => handleReject(user.id)}
                                            style={{
                                                padding: '0.5rem 1rem',
                                                backgroundColor: '#dc2626',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '0.375rem',
                                                cursor: 'pointer',
                                                fontWeight: '500'
                                            }}
                                        >
                                            Rechazar
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                            No hay solicitudes pendientes
                        </p>
                    )
                )}

                {activeTab === 'approved' && (
                    approvedUsers.length > 0 ? (
                        approvedUsers.map((user) => (
                            <div key={user.id} style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb' }}>
                                <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{user.full_name}</h3>
                                <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                                    <strong>Email:</strong> {user.email}
                                </p>
                                <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                                    <strong>Institución:</strong> {user.institution}
                                </p>
                                <p style={{ fontSize: '0.75rem', color: '#059669', marginTop: '0.5rem', fontWeight: '600' }}>
                                    ID: {user.temporary_id}
                                </p>
                            </div>
                        ))
                    ) : (
                        <p style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                            No hay usuarios aprobados
                        </p>
                    )
                )}
            </div>
        </div>
    )
}

export default ExternalUsersPanel