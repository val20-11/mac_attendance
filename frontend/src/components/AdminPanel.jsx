import { useState, useEffect } from 'react'
import { apiRequest } from '../services/api'

const AdminPanel = () => {
    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchEvents()
    }, [])

    const fetchEvents = async () => {
        try {
            const response = await apiRequest('/events/')
            setEvents(response.results || response)
        } catch (error) {
            console.error('Error fetching events:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando eventos...</div>

    return (
        <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1e3a8a' }}>
                Panel de Administración
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
                <div style={{ backgroundColor: '#f9f9f9', padding: '1rem', borderRadius: '0.5rem' }}>
                    <h3 style={{ color: '#374151' }}>Estadísticas</h3>
                    <p style={{ color: '#1e3a8a' }}>Total eventos: {events.length}</p>
                    <p style={{ color: '#1e3a8a' }}>Eventos activos: {events.filter(e => e.is_active).length}</p>
                </div>
                <div style={{ backgroundColor: '#f9f9f9', padding: '1rem', borderRadius: '0.5rem' }}>
                    <h3 style={{ color: '#374151' }}>Acciones rápidas</h3>
                    <button style={{ display: 'block', marginBottom: '0.5rem', padding: '0.5rem', backgroundColor: '#2563eb', color: 'white', border: 'none', borderRadius: '0.25rem', cursor: 'pointer' }}>
                        Importar datos
                    </button>
                    <button style={{ display: 'block', padding: '0.5rem', backgroundColor: '#059669', color: 'white', border: 'none', borderRadius: '0.25rem', cursor: 'pointer' }}>
                        Exportar reportes
                    </button>
                </div>
            </div>

            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', overflow: 'hidden', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb', margin: 0 }}>Eventos registrados</h3>
                {events.length > 0 ? (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead style={{ backgroundColor: '#f9fafb' }}>
                            <tr>
                                <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Título</th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Ponente</th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Fecha</th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Modalidad</th>
                            </tr>
                        </thead>
                        <tbody>
                            {events.map((event) => (
                                <tr key={event.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                                    <td style={{ padding: '1rem', fontSize: '0.875rem', fontWeight: '500', color: '#1e3a8a' }}>{event.title}</td>
                                    <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#374151' }}>{event.speaker}</td>
                                    <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>{event.date}</td>
                                    <td style={{ padding: '1rem', fontSize: '0.875rem' }}>
                                        <span style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', fontWeight: '600', borderRadius: '9999px', backgroundColor: event.modality === 'presencial' ? '#dcfdf7' : '#dbeafe', color: event.modality === 'presencial' ? '#065f46' : '#1e40af' }}>
                                            {event.modality}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>No hay eventos registrados</p>
                )}
            </div>
        </div>
    )
}

export default AdminPanel