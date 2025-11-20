// JS for _filters_clothing.html

        let activeFilters = {};
        let totalProducts = 24; // Total products available
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
            
            productCountElement.textContent = Math.min(displayedProducts, filteredCount);
            totalProductsElement.textContent = filteredCount;
            
            // Show/hide pagination container
            const paginationContainer = document.querySelector('.pagination-container');
            if (filteredCount > displayedProducts) {
                paginationContainer.style.display = 'flex';
                if (viewMoreElement) viewMoreElement.style.display = 'block';
            } else {
                paginationContainer.style.display = 'none';
                if (viewMoreElement) viewMoreElement.style.display = 'none';
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
            currentRangeElement.textContent = `${startItem}-${endItem}`;
            totalItemsElement.textContent = filteredCount;
            
            // Update prev/next buttons
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;
            
            // Generate page numbers
            generatePageNumbers(pageNumbers);
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
                const firstBtn = createPageButton(1);
                container.appendChild(firstBtn);
                
                if (startPage > 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'page-ellipsis';
                    ellipsis.textContent = '...';
                    container.appendChild(ellipsis);
                }
            }
            
            // Add visible page numbers
            for (let i = startPage; i <= endPage; i++) {
                const pageBtn = createPageButton(i);
                container.appendChild(pageBtn);
            }
            
            // Add last page if not visible
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'page-ellipsis';
                    ellipsis.textContent = '...';
                    container.appendChild(ellipsis);
                }
                
                const lastBtn = createPageButton(totalPages);
                container.appendChild(lastBtn);
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
            document.querySelector('.content-area').scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
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
            
            updateProductCount();
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
        }

        function sortProducts(sortBy) {
            const productGrid = document.getElementById('productGrid');
            const products = Array.from(productGrid.children);
            
            products.sort((a, b) => {
                const priceA = parseFloat(a.querySelector('.product-price').textContent.replace('$', ''));
                const priceB = parseFloat(b.querySelector('.product-price').textContent.replace('$', ''));
                const nameA = a.querySelector('.product-name').textContent;
                const nameB = b.querySelector('.product-name').textContent;
                
                switch(sortBy) {
                    case 'price-low':
                        return priceA - priceB;
                    case 'price-high':
                        return priceB - priceA;
                    case 'name-az':
                        return nameA.localeCompare(nameB);
                    case 'name-za':
                        return nameB.localeCompare(nameA);
                    case 'rating':
                        // Mock rating sort
                        return Math.random() - 0.5;
                    case 'newest':
                        // Mock newest sort
                        return Math.random() - 0.5;
                    default:
                        return 0;
                }
            });
            
            // Clear and re-append sorted products
            productGrid.innerHTML = '';
            products.forEach(product => productGrid.appendChild(product));
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            updateProductCount();
            
            // Add sort functionality
            const sortSelect = document.getElementById('sortBy');
            if (sortSelect) {
                sortSelect.addEventListener('change', function() {
                    if (this.value !== 'default') {
                        sortProducts(this.value);
                    }
                });
            }
            
            // Add pagination event listeners
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    goToPage(currentPage - 1);
                });
            }
            
            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    goToPage(currentPage + 1);
                });
            }
        });

        document.getElementById('minPrice')?.addEventListener('change', function() {
            const min = this.value;
            if (min) {
                updateFilter('price', `From $${min}`, true);
            }
        });

        document.getElementById('maxPrice')?.addEventListener('change', function() {
            const max = this.value;
            if (max) {
                updateFilter('price', `Up to $${max}`, true);
            }
        });

