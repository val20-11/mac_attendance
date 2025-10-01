import { useState, useEffect } from 'react'
import { apiRequest } from '../services/api'

const AttendancePanel = () => {
    const [selectedEvent, setSelectedEvent] = useState('')
    const [studentAccount, setStudentAccount] = useState('')
    const [events, setEvents] = useState([])
    const [recentAttendances, setRecentAttendances] = useState([])
    const [message, setMessage] = useState('')
    const [messageType, setMessageType] = useState('')

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

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
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
        </div>
    )
}

export default AttendancePanel