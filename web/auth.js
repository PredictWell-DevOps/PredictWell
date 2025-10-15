// auth.js — append a nav into the existing site header (keeps logo/tagline/glass)

(function () {
  // ----- minimal, scoped CSS for our nav only -----
  const CSS = `
    .pw-nav{ margin-left:auto; display:flex; gap:16px; align-items:center; }
    .pw-nav a{ color:#111; text-decoration:none; font-weight:600; }
    .pw-nav a:hover{ text-decoration:underline; }
    @media (max-width: 640px){ .pw-nav{ gap:10px; } }
  `;
  const s = document.createElement('style');
  s.textContent = CSS;
  document.head.appendChild(s);

  // ----- tiny auth helper -----
  const AUTH = {
    keyUser: 'pw_user',
    keyToken: 'pw_token',
    get user(){ try{ return JSON.parse(localStorage.getItem(this.keyUser)||'null'); }catch{ return null; } },
    get token(){ return localStorage.getItem(this.keyToken); },
    isAuthed(){ return !!this.user && !!this.token; },
    login(u){ localStorage.setItem(this.keyUser, JSON.stringify(u)); localStorage.setItem(this.keyToken, btoa(`${u.email}:${Date.now()}`)); },
    logout(){ localStorage.removeItem(this.keyUser); localStorage.removeItem(this.keyToken); },

    navHTML(){
  if(this.isAuthed()){
    const email = this.user?.email || 'Account';
    return `
      <nav class="pw-nav" id="pw-nav">
        <a href="index.html">Home</a>
        <a href="/portal/patient/login.html">Patient Portal</a>
        <a href="/portal/doctor/login.html">Doctor Portal</a>
        <a href="javascript:void(0)" id="pw-account">${email}</a>
        <a href="javascript:void(0)" id="pw-logout">Logout</a>
      </nav>`;
  } else {
    return `
      <nav class="pw-nav" id="pw-nav">
        <a href="index.html">Home</a>
        <a href="/portal/patient/login.html">Patient Portal</a>
        <a href="/portal/doctor/login.html">Doctor Portal</a>
      </nav>`;
  }
    },

    mountNav(){
      // 1) Find the existing header content wrapper
      //    (we DO NOT replace the header; we only append our nav)
      const host =
        document.querySelector('.header .header-inner') || // preferred (your site uses this)
        document.querySelector('header.header .header-inner') ||
        document.querySelector('header.header');            // safe fallback

      if(!host) return; // if no header is present, do nothing

      // avoid double-injecting
      if (host.querySelector('#pw-nav')) return;

      host.insertAdjacentHTML('beforeend', this.navHTML());

      // wire logout
      const lo = host.querySelector('#pw-logout');
      if (lo) lo.addEventListener('click', () => { this.logout(); location.href = 'login.html'; });
    }
  };

  // expose for other pages if needed
  window.PW_AUTH = AUTH;

  // mount after DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AUTH.mountNav());
  } else {
    AUTH.mountNav();
  }
})();
