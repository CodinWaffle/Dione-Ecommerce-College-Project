// JS for _occasionwear_carousel.html

        class OccasionwearCarousel {
            constructor() {
                this.wrapper = document.getElementById('carouselWrapper');
                this.prevBtn = document.getElementById('prevBtn');
                this.nextBtn = document.getElementById('nextBtn');
                this.cards = document.querySelectorAll('.card');
                this.currentIndex = 0;
                this.cardsToShow = Math.min(5, this.cards.length); // Show max 5 or available cards
                this.cardWidth = 320;
                this.cardGap = 20;
                this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);

                this.init();
                this.updateResponsiveSettings();
                window.addEventListener('resize', () => this.updateResponsiveSettings());
            }

            init() {
                // Ensure buttons are visible initially
                this.prevBtn.style.display = 'flex';
                this.nextBtn.style.display = 'flex';
                
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
                        // Future implementation: window.location.href = `/shop/clothing/occasionwear/${category}`;
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
                    // For occasionwear carousel with 5 cards, show max 5 to fit perfectly
                    this.cardsToShow = Math.min(5, this.cards.length);
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
                this.nextBtn.disabled = this.currentIndex >= this.maxIndex || this.maxIndex === 0;
                
                // Always show buttons for occasionwear carousel, just disable when not needed
                this.prevBtn.style.display = 'flex';
                this.nextBtn.style.display = 'flex';
                
                // Add visual styling for disabled state
                if (this.prevBtn.disabled) {
                    this.prevBtn.style.opacity = '0.5';
                } else {
                    this.prevBtn.style.opacity = '1';
                }
                
                if (this.nextBtn.disabled) {
                    this.nextBtn.style.opacity = '0.5';
                } else {
                    this.nextBtn.style.opacity = '1';
                }
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            new OccasionwearCarousel();
        });

