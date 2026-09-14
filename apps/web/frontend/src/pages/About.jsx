import React from "react";

const About = () => {
  return (
    <main className="about-page">
      <section className="page-hero">
        <div className="container">
          <span className="section-label">APEX STUDY</span>

          <h1>
            Biz haqimizda
          </h1>

          <p>
            Ta’lim orqali kuchli kelajak sari.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container about-page-grid">
          <div>
            <span className="section-label">BIZNING MAQSADIMIZ</span>

            <h2>
              Har bir o‘quvchi —
              <span> yangi imkoniyat.</span>
            </h2>
          </div>

          <div>
            <p>
              APEX STUDY — Bog‘ot tumani markazida joylashgan zamonaviy o‘quv
              markaz. Biz yoshlarning sifatli bilim olishi va o‘z kelajagini
              qurishiga yordam beramiz.
            </p>

            <p>
              Biz uchun ta’lim faqat dars o‘tish emas. Biz o‘quvchilarning
              mustaqil fikrlashi, o‘ziga bo‘lgan ishonchi va yuqori natijalarga
              erishishini qo‘llab-quvvatlaymiz.
            </p>

            <p>
              Markazimizda professional ustozlar, zamonaviy o‘quv dasturlari
              va qulay ta’lim muhiti mavjud.
            </p>
          </div>
        </div>
      </section>

      <section className="mission-section">
        <div className="container mission-grid">
          <div className="mission-card">
            <span>01</span>
            <h3>Bizning missiyamiz</h3>
            <p>
              Yoshlar uchun sifatli, zamonaviy va natijador ta’lim muhitini
              yaratish.
            </p>
          </div>

          <div className="mission-card">
            <span>02</span>
            <h3>Bizning qarashimiz</h3>
            <p>
              Bilimli, mustaqil fikrlaydigan va kelajakka ishonch bilan
              qaraydigan yoshlarni tarbiyalash.
            </p>
          </div>

          <div className="mission-card">
            <span>03</span>
            <h3>Bizning qadriyatimiz</h3>
            <p>
              Sifat, halollik, intizom, rivojlanish va har bir o‘quvchiga
              individual yondashuv.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
};

export default About;