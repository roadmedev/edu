import React from 'react'
import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav style={{ display: 'flex', gap: '1rem', padding: '1rem', borderBottom: '1px solid #ddd' }}>
      <Link to="/">Bosh sahifa</Link>
      <Link to="/about">Biz haqimizda</Link>
    </nav>
  )
}

export default Navbar
