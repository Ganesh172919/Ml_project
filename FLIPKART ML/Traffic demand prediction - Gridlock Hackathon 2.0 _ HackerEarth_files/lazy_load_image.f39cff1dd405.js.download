function lazyLoadImages() {
    function createObserver() {
        const elements = document.querySelectorAll('img, iframe');
        const observer = new window.IntersectionObserver(
        (entries, observerChild) => {
            entries.forEach((data) => {
            const entry = data;

            if (entry.isIntersecting && entry.target.getAttribute('data-src')) {
                entry.target.src = entry.target.getAttribute('data-src');
                entry.target.removeAttribute('data-src');
                observerChild.unobserve(entry.target);
            }
            });
        },
        {},
        );
        /* eslint-disable func-names */
        Array.prototype.map.call(elements, function(item) {
        observer.observe(item);
        });
    }

    /* eslint-enable func-names */
    if (!('IntersectionObserver' in window)) {
        const polyfill = document.createElement('script');
        polyfill.src =
        'https://polyfill.io/v2/polyfill.min.js?features=IntersectionObserver';
        document.head.appendChild(polyfill);

        polyfill.onload = () => {
        createObserver();
        };

        return;
    }

    createObserver();
}

lazyLoadImages();

  