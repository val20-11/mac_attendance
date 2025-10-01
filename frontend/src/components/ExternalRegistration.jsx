import { useState } from 'react'
import { apiRequest } from '../services/api'

const ExternalRegistration = ({ onBack }) => {
    const [formData, setFormData] = useState({
        full_name: ''
    })
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')
    const [messageType, setMessageType] = useState('')
    const [temporaryId, setTemporaryId] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setMessage('')

        try {
            const response = await apiRequest('/events/external/register/', {
                method: 'POST',
                body: formData
            })

            setMessage(response.message)
            setTemporaryId(response.temporary_id)
            setMessageType('success')
            setFormData({
                full_name: ''
            })
        } catch (error) {
            setMessage('Error al enviar solicitud: ' + (error.response?.data?.error || 'Error desconocido'))
            setMessageType('error')
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%)',
            padding: '2rem'
        }}>
            <div style={{ maxWidth: '600px', margin: '0 auto' }}>
                <button
                    onClick={onBack}
                    style={{
                        backgroundColor: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        border: '1px solid rgba(255,255,255,0.3)',
                        cursor: 'pointer',
                        marginBottom: '1rem'
                    }}
                >
                    ← Volver al Login
                </button>

                <div style={{
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: '1rem',
                    padding: '2rem',
                    border: '1px solid rgba(255,255,255,0.2)'
                }}>
                    <h1 style={{ color: 'white', fontSize: '1.8rem', marginBottom: '0.5rem', textAlign: 'center' }}>
                        Registro de Usuario Externo
                    </h1>
                    <p style={{ color: '#bfdbfe', textAlign: 'center', marginBottom: '2rem' }}>
                        Solicita acceso para asistir a las ponencias de MAC
                    </p>

                    {message && (
                        <div style={{
                            padding: '1rem',
                            marginBottom: '1rem',
                            borderRadius: '0.5rem',
                            backgroundColor: messageType === 'success' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                            color: 'white',
                            border: `1px solid ${messageType === 'success' ? '#22c55e' : '#ef4444'}`
                        }}>
                            {message}
                            {temporaryId && (
                                <div style={{ marginTop: '0.5rem', fontWeight: 'bold' }}>
                                    Guarda este ID: {temporaryId}
                                </div>
                            )}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', color: 'white', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                                Nombre Completo *
                            </label>
                            <input
                                type="text"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleChange}
                                required
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    borderRadius: '0.5rem',
                                    border: '1px solid rgba(255,255,255,0.3)',
                                    backgroundColor: 'rgba(255,255,255,0.1)',
                                    color: 'white'
                                }}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            style={{
                                width: '100%',
                                background: 'linear-gradient(to right, #2563eb, #7c3aed)',
                                color: 'white',
                                fontWeight: '600',
                                padding: '0.75rem',
                                borderRadius: '0.5rem',
                                border: 'none',
                                cursor: loading ? 'not-allowed' : 'pointer',
                                opacity: loading ? 0.5 : 1
                            }}
                        >
                            {loading ? 'Enviando...' : 'Enviar Solicitud'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default ExternalRegistration