import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { requestOtp, verifyOtp } from '../api/auth';
import { useAuth } from '../auth/AuthContext';

export default function LoginPage() {
  const [step, setStep] = useState('phone'); // phone | code
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [botUsername, setBotUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSendCode(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await requestOtp(phone);
      setStep('code');
    } catch (err) {
      setError(err.message);
      if (err.message.includes('ro\'yxatdan o\'tmagan')) setBotUsername('oquv_markaz_bot');
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await verifyOtp(phone, code);
      login(data);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="auth-mark">AS</div>
        <h1>ApexStudy</h1>
        <p className="auth-sub">
          {step === 'phone'
            ? 'Telegramda ro\'yxatdan o\'tgan telefon raqamingizni kiriting'
            : `${phone} raqamiga yuborilgan 6 xonali kodni kiriting`}
        </p>

        {step === 'phone' && (
          <form onSubmit={handleSendCode}>
            <input
              type="tel" placeholder="+998 90 123 45 67" value={phone}
              onChange={(e) => setPhone(e.target.value)} required autoFocus
            />
            <button type="submit" disabled={loading}>{loading ? 'Yuborilmoqda...' : 'Kod olish'}</button>
          </form>
        )}

        {step === 'code' && (
          <form onSubmit={handleVerify}>
            <input
              type="text" inputMode="numeric" placeholder="123456" value={code}
              onChange={(e) => setCode(e.target.value)} maxLength={6} required autoFocus
            />
            <button type="submit" disabled={loading}>{loading ? 'Tekshirilmoqda...' : 'Kirish'}</button>
            <button type="button" className="btn-link" onClick={() => setStep('phone')}>
              ← Raqamni o'zgartirish
            </button>
          </form>
        )}

        {error && (
          <div className="auth-error">
            {error}
            {botUsername && (
              <>
                {' '}
                <a href={`https://t.me/${botUsername}`} target="_blank" rel="noreferrer">Botni ochish →</a>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}