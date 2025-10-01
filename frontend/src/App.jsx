import './App.css'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import Dashboard from './components/Dashboard'

const MacAttendanceApp = () => {
    const { user, loading } = useAuth()

    if (loading) {
        return (
            <div style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#1e3a8a'
            }}>
                <div style={{ color: 'white', textAlign: 'center' }}>
                    <div style={{
                        width: '3rem',
                        height: '3rem',
                        border: '2px solid white',
                        borderTop: '2px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                        margin: '0 auto 1rem'
                    }}></div>
                    <p>Cargando sistema...</p>
                </div>
            </div>
        )
    }

    if (!user) {
        return <Login />
    }

    return <Dashboard />
}

function App() {
    return (
        <AuthProvider>
            <MacAttendanceApp />
        </AuthProvider>
    )
}

export default App