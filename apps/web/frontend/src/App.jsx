import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import About from "./pages/About";

import { BrowserRouter, Route, Routes } from "react-router-dom";

const App = () => {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>

      <footer className="footer">
        <div className="container footer-inner">
          <div>
            <div className="footer-logo">
              <span>APEX</span>
              <small>STUDY</small>
            </div>

            <p>
              Bilim sari birgalikda.
            </p>
          </div>

          <div className="footer-links">
            <a href="/">Bosh sahifa</a>
            <a href="/about">Biz haqimizda</a>
            <a href="#courses">Kurslar</a>
            <a href="#contact">Aloqa</a>
          </div>

          <div className="copyright">
            © 2026 APEX STUDY
          </div>
        </div>
      </footer>
    </BrowserRouter>
  );
};

export default App;