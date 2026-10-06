import { useAuth } from '../auth/AuthContext';

const ROLE_LABELS = { admin: 'Administrator', teacher: "O'qituvchi", student: "O'quvchi", user: 'Foydalanuvchi' };

export default function Layout({ children }) {
  const { auth, logout } = useAuth();

  return (
    <div className="shell">
      <header className="topbar">
        <span className="brand">ApexStudy</span>
        <div className="topbar-user">
          <span>{auth?.fullName}</span>
          <span className="role-tag">{ROLE_LABELS[auth?.role]}</span>
          <button className="btn-ghost" onClick={logout}>Chiqish</button>
        </div>
      </header>
      <main className="content">{children}</main>
    </div>
  );
}