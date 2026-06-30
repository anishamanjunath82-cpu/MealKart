/* mealKart - Hero Carousel Slider */

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('hero-slider');
    if (!slider) return;

    const wrapper = slider.querySelector('.carousel-wrapper');
    const slides = slider.querySelectorAll('.carousel-slide');
    const prevBtn = document.getElementById('slider-prev-btn');
    const nextBtn = document.getElementById('slider-next-btn');
    const dotsContainer = document.getElementById('slider-dots-container');

    let currentSlide = 0;
    const slideCount = slides.length;
    let autoPlayTimer = null;
    const autoPlayDelay = 5000; // 5 seconds

    // Initialize Dot Indicators
    if (dotsContainer) {
        for (let i = 0; i < slideCount; i++) {
            const dot = document.createElement('div');
            dot.classList.add('slider-dot');
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', () => {
                goToSlide(i);
                resetAutoPlay();
            });
            dotsContainer.appendChild(dot);
        }
    }

    const dots = dotsContainer ? dotsContainer.querySelectorAll('.slider-dot') : [];

    function updateSlider() {
        slides.forEach((slide, idx) => {
            if (idx === currentSlide) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });

        dots.forEach((dot, idx) => {
            if (idx === currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slideCount;
        updateSlider();
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + slideCount) % slideCount;
        updateSlider();
    }

    function goToSlide(index) {
        currentSlide = index;
        updateSlider();
    }

    // Set up button event listeners
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            prevSlide();
            resetAutoPlay();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            nextSlide();
            resetAutoPlay();
        });
    }

    // Auto Play Functions
    function startAutoPlay() {
        if (autoPlayTimer === null && slideCount > 1) {
            autoPlayTimer = setInterval(nextSlide, autoPlayDelay);
        }
    }

    function resetAutoPlay() {
        if (autoPlayTimer !== null) {
            clearInterval(autoPlayTimer);
            autoPlayTimer = null;
            startAutoPlay();
        }
    }

    // Start auto slider
    startAutoPlay();

    // Pause on hover
    slider.addEventListener('mouseenter', () => {
        if (autoPlayTimer !== null) {
            clearInterval(autoPlayTimer);
            autoPlayTimer = null;
        }
    });

    slider.addEventListener('mouseleave', () => {
        startAutoPlay();
    });
});
