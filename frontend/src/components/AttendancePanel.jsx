import { useState, useEffect } from 'react'
import { apiRequest } from '../services/api'

const AttendancePanel = () => {
    const [selectedEvent, setSelectedEvent] = useState('')
    const [studentAccount, setStudentAccount] = useState('')
    const [events, setEvents] = useState([])
    const [recentAttendances, setRecentAttendances] = useState([])
    const [message, setMessage] = useState('')
    const [messageType, setMessageType] = useState('')
    const [showExternalForm, setShowExternalForm] = useState(false)
    const [externalUser, setExternalUser] = useState({
        account_number: '',
        full_name: ''
    })
    const [searchQuery, setSearchQuery] = useState('')
    const [searchResults, setSearchResults] = useState([])
    const [searching, setSearching] = useState(false)

    useEffect(() => {
        fetchEvents()
        fetchRecentAttendances()
    }, [])

    const fetchEvents = async () => {
        try {
            const response = await apiRequest('/events/')
            setEvents(response.results || response)
        } catch (error) {
            console.error('Error fetching events:', error)
        }
    }

    const fetchRecentAttendances = async () => {
        try {
            const response = await apiRequest('/attendance/recent/')
            setRecentAttendances(response)
        } catch (error) {
            console.error('Error fetching recent attendances:', error)
        }
    }

    const registerAttendance = async () => {
        if (!selectedEvent || !studentAccount) {
            setMessage('Selecciona un evento e ingresa el número de cuenta')
            setMessageType('error')
            return
        }

        try {
            const response = await apiRequest('/attendance/', {
                method: 'POST',
                body: {
                    event_id: selectedEvent,
                    account_number: studentAccount,
                    registration_method: 'manual'
                }
            })

            setMessage(response.message)
            setMessageType('success')
            setStudentAccount('')

            fetchRecentAttendances()

        } catch (error) {
            const errorMessage = error.response?.data?.error || 'Error de conexión'
            setMessage(`Error: ${errorMessage}`)
            setMessageType('error')
        }
    }

    const createExternalUser = async (e) => {
        e.preventDefault()

        if (!externalUser.account_number || !externalUser.full_name) {
            setMessage('Número de cuenta y nombre completo son requeridos')
            setMessageType('error')
            return
        }

        if (!/^\d{7}$/.test(externalUser.account_number)) {
            setMessage('El número de cuenta debe tener exactamente 7 dígitos')
            setMessageType('error')
            return
        }

        try {
            const response = await apiRequest('/events/external/register/', {
                method: 'POST',
                body: externalUser
            })

            setMessage(`Usuario externo creado: ${response.full_name} - Cuenta: ${response.account_number}`)
            setMessageType('success')
            setExternalUser({ account_number: '', full_name: '' })
            setShowExternalForm(false)

        } catch (error) {
            const errorMessage = error.response?.data?.error || 'Error al crear usuario externo'
            setMessage(`Error: ${errorMessage}`)
            setMessageType('error')
        }
    }

    const searchExternalUsers = async () => {
        if (!searchQuery.trim()) {
            setSearchResults([])
            return
        }

        setSearching(true)
        try {
            const response = await apiRequest(`/events/external/search/?q=${encodeURIComponent(searchQuery)}`)
            setSearchResults(response.results || [])
            if (response.count === 0) {
                setMessage('No se encontraron usuarios externos')
                setMessageType('error')
            }
        } catch (error) {
            const errorMessage = error.response?.data?.error || 'Error al buscar usuarios externos'
            setMessage(`Error: ${errorMessage}`)
            setMessageType('error')
            setSearchResults([])
        } finally {
            setSearching(false)
        }
    }

    const handleSearchKeyPress = (e) => {
        if (e.key === 'Enter') {
            searchExternalUsers()
        }
    }

    return (
        <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1e3a8a' }}>
                Registro de Asistencia
            </h2>

            {message && (
                <div style={{
                    padding: '1rem',
                    marginBottom: '1rem',
                    borderRadius: '0.5rem',
                    backgroundColor: messageType === 'success' ? '#dcfdf7' : '#fef2f2',
                    color: messageType === 'success' ? '#065f46' : '#991b1b',
                    border: `1px solid ${messageType === 'success' ? '#10b981' : '#ef4444'}`,
                    position: 'relative'
                }}>
                    {message}
                    <button
                        onClick={() => setMessage('')}
                        style={{
                            position: 'absolute',
                            right: '10px',
                            top: '10px',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '18px',
                            fontWeight: 'bold'
                        }}
                    >
                        ×
                    </button>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
                <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                    <h3 style={{ marginBottom: '1rem', color: '#374151' }}>Registrar Asistencia Manual</h3>

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#1e3a8a' }}>
                            Seleccionar Evento
                        </label>
                        <select
                            value={selectedEvent}
                            onChange={(e) => setSelectedEvent(e.target.value)}
                            style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                        >
                            <option value="">Selecciona un evento...</option>
                            {events.map((event) => (
                                <option key={event.id} value={event.id}>
                                    {event.title} - {event.date}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#1e3a8a' }}>
                            Número de Cuenta (7 dígitos)
                        </label>
                        <input
                            type="text"
                            value={studentAccount}
                            onChange={(e) => {
                                const value = e.target.value.replace(/\D/g, '').slice(0, 7)
                                setStudentAccount(value)
                            }}
                            placeholder="1234567"
                            maxLength="7"
                            style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                        />
                    </div>

                    <button
                        onClick={registerAttendance}
                        style={{ width: '100%', backgroundColor: '#059669', color: 'white', padding: '0.75rem', borderRadius: '0.375rem', border: 'none', fontWeight: '600', cursor: 'pointer' }}
                    >
                        Registrar Asistencia
                    </button>
                </div>

                <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                    <h3 style={{ marginBottom: '1rem', color: '#374151' }}>Asistencias Recientes</h3>
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                        {recentAttendances.length > 0 ? (
                            recentAttendances.map((attendance, index) => (
                                <div key={index} style={{ padding: '0.5rem', borderBottom: '1px solid #535252ff', fontSize: '0.875rem', color: '#1e3a8a' }}>
                                    {attendance.attendee_name} - {attendance.event_title}
                                </div>
                            ))
                        ) : (
                            <p style={{ color: '#6b7280', fontStyle: 'italic' }}>No hay registros recientes</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Sección de Buscar Usuarios Externos */}
            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', marginBottom: '2rem' }}>
                <h3 style={{ color: '#374151', marginBottom: '1rem' }}>Buscar Usuarios Externos</h3>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={handleSearchKeyPress}
                        placeholder="Buscar por nombre o número de cuenta..."
                        style={{
                            flex: 1,
                            padding: '0.75rem',
                            border: '1px solid #d1d5db',
                            borderRadius: '0.375rem',
                            fontSize: '0.875rem'
                        }}
                    />
                    <button
                        onClick={searchExternalUsers}
                        disabled={searching}
                        style={{
                            backgroundColor: '#2563eb',
                            color: 'white',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '0.375rem',
                            border: 'none',
                            cursor: searching ? 'not-allowed' : 'pointer',
                            fontWeight: '500',
                            opacity: searching ? 0.5 : 1
                        }}
                    >
                        {searching ? 'Buscando...' : 'Buscar'}
                    </button>
                </div>

                {searchResults.length > 0 && (
                    <div style={{ marginTop: '1rem', border: '1px solid #e5e7eb', borderRadius: '0.375rem', overflow: 'hidden' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead style={{ backgroundColor: '#f9fafb' }}>
                                <tr>
                                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>
                                        Número de Cuenta
                                    </th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>
                                        Nombre Completo
                                    </th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>
                                        Fecha Creación
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {searchResults.map((user) => (
                                    <tr key={user.id} style={{ borderTop: '1px solid #e5e7eb' }}>
                                        <td style={{ padding: '0.75rem', fontSize: '0.875rem', fontWeight: '600', color: '#1e3a8a' }}>
                                            {user.account_number}
                                        </td>
                                        <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#374151' }}>
                                            {user.full_name}
                                        </td>
                                        <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>
                                            {user.created_at}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Sección de Crear Usuario Externo */}
            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ color: '#374151', margin: 0 }}>Crear Usuario Externo</h3>
                    <button
                        onClick={() => setShowExternalForm(!showExternalForm)}
                        style={{
                            backgroundColor: '#2563eb',
                            color: 'white',
                            padding: '0.5rem 1rem',
                            borderRadius: '0.375rem',
                            border: 'none',
                            cursor: 'pointer',
                            fontWeight: '500'
                        }}
                    >
                        {showExternalForm ? 'Cancelar' : '+ Nuevo Usuario Externo'}
                    </button>
                </div>

                {showExternalForm && (
                    <form onSubmit={createExternalUser} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#1e3a8a', fontSize: '0.875rem' }}>
                                Número de Cuenta (7 dígitos) *
                            </label>
                            <input
                                type="text"
                                value={externalUser.account_number}
                                onChange={(e) => {
                                    const value = e.target.value.replace(/\D/g, '').slice(0, 7)
                                    setExternalUser({ ...externalUser, account_number: value })
                                }}
                                placeholder="1234567"
                                maxLength="7"
                                required
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#1e3a8a', fontSize: '0.875rem' }}>
                                Nombre Completo *
                            </label>
                            <input
                                type="text"
                                value={externalUser.full_name}
                                onChange={(e) => setExternalUser({ ...externalUser, full_name: e.target.value })}
                                placeholder="Juan Pérez López"
                                required
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                            />
                        </div>
                        <div style={{ gridColumn: '1 / -1' }}>
                            <button
                                type="submit"
                                style={{
                                    backgroundColor: '#059669',
                                    color: 'white',
                                    padding: '0.75rem 1.5rem',
                                    borderRadius: '0.375rem',
                                    border: 'none',
                                    cursor: 'pointer',
                                    fontWeight: '600',
                                    width: '100%'
                                }}
                            >
                                Crear Usuario Externo
                            </button>
                        </div>
                    </form>
                )}

                <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '1rem', fontStyle: 'italic' }}>
                    Los usuarios externos son aprobados automáticamente y pueden acceder con su número de cuenta.
                </p>
            </div>
        </div>
    )
}

export default AttendancePanel