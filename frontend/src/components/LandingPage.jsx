import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const LandingPage = () => {
    const navigate = useNavigate()
    const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 })

    useEffect(() => {
        const handleMouseMove = (e) => {
            setCursorPos({ x: e.clientX, y: e.clientY })
        }

        document.addEventListener('mousemove', handleMouseMove)
        return () => document.removeEventListener('mousemove', handleMouseMove)
    }, [])

    const styles = {
        body: {
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            background: 'rgb(8, 36, 90)',
            color: '#fff',
            overflowX: 'hidden',
            margin: 0,
            padding: 0,
            minHeight: '100vh'
        },
        cursorGlow: {
            position: 'fixed',
            width: '600px',
            height: '600px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(189, 149, 0, 0.15), transparent 70%)',
            pointerEvents: 'none',
            transform: 'translate(-50%, -50%)',
            zIndex: 1,
            left: cursorPos.x,
            top: cursorPos.y,
            transition: 'opacity 0.3s'
        },
        nav: {
            position: 'fixed',
            top: 0,
            width: '100%',
            padding: '2rem 4rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(10px)'
        },
        logo: {
            fontSize: '1.3rem',
            fontWeight: 900,
            letterSpacing: '-0.5px',
            color: '#fff',
            display: 'flex',
            flexDirection: 'column',
            lineHeight: 1.2
        },
        logoLine1: {
            fontSize: '0.9rem',
            color: 'rgb(189, 149, 0)'
        },
        logoLine2: {
            fontSize: '1.1rem',
            fontWeight: 800
        },
        loginBtn: {
            padding: '0.6rem 1.5rem',
            background: 'linear-gradient(135deg, rgb(189, 149, 0), rgb(220, 180, 50))',
            borderRadius: '25px',
            boxShadow: '0 4px 15px rgba(189, 149, 0, 0.3)',
            color: '#fff',
            textDecoration: 'none',
            fontSize: '0.9rem',
            fontWeight: 500,
            transition: 'all 0.3s',
            border: 'none',
            cursor: 'pointer'
        },
        hero: {
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            overflow: 'hidden'
        },
        floatingShapes: {
            position: 'absolute',
            width: '100%',
            height: '100%',
            zIndex: 0
        },
        shape: {
            position: 'absolute',
            borderRadius: '30% 70% 70% 30% / 30% 30% 70% 70%',
            background: 'linear-gradient(135deg, rgba(189, 149, 0, 0.15), rgba(189, 149, 0, 0.05))'
        },
        heroContent: {
            textAlign: 'center',
            zIndex: 2,
            maxWidth: '900px',
            padding: '0 2rem'
        },
        h1: {
            fontSize: 'clamp(3rem, 8vw, 7rem)',
            fontWeight: 900,
            lineHeight: 1.1,
            marginBottom: '1.5rem',
            letterSpacing: '-3px'
        },
        gradientText: {
            background: 'linear-gradient(135deg, rgb(189, 149, 0) 0%, rgb(220, 180, 50) 50%, rgb(255, 215, 100) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            backgroundSize: '200% 200%'
        },
        subtitle: {
            fontSize: 'clamp(1.2rem, 2vw, 1.5rem)',
            color: '#a0a0a0',
            marginBottom: '1.5rem',
            fontWeight: 300
        },
        description: {
            fontSize: 'clamp(1rem, 1.5vw, 1.1rem)',
            color: '#b0b0b0',
            marginBottom: '3rem',
            maxWidth: '700px',
            marginLeft: 'auto',
            marginRight: 'auto',
            lineHeight: 1.6
        },
        ctaButton: {
            display: 'inline-block',
            padding: '1.2rem 3rem',
            background: 'linear-gradient(135deg, rgb(189, 149, 0), rgb(220, 180, 50))',
            color: '#fff',
            textDecoration: 'none',
            borderRadius: '50px',
            fontWeight: 600,
            fontSize: '1.1rem',
            transition: 'all 0.3s',
            boxShadow: '0 10px 40px rgba(189, 149, 0, 0.4)',
            position: 'relative',
            overflow: 'hidden',
            border: 'none',
            cursor: 'pointer'
        },
        services: {
            padding: '8rem 4rem',
            background: 'linear-gradient(180deg, rgb(8, 36, 90) 0%, rgb(5, 25, 65) 100%)'
        },
        sectionTitle: {
            fontSize: 'clamp(2.5rem, 5vw, 4rem)',
            fontWeight: 800,
            marginBottom: '4rem',
            textAlign: 'center'
        },
        servicesGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '2rem',
            maxWidth: '1200px',
            margin: '0 auto'
        },
        serviceCard: {
            background: 'rgba(255, 255, 255, 0.03)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
            padding: '3rem 2rem',
            transition: 'all 0.3s',
            position: 'relative',
            overflow: 'hidden'
        },
        serviceIcon: {
            fontSize: '3rem',
            marginBottom: '1.5rem'
        },
        footer: {
            padding: '3rem 4rem',
            textAlign: 'center',
            background: 'rgb(5, 20, 50)',
            borderTop: '1px solid rgba(189, 149, 0, 0.2)',
            color: '#666'
        }
    }

    const Shape = ({ style }) => (
        <div style={{ ...styles.shape, ...style }}>
            <style>
                {`
                    @keyframes float {
                        0%, 100% { transform: translate(0, 0) rotate(0deg); }
                        33% { transform: translate(50px, -50px) rotate(120deg); }
                        66% { transform: translate(-30px, 30px) rotate(240deg); }
                    }
                `}
            </style>
        </div>
    )

    return (
        <div style={styles.body}>
            <div style={styles.cursorGlow} />

            <nav style={styles.nav}>
                <div style={styles.logo}>
                    <span style={styles.logoLine1}>FES ACATLÁN</span>
                    <span style={styles.logoLine2}>UNAM</span>
                </div>
                <button
                    style={styles.loginBtn}
                    onClick={() => navigate('/login')}
                    onMouseEnter={(e) => {
                        e.target.style.boxShadow = '0 6px 20px rgba(189, 149, 0, 0.5)'
                        e.target.style.transform = 'translateY(-2px)'
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.boxShadow = '0 4px 15px rgba(189, 149, 0, 0.3)'
                        e.target.style.transform = 'translateY(0)'
                    }}
                >
                    Iniciar Sesión
                </button>
            </nav>

            <section style={styles.hero}>
                <div style={styles.floatingShapes}>
                    <Shape style={{
                        width: '300px',
                        height: '300px',
                        top: '10%',
                        left: '10%',
                        animation: 'float 20s infinite ease-in-out',
                        animationDelay: '0s'
                    }} />
                    <Shape style={{
                        width: '400px',
                        height: '400px',
                        bottom: '10%',
                        right: '10%',
                        animation: 'float 20s infinite ease-in-out',
                        animationDelay: '-7s'
                    }} />
                    <Shape style={{
                        width: '250px',
                        height: '250px',
                        top: '50%',
                        left: '50%',
                        animation: 'float 20s infinite ease-in-out',
                        animationDelay: '-14s'
                    }} />
                </div>
                <div style={styles.heroContent}>
                    <h1 style={styles.h1}>
                        Sistema de Asistencia <span style={styles.gradientText}>MAC</span>
                    </h1>
                    <p style={styles.subtitle}>Tu portal de eventos académicos</p>
                    <p style={styles.description}>
                        Registra tu asistencia, consulta eventos y mantén un seguimiento completo de tu
                        participación en las actividades de la Semana de Mac u otros eventos.
                    </p>
                    <button
                        style={styles.ctaButton}
                        onClick={() => navigate('/login')}
                        onMouseEnter={(e) => {
                            e.target.style.transform = 'translateY(-3px)'
                            e.target.style.boxShadow = '0 15px 50px rgba(189, 149, 0, 0.6)'
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.transform = 'translateY(0)'
                            e.target.style.boxShadow = '0 10px 40px rgba(189, 149, 0, 0.4)'
                        }}
                    >
                        Iniciar Sesión
                    </button>
                </div>
            </section>

            <section style={styles.services}>
                <h2 style={styles.sectionTitle}>
                    Acceso <span style={styles.gradientText}>rápido</span>
                </h2>
                <div style={styles.servicesGrid}>
                    <div
                        style={styles.serviceCard}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-10px)'
                            e.currentTarget.style.borderColor = 'rgba(189, 149, 0, 0.5)'
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)'
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                        }}
                    >
                        <div style={styles.serviceIcon}>👨‍🎓</div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', fontWeight: 700 }}>
                            Estudiantes y Asistentes
                        </h3>
                        <p style={{ color: '#a0a0a0', lineHeight: 1.6 }}>
                            Inicia sesión con tu número de cuenta para registrar tu asistencia y acceder a
                            todos los eventos académicos disponibles
                        </p>
                    </div>
                    <div
                        style={styles.serviceCard}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-10px)'
                            e.currentTarget.style.borderColor = 'rgba(189, 149, 0, 0.5)'
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)'
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                        }}
                    >
                        <div style={styles.serviceIcon}>🎫</div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', fontWeight: 700 }}>
                            Visitantes
                        </h3>
                        <p style={{ color: '#a0a0a0', lineHeight: 1.6 }}>
                            Solicita acceso para participar en nuestros eventos con un asistente y formar
                            parte de la comunidad académica
                        </p>
                    </div>
                </div>
            </section>

            <footer style={styles.footer}>
                <p>&copy; 2025 FES Acatlán - UNAM. Todos los derechos reservados.</p>
            </footer>
        </div>
    )
}

export default LandingPage
