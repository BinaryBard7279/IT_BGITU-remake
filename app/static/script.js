(() => {
  'use strict';

  // ================= 0. ИНИЦИАЛИЗАЦИЯ LENIS =================
  let lenis;
  if (typeof Lenis !== 'undefined') {
    lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
    });
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const targetElem = document.getElementById(targetId);
        if (targetElem) lenis.scrollTo(targetElem);
      });
    });
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
    f: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    default: '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/></svg>'
  };

  // ================= 2. FETCH DATA =================
  async function loadData() {
    try {
      // ОПТИМИЗАЦИЯ: 1 запрос вместо 6
      const res = await fetch('/api/initial-state');
      const data = await res.json();

      renderSpecialities(data.specialities);
      renderSubjects(data.subjects);
      renderFeatures(data.features);
      renderTeachers(data.teachers);
      renderAchievements(data.achievements);
      initRoadmap(data.directions);

      initObservers();
    } catch (err) {
      console.error('Ошибка загрузки данных:', err);
    }
  }

  // ================= 3. RENDER FUNCTIONS =================

  function renderSpecialities(data) {
    const dTrack = getById('directionsTrack');
    const dDots = getById('directionsDots');
    if (!dTrack || !data.length) return;

    dTrack.innerHTML = data.map(d => `
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
      </div>`).join('');

    dDots.innerHTML = data.map((_, i) => `<button class="directions-dot ${i===0?'is-active':''}" aria-label="Слайд ${i+1}"></button>`).join('');

    const dots = dDots.children;
    const count = data.length;
    let idx = 0;
    const set = i => {
      idx = (i + count) % count;
      dTrack.style.transform = `translateX(-${idx * 100}%)`;
      [...dots].forEach((d, n) => d.classList.toggle('is-active', n === idx));
    };
    dDots.addEventListener('click', e => e.target.classList.contains('directions-dot') && set([...dots].indexOf(e.target)));
    getById('directionsPrev')?.addEventListener('click', () => set(idx - 1));
    getById('directionsNext')?.addEventListener('click', () => set(idx + 1));
  }

  // --- Дисциплины (FontAwesome) ---
  function renderSubjects(data) {
    const grid = getById('subjectsGrid');
    if (!grid) return;
    
    grid.innerHTML = data.map((s, i) => {
      // Если в БД пусто, ставим дефолтную иконку (круг)
      // В БД ожидаем строку типа: "fa-solid fa-code"
      const iconClass = s.svg_code ? s.svg_code : 'fa-solid fa-circle';
      
      return `
      <div class="discipline-card reveal hover-lift" data-stagger>
        <div class="discipline-icon ${getColor(i)}">
           <i class="${esc(iconClass)}" style="font-size: 1.75rem;"></i>
        </div>
        <h4 class="discipline-title">${esc(s.name)}</h4>
        <p class="discipline-description">${esc(s.description)}</p>
      </div>
    `}).join('');
  }

  // --- Преимущества (FontAwesome) ---
  function renderFeatures(data) {
    const grid = getById('featuresGrid');
    if (!grid) return;
    
    grid.innerHTML = data.map((f, i) => {
      const iconClass = f.svg_code ? f.svg_code : 'fa-solid fa-check';

      return `
      <div class="feature-card hover-lift reveal" data-stagger>
        <div class="feature-icon ${getColor(i)}">
            <i class="${esc(iconClass)}" style="font-size: 1.5rem;"></i>
        </div>
        <div>
            <h3 class="feature-title">${esc(f.title)}</h3>
            <p class="feature-description">${esc(f.description)}</p>
        </div>
      </div>
    `}).join('');
  }
  // --- Преподаватели (Teachers) ---
  function renderTeachers(data) {
    const fTrack = getById('facultyTrack');
    if (!fTrack) return;

    const innerHtml = data.map(t => {
      // Если есть URL картинки, используем img, иначе цветную заглушку
      const imgBlock = t.image_url 
        ? `<img src="${esc(t.image_url)}" alt="${esc(t.fio)}" style="width:100%; height:100%; object-fit:cover; object-position: top center;">` 
        : `<div style="width:100%; height:100%; background:#ddd; display:flex; align-items:center; justify-content:center; color:#777;">Нет фото</div>`;

      return `
      <div class="faculty-card reveal" data-stagger>
        <div class="faculty-photo-placeholder" style="overflow:hidden;">
            ${imgBlock}
        </div>
        <div class="faculty-info">
          <h3 class="faculty-name">${esc(t.fio)}</h3>
          <p class="faculty-company">${esc(t.post)}</p>
          <p class="faculty-disciplines-title">Дисциплины:</p>
          <ul class="faculty-disciplines">${t.subjects.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>
        </div>
      </div>`
    }).join('');

    fTrack.innerHTML = `<div class="faculty-track-inner">${innerHtml}</div>`;
    initFacultyPhysics(fTrack);
  }

  // --- Достижения ---
  function renderAchievements(data) {
    const grid = getById('achievementsGrid');
    if (!grid) return;
    grid.innerHTML = data.map((a, i) => `
      <div class="achievement-card ${getBorder(i)} reveal">
        <div class="achievement-header">
            <span class="achievement-tag ${getColor(i)}">${esc(a.theme)}</span>
        </div>
        <h3 class="achievement-title">${esc(a.title)}</h3>
        <p class="achievement-desc">${esc(a.description)}</p>
      </div>
    `).join('');
  }

  // --- Roadmap Logic (План) ---
  // --- Roadmap Logic (План с группировкой и упаковкой) ---
  function initRoadmap(directionsData) {
    const rSelect = getById('roadmapSelect');
    const rGrid = getById('roadmap-grid');
    const rTip = getById('course-tooltip');
    
    if (!rGrid || !directionsData.length) return;

    // Заполняем Select
    rSelect.innerHTML = directionsData.map((d, i) => 
        `<option value="${i}">${esc(d.name)}</option>`
    ).join('');

    // --- Алгоритм упаковки предметов в строки ---
    const packDisciplines = (disciplines) => {
        // Сортировка: сначала ранние семестры, при равенстве - самые длинные
        const sorted = [...disciplines].sort((a, b) => {
            if (a.start_term !== b.start_term) return a.start_term - b.start_term;
            return (b.end_term - b.start_term) - (a.end_term - a.start_term);
        });

        const lanes = []; // Массив "строк"

        sorted.forEach(disc => {
            let placed = false;
            // Ищем строку, куда влезет предмет
            for (let lane of lanes) {
                const lastItem = lane[lane.length - 1];
                // Если предмет начинается ПОСЛЕ окончания последнего в строке
                if (disc.start_term > lastItem.end_term) {
                    lane.push(disc);
                    placed = true;
                    break;
                }
            }
            // Если не нашли место, создаем новую строку
            if (!placed) lanes.push([disc]);
        });
        return lanes;
    };

    // Функция отрисовки
    const drawGrid = (directionIndex) => {
        const direction = directionsData[directionIndex];
        const allDisciplines = direction.disciplines || [];

        // 1. Группируем предметы
        const groups = {};
        allDisciplines.forEach(d => {
            const gName = d.group || "Общие";
            if (!groups[gName]) groups[gName] = [];
            groups[gName].push(d);
        });

        // Сортировка групп ("Общие" всегда сверху)
        const groupNames = Object.keys(groups).sort((a, b) => {
            if(a === "Общие") return -1;
            if(b === "Общие") return 1;
            return a.localeCompare(b);
        });

        let html = '';

        groupNames.forEach((gName, gIndex) => {
            const groupDisciplines = groups[gName];
            const packedLanes = packDisciplines(groupDisciplines);
            const colorClass = getColor(gIndex);

            // Генерируем HTML для строк внутри группы
            const rowsHtml = packedLanes.map(lane => {
                let cellsHtml = '';
                let currentTerm = 1;

                lane.forEach(disc => {
                    // Пустота ДО предмета
                    if (disc.start_term > currentTerm) {
                        const emptySpan = disc.start_term - currentTerm;
                        cellsHtml += `<div class="roadmap-cell inactive" style="grid-column: span ${emptySpan};"></div>`;
                    }
                    // Предмет
                    const duration = disc.end_term - disc.start_term + 1;
                    cellsHtml += `
                        <div class="roadmap-cell active ${colorClass} start end" 
                             style="grid-column: span ${duration};"
                             data-desc="${esc(gName)} | Семестры: ${disc.start_term}-${disc.end_term}" 
                             data-name="${esc(disc.name)}">
                             <span class="roadmap-cell-text">${esc(disc.name)}</span>
                        </div>
                    `;
                    currentTerm = disc.end_term + 1;
                });

                // Пустота ПОСЛЕ последнего предмета
                if (currentTerm <= 8) {
                    const remaining = 9 - currentTerm;
                    cellsHtml += `<div class="roadmap-cell inactive" style="grid-column: span ${remaining};"></div>`;
                }

                return `<div class="roadmap-row" style="grid-template-columns: repeat(8, 1fr); display: grid;">${cellsHtml}</div>`;
            }).join('');

            // Сборка группы
            html += `
                <div class="roadmap-row">
                    <div class="roadmap-group-title">${esc(gName)}</div>
                    <div style="grid-column: span 8; display: flex; flex-direction: column; gap: 0.5rem;">
                        ${rowsHtml}
                    </div>
                </div>
                <div style="height: 1px; background: var(--border); margin: 0.5rem 0 1rem 0; opacity: 0.5; grid-column: 1 / -1;"></div>
            `;
        });

        rGrid.innerHTML = html;
    };

    drawGrid(0);
    rSelect.addEventListener('change', (e) => drawGrid(e.target.value));

    // Tooltip
    const bgMap = { 'bg-pastel-sky':'#bae6fd','bg-pastel-mint':'#a7f3d0','bg-pastel-peach':'#fecaca','bg-pastel-lavender':'#ddd6fe','bg-pastel-coral':'#fda4af','bg-pastel-sage':'#a7f3d0' };
    rGrid.addEventListener('mousemove', e => {
      const cell = e.target.closest('.active');
      if (cell) {
        const colorClass = Array.from(cell.classList).find(c => c.startsWith('bg-pastel'));
        const hex = bgMap[colorClass] || '#ccc';
        rTip.innerHTML = `
            <div class="tooltip-icon" style="background:${hex}"></div>
            <div class="tooltip-title">${cell.dataset.name}</div>
            <div class="tooltip-meta">${cell.dataset.desc}</div>`;
        rTip.style.display = 'block';
        rTip.style.top = `${e.clientY + 15}px`;
        rTip.style.left = `${e.clientX + 15}px`;
      } else rTip.style.display = 'none';
    }, { passive: true });
    rGrid.addEventListener('mouseleave', () => rTip.style.display = 'none');
  }
  // ================= 4. PHYSICS & UI (Старый код) =================
 function initObservers() {
    // Reveal анимации (уже было)
    const obs = new IntersectionObserver(es => es.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target)}}), {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
    document.querySelectorAll('.reveal').forEach(e => obs.observe(e));
    
    // ОПТИМИЗАЦИЯ ScrollSpy: Заменяем window.addEventListener('scroll') на IntersectionObserver
    const links = document.querySelectorAll('.nav-link');
    const sections = ['roadmap', 'faculty', 'features', 'disciplines', 'directions'].map(id => document.getElementById(id)).filter(Boolean);
    
    const spyObs = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                links.forEach(l => l.classList.toggle('active', l.dataset.target === entry.target.id));
            }
        });
    }, { rootMargin: '-30% 0px -70% 0px' }); // Триггер в верхней трети экрана
    
    sections.forEach(sec => spyObs.observe(sec));
  }

  function initObservers() {
    const obs = new IntersectionObserver(es => es.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target)}}), {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
    document.querySelectorAll('.reveal').forEach(e => obs.observe(e));
    
    document.querySelectorAll('.disciplines-grid, .features-grid, .faculty-track-inner').forEach(container => {
        const children = container.querySelectorAll('[data-stagger], .faculty-card');
        children.forEach((el, i) => {
          const delay = container.classList.contains('faculty-track-inner') ? 0.05 : 0.1;
          el.style.animationDelay = `${delay * (i + 1)}s`;
        });
      });
  }

  // Global UI
  const yearEl = getById('current-year');
  if(yearEl) yearEl.textContent = new Date().getFullYear();
  
  const header = getById('header');
  window.addEventListener('scroll', () => requestAnimationFrame(() => header.classList.toggle('scrolled', window.scrollY > 50)), {passive:true});


  // Form Submit
  const form = getById('applyForm');
  const msg = getById('formSuccess');
  if(form) form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const txt = btn.textContent;
    btn.disabled=true; btn.textContent='Отправка...';
    setTimeout(() => { btn.textContent=txt; btn.disabled=false; form.reset(); msg.style.display='flex'; setTimeout(()=>msg.style.display='none',5000); }, 1000);
  });
  
  // Nav Click
  const nav = document.querySelector('.header-nav');
  if(nav) nav.addEventListener('click', e => {
    if(e.target.classList.contains('nav-link')) {
        const targetId = e.target.dataset.target;
        const targetElem = getById(targetId);
        if(targetElem) {
            if(lenis) lenis.scrollTo(targetElem); 
            else targetElem.scrollIntoView({behavior:'smooth'}); 
        }
    }
  });

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

  // ЗАПУСК ЗАГРУЗКИ ДАННЫХ
  loadData();

})();