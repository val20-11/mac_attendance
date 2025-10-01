import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { apiRequest } from '../services/api'
import ExternalRegistration from './ExternalRegistration'

const Login = () => {
    const [credentials, setCredentials] = useState({
        account_number: '',
        password: ''
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showExternalForm, setShowExternalForm] = useState(false)

    const { login } = useAuth()

    if (showExternalForm) {
        return <ExternalRegistration onBack={() => setShowExternalForm(false)} />
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        if (!/^\d{7}$/.test(credentials.account_number)) {
            setError('El número de cuenta debe tener exactamente 7 dígitos')
            setLoading(false)
            return
        }

        try {
            const response = await apiRequest('/auth/login/', {
                method: 'POST',
                body: credentials
            })
            login(response.user, response.tokens)
        } catch (err) {
            setError('Error al iniciar sesión. Verifica tus credenciales.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem'
        }}>
            <div style={{
                backgroundColor: 'rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '1rem',
                padding: '2rem',
                width: '100%',
                maxWidth: '400px',
                border: '1px solid rgba(255,255,255,0.2)'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <h1 style={{ color: 'white', fontSize: '2rem', marginBottom: '0.5rem' }}>
                        MAC FES Acatlán
                    </h1>
                    <h2 style={{ color: '#bfdbfe', fontSize: '1.2rem' }}>
                        Sistema de Asistencia a Ponencias
                    </h2>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div>
                        <label style={{ display: 'block', color: 'white', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                            Número de Cuenta
                        </label>
                        <input
                            type="text"
                            value={credentials.account_number}
                            onChange={(e) => {
                                const value = e.target.value.replace(/\D/g, '').slice(0, 7)
                                setCredentials({
                                    ...credentials,
                                    account_number: value
                                })
                            }}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                borderRadius: '0.5rem',
                                backgroundColor: 'rgba(255,255,255,0.2)',
                                border: '1px solid rgba(255,255,255,0.3)',
                                color: 'white',
                                fontSize: '1rem'
                            }}
                            placeholder="1234567"
                            required
                            disabled={loading}
                            maxLength="7"
                        />
                        <small style={{ color: '#bfdbfe', fontSize: '0.8rem', display: 'block', marginTop: '0.25rem' }}>
                            Ingresa tu número de cuenta de 7 dígitos
                        </small>
                    </div>

                    <div>
                        <label style={{ display: 'block', color: 'white', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                            Contraseña
                        </label>
                        <input
                            type="password"
                            value={credentials.password}
                            onChange={(e) => setCredentials({
                                ...credentials,
                                password: e.target.value
                            })}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                borderRadius: '0.5rem',
                                backgroundColor: 'rgba(255,255,255,0.2)',
                                border: '1px solid rgba(255,255,255,0.3)',
                                color: 'white',
                                fontSize: '1rem'
                            }}
                            placeholder="Ingresa tu contraseña"
                            required
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div style={{
                            backgroundColor: 'rgba(239, 68, 68, 0.2)',
                            border: '1px solid rgb(239, 68, 68)',
                            color: '#fecaca',
                            padding: '0.75rem',
                            borderRadius: '0.5rem'
                        }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        style={{
                            width: '100%',
                            background: 'linear-gradient(to right, #2563eb, #7c3aed)',
                            color: 'white',
                            fontWeight: '600',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '0.5rem',
                            border: 'none',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            opacity: loading ? 0.5 : 1,
                            fontSize: '1rem'
                        }}
                        disabled={loading}
                    >
                        {loading ? 'Ingresando...' : 'Ingresar al Sistema MAC'}
                    </button>
                </form>

                <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                    <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem', marginBottom: '1rem' }}>
                        Estudiantes: Consulta tus asistencias<br />
                        Asistentes: Administra y registra asistencias
                    </p>
                    <button
                        onClick={() => setShowExternalForm(true)}
                        style={{
                            backgroundColor: 'transparent',
                            color: 'white',
                            border: '1px solid rgba(255,255,255,0.3)',
                            padding: '0.5rem 1rem',
                            borderRadius: '0.5rem',
                            cursor: 'pointer',
                            fontSize: '0.875rem'
                        }}
                    >
                        ¿Eres externo? Regístrate aquí
                    </button>
                </div>
            </div>
        </div>
    )
}

export default Login