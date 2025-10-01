import { useState, useEffect } from 'react'
import { apiRequest } from '../services/api'
import ExternalUsersPanel from './ExternalUsersPanel'

const AdminPanel = () => {
    const [activeTab, setActiveTab] = useState('events')
    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [newEvent, setNewEvent] = useState({
        title: '',
        description: '',
        event_type: 'conference',
        modality: 'presencial',
        speaker: '',
        date: '',
        start_time: '',
        end_time: '',
        location: '',
        max_capacity: 100,
        meeting_link: ''
    })

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

    const handleCreateEvent = async (e) => {
        e.preventDefault()
        try {
            await apiRequest('/events/', {
                method: 'POST',
                body: newEvent
            })
            alert('Evento creado exitosamente')
            setShowCreateForm(false)
            setNewEvent({
                title: '',
                description: '',
                event_type: 'conference',
                modality: 'presencial',
                speaker: '',
                date: '',
                start_time: '',
                end_time: '',
                location: '',
                max_capacity: 100,
                meeting_link: ''
            })
            fetchEvents()
        } catch (error) {
            alert('Error al crear evento: ' + (error.response?.data?.error || 'Error desconocido'))
        }
    }

    if (loading) return <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando...</div>

    return (
        <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1e3a8a' }}>
                Panel de Administración
            </h2>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', borderBottom: '2px solid #e5e7eb' }}>
                <button
                    onClick={() => setActiveTab('events')}
                    style={{
                        padding: '0.75rem 1.5rem',
                        border: 'none',
                        backgroundColor: 'transparent',
                        color: activeTab === 'events' ? '#2563eb' : '#6b7280',
                        borderBottom: activeTab === 'events' ? '2px solid #2563eb' : 'none',
                        fontWeight: '600',
                        cursor: 'pointer',
                        marginBottom: '-2px'
                    }}
                >
                    Gestión de Eventos
                </button>
                <button
                    onClick={() => setActiveTab('external')}
                    style={{
                        padding: '0.75rem 1.5rem',
                        border: 'none',
                        backgroundColor: 'transparent',
                        color: activeTab === 'external' ? '#2563eb' : '#6b7280',
                        borderBottom: activeTab === 'external' ? '2px solid #2563eb' : 'none',
                        fontWeight: '600',
                        cursor: 'pointer',
                        marginBottom: '-2px'
                    }}
                >
                    Usuarios Externos
                </button>
            </div>

            {/* Panel de Eventos */}
            {activeTab === 'events' && (
                <div>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <button
                            onClick={() => setShowCreateForm(!showCreateForm)}
                            style={{
                                backgroundColor: '#2563eb',
                                color: 'white',
                                padding: '0.75rem 1.5rem',
                                borderRadius: '0.5rem',
                                border: 'none',
                                cursor: 'pointer',
                                fontWeight: '500'
                            }}
                        >
                            {showCreateForm ? 'Cancelar' : '+ Crear Nuevo Evento'}
                        </button>
                    </div>

                    {showCreateForm && (
                        <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                            <h3 style={{ marginBottom: '1rem', color: '#1e3a8a' }}>Crear Nuevo Evento</h3>
                            <form onSubmit={handleCreateEvent} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                <div style={{ gridColumn: '1 / -1' }}>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Título *
                                    </label>
                                    <input
                                        type="text"
                                        value={newEvent.title}
                                        onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                <div style={{ gridColumn: '1 / -1' }}>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Descripción *
                                    </label>
                                    <textarea
                                        value={newEvent.description}
                                        onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                                        required
                                        rows="3"
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Ponente *
                                    </label>
                                    <input
                                        type="text"
                                        value={newEvent.speaker}
                                        onChange={(e) => setNewEvent({ ...newEvent, speaker: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Tipo de Evento *
                                    </label>
                                    <select
                                        value={newEvent.event_type}
                                        onChange={(e) => setNewEvent({ ...newEvent, event_type: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    >
                                        <option value="conference">Conferencia</option>
                                        <option value="workshop">Taller</option>
                                        <option value="panel">Mesa Redonda</option>
                                        <option value="seminar">Seminario</option>
                                    </select>
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Modalidad *
                                    </label>
                                    <select
                                        value={newEvent.modality}
                                        onChange={(e) => setNewEvent({ ...newEvent, modality: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    >
                                        <option value="presencial">Presencial</option>
                                        <option value="online">En línea</option>
                                        <option value="hybrid">Híbrido</option>
                                    </select>
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Fecha *
                                    </label>
                                    <input
                                        type="date"
                                        value={newEvent.date}
                                        onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Hora Inicio *
                                    </label>
                                    <input
                                        type="time"
                                        value={newEvent.start_time}
                                        onChange={(e) => setNewEvent({ ...newEvent, start_time: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Hora Fin *
                                    </label>
                                    <input
                                        type="time"
                                        value={newEvent.end_time}
                                        onChange={(e) => setNewEvent({ ...newEvent, end_time: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Ubicación *
                                    </label>
                                    <input
                                        type="text"
                                        value={newEvent.location}
                                        onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
                                        required
                                        placeholder="Aula, Salón o Enlace"
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                        Capacidad Máxima
                                    </label>
                                    <input
                                        type="number"
                                        value={newEvent.max_capacity}
                                        onChange={(e) => setNewEvent({ ...newEvent, max_capacity: parseInt(e.target.value) })}
                                        min="1"
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                    />
                                </div>
                                {(newEvent.modality === 'online' || newEvent.modality === 'hybrid') && (
                                    <div style={{ gridColumn: '1 / -1' }}>
                                        <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                                            Enlace de Reunión
                                        </label>
                                        <input
                                            type="url"
                                            value={newEvent.meeting_link}
                                            onChange={(e) => setNewEvent({ ...newEvent, meeting_link: e.target.value })}
                                            placeholder="https://zoom.us/..."
                                            style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' }}
                                        />
                                    </div>
                                )}
                                <div style={{ gridColumn: '1 / -1' }}>
                                    <button
                                        type="submit"
                                        style={{
                                            backgroundColor: '#059669',
                                            color: 'white',
                                            padding: '0.75rem 1.5rem',
                                            borderRadius: '0.5rem',
                                            border: 'none',
                                            cursor: 'pointer',
                                            fontWeight: '500',
                                            width: '100%'
                                        }}
                                    >
                                        Crear Evento
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', overflow: 'hidden', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                        <h3 style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb', margin: 0 }}>Eventos Registrados</h3>
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
            )}

            {/* Panel de Usuarios Externos */}
            {activeTab === 'external' && <ExternalUsersPanel />}
        </div>
    )
}

export default AdminPanel