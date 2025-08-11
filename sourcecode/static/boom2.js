(() => {
  const MAX_PARTICLES = 120;          
  const PARTICLES_PER_TICK = 3;       
  const LIFE = 500;                   
  const particles = [];
  let mouse = { x: 0, y: 0, dirty: false };

  
  for (let i = 0; i < MAX_PARTICLES; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.opacity = 0;
    p.addEventListener('animationend', () => {
      p.style.opacity = 0; 
    });
    document.body.appendChild(p);
    particles.push({ el: p, alive: false });
  }

  window.addEventListener('pointermove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.dirty = true;
  }, { passive: true });

  function loop() {
    if (mouse.dirty) {
      for (let i = 0; i < PARTICLES_PER_TICK; i++) {
        spawn(mouse.x, mouse.y);
      }
      mouse.dirty = false;
    }
    requestAnimationFrame(loop);
  }

  function spawn(x, y) {
    const slot = particles.find(p => !p.alive);
    if (!slot) return; 

    const p = slot.el;
    slot.alive = true;

    const size = rand(10, 18);
    const dx = rand(-8, 8);
    const dy = rand(30, 80);
    const hue = rand(10, 60);

    p.style.width = size + 'px';
    p.style.height = size + 'px';

    p.style.background = `radial-gradient(circle, rgba(255,255,255,0.95) 0%, hsl(${hue},100%,60%) 40%, rgba(255,0,0,0.6) 100%)`;
    p.style.setProperty('--x', (x - size / 2) + 'px');
    p.style.setProperty('--y', (y - size / 2) + 'px');
    p.style.setProperty('--dx', dx + 'px');
    p.style.setProperty('--dy', dy + 'px');

    p.style.setProperty('--particle-life', LIFE + 'ms');

    p.style.animation = 'none';
    
    p.offsetHeight;
    p.style.opacity = 1;
    p.style.animation = `exhaust var(--particle-life) ease-out forwards`;

    setTimeout(() => { slot.alive = false; }, LIFE);
  }

  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  loop();
})();