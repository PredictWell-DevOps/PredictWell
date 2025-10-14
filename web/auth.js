<script>
window.PW_AUTH = {
  keyUser: 'pw_user',
  keyToken: 'pw_token',
  get user(){ try { return JSON.parse(localStorage.getItem(this.keyUser)||'null'); } catch { return null; } },
  get token(){ return localStorage.getItem(this.keyToken); },
  isAuthed(){ return !!this.user && !!this.token; },
  login(u){ localStorage.setItem(this.keyUser, JSON.stringify(u)); localStorage.setItem(this.keyToken, btoa(`${u.email}:${Date.now()}`)); },
  logout(){ localStorage.removeItem(this.keyUser); localStorage.removeItem(this.keyToken); },
  headerHTML(){
    if(this.isAuthed()){
      const email = this.user?.email || 'Account';
      return `
        <nav class="nav">
          <a href="index.html">Home</a>
          <a href="eldercare-patient.html">Patient Portal</a>
          <span class="sep"></span>
          <a href="javascript:void(0)" id="pw-account">${email}</a>
          <a href="javascript:void(0)" id="pw-logout">Logout</a>
        </nav>`;
    } else {
      return `
        <nav class="nav">
          <a href="index.html">Home</a>
          <a href="eldercare-patient.html">Patient Portal</a>
          <span class="sep"></span>
          <a href="login.html">Login</a>
          <a href="register.html">Register</a>
        </nav>`;
    }
  },
  mountHeader(){
    const host = document.querySelector('header.header') || document.body.prepend(Object.assign(document.createElement('header'),{className:'header'}));
    if(host instanceof HTMLElement){
      host.innerHTML = this.headerHTML();
      const lo = document.getElementById('pw-logout');
      if(lo){ lo.addEventListener('click', ()=>{ this.logout(); location.href='login.html'; }); }
    }
  }
};

document.addEventListener('DOMContentLoaded', ()=> PW_AUTH.mountHeader());
</script>
<style>
.header{display:flex;justify-content:center;border-bottom:1px solid #eee;background:#fff}
.header .nav{display:flex;gap:14px;padding:12px 16px;align-items:center}
.header a{color:#111;text-decoration:none;font-weight:600}
.header .sep{flex:1}
</style>
