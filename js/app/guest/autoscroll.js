import { util } from '../../common/util.js';

export const autoscroll = (() => {

    const stateRun = '<i class="fa-solid fa-pause"></i>';
    const statePause = '<i class="fa-solid fa-angles-down"></i>';

    /**
     * Wait time before scrolling again after the guest interacts.
     */
    const delay = 3000;

    /**
     * @type {HTMLButtonElement|null}
     */
    let button = null;

    /**
     * Scroll speed in pixel per second.
     *
     * @type {number}
     */
    let speed = 30;

    /**
     * The guest wants the auto scroll on.
     *
     * @type {boolean}
     */
    let active = false;

    /**
     * The animation is currently running.
     *
     * @type {boolean}
     */
    let run = false;

    /**
     * Hold the scroll, a modal is open.
     *
     * @type {boolean}
     */
    let blocked = false;

    /**
     * @type {number|null}
     */
    let frame = null;

    /**
     * @type {number|null}
     */
    let last = null;

    /**
     * Leftover of the sub pixel movement.
     *
     * @type {number}
     */
    let rest = 0;

    /**
     * @returns {boolean}
     */
    const isEnd = () => Math.ceil(window.scrollY + window.innerHeight) >= document.documentElement.scrollHeight;

    /**
     * @param {boolean} isRun
     * @returns {void}
     */
    const setButton = (isRun) => {
        if (button) {
            util.safeInnerHTML(button, isRun ? stateRun : statePause);
        }
    };

    /**
     * @returns {void}
     */
    const stop = () => {
        run = false;
        last = null;
        rest = 0;

        if (frame !== null) {
            cancelAnimationFrame(frame);
            frame = null;
        }
    };

    /**
     * @param {number} now
     * @returns {void}
     */
    const animate = (now) => {
        if (!run) {
            return;
        }

        if (isEnd()) {
            active = false;
            stop();
            setButton(false);
            return;
        }

        if (last === null) {
            last = now;
            frame = requestAnimationFrame(animate);
            return;
        }

        // clamp it, the tab can be inactive for a long time.
        rest += speed * Math.min(now - last, 100) / 1000;
        last = now;

        const move = Math.floor(rest);
        if (move >= 1) {
            rest -= move;
            // must be instant, css scroll-behavior is smooth.
            window.scrollBy({ top: move, behavior: 'instant' });
        }

        frame = requestAnimationFrame(animate);
    };

    /**
     * @returns {void}
     */
    const play = () => {
        if (run || blocked || isEnd()) {
            return;
        }

        run = true;
        last = null;
        rest = 0;
        frame = requestAnimationFrame(animate);
    };

    /**
     * Scroll again only if the guest never turned it off.
     *
     * @returns {void}
     */
    const wake = util.debounce(() => {
        if (active) {
            play();
        }
    }, delay);

    /**
     * @param {Event} e
     * @returns {void}
     */
    const interact = (e) => {
        if (e.target?.closest?.('#button-autoscroll')) {
            return;
        }

        stop();
        wake();
    };

    /**
     * @returns {void}
     */
    const toggle = () => {
        active = !active;
        active ? play() : stop();
        setButton(active);
    };

    /**
     * @returns {void}
     */
    const init = () => {
        button = document.getElementById('button-autoscroll');

        if (document.body.getAttribute('data-autoscroll') !== 'true') {
            button?.remove();
            button = null;
            return;
        }

        speed = parseInt(document.body.getAttribute('data-autoscroll-speed')) || speed;

        button?.addEventListener('click', toggle);
        ['wheel', 'keydown', 'touchstart', 'touchmove', 'pointerdown', 'focusin'].forEach((n) => {
            window.addEventListener(n, interact, { passive: true, capture: true });
        });

        document.addEventListener('show.bs.modal', () => {
            blocked = true;
            stop();
        });

        document.addEventListener('hidden.bs.modal', () => {
            blocked = false;
            wake();
        });

        document.addEventListener('undangan.open', () => {
            button?.classList.remove('d-none');

            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                setButton(false);
                return;
            }

            active = true;
            setButton(true);

            // let the guest read the first section first.
            util.timeOut(wake, 1000);
        });
    };

    return {
        init,
    };
})();
