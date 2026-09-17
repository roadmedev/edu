import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

const Home = () => {
  const [message, setMessage] = useState("Yuklanmoqda...");

  useEffect(() => {
    fetch(`${API_URL}/hello`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Backend bilan bog‘lanib bo‘lmadi!"));
  }, []);

  const courses = [
    {
      icon: "🇬🇧",
      title: "Ingliz tili",
      text: "Boshlang‘ichdan yuqori darajagacha zamonaviy metodika asosida.",
      level: "Beginner — Advanced",
    },
    {
      icon: "🧮",
      title: "Matematika",
      text: "Maktab o‘quvchilari va abituriyentlar uchun maxsus dastur.",
      level: "5 — 11 sinf",
    },
    {
      icon: "🎓",
      title: "Abituriyentlar uchun maxsus",
      text: "OTMga kirish uchun intensiv va natijaga yo‘naltirilgan tayyorgarlik.",
      level: "Intensive",
    },
  ];

  const advantages = [
    {
      number: "01",
      title: "Tajribali ustozlar",
      text: "O‘z fanini chuqur biladigan va o‘quvchi bilan ishlash tajribasiga ega mutaxassislar.",
    },
    {
      number: "02",
      title: "Zamonaviy metodika",
      text: "Nazariya va amaliyotni birlashtirgan, natijaga yo‘naltirilgan ta’lim tizimi.",
    },
    {
      number: "03",
      title: "Individual yondashuv",
      text: "Har bir o‘quvchining darajasi va maqsadiga mos ta’lim jarayoni.",
    },
  ];

  return (
    <main>
      {/* HERO */}
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-content">
            <div className="badge">
              <span></span>
              Bog‘ot tumani markazidagi zamonaviy o‘quv markaz
            </div>

            <h1>
              Kelajagingizni
              <br />
              <strong>APEX STUDY</strong>
              <br />
              bilan quring.
            </h1>

            <p className="hero-description">
              Sifatli ta’lim, kuchli ustozlar va zamonaviy metodika.
              Maqsadingizga tezroq erishishingiz uchun biz siz bilan birgamiz.
            </p>

            <div className="hero-actions">
              <a href="#courses" className="primary-button">
                Kurslarni ko‘rish
                <span>→</span>
              </a>

              <a href="#contact" className="secondary-button">
                Biz bilan bog‘lanish
              </a>
            </div>

            <div className="hero-stats">
              <div>
                <strong>500+</strong>
                <span>O‘quvchilar</span>
              </div>

              <div>
                <strong>20+</strong>
                <span>Professional ustozlar</span>
              </div>

              <div>
                <strong>95%</strong>
                <span>Natijadorlik</span>
              </div>
            </div>
          </div>

          <div className="hero-visual">
            <div className="hero-card">
              <div className="big-logo">A</div>

              <div className="gold-line"></div>

              <h3>APEX</h3>
              <p>STUDY CENTER</p>

              <div className="floating-card card-one">
                <span>✓</span>
                Sifatli ta’lim
              </div>

              <div className="floating-card card-two">
                <span>★</span>
                Kuchli ustozlar
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* COURSES */}
      <section id="courses" className="section courses-section">
        <div className="container">
          <div className="section-heading">
            <span className="section-label">TA’LIM YO‘NALISHLARI</span>

            <h2>
              O‘zingizga mos
              <br />
              <span>kursni tanlang</span>
            </h2>

            <p>
              APEX STUDY | O'quv markazida zamonaviy ta’lim dasturlari va professional
              ustozlar sizning rivojlanishingiz uchun xizmat qiladi.
            </p>
          </div>

          <div className="courses-grid">
            {courses.map((course, index) => (
              <div className="course-card" key={index}>
                <div className="course-icon">{course.icon}</div>

                <span className="course-level">{course.level}</span>

                <h3>{course.title}</h3>

                <p>{course.text}</p>

                <a href="#contact">
                  Batafsil ma’lumot
                  <span>→</span>
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ABOUT */}
      <section className="about-section">
        <div className="container about-grid">
          <div className="about-image">
            <div className="about-logo">A</div>

            <div className="about-circle-text">
              APEX STUDY • EDUCATION • FUTURE •
            </div>
          </div>

          <div className="about-content">
            <span className="section-label">BIZ HAQIMIZDA</span>

            <h2>
              Bilim — eng katta
              <span> investitsiya.</span>
            </h2>

            <p>
              APEX STUDY — Bog‘ot tumani markazida faoliyat yurituvchi
              zamonaviy o‘quv markaz. Biz o‘quvchilarga sifatli ta’lim berish,
              ularning bilimini rivojlantirish va kelajakdagi maqsadlariga
              erishishiga yordam berishni asosiy vazifamiz deb bilamiz.
            </p>

            <p>
              Bizning jamoamiz har bir o‘quvchiga individual yondashadi va
              ta’lim jarayonini doimiy ravishda rivojlantirib boradi.
            </p>

            <a href="/about" className="primary-button">
              Biz haqimizda
              <span>→</span>
            </a>
          </div>
        </div>
      </section>

      {/* ADVANTAGES */}
      <section id="advantages" className="section advantages-section">
        <div className="container">
          <div className="section-heading center">
            <span className="section-label">NEGA APEX STUDY?</span>

            <h2>
              Natijaga olib boradigan
              <br />
              <span>ta’lim</span>
            </h2>
          </div>

          <div className="advantages-grid">
            {advantages.map((item, index) => (
              <div className="advantage" key={index}>
                <div className="advantage-number">{item.number}</div>

                <div>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* API STATUS */}
      <section className="api-section">
        <div className="container">
          <div className="api-box">
            <div>
              <span className="api-label">SYSTEM STATUS</span>
              <h3>APEX STUDY platformasi</h3>
            </div>

            <div className="api-status">
              <span></span>
              {message}
            </div>
          </div>
        </div>
      </section>

      {/* CONTACT */}
      <section id="contact" className="contact-section">
        <div className="container contact-box">
          <div>
            <span className="section-label">BOSHLASHGA TAYYORMISIZ?</span>

            <h2>
              Kelajagingizni
              <br />
              <span>bugundan boshlang.</span>
            </h2>

            <p>
              Kurslarimiz haqida batafsil ma’lumot olish uchun biz bilan
              bog‘laning.
            </p>
          </div>

          <div className="contact-actions">
            <a href="tel:+998870879009" className="primary-button">
              📞 Qo‘ng‘iroq qilish
            </a>

            <a
              href="https://t.me/@apex_studybot"
              target="_blank"
              rel="noreferrer"
              className="telegram-button"
            >
              Telegram
            </a>
          </div>
        </div>
      </section>
    </main>
  );
};

export default Home;