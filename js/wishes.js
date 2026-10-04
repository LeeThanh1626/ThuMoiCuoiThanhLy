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
    const colors = ['#b76e79', '#d4a373', '#6b9080', '#9d4edd'];

    // Tên khách lấy từ link (?to=...), giống cách guest.js đọc: "to=" phải ở cuối link.
    const raw = window.location.search.split('to=');
    let linkName = '';
    if (raw.length > 1 && raw[1].length >= 1) {
        try {
            // Bỏ tham số theo dõi mà Zalo/Facebook tự gắn vào cuối link (&utm_source=zalo...).
            linkName = window.decodeURIComponent(raw[1].replace(/&(utm_|fbclid|gclid|zarsrc)[^]*$/i, '')).trim();
        } catch {
            linkName = '';
        }
    }

    const nameInput = document.getElementById('wish-name');
    if (linkName) {
        nameInput.value = linkName.slice(0, 50);
    }

    const render = (wishes) => {
        list.replaceChildren(...wishes.map((w, i) => {
            const card = document.createElement('div');
            card.className = 'bg-theme-auto mt-4 p-4 shadow rounded-4 border-start border-4';
            card.style.borderColor = colors[i % colors.length];

            const msg = document.createElement('p');
            msg.className = 'mb-2';
            msg.style.cssText = 'font-size: 1rem; line-height: 1.8; white-space: pre-line';
            msg.textContent = w.loi_chuc;

            const name = document.createElement('p');
            name.className = 'mb-0 fw-bold';
            name.style.fontSize = '0.9rem';
            name.textContent = '— ' + w.ten;

            card.append(msg, name);
            return card;
        }));
    };

    const load = () => {
        if (!url) {
            return;
        }
        fetch(url)
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
                nameInput.value = linkName.slice(0, 50);
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
