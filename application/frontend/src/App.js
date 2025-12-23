import { useState, useEffect } from 'react';
import Login from './components/Login';
import AdminDashboard from './components/admin/AdminDashboard';
import DoctorDashboard from './components/doctor/DoctorDashboard';
import PatientDashboard from './components/patient/PatientDashboard';
import { login as apiLogin, logout as apiLogout, getCurrentUser } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const data = await getCurrentUser();
      setUser(data.user);
    } catch (err) {
      // Not authenticated, show login
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (email, password) => {
    const data = await apiLogin(email, password);
    setUser(data.user);
  };

  const handleLogout = async () => {
    try {
      await apiLogout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  // Route based on user role
  if (user.role === 'admin') {
    return <AdminDashboard user={user} onLogout={handleLogout} />;
  } else if (user.role === 'doctor') {
    return <DoctorDashboard user={user} onLogout={handleLogout} />;
  } else if (user.role === 'patient') {
    return <PatientDashboard user={user} onLogout={handleLogout} />;
  }

  return <div>Unknown role</div>;
}

export default App;
