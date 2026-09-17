import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="logo">
          <div className="logo-icon">A</div>

          <div className="logo-text">
            <span>APEX</span>
            <small>STUDY</small>
          </div>
        </Link>

        <nav className="nav-links">
          <Link to="/">Bosh sahifa</Link>
          <Link to="/about">Biz haqimizda</Link>
          <a href="#courses">Kurslar</a>
          <a href="#advantages">Afzalliklar</a>
          <a href="#blog">Blog</a>
          <a href="#contact">Aloqa</a>
        </nav>

        <a href="#contact" className="nav-button">
          Bog‘lanish
        </a>
      </div>
    </header>
  );
};

export default Navbar;