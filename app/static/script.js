(() => {
  'use strict';

  // ================= 0. ИНИЦИАЛИЗАЦИЯ LENIS =================
  let lenis;
  if (typeof Lenis !== 'undefined') {
    lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      touchMultiplier: 2,
    });
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
  }

  // ================= 1. UTIL & HELPERS =================
  const esc = s => (s ? String(s).replace(/[&<>'"]/g, t => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[t])) : '');
  const getById = id => document.getElementById(id);

  const COLORS = ['bg-pastel-sky', 'bg-pastel-mint', 'bg-pastel-peach', 'bg-pastel-lavender', 'bg-pastel-coral', 'bg-pastel-sage'];
  const BORDERS = ['border-sky', 'border-mint', 'border-peach', 'border-lavender', 'border-coral', 'border-sage'];
  const getColor = (i) => COLORS[i % COLORS.length];
  const getBorder = (i) => BORDERS[i % BORDERS.length];

  const ICONS = {
    q: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"/></svg>',
    t: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
    f: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>'
  };

  // Универсальный скролл
  const scrollToElem = (id) => {
    const el = typeof id === 'string' ? getById(id) : id;
    if (el) {
      if (lenis) lenis.scrollTo(el);
      else el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // ================= 2. FETCH & LOAD =================
  let allSpecialities = [];

  async function loadData() {
    const endpoints = [
      { key: 'speciality', url: '/speciality' },
      { key: 'subjects', url: '/subjects' },
      { key: 'features', url: '/features' },
      { key: 'teachers', url: '/teachers' },
      { key: 'achievements', url: '/achievements' },
      { key: 'directions', url: '/directions-with-disciplines' },
      { key: 'faqs', url: '/faqs' },
      { key: 'settings', url: '/settings' },
      { key: 'timeline', url: '/timeline' },
      { key: 'life', url: '/life-events' }
    ];

    // Загружаем всё параллельно, но обрабатываем каждую ошибку отдельно
    const results = await Promise.all(
      endpoints.map(e => fetch(e.url).then(r => r.json()).catch(err => {
        console.warn(`Ошибка загрузки ${e.key}:`, err);
        return null; // Возвращаем null вместо падения всего промиса
      }))
    );

    const [spec, subj, feat, teach, ach, dir, faq, sett, time, life] = results;

    if (spec) {
      allSpecialities = spec;
      initSpecialitiesFilter();
    }
    
    if (subj) renderSubjects(subj);
    if (feat) renderFeatures(feat);
    if (teach) renderTeachers(teach);
    if (ach) renderAchievements(ach);
    if (dir) {
        initRoadmap(dir);
        populateApplySelect(dir);
    }
    if (faq) renderFaqs(faq);
    if (sett) applySettings(sett);
    if (time) renderTimeline(time);
    if (life) renderLife(life);

    initObservers();
  }

  // ================= 3. RENDER FUNCTIONS =================

  function initSpecialitiesFilter() {
    const inputs = document.querySelectorAll('input[name="qualification"]');
    const update = () => {
      const active = document.querySelector('input[name="qualification"]:checked')?.value || 'Бакалавриат';
      renderSpecialities(allSpecialities.filter(s => s.qualification.toLowerCase() === active.toLowerCase()));
    };
    inputs.forEach(i => i.addEventListener('change', update));
    update();
  }

  let specIdx = 0;
  function renderSpecialities(data) {
    const track = getById('directionsTrack'), dots = getById('directionsDots');
    if (!track || !dots) return;

    track.innerHTML = data.length ? data.map(d => `
      <div class="direction-slide">
        <div class="direction-card">
          <div class="direction-card-head"><h3 class="direction-title">${esc(d.name)}</h3></div>
          <div class="direction-attrs">
            <div class="direction-attr"><span class="direction-attr-icon">${ICONS.q}</span><div><span class="direction-attr-label">Квалификация</span><span class="direction-attr-value">${esc(d.qualification)}</span></div></div>
            <div class="direction-attr"><span class="direction-attr-icon">${ICONS.t}</span><div><span class="direction-attr-label">Срок</span><span class="direction-attr-value">${d.term} года</span></div></div>
            <div class="direction-attr"><span class="direction-attr-icon">${ICONS.f}</span><div><span class="direction-attr-label">Направление</span><span class="direction-attr-value">${esc(d.direction)}</span></div></div>
          </div>
          <p class="direction-description">${esc(d.description)}</p>
        </div>
      </div>`).join('') : '<p style="padding:2rem; color:var(--muted-foreground);">Нет программ в этой категории.</p>';

    dots.innerHTML = data.map((_, i) => `<button class="directions-dot ${i===0?'is-active':''}" aria-label="Слайд ${i+1}"></button>`).join('');

    const set = i => {
      specIdx = (i + data.length) % data.length;
      track.style.transform = `translateX(-${specIdx * 100}%)`;
      [...dots.children].forEach((d, n) => d.classList.toggle('is-active', n === specIdx));
    };

    getById('directionsPrev').onclick = () => set(specIdx - 1);
    getById('directionsNext').onclick = () => set(specIdx + 1);
    dots.onclick = e => e.target.classList.contains('directions-dot') && set([...dots.children].indexOf(e.target));
  }

  function renderSubjects(data) {
    const grid = getById('subjectsGrid');
    if (grid) grid.innerHTML = data.map((s, i) => `
      <div class="discipline-card reveal hover-lift" data-stagger>
        <div class="discipline-icon ${getColor(i)}"><i class="${esc(s.svg_code || 'fa-solid fa-circle')}" style="font-size: 1.75rem;"></i></div>
        <h4 class="discipline-title">${esc(s.name)}</h4>
        <p class="discipline-description">${esc(s.description)}</p>
      </div>`).join('');
  }

  function renderFeatures(data) {
    const grid = getById('featuresGrid');
    if (grid) grid.innerHTML = data.map((f, i) => `
      <div class="feature-card hover-lift reveal" data-stagger>
        <div class="feature-icon ${getColor(i)}"><i class="${esc(f.svg_code || 'fa-solid fa-check')}" style="font-size: 1.5rem;"></i></div>
        <div><h3 class="feature-title">${esc(f.title)}</h3><p class="feature-description">${esc(f.description)}</p></div>
      </div>`).join('');
  }

  function renderTeachers(data) {
    const track = getById('facultyTrack');
    if (!track) return;
    track.innerHTML = `<div class="faculty-track-inner">${data.map(t => `
      <div class="faculty-card reveal" data-stagger>
        <div class="faculty-photo-placeholder" style="overflow:hidden;">
            ${t.image_url ? `<img src="${esc(t.image_url)}" alt="${esc(t.fio)}" loading="lazy" style="width:100%; height:100%; object-fit:cover; object-position: top center;">` : '<div style="width:100%; height:100%; background:#ddd; display:flex; align-items:center; justify-content:center; color:#777;">Нет фото</div>'}
        </div>
        <div class="faculty-info">
          <h3 class="faculty-name">${esc(t.fio)}</h3>
          <p class="faculty-company">${esc(t.post)}</p>
          <p class="faculty-disciplines-title">Дисциплины:</p>
          <ul class="faculty-disciplines">${t.subjects.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>
        </div>
      </div>`).join('')}</div>`;
    initFacultyPhysics(track);
  }

  function renderAchievements(data) {
    const grid = getById('achievementsGrid');
    if (grid) grid.innerHTML = data.map((a, i) => `
      <div class="achievement-card ${getBorder(i)} reveal">
        <div class="achievement-header"><span class="achievement-tag ${getColor(i)}">${esc(a.theme)}</span></div>
        <h3 class="achievement-title">${esc(a.title)}</h3>
        <p class="achievement-desc">${esc(a.description)}</p>
      </div>`).join('');
  }

  function renderLife(data) {
    const bGrid = getById('bentoGrid'), lArchive = getById('lifeArchive'), tBtn = getById('toggleLifeArchive');
    if (!bGrid || !lArchive || !data.length) return;

    const highlights = data.filter(d => d.is_main).slice(0, 4);
    const archive = data.filter(d => !highlights.includes(d));

    const cardHtml = (d, i, isArch = false) => `
      <div class="photo-card reveal ${isArch ? 'archive-card' : `bento-${i+1}`}" data-stagger>
        <img src="${esc(d.image_url)}" alt="${esc(d.title)}" loading="lazy">
        <div class="card-content">
          <span class="card-tag">${esc(d.tag)}</span>
          <h3 class="card-title">${esc(d.title)}</h3>
        </div>
      </div>`;

    bGrid.innerHTML = highlights.map((d, i) => cardHtml(d, i)).join('');
    lArchive.innerHTML = archive.map((d, i) => cardHtml(d, i, true)).join('');

    if (archive.length) {
      tBtn.style.display = 'inline-block';
      tBtn.textContent = `Показать еще ${archive.length} фото`;
      tBtn.onclick = () => {
        const isV = lArchive.classList.toggle('visible');
        tBtn.textContent = isV ? 'Свернуть архив' : `Показать еще ${archive.length} фото`;
        if (!isV) scrollToElem('institute-life');
      };
    }
  }

  function renderFaqs(data) {
    const container = getById('faqContainer');
    if (container) container.innerHTML = data.map(item => `
      <div class="faq-item">
        <button class="faq-question"><span>${esc(item.question)}</span><span class="faq-icon">+</span></button>
        <div class="faq-answer"><p>${esc(item.answer)}</p></div>
      </div>`).join('');
  }

  function applySettings(data) {
    data.forEach(s => {
      const el = getById(`setting_${s.key}`);
      if (el) s.key.endsWith('_link') && el.hasAttribute('href') ? el.href = s.value : el.innerHTML = s.value;
    });
  }

  function renderTimeline(data) {
    const wrapper = document.querySelector('.timeline-wrapper');
    if (wrapper && data.length) {
      wrapper.innerHTML = '<div class="timeline-line"></div>' + data.map((step, i) => `
        <div class="timeline-item reveal">
          <div class="timeline-marker ${esc(step.color_class)}">${i + 1}</div>
          <div class="timeline-content hover-lift">
            <span class="timeline-term">${esc(step.term)}</span>
            <h3 class="timeline-heading">${esc(step.title)}</h3>
            <p class="timeline-desc">${esc(step.description)}</p>
          </div>
        </div>`).join('');
    }
  }

  function populateApplySelect(directions) {
    const select = getById('leadDirection');
    if (select && directions.length) {
      select.innerHTML = select.options[0].outerHTML + directions.map(d => `<option value="${esc(d.name)}">${esc(d.name)}</option>`).join('');
    }
  }

  // ================= 4. ROADMAP & PHYSICS =================
  function initRoadmap(directionsData) {
    const rSelect = getById('roadmapSelect'), rGrid = getById('roadmap-grid'), rTip = getById('course-tooltip');
    if (!rGrid || !directionsData.length) return;

    rSelect.innerHTML = directionsData.map((d, i) => `<option value="${i}">${esc(d.name)}</option>`).join('');

    const drawGrid = (idx) => {
        const groups = {};
        directionsData[idx].disciplines.forEach(d => {
            const g = d.group || "Общие";
            if (!groups[g]) groups[g] = [];
            groups[g].push(d);
        });

        const gNames = Object.keys(groups).sort((a,b) => a==="Общие"?-1:b==="Общие"?1:a.localeCompare(b));
        rGrid.innerHTML = gNames.map((gName, gIdx) => {
            const lanes = [];
            [...groups[gName]].sort((a,b) => a.start_term - b.start_term || (b.end_term-b.start_term)-(a.end_term-a.start_term))
                .forEach(d => {
                    let p = lanes.find(l => d.start_term > l[l.length-1].end_term);
                    if(p) p.push(d); else lanes.push([d]);
                });

            const rows = lanes.map(lane => {
                let cells = '', cur = 1;
                lane.forEach(d => {
                    if (d.start_term > cur) cells += `<div class="roadmap-cell inactive" style="grid-column: span ${d.start_term-cur};"></div>`;
                    cells += `<div class="roadmap-cell active ${getColor(gIdx)} start end" style="grid-column: span ${d.end_term-d.start_term+1};" data-desc="${esc(gName)} | Сем: ${d.start_term}-${d.end_term}" data-name="${esc(d.name)}"><span class="roadmap-cell-text">${esc(d.name)}</span></div>`;
                    cur = d.end_term + 1;
                });
                if (cur <= 8) cells += `<div class="roadmap-cell inactive" style="grid-column: span ${9-cur};"></div>`;
                return `<div class="roadmap-row" style="grid-template-columns: repeat(8, 1fr); display: grid;">${cells}</div>`;
            }).join('');

            return `<div class="roadmap-row"><div class="roadmap-group-title">${esc(gName)}</div><div style="grid-column: span 8; display: flex; flex-direction: column; gap: 0.5rem;">${rows}</div></div><div style="height: 1px; background: var(--border); margin: 0.5rem 0 1rem 0; opacity: 0.5; grid-column: 1 / -1;"></div>`;
        }).join('');
    };

    drawGrid(0);
    rSelect.onchange = e => drawGrid(e.target.value);

    const bgMap = { 'bg-pastel-sky':'#bae6fd','bg-pastel-mint':'#a7f3d0','bg-pastel-peach':'#fecaca','bg-pastel-lavender':'#ddd6fe','bg-pastel-coral':'#fda4af','bg-pastel-sage':'#a7f3d0' };
    rGrid.onmousemove = e => {
      const c = e.target.closest('.active');
      if (c) {
        const cl = Array.from(c.classList).find(x => x.startsWith('bg-pastel'));
        rTip.innerHTML = `<div class="tooltip-icon" style="background:${bgMap[cl]||'#ccc'}"></div><div class="tooltip-title">${c.dataset.name}</div><div class="tooltip-meta">${c.dataset.desc}</div>`;
        rTip.style.display = 'block'; rTip.style.top = `${e.clientY + 15}px`; rTip.style.left = `${e.clientX + 15}px`;
      } else rTip.style.display = 'none';
    };
    rGrid.onmouseleave = () => rTip.style.display = 'none';
  }

  function initFacultyPhysics(fTrack) {
      const inner = fTrack.firstElementChild;
      let off = 0, max = 0, isD = false, start, startOff, last, vel = 0, rafP;
      const upd = () => { max = Math.max(0, inner.scrollWidth - fTrack.clientWidth); if(off>max) off=max; inner.style.transform = `translateX(-${off}px)`; };
      new ResizeObserver(upd).observe(fTrack);
      const move = x => { if(!isD) return; let n = startOff + (start - x); if(n<0 || n>max) n = startOff + (start-x)*0.5; off = n; vel = x - last; last = x; inner.style.transform = `translateX(-${off}px)`; };
      const inertia = () => { if(Math.abs(vel)<0.1) return fTrack.classList.remove('faculty-inertia'); vel*=0.89; off-=vel*1.2; if(off<0){off=0;vel=0} else if(off>max){off=max;vel=0} inner.style.transform = `translateX(-${off}px)`; rafP = requestAnimationFrame(inertia); };
      const end = () => { if(!isD) return; isD = false; fTrack.classList.remove('faculty-dragging'); if(off<0||off>max) { fTrack.classList.add('faculty-inertia'); off=Math.max(0,Math.min(max,off)); inner.style.transform=`translateX(-${off}px)`; } else inertia(); };
      const startDrag = x => { cancelAnimationFrame(rafP); fTrack.classList.add('faculty-dragging'); fTrack.classList.remove('faculty-inertia'); isD=true; start=last=x; startOff=off; vel=0; };
      fTrack.onmousedown = e => { e.preventDefault(); startDrag(e.pageX); };
      window.onmousemove = e => move(e.pageX);
      window.onmouseup = end;
      fTrack.ontouchstart = e => startDrag(e.touches[0].pageX);
      window.ontouchmove = e => move(e.touches[0].pageX);
      window.ontouchend = end;
      const scroll = d => { off = Math.max(0, Math.min(max, off + d * 324)); inner.style.transform = `translateX(-${off}px)`; };
      getById('facultyPrev').onclick = () => scroll(-1);
      getById('facultyNext').onclick = () => scroll(1);
  }

  // ================= 5. UI & OBSERVERS =================
  function initObservers() {
    const obs = new IntersectionObserver(es => es.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target)}}), {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
    document.querySelectorAll('.reveal').forEach(e => obs.observe(e));
    document.querySelectorAll('.disciplines-grid, .features-grid, .faculty-track-inner, .bento-grid, #lifeArchive').forEach(container => {
        container.querySelectorAll('[data-stagger], .faculty-card, .photo-card').forEach((el, i) => {
          el.style.animationDelay = `${(container.classList.contains('faculty-track-inner') ? 0.05 : 0.1) * (i + 1)}s`;
        });
    });
  }

  // Year & Header
  if(getById('current-year')) getById('current-year').textContent = new Date().getFullYear();
  const header = getById('header');
  window.addEventListener('scroll', () => requestAnimationFrame(() => header.classList.toggle('scrolled', window.scrollY > 50)), {passive:true});

  // ScrollSpy
  const links = document.querySelectorAll('.nav-link');
  const sections = ['apply','achievements','institute-life','roadmap','faculty','features','disciplines','directions'];
  window.addEventListener('scroll', () => {
    requestAnimationFrame(() => {
        const cur = sections.find(id => { const el = getById(id); return el && window.scrollY >= el.offsetTop - 300; });
        links.forEach(l => l.classList.toggle('active', l.dataset.target === cur));
    });
  }, {passive:true});

  // Global Clicks (Scroll & Menu)
  document.addEventListener('click', e => {
    const navLink = e.target.closest('.nav-link') || (e.target.tagName === 'A' && e.target.hash && getById(e.target.hash.substring(1)) ? e.target : null);
    if (navLink) {
        const targetId = navLink.dataset.target || navLink.hash.substring(1);
        if (targetId) {
            e.preventDefault();
            scrollToElem(targetId);
            getById('menuToggle').classList.remove('active');
            getById('navLinks').classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    if (e.target.closest('#menuToggle')) {
        const btn = getById('menuToggle'), menu = getById('navLinks');
        btn.classList.toggle('active');
        menu.classList.toggle('active');
        document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
    }

    const faqBtn = e.target.closest('.faq-question');
    if (faqBtn) {
        const item = faqBtn.parentElement, ans = item.querySelector('.faq-answer');
        const isA = item.classList.toggle('active');
        ans.style.maxHeight = isA ? ans.scrollHeight + 'px' : null;
        if (isA) document.querySelectorAll('.faq-item.active').forEach(i => { if(i!==item){i.classList.remove('active'); i.querySelector('.faq-answer').style.maxHeight=null;}});
    }
  });

  // Form
  const form = getById('applyForm');
  if(form) form.onsubmit = e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]'), txt = btn.textContent;
    btn.disabled=true; btn.textContent='Отправка...';
    setTimeout(() => { btn.textContent=txt; btn.disabled=false; form.reset(); getById('formSuccess').style.display='flex'; setTimeout(()=>getById('formSuccess').style.display='none',5000); }, 1000);
  };

  loadData();
})();
