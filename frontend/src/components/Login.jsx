import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { apiRequest } from '../services/api'

const Login = () => {
    const [accountNumber, setAccountNumber] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showScanner, setShowScanner] = useState(false)
    const [scannerReady, setScannerReady] = useState(false)
    const scannerRef = useRef(null)
    const quaggaInitialized = useRef(false)

    const { login } = useAuth()

    useEffect(() => {
        // Cargar Quagga.js desde CDN
        const script = document.createElement('script')
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js'
        script.async = true
        document.body.appendChild(script)

        return () => {
            if (document.body.contains(script)) {
                document.body.removeChild(script)
            }
            stopScanner()
        }
    }, [])

    const startScanner = () => {
        if (!window.Quagga) {
            setError('El lector de códigos de barras aún está cargando. Intenta de nuevo en un momento.')
            return
        }

        setShowScanner(true)
        setScannerReady(false)
        setError('')

        setTimeout(() => {
            if (quaggaInitialized.current) return

            window.Quagga.init({
                inputStream: {
                    type: 'LiveStream',
                    target: scannerRef.current,
                    constraints: {
                        facingMode: 'environment',
                        width: { min: 640 },
                        height: { min: 480 }
                    }
                },
                decoder: {
                    readers: [
                        'code_128_reader',
                        'ean_reader',
                        'ean_8_reader',
                        'code_39_reader',
                        'code_39_vin_reader',
                        'codabar_reader',
                        'upc_reader',
                        'upc_e_reader',
                        'i2of5_reader'
                    ]
                },
                locate: true,
                locator: {
                    patchSize: 'medium',
                    halfSample: true
                }
            }, (err) => {
                if (err) {
                    console.error('Error al iniciar escáner:', err)
                    setError('No se pudo acceder a la cámara. Verifica los permisos en tu navegador.')
                    setShowScanner(false)
                    return
                }
                
                window.Quagga.start()
                quaggaInitialized.current = true
                setScannerReady(true)
            })

            window.Quagga.onDetected((result) => {
                const code = result.codeResult.code
                console.log('Código detectado:', code)
                
                // Extraer solo los primeros 7 dígitos numéricos
                const numbers = code.replace(/\D/g, '').slice(0, 7)
                
                if (numbers.length === 7) {
                    setAccountNumber(numbers)
                    stopScanner()
                    
                    // Vibración de confirmación (si está disponible)
                    if (navigator.vibrate) {
                        navigator.vibrate(200)
                    }
                    
                    console.log('✓ Código escaneado exitosamente:', numbers)
                }
            })
        }, 100)
    }

    const stopScanner = () => {
        if (window.Quagga && quaggaInitialized.current) {
            window.Quagga.stop()
            window.Quagga.offDetected()
            quaggaInitialized.current = false
        }
        setShowScanner(false)
        setScannerReady(false)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        // Validar formato: 7 dígitos
        if (!/^\d{7}$/.test(accountNumber)) {
            setError('El número de cuenta debe tener exactamente 7 dígitos')
            setLoading(false)
            return
        }

        try {
            const response = await apiRequest('/auth/login/', {
                method: 'POST',
                body: { account_number: accountNumber }
            })
            login(response.user, response.tokens)
        } catch (err) {
            setError('Número de cuenta no encontrado o no autorizado.')
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
                            value={accountNumber}
                            onChange={(e) => {
                                const value = e.target.value.replace(/\D/g, '').slice(0, 7)
                                setAccountNumber(value)
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

                    {/* Botón Iniciar Sesión - PRIMERO */}
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

                    {/* Separador visual "o" */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                        margin: '0.5rem 0'
                    }}>
                        <div style={{ flex: 1, height: '1px', backgroundColor: 'rgba(255,255,255,0.3)' }}></div>
                        <div style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            backgroundColor: 'rgba(255,255,255,0.1)',
                            border: '1px solid rgba(255,255,255,0.3)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'rgba(255,255,255,0.7)',
                            fontSize: '0.9rem',
                            fontWeight: '500'
                        }}>
                            o
                        </div>
                        <div style={{ flex: 1, height: '1px', backgroundColor: 'rgba(255,255,255,0.3)' }}></div>
                    </div>

                    {/* Botón Escanear - DESPUÉS con ícono de cámara */}
                    <button
                        type="button"
                        onClick={startScanner}
                        disabled={loading}
                        style={{
                            width: '100%',
                            background: 'linear-gradient(to right, #059669, #10b981)',
                            color: 'white',
                            fontWeight: '600',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '0.5rem',
                            border: 'none',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            opacity: loading ? 0.5 : 1,
                            fontSize: '1rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem',
                            transition: 'transform 0.2s'
                        }}
                        onMouseOver={(e) => !loading && (e.currentTarget.style.transform = 'scale(1.02)')}
                        onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                            <circle cx="12" cy="13" r="4"></circle>
                        </svg>
                        Escanear Credencial
                    </button>
                </form>

                <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                    <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>
                        Estudiantes: Consulta tus asistencias<br />
                        Asistentes: Registra asistencias<br />
                        <span style={{ fontSize: '0.8rem' }}>Los usuarios externos deben solicitar su cuenta al asistente</span>
                    </p>
                </div>
            </div>

            {/* Modal del Escáner de Código de Barras */}
            {showScanner && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.95)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    padding: '1rem'
                }}>
                    <div style={{
                        width: '100%',
                        maxWidth: '500px',
                        textAlign: 'center'
                    }}>
                        <h3 style={{ 
                            color: 'white', 
                            marginBottom: '0.5rem', 
                            fontSize: '1.5rem',
                            fontWeight: 'bold'
                        }}>
                            Escanea tu Credencial
                        </h3>
                        <p style={{ 
                            color: '#bfdbfe', 
                            marginBottom: '1.5rem',
                            fontSize: '0.9rem'
                        }}>
                            {scannerReady 
                                ? 'Coloca el código de barras de tu credencial frente a la cámara'
                                : 'Iniciando cámara, por favor espera...'
                            }
                        </p>

                        <div 
                            ref={scannerRef}
                            style={{
                                width: '100%',
                                maxWidth: '400px',
                                height: '300px',
                                margin: '0 auto',
                                backgroundColor: '#000',
                                borderRadius: '0.5rem',
                                overflow: 'hidden',
                                position: 'relative',
                                border: scannerReady ? '3px solid #10b981' : '3px solid #6b7280'
                            }}
                        >
                            {!scannerReady && (
                                <div style={{
                                    position: 'absolute',
                                    top: '50%',
                                    left: '50%',
                                    transform: 'translate(-50%, -50%)',
                                    color: 'white',
                                    fontSize: '1.1rem'
                                }}>
                                    ⏳ Cargando cámara...
                                </div>
                            )}
                        </div>

                        {scannerReady && (
                            <div style={{
                                marginTop: '1rem',
                                padding: '0.5rem',
                                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                                borderRadius: '0.5rem',
                                border: '1px solid #10b981'
                            }}>
                                <p style={{ color: '#10b981', margin: 0, fontSize: '0.9rem' }}>
                                    📸 Cámara activa - Escaneo automático habilitado
                                </p>
                            </div>
                        )}

                        <button
                            onClick={stopScanner}
                            style={{
                                marginTop: '1.5rem',
                                background: 'rgba(239, 68, 68, 0.9)',
                                color: 'white',
                                fontWeight: '600',
                                padding: '0.75rem 2rem',
                                borderRadius: '0.5rem',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '1rem',
                                transition: 'background 0.2s'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 1)'}
                            onMouseOut={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.9)'}
                        >
                            ✕ Cancelar
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Login
