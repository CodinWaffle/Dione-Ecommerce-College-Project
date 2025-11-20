// JS for _filters_shoes.html

        let activeFilters = {};
        let totalProducts = 12; // Total products available
        let displayedProducts = 12; // Products shown per page
        let currentPage = 1;
        let totalPages = Math.ceil(totalProducts / displayedProducts);

        function toggleDropdown(header) {
            const section = header.parentElement;
            section.classList.toggle('active');
        }

        function resetAllFilters() {
            // Clear active filters
            activeFilters = {};
            
            // Reset all checkboxes
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Reset color swatches
            const colorSwatches = document.querySelectorAll('.color-swatch');
            colorSwatches.forEach(swatch => {
                swatch.classList.remove('selected');
            });
            
            // Reset price inputs
            const minPrice = document.getElementById('minPrice');
            const maxPrice = document.getElementById('maxPrice');
            if (minPrice) minPrice.value = '';
            if (maxPrice) maxPrice.value = '';
            
            // Update display
            updateSelectedFilters();
            updateProductCount();
        }

        function updateProductCount() {
            const productCountElement = document.getElementById('productCount');
            const viewMoreElement = document.getElementById('viewMore');
            const totalProductsElement = document.getElementById('totalProducts');
            
            // Calculate filtered products based on active filters
            let filteredCount = totalProducts;
            if (Object.keys(activeFilters).length > 0) {
                // In a real application, this would filter based on actual data
                filteredCount = Math.floor(totalProducts * 0.6); // Mock filtered result
            }
            
            // Update total pages based on filtered results
            totalPages = Math.ceil(filteredCount / displayedProducts);
            
            if (productCountElement) productCountElement.textContent = Math.min(displayedProducts, filteredCount);
            if (totalProductsElement) totalProductsElement.textContent = filteredCount;
            
            if (viewMoreElement) {
                if (filteredCount > displayedProducts) {
                    viewMoreElement.style.display = 'block';
                } else {
                    viewMoreElement.style.display = 'none';
                }
            }
            
            updatePagination();
        }

        function updatePagination() {
            const currentRangeElement = document.getElementById('currentRange');
            const totalItemsElement = document.getElementById('totalItems');
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            const pageNumbers = document.getElementById('pageNumbers');
            
            // Calculate filtered products
            let filteredCount = totalProducts;
            if (Object.keys(activeFilters).length > 0) {
                filteredCount = Math.floor(totalProducts * 0.6);
            }
            
            // Update range display
            const startItem = (currentPage - 1) * displayedProducts + 1;
            const endItem = Math.min(currentPage * displayedProducts, filteredCount);
            if (currentRangeElement) currentRangeElement.textContent = `${startItem}-${endItem}`;
            if (totalItemsElement) totalItemsElement.textContent = filteredCount;
            
            // Update prev/next buttons
            if (prevBtn) prevBtn.disabled = currentPage === 1;
            if (nextBtn) nextBtn.disabled = currentPage === totalPages;
            
            // Generate page numbers
            if (pageNumbers) generatePageNumbers(pageNumbers);
        }

        function generatePageNumbers(container) {
            container.innerHTML = '';
            
            const maxVisiblePages = 5;
            let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
            
            // Adjust start if we're near the end
            if (endPage - startPage + 1 < maxVisiblePages) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }
            
            // Add first page if not visible
            if (startPage > 1) {
                container.appendChild(createPageButton(1));
                if (startPage > 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'page-ellipsis';
                    ellipsis.textContent = '...';
                    container.appendChild(ellipsis);
                }
            }
            
            // Add visible page numbers
            for (let i = startPage; i <= endPage; i++) {
                container.appendChild(createPageButton(i));
            }
            
            // Add last page if not visible
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'page-ellipsis';
                    ellipsis.textContent = '...';
                    container.appendChild(ellipsis);
                }
                container.appendChild(createPageButton(totalPages));
            }
        }

        function createPageButton(pageNum) {
            const button = document.createElement('button');
            button.className = `page-btn ${pageNum === currentPage ? 'active' : ''}`;
            button.textContent = pageNum;
            button.dataset.page = pageNum;
            button.addEventListener('click', () => goToPage(pageNum));
            return button;
        }

        function goToPage(page) {
            if (page < 1 || page > totalPages) return;
            
            currentPage = page;
            updatePagination();
            
            // Scroll to top of content area
            const contentArea = document.querySelector('.content-area');
            if (contentArea) {
                contentArea.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }

        function updateFilter(category, value, isChecked) {
            if (!activeFilters[category]) {
                activeFilters[category] = [];
            }
            
            if (isChecked) {
                if (!activeFilters[category].includes(value)) {
                    activeFilters[category].push(value);
                }
            } else {
                activeFilters[category] = activeFilters[category].filter(item => item !== value);
                if (activeFilters[category].length === 0) {
                    delete activeFilters[category];
                }
            }
            
            updateSelectedFilters();
            updateProductCount();
        }

        function selectColor(swatch, colorName) {
            swatch.classList.toggle('selected');
            const isSelected = swatch.classList.contains('selected');
            updateFilter('color', colorName, isSelected);
        }

        function updateSelectedFilters() {
            const container = document.getElementById('selectedFilters');
            const resetBtn = document.getElementById('resetFiltersBtn');
            
            // Clear existing filter tags but keep the reset button
            const filterTags = container.querySelectorAll('.filter-tag');
            filterTags.forEach(tag => tag.remove());
            
            let hasFilters = false;
            Object.keys(activeFilters).forEach(category => {
                activeFilters[category].forEach(value => {
                    const tag = document.createElement('div');
                    tag.className = 'filter-tag';
                    tag.innerHTML = `
                        ${value}
                        <span class="remove" onclick="removeFilter('${category}', '${value}')">&times;</span>
                    `;
                    container.insertBefore(tag, resetBtn);
                    hasFilters = true;
                });
            });
            
            // Show/hide reset button based on whether there are active filters
            if (resetBtn) {
                resetBtn.style.display = hasFilters ? 'flex' : 'none';
            }
        }

        function removeFilter(category, value) {
            if (activeFilters[category]) {
                activeFilters[category] = activeFilters[category].filter(item => item !== value);
                if (activeFilters[category].length === 0) {
                    delete activeFilters[category];
                }
            }
            
            const checkbox = document.querySelector(`input[onchange*="${category}"][onchange*="${value}"]`);
            if (checkbox) {
                checkbox.checked = false;
            }
            
            if (category === 'color') {
                document.querySelectorAll('.color-swatch').forEach(swatch => {
                    if (swatch.onclick.toString().includes(value)) {
                        swatch.classList.remove('selected');
                    }
                });
            }
            
            updateSelectedFilters();
            updateProductCount();
        }

        const minPriceInput = document.getElementById('minPrice');
        const maxPriceInput = document.getElementById('maxPrice');
        
        if (minPriceInput) {
            minPriceInput.addEventListener('change', function() {
                const min = this.value;
                if (min) {
                    updateFilter('price', `From $${min}`, true);
                }
            });
        }

        if (maxPriceInput) {
            maxPriceInput.addEventListener('change', function() {
                const max = this.value;
                if (max) {
                    updateFilter('price', `Up to $${max}`, true);
                }
            });
        }

        function sortProducts(sortBy) {
            console.log('Sorting by:', sortBy);
            // In a real application, this would sort the products based on the selected criteria
            // For now, we'll just log it and could add visual feedback
            
            // Example sorting logic that could be implemented:
            // switch(sortBy) {
            //     case 'price-low':
            //         // Sort products by price ascending
            //         break;
            //     case 'price-high':
            //         // Sort products by price descending
            //         break;
            //     case 'newest':
            //         // Sort products by date added
            //         break;
            //     case 'popular':
            //         // Sort products by popularity
            //         break;
            //     default:
            //         // Default sorting (featured)
            //         break;
            // }
            
            // After sorting, update the display
            updateProductCount();
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            updateProductCount();
            
            // Initialize pagination event listeners
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            if (prevBtn) {
                prevBtn.addEventListener('click', function() {
                    if (currentPage > 1) {
                        goToPage(currentPage - 1);
                    }
                });
            }
            
            if (nextBtn) {
                nextBtn.addEventListener('click', function() {
                    if (currentPage < totalPages) {
                        goToPage(currentPage + 1);
                    }
                });
            }
            
            // Initialize sort dropdown
            const sortDropdown = document.getElementById('sortBy');
            if (sortDropdown) {
                sortDropdown.addEventListener('change', function() {
                    sortProducts(this.value);
                });
            }
        });
  
