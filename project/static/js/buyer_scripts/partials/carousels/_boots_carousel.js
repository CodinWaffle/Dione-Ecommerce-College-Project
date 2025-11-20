// JS for _boots_carousel.html

        class BootsCarousel {
            constructor() {
                this.wrapper = document.getElementById('carouselWrapper');
                this.prevBtn = document.getElementById('prevBtn');
                this.nextBtn = document.getElementById('nextBtn');
                this.cards = document.querySelectorAll('.card');
                this.currentIndex = 0;
                this.cardsToShow = 5;
                this.cardWidth = 320;
                this.cardGap = 20;
                this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);

                this.init();
                this.updateResponsiveSettings();
                window.addEventListener('resize', () => this.updateResponsiveSettings());
            }

            init() {
                this.prevBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.prev();
                });
                this.nextBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.next();
                });
                this.updateButtons();

                this.cards.forEach(card => {
                    card.addEventListener('click', () => {
                        const category = card.dataset.category;
                        console.log(`Clicked on ${category}`);
                        // For now, show alert - you can replace with actual navigation
                        alert(`You clicked on ${category}. Navigation to specific ${category} page will be implemented.`);
                        // Future implementation: window.location.href = `/shop/clothing/tops/${category}`;
                    });
                });
            }

            updateResponsiveSettings() {
                const containerWidth = this.wrapper.parentElement.offsetWidth;

                if (containerWidth <= 400) {
                    this.cardsToShow = 1;
                    this.cardWidth = 280;
                } else if (containerWidth <= 720) {
                    this.cardsToShow = 2;
                    this.cardWidth = 320;
                } else if (containerWidth <= 1080) {
                    this.cardsToShow = 3;
                    this.cardWidth = 320;
                } else if (containerWidth <= 1400) {
                    this.cardsToShow = 4;
                    this.cardWidth = 320;
                } else {
                    this.cardsToShow = 5;
                    this.cardWidth = 320;
                }

                this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
                this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
                this.updateCarousel();
            }

            prev() {
                if (this.currentIndex > 0) {
                    this.currentIndex--;
                    this.updateCarousel();
                }
            }

            next() {
                if (this.currentIndex < this.maxIndex) {
                    this.currentIndex++;
                    this.updateCarousel();
                }
            }

            updateCarousel() {
                const translateX = -(this.currentIndex * (this.cardWidth + this.cardGap));
                this.wrapper.style.transform = `translateX(${translateX}px)`;
                this.updateButtons();
            }

            updateButtons() {
                this.prevBtn.disabled = this.currentIndex === 0;
                this.nextBtn.disabled = this.currentIndex >= this.maxIndex;
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            new BootsCarousel();
        });

