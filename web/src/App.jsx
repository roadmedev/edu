import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import AdminHome from './pages/AdminHome';
import TeacherHome from './pages/TeacherHome';
import StudentHome from './pages/StudentHome';
import UserHome from './pages/UserHome';
import './styles/index.css';

const HOME_BY_ROLE = { admin: <AdminHome />, teacher: <TeacherHome />, student: <StudentHome />, user: <UserHome /> };

function RoleHome() {
  const { auth } = useAuth();
  if (!auth) return <Navigate to="/login" replace />;
  return HOME_BY_ROLE[auth.role] ?? <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><RoleHome /></ProtectedRoute>} />
          <Route path="/admin/*" element={<ProtectedRoute roles={['admin']}><AdminHome /></ProtectedRoute>} />
          <Route path="/teacher/*" element={<ProtectedRoute roles={['teacher']}><TeacherHome /></ProtectedRoute>} />
          <Route path="/student/*" element={<ProtectedRoute roles={['student']}><StudentHome /></ProtectedRoute>} />
          <Route path="/user/*" element={<ProtectedRoute roles={['user']}><UserHome /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}