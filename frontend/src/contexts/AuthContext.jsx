import { createContext, useContext, useState, useEffect } from 'react'
import { tokenManager, apiRequest } from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    // Intentar recuperar sesión al cargar
    useEffect(() => {
        const initAuth = async () => {
            const accessToken = tokenManager.getAccessToken()
            if (accessToken) {
                try {
                    // Verificar el token y obtener info del usuario
                    const response = await apiRequest('/auth/token/verify/', {
                        method: 'POST'
                    })
                    setUser(response.user)
                } catch (error) {
                    // Token inválido, limpiar
                    tokenManager.clearTokens()
                }
            }
            setLoading(false)
        }
        initAuth()
    }, [])

    const login = (userData, tokens) => {
        setUser(userData)
        if (tokens) {
            tokenManager.setTokens(tokens.access, tokens.refresh)
        }
    }

    const logout = () => {
        setUser(null)
        tokenManager.clearTokens()
    }

    const value = {
        user,
        login,
        logout,
        loading
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}