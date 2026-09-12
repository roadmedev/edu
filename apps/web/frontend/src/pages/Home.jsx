import { useEffect, useState } from "react"

const API_URL = import.meta.env.VITE_API_URL


const Home = () => {
  
  const [message, setMessage ] = useState("Yuklanmoqda...")

  useEffect(() => {
    fetch(`${API_URL}/hello`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Backend bilan bog'lanib bo'lmadi!"))
  }, [])
  
  return (
    <div>
      <h1>Apex Study | Zamonaviy o'quv markaz</h1>
      <p>Bosh sahifaga xush kelibsiz!</p>
      <p>
        Backend'dan kelgan ma'lumot: <strong>{message}</strong>
      </p>
    </div>
  )
}

export default Home
