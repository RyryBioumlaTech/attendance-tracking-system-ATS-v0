function updateDate(){

    let now = new Date();

    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    const timeString = hours + ":" + minutes + ":" + seconds;
    document.getElementById("time").textContent =  timeString;

    const days = ['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'];
    const months = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];

    const day = days[now.getDay()];
    const daynumber = now.getDate();
    const month = months[now.getMonth()];
    const year = now.getFullYear();

    const dateString = day + " " + daynumber + " " + month + " " + year;
    document.getElementById("date").textContent = dateString;
}

function showToast(message, duration = 10000) {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 1);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function updateQr(){
    
    fetch('/qr_update')
        .then(response => response.json())
        .then(data => {
            const qrImg = document.getElementById('qr');
            qrImg.src = "data:image/png;base64," + data.qr;
        })
}

setInterval(updateDate, 1000);

function syncQrUpdate() {
    const now = new Date();
    const NextMinute = (60 - now.getSeconds()) * 1000 - now.getMilliseconds();

    setTimeout(() => {
        updateQr();
        setInterval(updateQr, 60000);
    }, NextMinute);
}

window.onload = () => {
    updateDate();
    updateQr();
    syncQrUpdate();
};

function showToast(message, duration = 3000) {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

const socket = io();
socket.on('qr_validated', (data) => {
    showToast(`Scan success for ${data.name} ! `);
    updateQr();
});


(() => {
  const canvas = document.getElementById('bg-net');
  const ctx = canvas.getContext('2d');

  // ====== Paramètres à tweaker ======
  const CONFIG = {
    density: 0.00018,      // nombre de particules par pixel (≈ 0.00012–0.00025)
    maxSpeed: 0.6,         // vitesse max (px/frame)
    radius: 2.0,           // rayon des points
    linkDist: 120,         // distance max pour relier (px)
    lineWidth: 1,          // épaisseur des lignes
    dotColor: 'rgba(255,255,255,0.8)',
    lineColor: 'rgba(255,255,255,0.15)',
    mouseInfluence: 160,   // distance d'influence de la souris (0 pour désactiver)
    bounce: true           // rebondir sur les bords
  };

  let particles = [];
  let w = 0, h = 0, dpr = Math.max(1, window.devicePixelRatio || 1);
  const mouse = { x: null, y: null, active: false };

  function resize() {
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.width  = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // recalculer le nombre de particules selon la surface
    const targetCount = Math.round(w * h * CONFIG.density);
    adjustParticleCount(targetCount);
  }

  function rand(min, max) { return Math.random() * (max - min) + min; }

  function createParticle() {
    const angle = Math.random() * Math.PI * 2;
    const speed = rand(0.2, CONFIG.maxSpeed);
    return {
      x: Math.random() * w,
      y: Math.random() * h,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed
    };
  }

  function adjustParticleCount(target) {
    if (particles.length < target) {
      for (let i = particles.length; i < target; i++) particles.push(createParticle());
    } else if (particles.length > target) {
      particles.length = target;
    }
  }

  function step() {
    ctx.clearRect(0, 0, w, h);

    // Mise à jour positions + dessin points
    ctx.fillStyle = CONFIG.dotColor;
    for (let p of particles) {
      p.x += p.vx; p.y += p.vy;

      if (CONFIG.bounce) {
        if (p.x <= 0 || p.x >= w) p.vx *= -1;
        if (p.y <= 0 || p.y >= h) p.vy *= -1;
        // clamp pour rester à l'écran
        if (p.x < 0) p.x = 0; else if (p.x > w) p.x = w;
        if (p.y < 0) p.y = 0; else if (p.y > h) p.y = h;
      } else {
        // wrap-around
        if (p.x < 0) p.x = w; else if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h; else if (p.y > h) p.y = 0;
      }

      // léger aimant vers la souris
      if (CONFIG.mouseInfluence > 0 && mouse.active) {
        const dx = p.x - mouse.x, dy = p.y - mouse.y;
        const d2 = dx*dx + dy*dy;
        if (d2 < CONFIG.mouseInfluence * CONFIG.mouseInfluence && d2 > 0.0001) {
          const d = Math.sqrt(d2);
          const force = (CONFIG.mouseInfluence - d) / CONFIG.mouseInfluence * 0.03; // 0.0–0.03
          p.vx += (dx / d) * force;
          p.vy += (dy / d) * force;
        }
      }

      // dessiner le point
      ctx.beginPath();
      ctx.arc(p.x, p.y, CONFIG.radius, 0, Math.PI * 2);
      ctx.fill();
    }

    // Lignes entre particules proches (optimisé par quadrillage simple)
    ctx.lineWidth = CONFIG.lineWidth;
    ctx.strokeStyle = CONFIG.lineColor;

    // Partitionner l'espace en cellules pour limiter les comparaisons
    const cellSize = CONFIG.linkDist;
    const cols = Math.ceil(w / cellSize);
    const rows = Math.ceil(h / cellSize);
    const grid = Array.from({ length: cols * rows }, () => []);
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      const cx = Math.min(cols - 1, Math.max(0, (p.x / cellSize) | 0));
      const cy = Math.min(rows - 1, Math.max(0, (p.y / cellSize) | 0));
      grid[cy * cols + cx].push(i);
    }

    function neighbors(cx, cy) {
      const out = [];
      for (let y = cy - 1; y <= cy + 1; y++) {
        if (y < 0 || y >= rows) continue;
        for (let x = cx - 1; x <= cx + 1; x++) {
          if (x < 0 || x >= cols) continue;
          out.push(grid[y * cols + x]);
        }
      }
      return out.flat();
    }

    for (let cy = 0; cy < rows; cy++) {
      for (let cx = 0; cx < cols; cx++) {
        const idxs = grid[cy * cols + cx];
        const neigh = neighbors(cx, cy);
        for (let i = 0; i < idxs.length; i++) {
          const a = particles[idxs[i]];
          for (let j = 0; j < neigh.length; j++) {
            const b = particles[neigh[j]];
            if (a === b) continue;
            const dx = a.x - b.x, dy = a.y - b.y;
            const d2 = dx*dx + dy*dy;
            if (d2 <= CONFIG.linkDist * CONFIG.linkDist) {
              const alpha = 1 - (Math.sqrt(d2) / CONFIG.linkDist);
              ctx.globalAlpha = Math.min(0.6, alpha); // fondu selon distance
              ctx.beginPath();
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
              ctx.stroke();
              ctx.globalAlpha = 1;
            }
          }
        }
      }
    }
    requestAnimationFrame(step);
  }

  // Souris / tactile
  window.addEventListener('mousemove', e => {
    mouse.x = e.clientX; mouse.y = e.clientY; mouse.active = true;
  }, { passive: true });
  window.addEventListener('mouseleave', () => { mouse.active = false; });
  window.addEventListener('touchstart', e => {
    const t = e.touches[0]; mouse.x = t.clientX; mouse.y = t.clientY; mouse.active = true;
  }, { passive: true });
  window.addEventListener('touchmove', e => {
    const t = e.touches[0]; mouse.x = t.clientX; mouse.y = t.clientY; mouse.active = true;
  }, { passive: true });
  window.addEventListener('touchend', () => { mouse.active = false; });
  // Init
  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(step);
})();