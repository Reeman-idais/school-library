/**
 * المكتبة المدرسية - واجهة المستخدم
 * نظام متكامل بصفحات منفصلة وتبويب جانبي
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'library_session';
  let currentRole = null;
  let currentUsername = null;
  let allUserBooks = [];
  let allLibBooks = [];

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  // ========== التخزين ==========
  function getSession() {
    try {
      const s = localStorage.getItem(STORAGE_KEY);
      return s ? JSON.parse(s) : null;
    } catch { return null; }
  }
  function setSession(r, u) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ role: r, username: u }));
  }
  function clearSession() {
    localStorage.removeItem(STORAGE_KEY);
  }

  // ========== التنقل بين الصفحات ==========
  function showPage(pageId) {
    $$('.page').forEach(p => p.classList.remove('active'));
    const p = $(`#page-${pageId}`);
    if (p) p.classList.add('active');
  }

  function showView(parentId, viewId) {
    const parent = $(`#page-${parentId}`);
    if (!parent) return;
    $$('.view', parent).forEach(v => v.classList.remove('active'));
    const v = $(`#view-${viewId}`);
    if (v) v.classList.add('active');
  }

  function setNavActive(parentId, pageName) {
    const parent = $(`#page-${parentId}`);
    if (!parent) return;
    $$('.nav-item', parent).forEach(n => n.classList.remove('active'));
    const n = $(`.nav-item[data-page="${pageName}"]`, parent);
    if (n) n.classList.add('active');
  }

  // ========== الإشعارات ==========
  function toast(msg, type = 'info') {
    const el = $('#toast');
    if (!el) return;
    el.textContent = msg;
    el.className = `toast ${type} show`;
    setTimeout(() => el.classList.remove('show'), 3000);
  }

  // ========== API ==========
  async function api(cmd, args) {
    try {
      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, args }),
      });
      const data = await res.json();
      return data;
    } catch (err) {
      toast('خطأ في الاتصال. تأكد من تشغيل الخادم.', 'error');
      return { success: false, stderr: err.message };
    }
  }
  // Try fetching books directly from the REST API (/api/books).
  // Falls back to the CLI execution API when not available.
  async function fetchBooksFromServer() {
    try {
      const res = await fetch('/api/books');
      if (!res.ok) throw new Error('Not available');
      const data = await res.json();
      // normalize keys to match parseBooks expectations
      return data.map(b => ({
        id: b.id,
        title: b.title,
        author: b.author,
        status: b.status || 'Available',
        pickedBy: b.picked_by || null,
      }));
    } catch (err) {
      return null; // signal to use CLI fallback
    }
  }
  // ========== تحليل مخرجات CLI ==========
  function parseBooks(stdout) {
    const books = [];
    const lines = (stdout || '').trim().split('\n');
    for (const line of lines) {
      if (!line || line.startsWith('All books') || line.startsWith('ID') || /^-+$/.test(line)) continue;
      const id = line.substring(0, 6).trim();
      const title = line.substring(6, 36).trim();
      const author = line.substring(36, 61).trim();
      const status = line.substring(61, 73).trim();
      const pickedBy = line.substring(73, 88).trim();
      if (id && /^\d+$/.test(id)) {
        books.push({
          id: parseInt(id, 10),
          title: title || '-',
          author: author || '-',
          status: status || 'Available',
          pickedBy: pickedBy === '-' ? null : pickedBy,
        });
      }
    }
    return books;
  }

  function parsePicked(stdout) {
    const books = [];
    const lines = (stdout || '').trim().split('\n');
    for (const line of lines) {
      if (!line || line.startsWith('Picked books') || line.startsWith('ID') || /^-+$/.test(line)) continue;
      const id = line.substring(0, 6).trim();
      const title = line.substring(6, 36).trim();
      const author = line.substring(36, 61).trim();
      const pickedBy = line.substring(61, 76).trim();
      if (id && /^\d+$/.test(id)) {
        books.push({
          id: parseInt(id, 10),
          title: title || '-',
          author: author || '-',
          pickedBy: pickedBy === '-' ? null : pickedBy,
        });
      }
    }
    return books;
  }

  function esc(t) {
    const d = document.createElement('div');
    d.textContent = t || '';
    return d.innerHTML;
  }

  function statusClass(s) {
    const x = (s || '').toLowerCase();
    if (x === 'available') return 'status-available';
    if (x === 'picked') return 'status-picked';
    return 'status-borrowed';
  }
  function statusLabel(s) {
    const m = { Available: 'متاح', Picked: 'محجوز', Borrowed: 'مُعار' };
    return m[s] || s;
  }

  function filterBooks(books, q) {
    if (!q || !q.trim()) return books;
    const k = q.trim().toLowerCase();
    return books.filter(b =>
      (b.title || '').toLowerCase().includes(k) || (b.author || '').toLowerCase().includes(k)
    );
  }

  // ========== المستخدم: عرض الكتب ==========
  async function loadUserBooks() {
    const list = $('#books-list');
    const empty = $('#books-empty');
    const loading = $('#books-loading');
    if (!list) return;

    if (loading) loading.classList.remove('hidden');
    if (empty) empty.classList.add('hidden');
    list.innerHTML = '';

    // Try REST API first
    const serverBooks = await fetchBooksFromServer();
    if (serverBooks) {
      if (loading) loading.classList.add('hidden');
      allUserBooks = serverBooks;
    } else {
      const r = await api('list-books', ['--username', currentUsername]);
      if (loading) loading.classList.add('hidden');

      if (!r.success) {
        if (empty) {
          empty.textContent = r.stderr || 'حدث خطأ';
          empty.classList.remove('hidden');
        }
        return;
      }

      allUserBooks = parseBooks(r.stdout);
    }
    const searchQ = ($('#search-user-books') || {}).value || '';
    const books = filterBooks(allUserBooks, searchQ);
    if (books.length === 0) {
      if (empty) {
        empty.textContent = searchQ ? 'لا توجد نتائج للبحث' : 'لا توجد كتب';
        empty.classList.remove('hidden');
      }
      return;
    }

    list.innerHTML = books.map(b => `
      <div class="book-card">
        <h3>${esc(b.title)}</h3>
        <p class="author">${esc(b.author)}</p>
        <span class="status-badge ${statusClass(b.status)}">${statusLabel(b.status)}</span>
        ${b.status === 'Available' ? `<button type="button" class="btn btn-primary btn-sm btn-pick" data-id="${b.id}">حجز</button>` : ''}
      </div>
    `).join('');

    list.querySelectorAll('.btn-pick').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const r2 = await api('pick-book', ['--id', id, '--username', currentUsername]);
        if (r2.success) {
          toast('تم الحجز بنجاح', 'success');
          loadUserBooks();
          loadUserPicked();
        } else {
          toast(r2.stderr || 'حدث خطأ', 'error');
        }
      });
    });
  }

  async function loadUserPicked() {
    const r = await api('list-books', ['--username', currentUsername]);
    const books = r.success ? parseBooks(r.stdout) : [];
    const picked = books.filter(b => b.pickedBy === currentUsername);

    const list = $('#my-picked-list');
    const empty = $('#my-picked-empty');
    if (!list) return;

    if (picked.length === 0) {
      list.innerHTML = '';
      if (empty) empty.classList.remove('hidden');
    } else {
      if (empty) empty.classList.add('hidden');
      list.innerHTML = `<table class="data-table"><thead><tr><th>#</th><th>العنوان</th><th>المؤلف</th></tr></thead><tbody>${
        picked.map(b => `<tr><td>${b.id}</td><td>${esc(b.title)}</td><td>${esc(b.author)}</td></tr>`).join('')
      }</tbody></table>`;
    }
  }

  // ========== أمين المكتبة ==========
  function renderLibBooksTable(books) {
    const container = $('#lib-books-list');
    if (!container) return;

    const searchQ = ($('#search-lib-books') || {}).value || '';
    const filtered = filterBooks(books, searchQ);
    if (filtered.length === 0) {
      container.innerHTML = `<div class="empty-state">${searchQ ? 'لا توجد نتائج للبحث' : 'لا توجد كتب'}</div>`;
      return;
    }
    container.innerHTML = `<table class="data-table"><thead><tr><th>#</th><th>العنوان</th><th>المؤلف</th><th>الحالة</th><th>محجوز</th><th>إجراءات</th></tr></thead><tbody>${
      filtered.map(b => {
        let actions = `<button type="button" class="btn btn-primary btn-sm btn-edit" data-id="${b.id}">تعديل</button> `;
        actions += `<button type="button" class="btn btn-danger btn-sm btn-delete" data-id="${b.id}">حذف</button>`;
        if (b.status === 'Borrowed') {
          actions += ` <button type="button" class="btn btn-success btn-sm btn-return" data-id="${b.id}">إرجاع</button>`;
        }
        return `<tr><td>${b.id}</td><td>${esc(b.title)}</td><td>${esc(b.author)}</td><td><span class="status-badge ${statusClass(b.status)}">${statusLabel(b.status)}</span></td><td>${esc(b.pickedBy || '-')}</td><td class="cell-actions">${actions}</td></tr>`;
      }).join('')
    }</tbody></table>`;

    container.querySelectorAll('.btn-edit').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id, 10);
        const book = allLibBooks.find(b => b.id === id) || {};
        $('#edit-id').value = id;
        $('#edit-title').value = book.title || '';
        $('#edit-author').value = book.author || '';
        $('#modal-edit').classList.add('show');
      });
    });
    container.querySelectorAll('.btn-delete').forEach(btn => {
      btn.addEventListener('click', async () => {
        const idStr = btn.dataset.id;
        const id = parseInt(idStr, 10);
        const book = allLibBooks.find(b => b.id === id) || {};
        if (!confirm(`حذف الكتاب "${book.title || id}"؟`)) return;
        const r2 = await api('delete-book', ['--id', idStr, '--librarian']);
        if (r2.success) {
          toast('تم الحذف', 'success');
          loadLibBooks();
        } else {
          toast(r2.stderr || 'حدث خطأ', 'error');
        }
      });
    });
    container.querySelectorAll('.btn-return').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const r2 = await api('return-book', ['--id', id, '--librarian']);
        if (r2.success) {
          toast('تم إرجاع الكتاب', 'success');
          loadLibBooks();
          loadLibPicked();
        } else {
          toast(r2.stderr || 'حدث خطأ', 'error');
        }
      });
    });
  }

  async function loadLibBooks() {
    // Try REST API first
    const serverBooks = await fetchBooksFromServer();
    if (serverBooks) {
      allLibBooks = serverBooks;
      renderLibBooksTable(allLibBooks);
      return;
    }

    const r = await api('list-books', ['--librarian']);
    if (!r.success) {
      const container = $('#lib-books-list');
      if (container) container.innerHTML = `<div class="empty-state">${esc(r.stderr)}</div>`;
      return;
    }
    allLibBooks = parseBooks(r.stdout);
    renderLibBooksTable(allLibBooks);
  }

  async function loadLibPicked() {
    const r = await api('list-picked', ['--librarian']);
    const container = $('#lib-picked-list');
    if (!container) return;

    if (!r.success || !parsePicked(r.stdout).length) {
      container.innerHTML = '<div class="empty-state">لا توجد كتب محجوزة</div>';
      return;
    }
    const books = parsePicked(r.stdout);
    container.innerHTML = `<table class="data-table"><thead><tr><th>#</th><th>العنوان</th><th>المؤلف</th><th>محجوز</th><th>إجراءات</th></tr></thead><tbody>${
      books.map(b => `<tr>
        <td>${b.id}</td><td>${esc(b.title)}</td><td>${esc(b.author)}</td><td>${esc(b.pickedBy || '-')}</td>
        <td class="cell-actions">
          <button type="button" class="btn btn-primary btn-sm btn-approve" data-id="${b.id}">موافقة</button>
          <button type="button" class="btn btn-danger btn-sm btn-reject" data-id="${b.id}">عدم الموافقة</button>
        </td>
      </tr>`).join('')
    }</tbody></table>`;

    container.querySelectorAll('.btn-approve').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const r2 = await api('approve-borrow', ['--id', id, '--librarian']);
        if (r2.success) {
          toast('تمت الموافقة', 'success');
          loadLibBooks();
          loadLibPicked();
        } else {
          toast(r2.stderr || 'حدث خطأ', 'error');
        }
      });
    });

    container.querySelectorAll('.btn-reject').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const r2 = await api('update-status', ['--id', id, '--status', 'Available', '--librarian']);
        if (r2.success) {
          toast('تم رفض الحجز وإرجاع الكتاب إلى متاح', 'success');
          loadLibBooks();
          loadLibPicked();
        } else {
          toast(r2.stderr || 'حدث خطأ', 'error');
        }
      });
    });
  }

  // ========== خروج ==========
  function logout() {
    clearSession();
    currentRole = null;
    currentUsername = null;
    $('#input-username').value = '';
    $('#input-password').value = '';
    showPage('login');
  }

  // Authenticate via backend API
  async function authenticateUser(username, password) {
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: (username || '').trim(), password: (password || '').trim() }),
      });
      const data = await res.json();
      if (data.success) {
        return { role: data.role, username: data.username };
      }
      toast(data.message || 'اسم المستخدم أو كلمة المرور غير صحيحة', 'error');
      return null;
    } catch (err) {
      toast('خطأ في الاتصال بالخادم. تأكد من تشغيل الخادم.', 'error');
      return null;
    }
  }

  // ========== تهيئة الأحداث ==========
  function init() {
    const formLogin = $('#form-login');
    const inputUsername = $('#input-username');
    const inputPassword = $('#input-password');

    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = inputUsername.value.trim();
      const password = inputPassword.value;

      const result = await authenticateUser(username, password);
      if (!result) {
        return;
      }

      currentRole = result.role;
      currentUsername = result.username || username;
      setSession(result.role, currentUsername);

      if (result.role === 'user') {
        showPage('user');
        $('#user-display-name').textContent = username.trim();
        showView('user', 'user-books');
        setNavActive('user', 'user-books');
        $('#user-page-title').textContent = 'جميع الكتب';
        loadUserBooks();
        loadUserPicked();
      } else {
        showPage('librarian');
        showView('librarian', 'lib-books');
        setNavActive('librarian', 'lib-books');
        $('#lib-page-title').textContent = 'جميع الكتب';
        loadLibBooks();
        loadLibPicked();
      }
    });

    // تنقل المستخدم
    $('#page-user').addEventListener('click', (e) => {
      const nav = e.target.closest('.nav-item');
      if (!nav) return;
      e.preventDefault();
      const page = nav.dataset.page;
      setNavActive('user', page);
      showView('user', page);
      $('#user-page-title').textContent = page === 'user-books' ? 'جميع الكتب' : 'كتبي المحجوزة';
      if (page === 'user-books') loadUserBooks();
      else loadUserPicked();
    });

    // تنقل أمين المكتبة
    $('#page-librarian').addEventListener('click', (e) => {
      const nav = e.target.closest('.nav-item');
      if (!nav) return;
      e.preventDefault();
      const page = nav.dataset.page;
      setNavActive('librarian', page);
      showView('librarian', page);
      const titles = { 'lib-books': 'جميع الكتب', 'lib-picked': 'الكتب المحجوزة', 'lib-add': 'إضافة كتاب', 'lib-register': 'تسجيل مستخدم' };
      $('#lib-page-title').textContent = titles[page] || '';
      if (page === 'lib-books') loadLibBooks();
      else if (page === 'lib-picked') loadLibPicked();
    });

    // أزرار الخروج والتحديث
    $('#btn-user-logout')?.addEventListener('click', logout);
    $('#btn-lib-logout')?.addEventListener('click', logout);
    $('#btn-refresh-books')?.addEventListener('click', loadUserBooks);
    $('#btn-refresh-lib')?.addEventListener('click', loadLibBooks);
    $('#btn-refresh-picked')?.addEventListener('click', loadLibPicked);

    // نماذج أمين المكتبة
    $('#form-add-book')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = $('#add-id').value.trim();
      const title = $('#add-title').value.trim();
      const author = $('#add-author').value.trim();
      if (!id || !title || !author) {
        toast('املأ جميع الحقول', 'error');
        return;
      }
      if (!/^\d{4,}$/.test(id)) {
        toast('رقم الكتاب يجب أن يكون 4 أرقام على الأقل', 'error');
        return;
      }
      const r = await api('add-book', [id, title, author, '--librarian']);
      if (r.success) {
        toast('تمت إضافة الكتاب', 'success');
        e.target.reset();
        loadLibBooks();
      } else {
        toast(r.stderr || 'حدث خطأ', 'error');
      }
    });

    // نموذج تسجيل المستخدم
    $('#form-register')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = $('#reg-username').value.trim();
      const password = $('#reg-password').value.trim();
      const role = $('#reg-role').value.trim();
      if (!username || !password || !role) {
        toast('املأ جميع الحقول', 'error');
        return;
      }
      if (!/^\d+$/.test(password)) {
        toast('كلمة المرور يجب أن تكون أرقاماً فقط', 'error');
        return;
      }
      const r = await api('register-user', [username, password, role]);
      if (r.success) {
        toast('تم تسجيل المستخدم بنجاح', 'success');
        e.target.reset();
      } else {
        toast(r.stderr || 'حدث خطأ', 'error');
      }
    });

    // تعديل الكتاب
    $('#form-edit-book')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = $('#edit-id').value.trim();
      const title = $('#edit-title').value.trim();
      const author = $('#edit-author').value.trim();
      if (!id || !title || !author) {
        toast('املأ جميع الحقول', 'error');
        return;
      }
      const r = await api('update-book', [id, title, author, '--librarian']);
      if (r.success) {
        toast('تم التعديل', 'success');
        $('#modal-edit').classList.remove('show');
        loadLibBooks();
      } else {
        toast(r.stderr || 'حدث خطأ', 'error');
      }
    });
    $('.btn-cancel-edit')?.addEventListener('click', () => $('#modal-edit')?.classList.remove('show'));
    $('#modal-edit')?.addEventListener('click', (e) => {
      if (e.target.id === 'modal-edit') e.target.classList.remove('show');
    });

    // البحث
    $('#search-user-books')?.addEventListener('input', () => {
      if (allUserBooks.length === 0) return;
      const q = $('#search-user-books').value.trim();
      const books = filterBooks(allUserBooks, q);
      const list = $('#books-list');
      const empty = $('#books-empty');
      if (!list) return;
      if (books.length === 0) {
        list.innerHTML = '';
        if (empty) {
          empty.textContent = q ? 'لا توجد نتائج للبحث' : 'لا توجد كتب';
          empty.classList.remove('hidden');
        }
      } else {
        if (empty) empty.classList.add('hidden');
        list.innerHTML = books.map(b => `
          <div class="book-card">
            <h3>${esc(b.title)}</h3>
            <p class="author">${esc(b.author)}</p>
            <span class="status-badge ${statusClass(b.status)}">${statusLabel(b.status)}</span>
            ${b.status === 'Available' ? `<button type="button" class="btn btn-primary btn-sm btn-pick" data-id="${b.id}">حجز</button>` : ''}
          </div>
        `).join('');
        list.querySelectorAll('.btn-pick').forEach(btn => {
          btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const r2 = await api('pick-book', [id, currentUsername]);
            if (r2.success) {
              toast('تم الحجز بنجاح', 'success');
              loadUserBooks();
              loadUserPicked();
            } else {
              toast(r2.stderr || 'حدث خطأ', 'error');
            }
          });
        });
      }
    });
    $('#search-lib-books')?.addEventListener('input', () => {
      if (allLibBooks.length > 0) renderLibBooksTable(allLibBooks);
    });



    // استعادة الجلسة
    const session = getSession();
    if (session) {
      currentRole = session.role;
      currentUsername = session.username;
      if (currentRole === 'user') {
        showPage('user');
        $('#user-display-name').textContent = currentUsername;
        showView('user', 'user-books');
        setNavActive('user', 'user-books');
        loadUserBooks();
        loadUserPicked();
      } else {
        showPage('librarian');
        showView('librarian', 'lib-books');
        setNavActive('librarian', 'lib-books');
        loadLibBooks();
        loadLibPicked();
      }
    } else {
      showPage('login');
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
