import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { apiRequest } from '../services/api'

const StudentPanel = () => {
    const { user } = useAuth()
    const [attendanceStats, setAttendanceStats] = useState(null)
    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchStudentData()
    }, [])

    const fetchStudentData = async () => {
        try {
            const [eventsRes, statsRes] = await Promise.all([
                apiRequest('/events/'),
                apiRequest(`/attendance/stats/?account_number=${user.profile?.account_number}`)
            ])

            setEvents(eventsRes.results || eventsRes)
            setAttendanceStats(statsRes)
        } catch (error) {
            console.error('Error fetching student data:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando información...</div>
    }

    return (
        <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1e3a8a' }}>
                Registro de Asistencia
            </h2>

            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', marginBottom: '1.5rem' }}>
                <h3 style={{ marginBottom: '1rem', color: '#374151' }}>Estadísticas de Asistencia</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                    <div style={{ backgroundColor: '#dbeafe', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1e40af' }}>
                            {attendanceStats?.attended_events || 0}
                        </div>
                        <div style={{ color: '#1e40af', fontSize: '0.875rem' }}>Eventos Asistidos</div>
                    </div>
                    <div style={{ backgroundColor: '#dcfdf7', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#065f46' }}>
                            {attendanceStats?.total_events || 0}
                        </div>
                        <div style={{ color: '#065f46', fontSize: '0.875rem' }}>Total de Eventos</div>
                    </div>
                    <div style={{ backgroundColor: '#fef3c7', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#92400e' }}>
                            {attendanceStats?.attendance_percentage?.toFixed(1) || 0}%
                        </div>
                        <div style={{ color: '#92400e', fontSize: '0.875rem' }}>Porcentaje</div>
                    </div>
                </div>
            </div>

            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', overflow: 'hidden', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                {events.length > 0 ? (
                    <div>
                        {events.map((event) => (
                            <div key={event.id} style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb' }}>
                                <div style={{ display: 'flex', justifyContent: 'between', alignItems: 'start' }}>
                                    <div style={{ flex: 1 }}>
                                        <h4 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.5rem', color: '#1e3a8a' }}>
                                            {event.title}
                                        </h4>
                                        <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>{event.description}</p>
                                        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                                            <span>📅 {event.date}</span>
                                            <span>🕒 {event.start_time} - {event.end_time}</span>
                                            <span>📍 {event.location}</span>
                                            <span>👨‍🏫 {event.speaker}</span>
                                        </div>
                                    </div>
                                    <span style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', fontWeight: '600', borderRadius: '9999px', backgroundColor: event.modality === 'presencial' ? '#dcfdf7' : '#dbeafe', color: event.modality === 'presencial' ? '#065f46' : '#1e40af' }}>
                                        {event.modality}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>No hay eventos disponibles</p>
                )}
            </div>
        </div>
    )
}

export default StudentPanel