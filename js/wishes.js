// Lời chúc của khách mời, lưu trên Google Sheet qua Apps Script Web App.
(() => {
    const root = document.getElementById('wishes');
    if (!root) {
        return;
    }

    const url = root.dataset.url;
    const form = document.getElementById('wish-form');
    const list = document.getElementById('wish-list');
    const status = document.getElementById('wish-status');

    // Tên khách lấy từ link (?to=...), giống cách guest.js đọc: "to=" phải ở cuối link.
    const raw = window.location.search.split('to=');
    let linkName = '';
    if (raw.length > 1 && raw[1].length >= 1) {
        try {
            // Bỏ tham số theo dõi mà Zalo/Facebook tự gắn vào cuối link (&utm_source=zalo...),
            // và đổi "+" (Facebook mã hoá dấu cách) thành dấu cách.
            const value = raw[1].replace(/&(utm_|fbclid|gclid|zarsrc)[^]*$/i, '').replace(/\+/g, ' ');
            linkName = window.decodeURIComponent(value).trim();
        } catch {
            linkName = '';
        }
    }

    // Link ?to=admintl xem được tất cả lời chúc (Apps Script quyết định), không điền sẵn tên.
    const isAdmin = linkName.toLowerCase() === 'admintl';
    const defaultName = isAdmin ? '' : linkName.slice(0, 50);

    const nameInput = document.getElementById('wish-name');
    nameInput.value = defaultName;

    const render = (wishes) => {
        if (!wishes.length) {
            list.replaceChildren();
            return;
        }

        const title = document.createElement('div');
        title.className = 'wish-list-title';
        if (isAdmin) {
            title.textContent = `Tất cả lời chúc (${wishes.length})`;
        } else {
            title.textContent = wishes.length > 1 ? 'Những lời chúc bạn đã gửi' : 'Lời chúc bạn đã gửi';
        }

        list.replaceChildren(title, ...wishes.map((w) => {
            const card = document.createElement('figure');
            card.className = 'wish-card';

            const msg = document.createElement('blockquote');
            msg.className = 'wish-card-message';
            msg.textContent = w.loi_chuc;

            const name = document.createElement('figcaption');
            name.className = 'wish-card-name';
            const heart = document.createElement('i');
            heart.className = 'fa-solid fa-heart';
            name.append(w.ten, heart);

            card.append(msg, name);

            if (isAdmin) {
                if (w.an) {
                    card.classList.add('wish-card-hidden');
                }
                const meta = document.createElement('div');
                meta.className = 'wish-card-meta';
                const time = w.time ? new Date(w.time).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '';
                meta.textContent = [w.an ? 'Đã ẩn' : '', w.ten_link ? `Link: ${w.ten_link}` : 'Không có tên trên link', time]
                    .filter(Boolean)
                    .join(' · ');
                card.append(meta);
            }

            return card;
        }));
    };

    const load = () => {
        // Mỗi khách chỉ thấy lời chúc của chính mình (theo tên trong link).
        if (!url || !linkName) {
            return;
        }
        fetch(`${url}?to=${encodeURIComponent(linkName)}`)
            .then((res) => res.json())
            .then(render)
            .catch(() => {});
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!url) {
            status.textContent = 'Chưa cấu hình nơi lưu lời chúc.';
            return;
        }

        const button = form.querySelector('button');
        button.disabled = true;
        status.textContent = 'Đang gửi...';

        // text/plain tránh preflight CORS mà Apps Script không hỗ trợ.
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body: JSON.stringify({
                ten: nameInput.value.trim(),
                ten_link: linkName,
                loi_chuc: document.getElementById('wish-message').value.trim(),
            }),
        })
            .then((res) => res.json())
            .then((res) => {
                if (!res.ok) {
                    throw new Error(res.error);
                }
                form.reset();
                nameInput.value = defaultName;
                status.textContent = 'Cảm ơn bạn đã gửi lời chúc! 💖';
                load();
            })
            .catch(() => {
                status.textContent = 'Gửi không thành công, vui lòng thử lại.';
            })
            .finally(() => {
                button.disabled = false;
            });
    });

    load();
})();
