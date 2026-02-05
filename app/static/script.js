/* БГИТУ IT-Институт — Updated JS (No Stars, No Badges, Smooth Carousel) */
(() => {
  'use strict';

  // Данные (заморожены для производительности)
  const DATA = Object.freeze({
    courses: [
      { n: 'Информатика', s: 1, e: 2, c: 'bg-pastel-sky', d: 'Базовые основы программирования и алгоритмического мышления' },
      { n: 'Алгоритмы и структуры', s: 2, e: 3, c: 'bg-pastel-mint', d: 'Фундаментальные алгоритмы, сложность, оптимизация' },
      { n: 'Frontend-разработка', s: 3, e: 4, c: 'bg-pastel-peach', d: 'HTML, CSS, JS, React и современные фреймворки' },
      { n: 'Backend (Java/C#)', s: 4, e: 5, c: 'bg-pastel-coral', d: 'Серверная разработка, REST API, микросервисы' },
      { n: 'Базы данных', s: 4, e: 6, c: 'bg-pastel-lavender', d: 'SQL, NoSQL, проектирование и оптимизация БД' },
      { n: 'ML и ИИ', s: 5, e: 7, c: 'bg-pastel-sage', d: 'Python, нейросети, обработка данных, ML-модели' },
      { n: 'Мобильная разработка', s: 6, e: 7, c: 'bg-pastel-sky', d: 'Кроссплатформенная и нативная разработка' },
      { n: 'Дипломный проект', s: 7, e: 8, c: 'bg-pastel-mint', d: 'Реальный проект для компании-партнёра' }
    ],
    directions: [
      { t: 'Кибербезопасность', q: 'Бакалавр', tm: '4 года', f: 'Информатика и ВТ', d: 'Защита систем от кибератак и безопасность данных.' },
      { t: 'Искусственный интеллект', q: 'Бакалавр', tm: '4 года', f: 'Информатика и ВТ', d: 'Машинное обучение, нейросети, NLP и Big Data.' },
      { t: 'Автоматизированное проектирование', q: 'Бакалавр', tm: '4 года', f: 'Информатика и ВТ', d: 'Робототехника, CAD-технологии и автоматизация.' },
      { t: 'Информационные системы', q: 'Бакалавр', tm: '4 года', f: 'ИСиТ', d: 'Проектирование корпоративных систем.' },
      { t: 'Программная инженерия', q: 'Бакалавр', tm: '4 года', f: 'Программная инженерия', d: 'Полный цикл разработки ПО: от архитектуры до DevOps.' }
    ],
    faculty: [
      { n: 'Волков Артем Дмитриевич', c: 'Техно-Сфера', s: ['Кибербезопасность', 'Защита сетей', 'Криптография'] },
      { n: 'Лебедева Виктория Игоревна', c: 'ИТ-Альянс', s: ['Java', 'ООП', 'Enterprise'] },
      { n: 'Романов Максим Сергеевич', c: 'Спектр Софт', s: ['JavaScript', 'Frontend', 'React'] },
      { n: 'Соловьева Екатерина Павловна', c: 'ИнноТех', s: ['Java', 'Backend архитектура'] },
      { n: 'Орлов Никита Александрович', c: 'ДатаЛаб', s: ['Аналитика данных', 'Python'] },
      { n: 'Морозова Дарья Викторовна', c: 'ПрофРазработка', s: ['Системный анализ', 'Бизнес-аналитика'] },
      { n: 'Павлов Андрей Николаевич', c: 'Глобал Системы', s: ['Frontend', 'JavaScript', 'TypeScript'] }
    ],
    achievements: [
      { t: 'II место в Первенстве РФ', d: 'Серебро на нац. первенстве по спорт. программированию.', g: 'Спорт.прог', c: 'bg-pastel-sky', b: 'border-sky' },
      { t: 'III место «Лесное многоборье»', d: 'Команда магистров в тройке лидеров вузов страны.', g: 'Экология', c: 'bg-pastel-mint', b: 'border-mint' },
      { t: 'Победы в конкурсе «УМНИК»', d: 'Гранты на реализацию высокотехнологичных проектов.', g: 'Наука', c: 'bg-pastel-lavender', b: 'border-lavender' }
    ]
  });

  const ICONS = {
    q: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"/></svg>',
    t: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
    f: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>'
  };

  const esc = s => s.replace(/[&<>'"]/g, t => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[t]));
  const getById = id => document.getElementById(id);

  // === RENDER ===
  
  // 1. Directions (УБРАН badge, УБРАН класс reveal)
  const dTrack = getById('directionsTrack');
  const dDots = getById('directionsDots');
  if (dTrack) {
    dTrack.innerHTML = DATA.directions.map(d => `
      <div class="direction-slide">
        <div class="direction-card"> 
          <div class="direction-card-head"><h3 class="direction-title">${esc(d.t)}</h3></div>
          <div class="direction-attrs">
            <div class="direction-attr"><span class="direction-attr-icon">${ICONS.q}</span><div><span class="direction-attr-label">Квалификация</span><span class="direction-attr-value">${esc(d.q)}</span></div></div>
            <div class="direction-attr"><span class="direction-attr-icon">${ICONS.t}</span><div><span class="direction-attr-label">Срок</span><span class="direction-attr-value">${esc(d.tm)}</span></div></div>
            <div class="direction-attr"><span class="direction-attr-icon">${ICONS.f}</span><div><span class="direction-attr-label">Направление</span><span class="direction-attr-value">${esc(d.f)}</span></div></div>
          </div>
          <p class="direction-description">${esc(d.d)}</p>
        </div>
      </div>`).join('');
    dDots.innerHTML = DATA.directions.map(() => `<button class="directions-dot"></button>`).join('');
    
    const slides = dTrack.children, dots = dDots.children;
    let idx = 0;
    const set = i => {
      idx = (i + slides.length) % slides.length;
      [...slides].forEach((s, n) => s.classList.toggle('is-active', n === idx));
      [...dots].forEach((d, n) => { d.classList.toggle('is-active', n === idx); d.ariaCurrent = n===idx; });
    };
    dDots.addEventListener('click', e => e.target.tagName === 'BUTTON' && set([...dots].indexOf(e.target)));
    getById('directionsPrev')?.addEventListener('click', () => set(idx - 1));
    getById('directionsNext')?.addEventListener('click', () => set(idx + 1));
    set(0);
  }

  // 2. Roadmap
  const rGrid = getById('roadmap-grid');
  const rTip = getById('course-tooltip');
  if (rGrid) {
    const cols = { 'bg-pastel-sky':'#bae6fd','bg-pastel-mint':'#a7f3d0','bg-pastel-peach':'#fecaca','bg-pastel-lavender':'#ddd6fe','bg-pastel-coral':'#fda4af','bg-pastel-sage':'#a7f3d0' };
    rGrid.innerHTML = DATA.courses.map((c, idx) => {
      let cells = '';
      for(let i=1; i<=8; i++) {
        const act = i >= c.s && i <= c.e;
        cells += `<div class="roadmap-cell ${act?`active ${c.c}`:'inactive'} ${i===c.s?'start':''} ${i===c.e?'end':''}" ${act?`data-i="${idx}"`:''}>${i===c.s?`<span class="roadmap-cell-text">${c.n}</span>`:''}</div>`;
      }
      return `<div class="roadmap-row">${cells}</div>`;
    }).join('');

    rGrid.addEventListener('mousemove', e => {
      const cell = e.target.closest('.active');
      if (cell) {
        const c = DATA.courses[cell.dataset.i];
        rTip.innerHTML = `<div class="tooltip-icon" style="background:${cols[c.c]}"></div><div class="tooltip-title">${c.n}</div><div class="tooltip-description">${c.d}</div><div class="tooltip-meta">Сем. ${c.s}–${c.e}</div>`;
        Object.assign(rTip.style, { display: 'block', top: `${e.clientY+15}px`, left: `${e.clientX+15}px` });
      } else rTip.style.display = 'none';
    }, { passive: true });
    rGrid.addEventListener('mouseleave', () => rTip.style.display = 'none');
  }

  // 3. Achievements (УБРАНА иконка звезды)
  const aGrid = getById('achievementsGrid');
  if(aGrid) aGrid.innerHTML = DATA.achievements.map(a => `<div class="achievement-card ${a.b} reveal"><div class="achievement-header"><span class="achievement-tag ${a.c}">${a.g}</span></div><h3 class="achievement-title">${esc(a.t)}</h3><p class="achievement-desc">${esc(a.d)}</p></div>`).join('');


  // 4. Faculty
  const fTrack = getById('facultyTrack');
  if (fTrack) {
    const innerHtml = DATA.faculty.map(p => `
      <div class="faculty-card reveal" data-stagger>
        <div class="faculty-photo-placeholder"></div>
        <div class="faculty-info">
          <h3 class="faculty-name">${esc(p.n)}</h3>
          <p class="faculty-company">${esc(p.c)}</p>
          <p class="faculty-disciplines-title">Дисциплины:</p>
          <ul class="faculty-disciplines">${p.s.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>
        </div>
      </div>`).join('');
    fTrack.innerHTML = `<div class="faculty-track-inner">${innerHtml}</div>`;

    const startPhysics = () => {
      const inner = fTrack.firstElementChild;
      let off = 0, max = 0, isD = false, start, startOff, last, vel = 0, raf;
      const upd = () => { max = Math.max(0, inner.scrollWidth - fTrack.clientWidth); if(off>max) off=max; inner.style.transform = `translateX(-${off}px)`; };
      new ResizeObserver(upd).observe(fTrack);
      const move = x => {
        if(!isD) return;
        let n = startOff + (start - x);
        if(n<0 || n>max) n = startOff + (start-x)*0.5;
        off = n; vel = x - last; last = x;
        inner.style.transform = `translateX(-${off}px)`;
      };
      const inertia = () => {
        if(Math.abs(vel)<0.1) return fTrack.classList.remove('faculty-inertia');
        vel*=0.95; off-=vel*1.5;
        if(off<0){off=0;vel=0} else if(off>max){off=max;vel=0}
        inner.style.transform = `translateX(-${off}px)`;
        raf = requestAnimationFrame(inertia);
      };
      const end = () => {
        if(!isD) return;
        isD = false; fTrack.classList.remove('faculty-dragging');
        if(off<0||off>max) { fTrack.classList.add('faculty-inertia'); off=Math.max(0,Math.min(max,off)); inner.style.transform=`translateX(-${off}px)`; }
        else inertia();
      };
      const startDrag = x => { cancelAnimationFrame(raf); fTrack.classList.add('faculty-dragging'); fTrack.classList.remove('faculty-inertia'); isD=true; start=last=x; startOff=off; vel=0; };

      fTrack.addEventListener('mousedown', e => { e.preventDefault(); startDrag(e.pageX); });
      window.addEventListener('mousemove', e => move(e.pageX));
      window.addEventListener('mouseup', end);
      window.addEventListener('mouseleave', end);
      fTrack.addEventListener('touchstart', e => startDrag(e.touches[0].pageX), {passive:true});
      window.addEventListener('touchmove', e => move(e.touches[0].pageX), {passive:false});
      window.addEventListener('touchend', end);

      const scroll = d => {
        const w = inner.firstElementChild ? inner.firstElementChild.offsetWidth + 24 : 300;
        off = Math.max(0, Math.min(max, off + d * w));
        fTrack.classList.add('faculty-inertia');
        inner.style.transform = `translateX(-${off}px)`;
      };
      getById('facultyPrev')?.addEventListener('click', () => scroll(-1));
      getById('facultyNext')?.addEventListener('click', () => scroll(1));
    };

    new IntersectionObserver((entries, obs) => {
      if (entries[0].isIntersecting) { startPhysics(); obs.disconnect(); }
    }).observe(fTrack);
  }

  // === GLOBAL UI & ANIMATIONS ===
  const yearEl = getById('current-year');
  if(yearEl) yearEl.textContent = new Date().getFullYear();
  
  const header = getById('header');
  window.addEventListener('scroll', () => requestAnimationFrame(() => header.classList.toggle('scrolled', window.scrollY > 50)), {passive:true});

  const obs = new IntersectionObserver(es => es.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target)}}), {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(e => obs.observe(e));

  const staggerSelector = '.disciplines-grid, .features-grid, .directions-carousel, .faculty-track-inner';
  document.querySelectorAll(staggerSelector).forEach(container => {
    const children = container.querySelectorAll('[data-stagger], .faculty-card');
    children.forEach((el, i) => {
      const delay = container.classList.contains('faculty-track-inner') ? 0.05 : 0.1;
      el.style.animationDelay = `${delay * (i + 1)}s`;
    });
  });

  // Form
  const form = getById('applyForm');
  const msg = getById('formSuccess');
  if(form) form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const txt = btn.textContent;
    btn.disabled=true; btn.textContent='Отправка...';
    setTimeout(() => { btn.textContent=txt; btn.disabled=false; form.reset(); msg.style.display='flex'; setTimeout(()=>msg.style.display='none',5000); }, 1000);
  });

  // Nav
  const nav = document.querySelector('.header-nav');
  const links = document.querySelectorAll('.nav-link');
  if(nav) nav.addEventListener('click', e => {
    if(e.target.classList.contains('nav-link')) getById(e.target.dataset.target)?.scrollIntoView({behavior:'smooth'});
  });

  // ScrollSpy
  let tick = false;
  window.addEventListener('scroll', () => {
    if(!tick) {
      window.requestAnimationFrame(() => {
        const curr = ['roadmap','faculty','features','disciplines','directions'].find(id => {
           const el = getById(id); return el && window.scrollY >= el.offsetTop - 200;
        });
        links.forEach(l => l.classList.toggle('active', l.dataset.target === curr));
        tick = false;
      });
      tick = true;
    }
  }, {passive:true});

  // FAQ
  document.querySelector('.faq-column')?.addEventListener('click', e => {
    const btn = e.target.closest('.faq-question');
    if(!btn) return;
    const item = btn.parentElement, ans = item.querySelector('.faq-answer');
    if(item.classList.contains('active')) {
      item.classList.remove('active'); ans.style.maxHeight = null;
    } else {
      document.querySelectorAll('.faq-item.active').forEach(i => { i.classList.remove('active'); i.querySelector('.faq-answer').style.maxHeight = null; });
      item.classList.add('active'); ans.style.maxHeight = ans.scrollHeight + 'px';
    }
  });

})();